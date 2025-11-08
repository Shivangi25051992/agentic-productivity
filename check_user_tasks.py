#!/usr/bin/env python3
"""Check if a specific user has tasks in Firestore"""

import os
import sys
from google.cloud import firestore
from dotenv import load_dotenv

load_dotenv()
load_dotenv('.env.local', override=True)

def main():
    # Get user email from command line or use default
    user_email = sys.argv[1] if len(sys.argv) > 1 else "pc@demo.com"
    
    project_id = os.getenv('GOOGLE_CLOUD_PROJECT', 'productivityai-mvp')
    print(f"🔗 Connecting to project: {project_id}")
    print(f"👤 Looking for user: {user_email}\n")
    
    db = firestore.Client(project=project_id)
    
    # First, find the user_id from email
    print("Step 1: Finding user_id from email...")
    user_profiles = db.collection('user_profiles').where('email', '==', user_email).limit(1).stream()
    
    user_id = None
    for profile in user_profiles:
        user_id = profile.id
        print(f"✅ Found user_id: {user_id}\n")
        break
    
    if not user_id:
        # Try users collection
        print("  Not found in user_profiles, trying users collection...")
        users = db.collection('users').where('email', '==', user_email).limit(1).stream()
        for user in users:
            user_id = user.id
            print(f"✅ Found user_id: {user_id}\n")
            break
    
    if not user_id:
        print(f"❌ User not found with email: {user_email}")
        return
    
    # Check tasks collection
    print("Step 2: Checking tasks collection...")
    tasks = list(db.collection('tasks').where('user_id', '==', user_id).stream())
    
    if tasks:
        print(f"✅ Found {len(tasks)} task(s) for user:\n")
        for task in tasks:
            data = task.to_dict()
            print(f"  Task ID: {task.id}")
            print(f"  Title: {data.get('title', 'N/A')}")
            print(f"  Status: {data.get('status', 'N/A')}")
            print(f"  Due Date: {data.get('due_date', 'None')}")
            print(f"  Created: {data.get('created_at', 'N/A')}")
            print(f"  Fields: {list(data.keys())}")
            print()
    else:
        print(f"❌ No tasks found for user {user_id}")
        print("\n  Possible reasons:")
        print("  1. User hasn't created any tasks yet")
        print("  2. Task creation is failing silently")
        print("  3. Tasks are being saved elsewhere (subcollection?)")
    
    # Check if tasks are in subcollection
    print("\nStep 3: Checking users/{user_id}/tasks subcollection...")
    subtasks = list(db.collection('users').document(user_id).collection('tasks').stream())
    
    if subtasks:
        print(f"✅ Found {len(subtasks)} task(s) in subcollection:\n")
        for task in subtasks:
            data = task.to_dict()
            print(f"  Task ID: {task.id}")
            print(f"  Title: {data.get('title', 'N/A')}")
            print(f"  Fields: {list(data.keys())}")
            print()
    else:
        print(f"❌ No tasks found in subcollection either")
    
    # Check fitness logs to confirm user has data
    print("\nStep 4: Checking fitness_logs for comparison...")
    logs = list(db.collection('users').document(user_id).collection('fitness_logs').limit(3).stream())
    
    if logs:
        print(f"✅ User HAS {len(logs)} fitness log(s) - so data IS being saved!")
        for log in logs:
            data = log.to_dict()
            print(f"  - {data.get('log_type')}: {data.get('content')}")
    else:
        print(f"⚠️  User has no fitness logs either")
    
    print("\n" + "="*80)
    print("CONCLUSION:")
    print("="*80)
    if not tasks and not subtasks:
        print("❌ User has NO tasks in Firestore")
        print("   → Task creation is likely failing OR user hasn't created tasks yet")
    elif tasks:
        print(f"✅ User has {len(tasks)} task(s) in flat 'tasks' collection")
    elif subtasks:
        print(f"✅ User has {len(subtasks)} task(s) in subcollection")
        print("   → Backend queries need to be updated to look in subcollections!")

if __name__ == '__main__':
    main()

