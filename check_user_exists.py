import firebase_admin
from firebase_admin import credentials, firestore
import sys

# Initialize Firebase
cred = credentials.ApplicationDefault()
firebase_admin.initialize_app(cred, {
    'projectId': 'productivityai-mvp'
})

db = firestore.client()

# Check for Shivangi's user
email = "shivganga25shingatwar@gmail.com"

print(f"🔍 Searching for user with email: {email}")
print("=" * 80)

# Check users collection
print("\n📁 Checking 'users' collection...")
users_ref = db.collection('users')
users_docs = list(users_ref.stream())
print(f"Total users in collection: {len(users_docs)}")

for doc in users_docs:
    user_data = doc.to_dict()
    if user_data.get('email') == email:
        print(f"\n✅ FOUND in 'users' collection:")
        print(f"   Document ID: {doc.id}")
        print(f"   Data: {user_data}")
        user_id = doc.id
        break
else:
    print(f"\n❌ NOT FOUND in 'users' collection")
    user_id = None

# Check user_profiles collection
print("\n📁 Checking 'user_profiles' collection...")
profiles_ref = db.collection('user_profiles')
profiles_docs = list(profiles_ref.stream())
print(f"Total profiles in collection: {len(profiles_docs)}")

for doc in profiles_docs:
    profile_data = doc.to_dict()
    # Check by user_id if we found it, or by name
    if user_id and doc.id == user_id:
        print(f"\n✅ FOUND profile by user_id:")
        print(f"   Document ID: {doc.id}")
        print(f"   Name: {profile_data.get('name')}")
        print(f"   Onboarding completed: {profile_data.get('onboarding_completed')}")
        break
    elif profile_data.get('name') == 'Shivangi':
        print(f"\n✅ FOUND profile by name:")
        print(f"   Document ID: {doc.id}")
        print(f"   Name: {profile_data.get('name')}")
        print(f"   Onboarding completed: {profile_data.get('onboarding_completed')}")
        if not user_id:
            print(f"\n⚠️  WARNING: Profile exists but user doesn't exist in 'users' collection!")
            print(f"   This is the ROOT CAUSE of the mobile auth issue!")
        break
else:
    print(f"\n❌ NOT FOUND in 'user_profiles' collection")

print("\n" + "=" * 80)
print("✅ Check complete")
