#!/usr/bin/env python3
"""
Migrate chat history to subcollection structure with sessions
OLD: chat_history/{messageId} (flat collection with user_id field)
NEW: users/{userId}/chat_sessions/{sessionId}/messages/{messageId} (nested subcollections)

Groups messages by date into sessions for better organization
"""

import os
from google.cloud import firestore
from google.oauth2 import service_account
from datetime import datetime, timedelta
from collections import defaultdict

# Initialize Firestore
project_id = os.getenv("GOOGLE_CLOUD_PROJECT", "productivityai-mvp")
credentials_path = "/Users/pchintanwar/keys/productivityai-mvp-0017f7241a58.json"
credentials = service_account.Credentials.from_service_account_file(credentials_path)
db = firestore.Client(project=project_id, credentials=credentials)

def migrate_chat_history(user_id: str) -> int:
    """Migrate all chat messages for a single user"""
    try:
        print(f"  Migrating chat history for {user_id}...")
        
        # Get all messages for this user
        old_messages = db.collection('chat_history')\
                         .where('user_id', '==', user_id)\
                         .stream()
        
        # Group messages by date (session)
        sessions = defaultdict(list)
        
        for msg in old_messages:
            msg_data = msg.to_dict()
            timestamp = msg_data.get('timestamp', datetime.now())
            
            # Get date for session grouping
            if hasattr(timestamp, 'date'):
                date_str = timestamp.date().isoformat()
            else:
                date_str = datetime.now().date().isoformat()
            
            sessions[date_str].append({
                'id': msg.id,
                'data': msg_data,
                'timestamp': timestamp
            })
        
        # Create sessions and migrate messages
        migrated_count = 0
        
        for session_date, messages in sessions.items():
            # Sort messages by timestamp
            messages.sort(key=lambda x: x['timestamp'])
            
            # Create session document
            session_id = session_date  # Use date as session ID
            first_message_time = messages[0]['timestamp']
            last_message_time = messages[-1]['timestamp']
            
            session_doc = {
                'sessionId': session_id,
                'title': f"Chat - {session_date}",
                'startedAt': first_message_time,
                'lastMessageAt': last_message_time,
                'messageCount': len(messages),
                'expiresAt': last_message_time + timedelta(days=7) if hasattr(last_message_time, '__add__') else datetime.now() + timedelta(days=7),
                'archived': False
            }
            
            session_ref = db.collection('users').document(user_id)\
                            .collection('chat_sessions').document(session_id)
            session_ref.set(session_doc)
            
            # Migrate messages to session
            for msg in messages:
                msg_data = msg['data']
                
                new_message = {
                    'messageId': msg['id'],
                    'role': msg_data.get('role', 'user'),
                    'content': msg_data.get('content', ''),
                    'metadata': msg_data.get('metadata', {}),
                    'timestamp': msg['timestamp']
                }
                
                message_ref = session_ref.collection('messages').document(msg['id'])
                message_ref.set(new_message)
                
                migrated_count += 1
        
        print(f"    ✅ Migrated {migrated_count} messages into {len(sessions)} sessions")
        return migrated_count
        
    except Exception as e:
        print(f"    ❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return 0

def main():
    """Migrate all chat history"""
    print("=" * 70)
    print("💬 MIGRATING CHAT HISTORY")
    print("=" * 70)
    print()
    
    # Get all unique user IDs from chat_history
    messages = db.collection('chat_history').stream()
    user_ids = set()
    
    for msg in messages:
        data = msg.to_dict()
        user_id = data.get('user_id')
        if user_id:
            user_ids.add(user_id)
    
    print(f"Found {len(user_ids)} users with chat history")
    print()
    
    total_migrated = 0
    for user_id in user_ids:
        count = migrate_chat_history(user_id)
        total_migrated += count
    
    print()
    print("=" * 70)
    print(f"✅ Migration complete: {total_migrated} messages migrated")
    print("=" * 70)

if __name__ == "__main__":
    main()

