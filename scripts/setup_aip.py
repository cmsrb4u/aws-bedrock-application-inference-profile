#!/usr/bin/env python3
"""
Setup script for AWS Bedrock Application Inference Profiles environment.

This script initializes the boto3 clients and validates access to Bedrock.
"""

import boto3
import sys
from pathlib import Path

# Add parent directory to path for imports
sys.path.append(str(Path(__file__).parent.parent))

from config.settings import REGION, ModelId

print("=" * 80)
print("🚀 Setting up AWS Bedrock Application Inference Profiles Environment")
print("=" * 80)

try:
    # Initialize Bedrock clients
    bedrock_client = boto3.client('bedrock', region_name=REGION)
    bedrock_runtime = boto3.client('bedrock-runtime', region_name=REGION)

    print(f"\n✅ Bedrock Client initialized")
    print(f"   Region: {REGION}")
    print(f"   Service: bedrock (for AIP management)")

    print(f"\n✅ Bedrock Runtime Client initialized")
    print(f"   Region: {REGION}")
    print(f"   Service: bedrock-runtime (for model inference)")

    # Validate access by listing inference profiles
    print(f"\n🔍 Validating Bedrock access...")
    response = bedrock_client.list_inference_profiles(maxResults=1)

    if 'inferenceProfileSummaries' in response:
        print(f"   ✅ Successfully connected to Bedrock")
        print(f"   Found {len(response['inferenceProfileSummaries'])} system profiles")
    else:
        print(f"   ⚠️  No inference profiles found")

    # Check for the default system profile
    print(f"\n📋 Checking for default system profile...")
    print(f"   Looking for: {ModelId.DEFAULT}")

    response = bedrock_client.list_inference_profiles()
    system_profile_found = False

    for profile in response.get('inferenceProfileSummaries', []):
        if profile['inferenceProfileId'] == ModelId.DEFAULT:
            system_profile_found = True
            print(f"   ✅ System profile found")
            print(f"   ARN: {profile['inferenceProfileArn']}")
            break

    if not system_profile_found:
        print(f"   ❌ System profile not found: {ModelId.DEFAULT}")
        print(f"   Please ensure you have access to Claude models in Bedrock")

except Exception as e:
    print(f"\n❌ Error during setup: {str(e)}")
    print(f"\n📝 Troubleshooting:")
    print(f"   1. Ensure AWS credentials are configured: aws configure")
    print(f"   2. Verify Bedrock access in region: {REGION}")
    print(f"   3. Check IAM permissions for bedrock:* actions")
    sys.exit(1)

print("\n" + "=" * 80)
print("✅ Setup Complete! Environment is ready for Application Inference Profiles")
print("=" * 80)

print("\n💡 Next Steps:")
print("   1. Run: python scripts/create_tenant_profiles.py")
print("   2. Run: python scripts/test_profiles.py")
print("   3. Run: python scripts/invoke_and_visualize.py")