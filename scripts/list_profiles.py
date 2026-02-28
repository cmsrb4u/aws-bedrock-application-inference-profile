#!/usr/bin/env python3
"""
List all Application Inference Profiles in the account.

This script lists both system profiles and custom application profiles.
"""

import boto3
import sys
from pathlib import Path
from datetime import datetime

# Add parent directory to path for imports
sys.path.append(str(Path(__file__).parent.parent))

from config.settings import REGION

# Initialize Bedrock client
bedrock_client = boto3.client('bedrock', region_name=REGION)

print("=" * 80)
print("📋 Listing Application Inference Profiles")
print("=" * 80)
print(f"Region: {REGION}")
print("=" * 80)

try:
    # List all inference profiles
    response = bedrock_client.list_inference_profiles()

    profiles = response.get('inferenceProfileSummaries', [])

    if not profiles:
        print("\n⚠️  No inference profiles found")
        sys.exit(0)

    # Separate system and application profiles
    system_profiles = []
    application_profiles = []

    for profile in profiles:
        if profile['type'] == 'SYSTEM_DEFINED':
            system_profiles.append(profile)
        else:
            application_profiles.append(profile)

    # Display system profiles
    if system_profiles:
        print(f"\n🔧 System Profiles ({len(system_profiles)})")
        print("-" * 60)
        for profile in system_profiles:
            print(f"\n   ID: {profile['inferenceProfileId']}")
            print(f"   Name: {profile['inferenceProfileName']}")
            print(f"   Type: {profile['type']}")
            print(f"   Status: {profile['status']}")
            print(f"   Models: {', '.join(profile.get('models', []))}")
            if 'description' in profile:
                print(f"   Description: {profile['description']}")

    # Display application profiles
    if application_profiles:
        print(f"\n🏢 Application Profiles ({len(application_profiles)})")
        print("-" * 60)
        for profile in application_profiles:
            print(f"\n   Name: {profile['inferenceProfileName']}")
            print(f"   ID: {profile['inferenceProfileId']}")
            print(f"   ARN: {profile['inferenceProfileArn']}")
            print(f"   Type: {profile['type']}")
            print(f"   Status: {profile['status']}")
            print(f"   Models: {', '.join(profile.get('models', []))}")

            # Get detailed information
            try:
                detailed = bedrock_client.get_inference_profile(
                    inferenceProfileIdentifier=profile['inferenceProfileId']
                )

                # Display tags if present
                if 'tags' in detailed:
                    print(f"   Tags:")
                    for tag in detailed['tags']:
                        print(f"      - {tag['key']}: {tag['value']}")

                # Display creation time
                if 'createdAt' in detailed:
                    created_at = detailed['createdAt']
                    if isinstance(created_at, str):
                        print(f"   Created: {created_at}")
                    else:
                        print(f"   Created: {datetime.fromtimestamp(created_at).isoformat()}")

            except Exception as e:
                print(f"   ⚠️  Could not fetch details: {str(e)[:50]}")

    # Summary
    print("\n" + "=" * 80)
    print("📊 Summary")
    print("=" * 80)
    print(f"   Total Profiles: {len(profiles)}")
    print(f"   System Profiles: {len(system_profiles)}")
    print(f"   Application Profiles: {len(application_profiles)}")

    # Check for our tenant profiles
    tenant_profile_names = ['aip-tenant-a-marketing', 'aip-tenant-b-sales', 'aip-tenant-c-engineering']
    found_tenant_profiles = []

    for profile in application_profiles:
        if profile['inferenceProfileName'] in tenant_profile_names:
            found_tenant_profiles.append(profile['inferenceProfileName'])

    if found_tenant_profiles:
        print(f"\n✅ Found {len(found_tenant_profiles)} tenant profiles:")
        for name in found_tenant_profiles:
            print(f"   - {name}")
    else:
        print("\n⚠️  No tenant profiles found. Run create_tenant_profiles.py to create them.")

except Exception as e:
    print(f"\n❌ Error listing profiles: {str(e)}")
    sys.exit(1)

print("\n" + "=" * 80)
print("✅ Profile listing complete")
print("=" * 80)