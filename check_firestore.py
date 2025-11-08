import firebase_admin
from firebase_admin import credentials, firestore
import os
from dotenv import load_dotenv

load_dotenv()

# Initialize Firebase
if not firebase_admin._apps:
    cred_path = os.getenv('GOOGLE_APPLICATION_CREDENTIALS')
    cred = credentials.Certificate(cred_path)
    firebase_admin.initialize_app(cred)

db = firestore.client()

user_id = "saloAvPLMsY1LWrKCwFAD8pXWt42"

print(f"🔍 Checking meal plans for user: {user_id}\n")

# Get all meal plans (no filter)
query = db.collection('users').document(user_id).collection('meal_plans').order_by('created_at', direction=firestore.Query.DESCENDING).limit(10)

print("📋 All meal plans (ordered by created_at DESC):\n")
for doc in query.stream():
    data = doc.to_dict()
    print(f"ID: {doc.id}")
    print(f"  is_active: {data.get('is_active')}")
    print(f"  week_start_date: {data.get('week_start_date')}")
    print(f"  created_at: {data.get('created_at')}")
    print(f"  meals count: {len(data.get('meals', []))}")
    print()
