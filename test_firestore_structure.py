#!/usr/bin/env python3
"""
Direct Firestore test to verify new subcollection structure
"""

from google.cloud import firestore
from google.oauth2 import service_account
import os
from datetime import datetime
from dotenv import load_dotenv

load_dotenv()
load_dotenv('.env.local', override=True)

# Initialize Firestore (using default credentials from environment)
db = firestore.Client(project=os.getenv('GOOGLE_CLOUD_PROJECT', 'aiproductivity-d6cf6'))

TEST_USER_ID = "Po6FIpjF4cM1WWt8duHjD1BXqY13"  # Alice

def test_new_structure():
    """Test reading from new subcollection structure"""
    print("=" * 60)
    print("🧪 TESTING NEW FIRESTORE STRUCTURE")
    print("=" * 60)
    
    # Test 1: Check fitness logs in subcollection
    print("\n📋 TEST 1: Check Fitness Logs Subcollection")
    fitness_logs_ref = db.collection('users').document(TEST_USER_ID).collection('fitness_logs')
    logs = list(fitness_logs_ref.limit(5).stream())
    print(f"✅ Found {len(logs)} fitness logs in subcollection")
    
    for log in logs[:3]:
        data = log.to_dict()
        log_type = data.get('log_type', 'unknown')
        content = data.get('content', '')[:50]
        print(f"  - {log_type}: {content}...")
    
    # Test 2: Check chat sessions
    print("\n📋 TEST 2: Check Chat Sessions")
    sessions_ref = db.collection('users').document(TEST_USER_ID).collection('chat_sessions')
    sessions = list(sessions_ref.limit(5).stream())
    print(f"✅ Found {len(sessions)} chat sessions")
    
    for session in sessions:
        session_data = session.to_dict()
        session_id = session.id
        message_count = session_data.get('messageCount', 0)
        print(f"  - Session {session_id}: {message_count} messages")
        
        # Check messages in this session
        messages_ref = session.reference.collection('messages')
        messages = list(messages_ref.limit(3).stream())
        print(f"    Found {len(messages)} messages in subcollection")
        
        for msg in messages[:2]:
            msg_data = msg.to_dict()
            role = msg_data.get('role', 'unknown')
            content = msg_data.get('content', '')[:40]
            print(f"      - {role}: {content}...")
    
    # Test 3: Check old flat structure (for comparison)
    print("\n📋 TEST 3: Check Old Flat Structure (for comparison)")
    old_logs = list(db.collection('fitness_logs').where('user_id', '==', TEST_USER_ID).limit(5).stream())
    print(f"✅ Found {len(old_logs)} fitness logs in OLD flat collection")
    
    old_chat = list(db.collection('chat_history').where('user_id', '==', TEST_USER_ID).limit(5).stream())
    print(f"✅ Found {len(old_chat)} chat messages in OLD flat collection")
    
    # Summary
    print("\n" + "=" * 60)
    print("🎯 STRUCTURE SUMMARY")
    print("=" * 60)
    print(f"NEW Structure:")
    print(f"  - Fitness logs in subcollection: {len(logs)}")
    print(f"  - Chat sessions: {len(sessions)}")
    print(f"\nOLD Structure:")
    print(f"  - Fitness logs in flat collection: {len(old_logs)}")
    print(f"  - Chat messages in flat collection: {len(old_chat)}")
    print("=" * 60)
    
    if len(logs) > 0 or len(sessions) > 0:
        print("✅ NEW STRUCTURE IS WORKING!")
    else:
        print("⚠️  NEW STRUCTURE IS EMPTY (migration may not have run)")

if __name__ == "__main__":
    try:
        test_new_structure()
    except Exception as e:
        print(f"\n❌ Test failed: {e}")
        import traceback
        traceback.print_exc()

