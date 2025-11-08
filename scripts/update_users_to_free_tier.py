#!/usr/bin/env python3
"""
Script to update all existing users to free tier with default values.
This ensures all users have subscription_tier, meal_plans_generated_this_week, and week_start_for_limit fields.
"""

import sys
import os
from datetime import datetime

# Add parent directory to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from dotenv import load_dotenv

# Load environment variables
load_dotenv()
load_dotenv('.env.local', override=True)

from google.cloud import firestore

# Initialize Firestore client
project_id = os.getenv("GOOGLE_CLOUD_PROJECT")
if project_id:
    db = firestore.Client(project=project_id)
else:
    db = firestore.Client()

def update_all_users_to_free_tier():
    """Update all users in user_profiles collection to have free tier fields."""
    
    print("🔍 Fetching all user profiles...")
    
    try:
        # Get all user profiles
        profiles_ref = db.collection('user_profiles')
        profiles = profiles_ref.stream()
        
        updated_count = 0
        skipped_count = 0
        error_count = 0
        
        for profile_doc in profiles:
            profile_id = profile_doc.id
            profile_data = profile_doc.to_dict()
            
            # Check if user already has the fields
            has_tier = 'subscription_tier' in profile_data
            has_count = 'meal_plans_generated_this_week' in profile_data
            has_week_start = 'week_start_for_limit' in profile_data
            
            if has_tier and has_count and has_week_start:
                print(f"⏭️  Skipping {profile_data.get('name', profile_id)}: Already has free tier fields")
                skipped_count += 1
                continue
            
            # Prepare update data
            update_data = {}
            
            if not has_tier:
                update_data['subscription_tier'] = 'free'
            
            if not has_count:
                update_data['meal_plans_generated_this_week'] = 0
            
            if not has_week_start:
                update_data['week_start_for_limit'] = datetime.utcnow()
            
            # Update the profile
            try:
                profiles_ref.document(profile_id).update(update_data)
                print(f"✅ Updated {profile_data.get('name', profile_id)}: {', '.join(update_data.keys())}")
                updated_count += 1
            except Exception as e:
                print(f"❌ Error updating {profile_id}: {e}")
                error_count += 1
        
        print("\n" + "="*60)
        print("📊 SUMMARY")
        print("="*60)
        print(f"✅ Updated: {updated_count} users")
        print(f"⏭️  Skipped: {skipped_count} users (already had fields)")
        print(f"❌ Errors: {error_count} users")
        print("="*60)
        
        if updated_count > 0:
            print("\n🎉 Successfully updated all users to free tier!")
        else:
            print("\n✅ All users already have free tier fields!")
        
        return True
        
    except Exception as e:
        print(f"\n❌ Fatal error: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    print("="*60)
    print("🔧 UPDATE ALL USERS TO FREE TIER")
    print("="*60)
    print()
    
    success = update_all_users_to_free_tier()
    
    if success:
        print("\n✅ Script completed successfully!")
        sys.exit(0)
    else:
        print("\n❌ Script failed!")
        sys.exit(1)

