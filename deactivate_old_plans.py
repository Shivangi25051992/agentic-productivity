import firebase_admin
from firebase_admin import credentials, firestore
import os
from dotenv import load_dotenv
from datetime import datetime

load_dotenv()

# Initialize Firebase
if not firebase_admin._apps:
    cred_path = os.getenv('GOOGLE_APPLICATION_CREDENTIALS')
    cred = credentials.Certificate(cred_path)
    firebase_admin.initialize_app(cred)

db = firestore.client()
user_id = "saloAvPLMsY1LWrKCwFAD8pXWt42"

print(f"🔍 Finding all active plans for week 2025-11-03...")

# Get all plans for the user
plans_ref = db.collection('users').document(user_id).collection('meal_plans')
all_plans = plans_ref.order_by('created_at', direction=firestore.Query.DESCENDING).stream()

active_plans = []
for doc in all_plans:
    data = doc.to_dict()
    week_start = data.get('week_start_date')
    is_active = data.get('is_active', True)
    created_at = data.get('created_at')
    
    if week_start == '2025-11-03' and is_active:
        active_plans.append({
            'id': doc.id,
            'created_at': created_at,
            'dietary_prefs': data.get('dietary_preferences', [])
        })
        print(f"   📋 Active Plan: {doc.id[:8]}... | Created: {created_at} | Prefs: {data.get('dietary_preferences', [])}")

print(f"\n✅ Found {len(active_plans)} active plans for week 2025-11-03")

if len(active_plans) > 1:
    print(f"\n🔧 Keeping NEWEST plan (first one), deactivating {len(active_plans)-1} old plans...")
    
    # Keep the first one (newest), deactivate the rest
    for i, plan in enumerate(active_plans[1:], 1):
        print(f"   🔵 Deactivating plan {i}: {plan['id'][:8]}...")
        plans_ref.document(plan['id']).update({
            'is_active': False,
            'updated_at': datetime.utcnow()
        })
    
    print(f"\n✅ Done! Only the newest plan is now active: {active_plans[0]['id']}")
else:
    print(f"\n✅ Only 1 active plan - no action needed")

