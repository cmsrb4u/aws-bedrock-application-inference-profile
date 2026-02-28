#!/usr/bin/env python3
"""
Delete Application Inference Profiles.

This script can delete specific profiles or all custom application profiles.
Use with caution - deletion is permanent!
"""

import boto3
import sys
import argparse
from pathlib import Path

# Add parent directory to path for imports
sys.path.append(str(Path(__file__).parent.parent))

from config.settings import REGION, TENANT_CONFIGS

# Initialize Bedrock client
bedrock_client = boto3.client('bedrock', region_name=REGION)

def delete_profile(profile_name):
    """Delete a specific inference profile."""
    try:
        print(f"   Deleting: {profile_name}...")
        bedrock_client.delete_inference_profile(
            inferenceProfileIdentifier=profile_name
        )
        print(f"   ✅ Deleted: {profile_name}")
        return True
    except bedrock_client.exceptions.ResourceNotFoundException:
        print(f"   ⚠️  Profile not found: {profile_name}")
        return False
    except Exception as e:
        print(f"   ❌ Error deleting {profile_name}: {str(e)}")
        return False

def main():
    parser = argparse.ArgumentParser(description='Delete Application Inference Profiles')
    parser.add_argument('--all', action='store_true',
                       help='Delete all custom application profiles')
    parser.add_argument('--tenant', choices=['tenant_a', 'tenant_b', 'tenant_c', 'all'],
                       help='Delete specific tenant profile(s)')
    parser.add_argument('--profile', type=str,
                       help='Delete a specific profile by name')
    parser.add_argument('--force', action='store_true',
                       help='Skip confirmation prompt')

    args = parser.parse_args()

    print("=" * 80)
    print("🗑️  Delete Application Inference Profiles")
    print("=" * 80)
    print(f"Region: {REGION}")
    print("=" * 80)

    profiles_to_delete = []

    if args.all:
        # Get all application profiles
        response = bedrock_client.list_inference_profiles()
        for profile in response.get('inferenceProfileSummaries', []):
            if profile['type'] == 'APPLICATION':
                profiles_to_delete.append(profile['inferenceProfileName'])

        if not profiles_to_delete:
            print("\n⚠️  No application profiles found to delete")
            return

        print(f"\n⚠️  Found {len(profiles_to_delete)} application profiles to delete:")
        for name in profiles_to_delete:
            print(f"   - {name}")

    elif args.tenant:
        if args.tenant == 'all':
            # Delete all tenant profiles
            for tenant_id, config in TENANT_CONFIGS.items():
                profiles_to_delete.append(config['profile_name'])
        else:
            # Delete specific tenant profile
            if args.tenant in TENANT_CONFIGS:
                profiles_to_delete.append(TENANT_CONFIGS[args.tenant]['profile_name'])
            else:
                print(f"\n❌ Unknown tenant: {args.tenant}")
                return

        print(f"\n📋 Profiles to delete:")
        for name in profiles_to_delete:
            print(f"   - {name}")

    elif args.profile:
        profiles_to_delete.append(args.profile)
        print(f"\n📋 Profile to delete: {args.profile}")

    else:
        print("\n❌ Please specify profiles to delete:")
        print("   --all: Delete all application profiles")
        print("   --tenant [name]: Delete specific tenant profile")
        print("   --profile [name]: Delete specific profile by name")
        return

    # Confirmation
    if not args.force:
        print("\n⚠️  WARNING: Deletion is permanent and cannot be undone!")
        confirmation = input("   Type 'DELETE' to confirm: ")
        if confirmation != 'DELETE':
            print("\n❌ Deletion cancelled")
            return

    # Delete profiles
    print("\n🗑️  Deleting profiles...")
    print("-" * 60)

    deleted_count = 0
    failed_count = 0

    for profile_name in profiles_to_delete:
        if delete_profile(profile_name):
            deleted_count += 1
        else:
            failed_count += 1

    # Summary
    print("\n" + "=" * 80)
    print("📊 Deletion Summary")
    print("=" * 80)
    print(f"   Deleted: {deleted_count}")
    print(f"   Failed: {failed_count}")

    if deleted_count > 0:
        print("\n✅ Profiles deleted successfully")

        # Update config file if tenant profiles were deleted
        config_file = Path(__file__).parent.parent / 'config' / 'tenant_profiles.json'
        if config_file.exists():
            print(f"\n💡 Note: You may want to run create_tenant_profiles.py to recreate profiles")

if __name__ == "__main__":
    main()