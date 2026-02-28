#!/usr/bin/env python3
"""
Invoke Application Inference Profiles and Visualize Metrics.

This script:
1. Makes inference calls using tenant-specific profiles
2. Waits for CloudWatch metrics to propagate
3. Fetches the metrics
4. Creates comparison visualizations
"""

import boto3
import json
import time
import sys
from pathlib import Path
from datetime import datetime, timedelta
import matplotlib.pyplot as plt

# Add parent directory to path for imports
sys.path.append(str(Path(__file__).parent.parent))

from config.settings import REGION, CloudWatchConfig, TestPrompts

print("=" * 80)
print("🚀 Invoking Application Inference Profiles & Generating Metrics")
print("=" * 80)

# Load tenant profiles
config_file = Path(__file__).parent.parent / 'config' / 'tenant_profiles.json'

try:
    with open(config_file, 'r') as f:
        profile_config = json.load(f)
except FileNotFoundError:
    print(f"❌ Profile configuration not found at {config_file}")
    print("   Please run: python scripts/create_tenant_profiles.py first")
    sys.exit(1)

bedrock_runtime = boto3.client('bedrock-runtime', region_name=REGION)
cloudwatch = boto3.client('cloudwatch', region_name=REGION)

# Prepare test scenarios
test_prompts = {
    "tenant_a": {
        "prompt": TestPrompts.ANALYTICS,
        "profile_arn": profile_config['profiles']['tenant_a']['profile_arn'],
        "name": "Tenant A (Marketing)",
        "color": "blue"
    },
    "tenant_b": {
        "prompt": TestPrompts.CREATIVE,
        "profile_arn": profile_config['profiles']['tenant_b']['profile_arn'],
        "name": "Tenant B (Sales)",
        "color": "green"
    }
}

print("\n📞 Making inference calls...")
print("-" * 80)

call_times = []
results = {}

# Make multiple calls for each tenant to generate metrics
num_calls_per_tenant = 3

for tenant_id, config in test_prompts.items():
    print(f"\n🏢 {config['name']}")
    print(f"   Profile: {config['profile_arn'].split('/')[-1]}")

    tenant_results = []

    for i in range(num_calls_per_tenant):
        body = json.dumps({
            "messages": [{
                "role": "user",
                "content": [{"type": "text", "text": f"{config['prompt']} (Call {i+1})"}]
            }],
            "max_tokens": 256,
            "anthropic_version": "bedrock-2023-05-31"
        })

        call_time = datetime.now()
        call_times.append(call_time)

        try:
            response = bedrock_runtime.invoke_model(
                modelId=config['profile_arn'],
                body=body
            )

            response_body = json.loads(response['body'].read())
            input_tokens = response_body['usage']['input_tokens']
            output_tokens = response_body['usage']['output_tokens']

            tenant_results.append({
                'input_tokens': input_tokens,
                'output_tokens': output_tokens,
                'call_time': call_time
            })

            print(f"   Call {i+1}: ✅ {input_tokens} input, {output_tokens} output tokens")

        except Exception as e:
            print(f"   Call {i+1}: ❌ Error - {str(e)[:50]}")

        time.sleep(2)  # Small delay between calls

    results[tenant_id] = tenant_results

print("\n" + "=" * 80)
print("⏳ Waiting for CloudWatch metrics to propagate...")
print("   This typically takes 3-5 minutes. Please be patient...")
print("=" * 80)

# Wait for metrics to propagate
wait_time = 240  # 4 minutes
for i in range(wait_time // 30):
    remaining = wait_time - (i * 30)
    print(f"   ⏱️  {remaining} seconds remaining...")
    time.sleep(30)

print("   ✅ Wait complete - fetching metrics now")

# Function to fetch metrics for a profile
def fetch_metrics(profile_arn, tenant_name):
    """Fetch CloudWatch metrics for a specific profile."""

    profile_id = profile_arn.split('/')[-1]
    end_time = datetime.utcnow()
    start_time = end_time - timedelta(minutes=CloudWatchConfig.LOOKBACK_MINUTES)

    print(f"\n{'=' * 60}")
    print(f"📊 Fetching metrics for {tenant_name}")
    print(f"   Profile ID: {profile_id}")
    print(f"{'=' * 60}")

    metrics_data = {}

    # Fetch each metric type
    for metric_key, metric_name in CloudWatchConfig.METRICS.items():
        if metric_key in ["THROTTLED", "ERRORS"]:  # Skip error metrics for now
            continue

        try:
            response = cloudwatch.get_metric_statistics(
                Namespace=CloudWatchConfig.NAMESPACE,
                MetricName=metric_name,
                Dimensions=[{'Name': 'InferenceProfileId', 'Value': profile_id}],
                StartTime=start_time,
                EndTime=end_time,
                Period=CloudWatchConfig.PERIOD,
                Statistics=['Sum', 'Average', 'Maximum']
            )

            if response['Datapoints']:
                total = sum(dp['Sum'] for dp in response['Datapoints'])
                metrics_data[metric_key] = {
                    'total': total,
                    'datapoints': sorted(response['Datapoints'], key=lambda x: x['Timestamp'])
                }
                print(f"   {metric_name}: {int(total)}")
            else:
                print(f"   {metric_name}: No data")
                metrics_data[metric_key] = {'total': 0, 'datapoints': []}

        except Exception as e:
            print(f"   Error fetching {metric_name}: {str(e)[:50]}")
            metrics_data[metric_key] = {'total': 0, 'datapoints': []}

    return metrics_data

# Fetch metrics for both tenants
print("\n📈 Fetching CloudWatch Metrics")
print("=" * 80)

tenant_metrics = {}
for tenant_id, config in test_prompts.items():
    metrics = fetch_metrics(config['profile_arn'], config['name'])
    tenant_metrics[tenant_id] = metrics

# Create visualization
print("\n📊 Creating Visualization")
print("=" * 80)

fig, axes = plt.subplots(2, 2, figsize=(12, 8))
fig.suptitle('Application Inference Profile Metrics by Tenant', fontsize=16)

# Plot 1: Invocations comparison
ax1 = axes[0, 0]
tenants = list(test_prompts.keys())
invocations = [tenant_metrics[t].get('INVOCATIONS', {}).get('total', 0) for t in tenants]
colors = [test_prompts[t]['color'] for t in tenants]
bars1 = ax1.bar([test_prompts[t]['name'] for t in tenants], invocations, color=colors)
ax1.set_title('Total Invocations')
ax1.set_ylabel('Count')
ax1.grid(True, alpha=0.3)

# Add value labels on bars
for bar, val in zip(bars1, invocations):
    height = bar.get_height()
    ax1.text(bar.get_x() + bar.get_width()/2., height,
             f'{int(val)}', ha='center', va='bottom')

# Plot 2: Token usage comparison
ax2 = axes[0, 1]
input_tokens = [tenant_metrics[t].get('INPUT_TOKENS', {}).get('total', 0) for t in tenants]
output_tokens = [tenant_metrics[t].get('OUTPUT_TOKENS', {}).get('total', 0) for t in tenants]

x_pos = range(len(tenants))
width = 0.35

bars2 = ax2.bar([p - width/2 for p in x_pos], input_tokens, width,
                label='Input Tokens', color=['lightblue', 'lightgreen'])
bars3 = ax2.bar([p + width/2 for p in x_pos], output_tokens, width,
                label='Output Tokens', color=['darkblue', 'darkgreen'])

ax2.set_title('Token Usage by Tenant')
ax2.set_ylabel('Tokens')
ax2.set_xticks(x_pos)
ax2.set_xticklabels([test_prompts[t]['name'] for t in tenants])
ax2.legend()
ax2.grid(True, alpha=0.3)

# Plot 3: Time series of invocations
ax3 = axes[1, 0]
for tenant_id, config in test_prompts.items():
    datapoints = tenant_metrics[tenant_id].get('INVOCATIONS', {}).get('datapoints', [])
    if datapoints:
        times = [dp['Timestamp'] for dp in datapoints]
        values = [dp['Sum'] for dp in datapoints]
        ax3.plot(times, values, marker='o', label=config['name'], color=config['color'])

ax3.set_title('Invocations Over Time')
ax3.set_xlabel('Time')
ax3.set_ylabel('Invocations')
ax3.legend()
ax3.grid(True, alpha=0.3)

# Rotate x-axis labels for better readability
for label in ax3.get_xticklabels():
    label.set_rotation(45) ax3.set_xticklabels(ax3.get_xticklabels(), rotation=45, ha='right')

# Plot 4: Total tokens per tenant
ax4 = axes[1, 1]
total_tokens = [
    tenant_metrics[t].get('INPUT_TOKENS', {}).get('total', 0) +
    tenant_metrics[t].get('OUTPUT_TOKENS', {}).get('total', 0)
    for t in tenants
]

bars4 = ax4.bar([test_prompts[t]['name'] for t in tenants], total_tokens, color=colors)
ax4.set_title('Total Tokens Used')
ax4.set_ylabel('Tokens')
ax4.grid(True, alpha=0.3)

# Add value labels on bars
for bar, val in zip(bars4, total_tokens):
    height = bar.get_height()
    ax4.text(bar.get_x() + bar.get_width()/2., height,
             f'{int(val)}', ha='center', va='bottom')

plt.tight_layout()

# Save the plot
output_dir = Path(__file__).parent.parent / 'output'
output_dir.mkdir(exist_ok=True)
plot_file = output_dir / f'metrics_{datetime.now().strftime("%Y%m%d_%H%M%S")}.png'
plt.savefig(plot_file, dpi=150, bbox_inches='tight')
print(f"   ✅ Visualization saved to: {plot_file}")

# Display the plot (if running interactively)
try:
    plt.show()
except:
    print("   ℹ️  Unable to display plot (running in non-interactive mode)")

# Summary
print("\n" + "=" * 80)
print("📊 Metrics Summary")
print("=" * 80)

for tenant_id, config in test_prompts.items():
    metrics = tenant_metrics[tenant_id]
    print(f"\n{config['name']}:")
    print(f"   Invocations: {int(metrics.get('INVOCATIONS', {}).get('total', 0))}")
    print(f"   Input Tokens: {int(metrics.get('INPUT_TOKENS', {}).get('total', 0))}")
    print(f"   Output Tokens: {int(metrics.get('OUTPUT_TOKENS', {}).get('total', 0))}")
    print(f"   Total Tokens: {int(metrics.get('INPUT_TOKENS', {}).get('total', 0) + metrics.get('OUTPUT_TOKENS', {}).get('total', 0))}")

print("\n" + "=" * 80)
print("✅ Complete! Metrics have been fetched and visualized")
print("=" * 80)

print("\n🎯 Key Takeaways:")
print("   1. Each tenant's usage is tracked separately")
print("   2. Metrics are available in CloudWatch with InferenceProfileId dimension")
print("   3. Complete isolation enables accurate cost allocation")
print("   4. Visualizations help monitor multi-tenant usage patterns")