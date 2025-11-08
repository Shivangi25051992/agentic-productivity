import firebase_admin
from firebase_admin import credentials, firestore
from dotenv import load_dotenv
import os
from datetime import datetime

load_dotenv('.env.local', override=True)

# Get Firebase credentials path from environment
creds_path = os.getenv('GOOGLE_APPLICATION_CREDENTIALS')
if not creds_path:
    print("❌ GOOGLE_APPLICATION_CREDENTIALS not set in .env.local")
    exit(1)

# Initialize Firebase
if not firebase_admin._apps:
    cred = credentials.Certificate(creds_path)
    firebase_admin.initialize_app(cred)

db = firestore.client()

# Get all profiles
profiles_ref = db.collection('profiles')
profiles = list(profiles_ref.stream())

print(f"Found {len(profiles)} profiles")
print("")

for profile_doc in profiles:
    profile_id = profile_doc.id
    profile_data = profile_doc.to_dict()
    
    # Check if fields exist
    has_tier = 'subscription_tier' in profile_data
    has_counter = 'meal_plans_generated_this_week' in profile_data
    has_week_start = 'week_start_for_limit' in profile_data
    
    print(f"Profile: {profile_id}")
    print(f"  Email: {profile_data.get('email', 'N/A')}")
    print(f"  Has subscription_tier: {has_tier}")
    print(f"  Has meal_plans_generated_this_week: {has_counter}")
    print(f"  Has week_start_for_limit: {has_week_start}")
    
    # Add missing fields
    updates = {}
    if not has_tier:
        updates['subscription_tier'] = 'free'
    if not has_counter:
        updates['meal_plans_generated_this_week'] = 0
    if not has_week_start:
        updates['week_start_for_limit'] = datetime.now().isoformat()
    
    if updates:
        profiles_ref.document(profile_id).update(updates)
        print(f"  ✅ Updated with: {updates}")
    else:
        print(f"  ✅ Already has all fields")
    print("")

print("✅ Done!")
