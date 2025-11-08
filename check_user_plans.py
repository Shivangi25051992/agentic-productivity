import firebase_admin
from firebase_admin import credentials, firestore
from dotenv import load_dotenv
import os

load_dotenv('.env.local', override=True)

# Initialize Firebase
if not firebase_admin._apps:
    cred = credentials.Certificate(os.getenv('FIREBASE_CREDENTIALS_PATH'))
    firebase_admin.initialize_app(cred)

db = firestore.client()

# Check both users
users = [
    'ACjSKgsfS0NkgSQYCvAEtnRvMO43',  # test@test15.com (from frontend)
    'v8Opsbu6omZMRQyjmMqs6vLe18r1'   # (from backend logs)
]

for user_id in users:
    print(f"\n{'='*60}")
    print(f"User: {user_id}")
    print(f"{'='*60}")
    
    # Check meal plans
    plans_ref = db.collection('users').document(user_id).collection('meal_plans')
    plans = list(plans_ref.stream())
    
    print(f"Found {len(plans)} meal plans:")
    for plan in plans:
        data = plan.to_dict()
        print(f"  - {plan.id}")
        print(f"    Week: {data.get('week_start_date')} to {data.get('week_end_date')}")
        print(f"    Active: {data.get('is_active', 'N/A')}")
        print(f"    Meals: {len(data.get('meals', []))}")
