#!/usr/bin/env python3
"""
Delete all logs for a specific user (keep profile and goals)
"""

import os
import sys
from dotenv import load_dotenv

# Load environment variables
load_dotenv()
load_dotenv('.env.local', override=True)

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from google.cloud import firestore

def delete_user_logs(email: str):
    """Delete all fitness logs and chat history for a user"""
    
    # Initialize Firestore
    project_id = os.getenv("GOOGLE_CLOUD_PROJECT")
    db = firestore.Client(project=project_id)
    
    # Get user by email
    users_ref = db.collection("users")
    query = users_ref.where("email", "==", email).limit(1)
    users = list(query.stream())
    
    if not users:
        print(f"❌ User not found: {email}")
        return
    
    user_doc = users[0]
    user_id = user_doc.id
    user_data = user_doc.to_dict()
    
    print(f"✅ Found user: {user_data.get('name', 'Unknown')} ({email})")
    print(f"   User ID: {user_id}")
    
    # Delete fitness logs
    print("\n🗑️  Deleting fitness logs...")
    fitness_logs_ref = db.collection("fitness_logs")
    query = fitness_logs_ref.where("user_id", "==", user_id)
    logs = list(query.stream())
    
    deleted_logs = 0
    for log in logs:
        log.reference.delete()
        deleted_logs += 1
    
    print(f"   ✅ Deleted {deleted_logs} fitness logs")
    
    # Delete chat history
    print("\n🗑️  Deleting chat history...")
    chat_history_ref = db.collection("chat_history")
    query = chat_history_ref.where("user_id", "==", user_id)
    messages = list(query.stream())
    
    deleted_messages = 0
    for message in messages:
        message.reference.delete()
        deleted_messages += 1
    
    print(f"   ✅ Deleted {deleted_messages} chat messages")
    
    # Delete tasks
    print("\n🗑️  Deleting tasks...")
    tasks_ref = db.collection("tasks")
    query = tasks_ref.where("user_id", "==", user_id)
    tasks = list(query.stream())
    
    deleted_tasks = 0
    for task in tasks:
        task.reference.delete()
        deleted_tasks += 1
    
    print(f"   ✅ Deleted {deleted_tasks} tasks")
    
    print(f"\n✅ All logs deleted for {email}")
    print(f"   Profile and goals preserved ✓")
    print(f"\n📊 Summary:")
    print(f"   - Fitness logs deleted: {deleted_logs}")
    print(f"   - Chat messages deleted: {deleted_messages}")
    print(f"   - Tasks deleted: {deleted_tasks}")
    print(f"   - User profile: KEPT")
    print(f"   - User goals: KEPT")

if __name__ == "__main__":
    email = "alice.test@aiproductivity.app"
    
    print("="*80)
    print("🗑️  DELETE USER LOGS")
    print("="*80)
    print(f"\nTarget user: {email}")
    print("This will delete:")
    print("  ✓ All fitness logs (meals, workouts)")
    print("  ✓ All chat history")
    print("  ✓ All tasks")
    print("\nThis will KEEP:")
    print("  ✓ User profile")
    print("  ✓ User goals and settings")
    print("\n" + "="*80)
    
    confirm = input("\nProceed? (yes/no): ").strip().lower()
    
    if confirm == "yes":
        delete_user_logs(email)
    else:
        print("❌ Cancelled")

