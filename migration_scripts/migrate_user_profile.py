#!/usr/bin/env python3
"""
Migrate user profile data to subcollection structure
OLD: users/{userId} (flat document)
NEW: users/{userId}/profile/current (subcollection)
"""

import os
from google.cloud import firestore
from google.oauth2 import service_account
from datetime import datetime

# Initialize Firestore
project_id = os.getenv("GOOGLE_CLOUD_PROJECT", "productivityai-mvp")
credentials_path = "/Users/pchintanwar/keys/productivityai-mvp-0017f7241a58.json"
credentials = service_account.Credentials.from_service_account_file(credentials_path)
db = firestore.Client(project=project_id, credentials=credentials)

def migrate_user_profile(user_id: str) -> bool:
    """Migrate single user's profile to subcollection"""
    try:
        print(f"  Migrating profile for {user_id}...")
        
        # Get old user document
        old_user_ref = db.collection('users').document(user_id)
        old_user = old_user_ref.get()
        
        if not old_user.exists:
            print(f"    ⚠️  User {user_id} not found, skipping")
            return False
        
        old_data = old_user.to_dict()
        
        # Create new profile subcollection document
        new_profile = {
            'fitnessGoal': old_data.get('fitness_goal', 'maintain'),
            'activityLevel': 'moderately_active',  # Default
            'dailyCalorieGoal': old_data.get('daily_calorie_goal', 2000),
            'macroTargets': {
                'proteinPercent': 30,
                'carbsPercent': 40,
                'fatPercent': 30
            },
            'measurements': {
                'weight': old_data.get('weight', 70),
                'height': old_data.get('height', 170),
                'age': old_data.get('age', 30),
                'gender': old_data.get('gender', 'prefer_not_to_say')
            },
            'preferences': {
                'preferredFoods': old_data.get('preferred_foods', []),
                'dislikedFoods': old_data.get('disliked_foods', []),
                'allergies': [],
                'dietaryRestrictions': []
            },
            'updatedAt': firestore.SERVER_TIMESTAMP
        }
        
        # Write to new location
        new_profile_ref = db.collection('users').document(user_id)\
                            .collection('profile').document('current')
        new_profile_ref.set(new_profile)
        
        # Update root user document (keep minimal data)
        root_user = {
            'userId': user_id,
            'email': old_data.get('email'),
            'displayName': old_data.get('display_name', ''),
            'photoURL': old_data.get('photo_url', ''),
            'createdAt': old_data.get('created_at', firestore.SERVER_TIMESTAMP),
            'updatedAt': firestore.SERVER_TIMESTAMP,
            'lastActiveAt': firestore.SERVER_TIMESTAMP,
            'accountStatus': 'active',
            'privacySettings': {
                'shareProfile': False,
                'shareProgress': False,
                'allowAnalytics': True
            }
        }
        old_user_ref.set(root_user)
        
        print(f"    ✅ Profile migrated")
        return True
        
    except Exception as e:
        print(f"    ❌ Error: {e}")
        return False

def main():
    """Migrate all user profiles"""
    print("=" * 70)
    print("👤 MIGRATING USER PROFILES")
    print("=" * 70)
    print()
    
    # Get all users
    users = db.collection('users').stream()
    
    migrated = 0
    failed = 0
    
    for user in users:
        if migrate_user_profile(user.id):
            migrated += 1
        else:
            failed += 1
    
    print()
    print("=" * 70)
    print(f"✅ Migration complete: {migrated} migrated, {failed} failed")
    print("=" * 70)

if __name__ == "__main__":
    main()

