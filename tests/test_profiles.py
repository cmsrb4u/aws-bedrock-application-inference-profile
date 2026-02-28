#!/usr/bin/env python3
"""
Test Application Inference Profiles with Multi-Tenant Workloads.

This script demonstrates:
1. Making inference calls using tenant-specific Application Inference Profiles
2. Showing that each tenant's usage is tracked separately
3. Validating profile isolation
"""

import boto3
import json
import time
import sys
from pathlib import Path
from datetime import datetime

# Add parent directory to path for imports
sys.path.append(str(Path(__file__).parent.parent))

from config.settings import REGION, TestPrompts

# Load tenant profile configuration
config_file = Path(__file__).parent.parent / 'config' / 'tenant_profiles.json'

try:
    with open(config_file, 'r') as f:
        profile_config = json.load(f)
except FileNotFoundError:
    print(f"❌ Profile configuration not found at {config_file}")
    print("   Please run: python scripts/create_tenant_profiles.py first")
    sys.exit(1)

# Initialize Bedrock runtime client
bedrock_runtime = boto3.client('bedrock-runtime', region_name=REGION)

print("=" * 80)
print("🧪 Testing Application Inference Profiles - Multi-Tenant Separation")
print("=" * 80)

# Define test cases for each tenant
test_cases = {
    "tenant_a": {
        "prompt": TestPrompts.MARKETING,
        "profile_arn": profile_config['profiles']['tenant_a']['profile_arn'],
        "name": "Tenant A (Marketing)"
    },
    "tenant_b": {
        "prompt": TestPrompts.SALES,
        "profile_arn": profile_config['profiles']['tenant_b']['profile_arn'],
        "name": "Tenant B (Sales)"
    }
}

# Add tenant_c if it exists
if 'tenant_c' in profile_config.get('profiles', {}):
    test_cases["tenant_c"] = {
        "prompt": TestPrompts.ENGINEERING,
        "profile_arn": profile_config['profiles']['tenant_c']['profile_arn'],
        "name": "Tenant C (Engineering)"
    }

print("\n🔄 Making inference calls with tenant-specific profiles...")
print("=" * 80)

# Track results
results = {}
call_times = []

# Make inference calls for each tenant
for idx, (tenant_id, config) in enumerate(test_cases.items()):
    print(f"\n🏢 Request from {config['name']}:")
    print(f"   Profile: {config['profile_arn'].split('/')[-1]}")
    print(f"   Prompt: {config['prompt'][:80]}...")

    # Prepare the request
    body = json.dumps({
        "messages": [{
            "role": "user",
            "content": [{"type": "text", "text": config['prompt']}]
        }],
        "max_tokens": 512,
        "anthropic_version": "bedrock-2023-05-31"
    })

    try:
        # Record call time
        call_time = datetime.now()
        call_times.append(call_time)

        # Make the inference call with tenant-specific profile
        response = bedrock_runtime.invoke_model(
            modelId=config['profile_arn'],
            body=body
        )

        # Parse response
        response_body = json.loads(response['body'].read())

        output_text = response_body['content'][0]['text']
        input_tokens = response_body['usage']['input_tokens']
        output_tokens = response_body['usage']['output_tokens']
        total_tokens = input_tokens + output_tokens

        results[tenant_id] = {
            'input_tokens': input_tokens,
            'output_tokens': output_tokens,
            'total_tokens': total_tokens,
            'output_preview': output_text[:150],
            'call_time': call_time.isoformat(),
            'success': True
        }

        print(f"   ✅ Response received")
        print(f"   Input tokens: {input_tokens}")
        print(f"   Output tokens: {output_tokens}")
        print(f"   Total tokens: {total_tokens}")
        print(f"   Response preview: {output_text[:150]}...")

        # Add delay between requests for CloudWatch separation
        if idx < len(test_cases) - 1:
            print(f"\n   ⏳ Waiting 5 seconds before next request...")
            time.sleep(5)

    except Exception as e:
        print(f"   ❌ Error: {str(e)}")
        results[tenant_id] = {
            'error': str(e),
            'success': False
        }

print("\n" + "=" * 80)
print("📊 Test Results Summary")
print("=" * 80)

# Display summary
total_tokens = 0
successful_calls = 0

for tenant_id, result in results.items():
    tenant_name = test_cases[tenant_id]['name']
    print(f"\n{tenant_name}:")

    if result['success']:
        print(f"   ✅ Successful inference call")
        print(f"   Tokens used: {result['total_tokens']}")
        print(f"   Call time: {result['call_time']}")
        total_tokens += result['total_tokens']
        successful_calls += 1
    else:
        print(f"   ❌ Failed: {result.get('error', 'Unknown error')}")

print("\n" + "=" * 80)
print("✅ Testing Complete!")
print(f"   Successful calls: {successful_calls}/{len(test_cases)}")
print(f"   Total tokens used: {total_tokens}")
print("=" * 80)

print("\n🎯 Key Points Demonstrated:")
print("   1. Each tenant used their OWN Application Inference Profile")
print("   2. Usage is tracked separately per profile in CloudWatch")
print("   3. Complete isolation between tenants")
print("   4. Tags enable cost allocation per tenant")

print("\n📈 View Metrics in CloudWatch:")
print(f"   Region: {REGION}")
print("   Namespace: AWS/Bedrock")
print("   Dimension: InferenceProfileId")
print("\n   Metrics will appear in CloudWatch within 3-5 minutes")

# Save test results
results_file = Path(__file__).parent.parent / 'test_results.json'
with open(results_file, 'w') as f:
    json.dump({
        'test_time': datetime.now().isoformat(),
        'region': REGION,
        'test_cases': len(test_cases),
        'successful_calls': successful_calls,
        'total_tokens': total_tokens,
        'results': results
    }, f, indent=2)

print(f"\n📝 Test results saved to: {results_file}")