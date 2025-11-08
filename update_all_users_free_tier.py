from google.cloud import firestore
from datetime import datetime
import os
from dotenv import load_dotenv

load_dotenv('.env.local', override=True)

# Initialize Firestore
project_id = os.getenv('FIREBASE_PROJECT_ID')
db = firestore.Client(project=project_id)

print("🔄 Updating all users to free tier...")
print("")

# Get all profiles
profiles_ref = db.collection('user_profiles')
profiles = list(profiles_ref.stream())

print(f"Found {len(profiles)} user profiles")
print("")

updated_count = 0
for profile_doc in profiles:
    profile_id = profile_doc.id
    profile_data = profile_doc.to_dict()
    
    # Check if fields exist
    has_tier = 'subscription_tier' in profile_data
    has_counter = 'meal_plans_generated_this_week' in profile_data
    has_week_start = 'week_start_for_limit' in profile_data
    
    print(f"📋 Profile: {profile_id}")
    print(f"   Name: {profile_data.get('name', 'N/A')}")
    
    # Add missing fields
    updates = {}
    if not has_tier:
        updates['subscription_tier'] = 'free'
        print(f"   ➕ Adding subscription_tier: free")
    else:
        print(f"   ✓ Has subscription_tier: {profile_data.get('subscription_tier')}")
        
    if not has_counter:
        updates['meal_plans_generated_this_week'] = 0
        print(f"   ➕ Adding meal_plans_generated_this_week: 0")
    else:
        print(f"   ✓ Has meal_plans_generated_this_week: {profile_data.get('meal_plans_generated_this_week')}")
        
    if not has_week_start:
        updates['week_start_for_limit'] = datetime.now()
        print(f"   ➕ Adding week_start_for_limit: now")
    else:
        print(f"   ✓ Has week_start_for_limit")
    
    if updates:
        profiles_ref.document(profile_id).update(updates)
        print(f"   ✅ Updated!")
        updated_count += 1
    else:
        print(f"   ✅ Already has all fields")
    print("")

print(f"✅ Done! Updated {updated_count} profiles")
