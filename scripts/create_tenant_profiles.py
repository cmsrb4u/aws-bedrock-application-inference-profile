#!/usr/bin/env python3
"""
Create Application Inference Profiles for Multi-Tenant Architecture.

This script creates separate Application Inference Profiles for different tenants,
each with their own tags for cost tracking and usage monitoring.
"""

import boto3
import json
import sys
from pathlib import Path

# Add parent directory to path for imports
sys.path.append(str(Path(__file__).parent.parent))

from config.settings import REGION, ModelId, TENANT_CONFIGS

# Initialize Bedrock client
bedrock_client = boto3.client('bedrock', region_name=REGION)

print("=" * 80)
print("🏗️  Creating Application Inference Profiles for Multi-Tenant Setup")
print("=" * 80)

# Get the system inference profile ARN to copy from
print(f"\n📋 Source Model Configuration:")
print(f"   System Inference Profile: {ModelId.DEFAULT}")

# Find the system profile ARN
try:
    response = bedrock_client.list_inference_profiles()
    system_profile_arn = None

    for profile in response['inferenceProfileSummaries']:
        if profile['inferenceProfileId'] == ModelId.DEFAULT:
            system_profile_arn = profile['inferenceProfileArn']
            print(f"   System Profile ARN: {system_profile_arn}")
            break

    if not system_profile_arn:
        print(f"❌ Could not find system profile ARN for {ModelId.DEFAULT}")
        sys.exit(1)

except Exception as e:
    print(f"❌ Error listing inference profiles: {e}")
    sys.exit(1)

print("\n" + "=" * 80)

# Create Application Inference Profiles for each tenant
created_profiles = {}

for tenant_id, config in TENANT_CONFIGS.items():
    print(f"\n🏢 Creating profile for {tenant_id.upper().replace('_', ' ')}...")
    print(f"   Profile Name: {config['profile_name']}")
    print(f"   Description: {config['description']}")
    print(f"   Tags: {len(config['tags'])} tags")

    try:
        response = bedrock_client.create_inference_profile(
            inferenceProfileName=config['profile_name'],
            description=config['description'],
            modelSource={
                'copyFrom': system_profile_arn
            },
            tags=config['tags']
        )

        profile_arn = response['inferenceProfileArn']
        status = response['status']

        created_profiles[tenant_id] = {
            'profile_name': config['profile_name'],
            'profile_arn': profile_arn,
            'status': status,
            'tags': config['tags']
        }

        print(f"   ✅ Profile created successfully!")
        print(f"   ARN: {profile_arn}")
        print(f"   Status: {status}")

    except bedrock_client.exceptions.ResourceNotFoundException as e:
        print(f"   ❌ Error: Model not found - {e}")
    except bedrock_client.exceptions.ValidationException as e:
        print(f"   ❌ Validation error - {e}")
    except Exception as e:
        # Check if profile already exists
        if "already exists" in str(e).lower() or "ConflictException" in str(e):
            print(f"   ⚠️  Profile already exists, fetching existing profile...")
            try:
                # Get the existing profile
                existing_response = bedrock_client.get_inference_profile(
                    inferenceProfileIdentifier=config['profile_name']
                )
                profile_arn = existing_response['inferenceProfileArn']
                status = existing_response['status']

                created_profiles[tenant_id] = {
                    'profile_name': config['profile_name'],
                    'profile_arn': profile_arn,
                    'status': status,
                    'tags': config['tags']
                }

                print(f"   ✅ Using existing profile")
                print(f"   ARN: {profile_arn}")
                print(f"   Status: {status}")
            except Exception as fetch_error:
                print(f"   ❌ Error fetching existing profile: {fetch_error}")
        else:
            print(f"   ❌ Error creating profile: {e}")

print("\n" + "=" * 80)
print("📊 Summary of Application Inference Profiles")
print("=" * 80)

for tenant_id, profile_info in created_profiles.items():
    print(f"\n{tenant_id.upper().replace('_', ' ')}:")
    print(f"   Name: {profile_info['profile_name']}")
    print(f"   ARN: {profile_info['profile_arn']}")
    print(f"   Status: {profile_info['status']}")
    print(f"   Tags:")
    for tag in profile_info['tags']:
        print(f"      - {tag['key']}: {tag['value']}")

# Save profile information to a file for later use
profile_config = {
    'region': REGION,
    'system_profile_arn': system_profile_arn,
    'profiles': created_profiles
}

output_file = Path(__file__).parent.parent / 'config' / 'tenant_profiles.json'
with open(output_file, 'w') as f:
    json.dump(profile_config, f, indent=2)

print("\n" + "=" * 80)
print("✅ Setup Complete!")
print(f"   Profile configuration saved to: {output_file}")
print("=" * 80)

print("\n💡 Next Steps:")
print("   1. Test profiles: python scripts/test_profiles.py")
print("   2. Generate metrics: python scripts/invoke_and_visualize.py")
print("   3. View in CloudWatch: Check metrics with InferenceProfileId dimension")