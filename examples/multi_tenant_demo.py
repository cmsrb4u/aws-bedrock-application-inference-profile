#!/usr/bin/env python3
"""
Complete Multi-Tenant Demo with Application Inference Profiles.

This demo shows a complete workflow:
1. Create tenant profiles
2. Make concurrent inference calls
3. Monitor metrics
4. Generate reports
"""

import boto3
import json
import time
import concurrent.futures
from pathlib import Path
import sys
from datetime import datetime

# Add parent directory to path for imports
sys.path.append(str(Path(__file__).parent.parent))

from config.settings import REGION, TENANT_CONFIGS, TestPrompts

print("=" * 80)
print("🎯 Complete Multi-Tenant Demo with Application Inference Profiles")
print("=" * 80)

# Initialize clients
bedrock_client = boto3.client('bedrock', region_name=REGION)
bedrock_runtime = boto3.client('bedrock-runtime', region_name=REGION)

# Load or create profiles
config_file = Path(__file__).parent.parent / 'config' / 'tenant_profiles.json'

if config_file.exists():
    print("\n📋 Loading existing tenant profiles...")
    with open(config_file, 'r') as f:
        profile_config = json.load(f)
    print(f"   ✅ Loaded {len(profile_config['profiles'])} profiles")
else:
    print("\n⚠️  No profiles found. Please run: python scripts/create_tenant_profiles.py")
    sys.exit(1)

# Define tenant workloads
workloads = {
    "tenant_a": {
        "name": "Marketing Department",
        "profile_arn": profile_config['profiles']['tenant_a']['profile_arn'],
        "prompts": [
            "Create a marketing slogan for eco-friendly products",
            "Write a brief email campaign for B2B software",
            "Generate social media content ideas for tech startups"
        ]
    },
    "tenant_b": {
        "name": "Sales Department",
        "profile_arn": profile_config['profiles']['tenant_b']['profile_arn'],
        "prompts": [
            "Create a sales pitch for cloud migration services",
            "Write follow-up email templates for prospects",
            "Generate objection handling responses for SaaS sales"
        ]
    }
}

# Add tenant_c if it exists
if 'tenant_c' in profile_config.get('profiles', {}):
    workloads["tenant_c"] = {
        "name": "Engineering Department",
        "profile_arn": profile_config['profiles']['tenant_c']['profile_arn'],
        "prompts": [
            "Write a Python function for data validation",
            "Explain microservices architecture best practices",
            "Create a SQL query for user analytics"
        ]
    }

def make_inference_call(tenant_id, prompt, profile_arn):
    """Make a single inference call for a tenant."""
    try:
        body = json.dumps({
            "messages": [{
                "role": "user",
                "content": [{"type": "text", "text": prompt}]
            }],
            "max_tokens": 256,
            "anthropic_version": "bedrock-2023-05-31"
        })

        start_time = time.time()
        response = bedrock_runtime.invoke_model(
            modelId=profile_arn,
            body=body
        )
        latency = (time.time() - start_time) * 1000  # Convert to milliseconds

        response_body = json.loads(response['body'].read())

        return {
            'tenant_id': tenant_id,
            'prompt': prompt[:50] + '...',
            'input_tokens': response_body['usage']['input_tokens'],
            'output_tokens': response_body['usage']['output_tokens'],
            'latency_ms': latency,
            'success': True,
            'response_preview': response_body['content'][0]['text'][:100] + '...'
        }

    except Exception as e:
        return {
            'tenant_id': tenant_id,
            'prompt': prompt[:50] + '...',
            'error': str(e),
            'success': False
        }

print("\n🚀 Starting Multi-Tenant Inference Demo")
print("=" * 80)

# Track all results
all_results = []
start_time = datetime.now()

# Process workloads concurrently
with concurrent.futures.ThreadPoolExecutor(max_workers=5) as executor:
    futures = []

    for tenant_id, workload in workloads.items():
        print(f"\n🏢 Submitting workload for {workload['name']}")
        print(f"   Profile: {workload['profile_arn'].split('/')[-1]}")
        print(f"   Prompts: {len(workload['prompts'])}")

        for prompt in workload['prompts']:
            future = executor.submit(
                make_inference_call,
                tenant_id,
                prompt,
                workload['profile_arn']
            )
            futures.append(future)

    print("\n⏳ Processing inference calls concurrently...")
    print("-" * 60)

    # Wait for all futures to complete
    completed = 0
    for future in concurrent.futures.as_completed(futures):
        result = future.result()
        all_results.append(result)
        completed += 1

        if result['success']:
            print(f"   ✅ [{completed}/{len(futures)}] {result['tenant_id']}: "
                  f"{result['input_tokens']} + {result['output_tokens']} tokens, "
                  f"{result['latency_ms']:.0f}ms")
        else:
            print(f"   ❌ [{completed}/{len(futures)}] {result['tenant_id']}: "
                  f"Error - {result.get('error', 'Unknown')[:50]}")

end_time = datetime.now()
total_duration = (end_time - start_time).total_seconds()

# Generate summary report
print("\n" + "=" * 80)
print("📊 Multi-Tenant Demo Summary Report")
print("=" * 80)

print(f"\n⏱️  Execution Time: {total_duration:.2f} seconds")
print(f"📞 Total Calls: {len(all_results)}")
print(f"✅ Successful: {sum(1 for r in all_results if r['success'])}")
print(f"❌ Failed: {sum(1 for r in all_results if not r['success'])}")

# Per-tenant statistics
print("\n📈 Per-Tenant Statistics:")
print("-" * 60)

for tenant_id, workload in workloads.items():
    tenant_results = [r for r in all_results if r['tenant_id'] == tenant_id]

    if tenant_results:
        successful = [r for r in tenant_results if r['success']]

        if successful:
            total_input = sum(r['input_tokens'] for r in successful)
            total_output = sum(r['output_tokens'] for r in successful)
            total_tokens = total_input + total_output
            avg_latency = sum(r['latency_ms'] for r in successful) / len(successful)

            print(f"\n{workload['name']}:")
            print(f"   Calls: {len(tenant_results)} ({len(successful)} successful)")
            print(f"   Total Tokens: {total_tokens} (Input: {total_input}, Output: {total_output})")
            print(f"   Average Latency: {avg_latency:.0f}ms")
            print(f"   Profile: {workload['profile_arn'].split('/')[-1]}")
        else:
            print(f"\n{workload['name']}:")
            print(f"   All {len(tenant_results)} calls failed")

# Save results to file
output_dir = Path(__file__).parent.parent / 'output'
output_dir.mkdir(exist_ok=True)

results_file = output_dir / f'demo_results_{datetime.now().strftime("%Y%m%d_%H%M%S")}.json'
with open(results_file, 'w') as f:
    json.dump({
        'start_time': start_time.isoformat(),
        'end_time': end_time.isoformat(),
        'duration_seconds': total_duration,
        'total_calls': len(all_results),
        'results': all_results
    }, f, indent=2)

print(f"\n📝 Detailed results saved to: {results_file}")

# Key takeaways
print("\n" + "=" * 80)
print("🎯 Key Takeaways")
print("=" * 80)

print("\n1. **Concurrent Processing**: Multiple tenants processed simultaneously")
print("2. **Profile Isolation**: Each tenant used their own AIP")
print("3. **Metrics Tracking**: Usage tracked separately per profile")
print("4. **Cost Attribution**: Tags enable per-tenant cost allocation")
print("5. **Scalability**: System handles multiple concurrent workloads")

print("\n📈 Next Steps:")
print("   1. View metrics in CloudWatch (wait 3-5 minutes)")
print("   2. Check Cost Explorer for per--tag cost breakdown")
print("   3. Set up CloudWatch alarms for usage thresholds")
print("   4. Implement quota limits with CCWB integration")

print("\n✅ Multi-Tenant Demo Complete!")
print("=" * 80)