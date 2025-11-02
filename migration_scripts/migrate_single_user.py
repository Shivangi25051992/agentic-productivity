#!/usr/bin/env python3
"""
Migrate a single user's data (for testing)
Usage: python migrate_single_user.py <user_email>
"""

import sys
import os
from google.cloud import firestore
from google.oauth2 import service_account

# Initialize Firestore
project_id = os.getenv("GOOGLE_CLOUD_PROJECT", "productivityai-mvp")
credentials_path = "/Users/pchintanwar/keys/productivityai-mvp-0017f7241a58.json"
credentials = service_account.Credentials.from_service_account_file(credentials_path)
db = firestore.Client(project=project_id, credentials=credentials)

# Import migration functions
from migrate_user_profile import migrate_user_profile
from migrate_fitness_logs import migrate_fitness_logs
from migrate_chat_history import migrate_chat_history

def get_user_id_by_email(email: str) -> str:
    """Get user ID from email"""
    users = db.collection('users').where('email', '==', email).limit(1).stream()
    
    for user in users:
        return user.id
    
    return None

def verify_migration(user_id: str) -> dict:
    """Verify migration was successful"""
    print("\n" + "=" * 70)
    print("🔍 VERIFYING MIGRATION")
    print("=" * 70)
    
    results = {
        'profile': False,
        'fitness_logs': 0,
        'chat_sessions': 0,
        'chat_messages': 0
    }
    
    # Check profile
    profile = db.collection('users').document(user_id)\
                .collection('profile').document('current').get()
    results['profile'] = profile.exists
    print(f"  Profile: {'✅' if profile.exists else '❌'}")
    
    # Check fitness logs
    logs = db.collection('users').document(user_id)\
             .collection('fitness_logs').stream()
    results['fitness_logs'] = len(list(logs))
    print(f"  Fitness logs: {results['fitness_logs']}")
    
    # Check chat sessions
    sessions = db.collection('users').document(user_id)\
                 .collection('chat_sessions').stream()
    session_list = list(sessions)
    results['chat_sessions'] = len(session_list)
    print(f"  Chat sessions: {results['chat_sessions']}")
    
    # Count messages across all sessions
    total_messages = 0
    for session in session_list:
        messages = db.collection('users').document(user_id)\
                     .collection('chat_sessions').document(session.id)\
                     .collection('messages').stream()
        total_messages += len(list(messages))
    results['chat_messages'] = total_messages
    print(f"  Chat messages: {results['chat_messages']}")
    
    return results

def main():
    if len(sys.argv) < 2:
        print("Usage: python migrate_single_user.py <user_email>")
        print("Example: python migrate_single_user.py alice.test@aiproductivity.app")
        sys.exit(1)
    
    email = sys.argv[1]
    
    print("=" * 70)
    print(f"🚀 MIGRATING SINGLE USER: {email}")
    print("=" * 70)
    print()
    
    # Get user ID
    user_id = get_user_id_by_email(email)
    
    if not user_id:
        print(f"❌ User not found: {email}")
        sys.exit(1)
    
    print(f"✅ Found user: {user_id}")
    print()
    
    # Run migrations
    print("Step 1: Migrating user profile...")
    migrate_user_profile(user_id)
    print()
    
    print("Step 2: Migrating fitness logs...")
    migrate_fitness_logs(user_id)
    print()
    
    print("Step 3: Migrating chat history...")
    migrate_chat_history(user_id)
    print()
    
    # Verify
    results = verify_migration(user_id)
    
    # Summary
    print("\n" + "=" * 70)
    print("✅ MIGRATION COMPLETE")
    print("=" * 70)
    print(f"User: {email} ({user_id})")
    print(f"Profile: {'✅ Migrated' if results['profile'] else '❌ Failed'}")
    print(f"Fitness logs: {results['fitness_logs']} migrated")
    print(f"Chat sessions: {results['chat_sessions']} created")
    print(f"Chat messages: {results['chat_messages']} migrated")
    print()
    
    if results['profile'] and (results['fitness_logs'] > 0 or results['chat_messages'] > 0):
        print("🎉 Migration successful! You can now test the app with this user.")
    else:
        print("⚠️  Migration completed but some data may be missing. Please review.")

if __name__ == "__main__":
    main()

