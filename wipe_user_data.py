#!/usr/bin/env python3
import os
import sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from google.cloud import firestore

# Initialize Firestore with credentials
os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = '/Users/pchintanwar/keys/productivityai-mvp-0017f7241a58.json'
project_id = "productivityai-mvp"
db = firestore.Client(project=project_id)

email = "alice.test@aiproductivity.app"

# Get user
users_ref = db.collection("users")
query = users_ref.where("email", "==", email).limit(1)
users = list(query.stream())

if users:
    user_doc = users[0]
    user_id = user_doc.id
    print(f"Found user: {user_id}")
    
    # Delete fitness logs
    fitness_logs_ref = db.collection("fitness_logs")
    query = fitness_logs_ref.where("user_id", "==", user_id)
    logs = list(query.stream())
    
    for log in logs:
        log.reference.delete()
    print(f"Deleted {len(logs)} fitness logs")
    
    # Delete chat history
    chat_history_ref = db.collection("chat_history")
    query = chat_history_ref.where("user_id", "==", user_id)
    messages = list(query.stream())
    
    for message in messages:
        message.reference.delete()
    print(f"Deleted {len(messages)} chat messages")
    
    # Delete tasks
    tasks_ref = db.collection("tasks")
    query = tasks_ref.where("user_id", "==", user_id)
    tasks = list(query.stream())
    
    for task in tasks:
        task.reference.delete()
    print(f"Deleted {len(tasks)} tasks")
    
    print(f"\n✅ Total deleted: {len(logs) + len(messages) + len(tasks)} items")
else:
    print("User not found")

