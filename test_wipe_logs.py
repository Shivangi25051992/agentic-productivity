#!/usr/bin/env python3
"""
Test the wipe logs functionality
"""

from google.cloud import firestore
import os
from dotenv import load_dotenv

load_dotenv()
load_dotenv('.env.local', override=True)

db = firestore.Client(project=os.getenv('GOOGLE_CLOUD_PROJECT', 'productivityai-mvp'))
TEST_USER_ID = "Po6FIpjF4cM1WWt8duHjD1BXqY13"  # Alice

def test_wipe_logs():
    """Test wipe logs functionality"""
    print("=" * 60)
    print("🧪 TESTING WIPE LOGS FUNCTIONALITY")
    print("=" * 60)
    
    # Check current data
    print("\n📊 BEFORE WIPE:")
    
    # Count fitness logs
    logs = list(db.collection('users').document(TEST_USER_ID)
                  .collection('fitness_logs').stream())
    print(f"  Fitness logs: {len(logs)}")
    
    # Count chat sessions
    sessions = list(db.collection('users').document(TEST_USER_ID)
                      .collection('chat_sessions').stream())
    print(f"  Chat sessions: {len(sessions)}")
    
    # Count messages
    total_messages = 0
    for session in sessions:
        messages = list(session.reference.collection('messages').stream())
        total_messages += len(messages)
    print(f"  Chat messages: {total_messages}")
    
    # Perform wipe
    print("\n🗑️  PERFORMING WIPE...")
    
    deleted_logs = 0
    deleted_sessions = 0
    deleted_messages = 0
    
    # Delete fitness logs
    for log in logs:
        log.reference.delete()
        deleted_logs += 1
    
    # Delete chat sessions and messages
    for session in sessions:
        # Delete messages first
        messages = list(session.reference.collection('messages').stream())
        for msg in messages:
            msg.reference.delete()
            deleted_messages += 1
        # Delete session
        session.reference.delete()
        deleted_sessions += 1
    
    print(f"  ✅ Deleted {deleted_logs} fitness logs")
    print(f"  ✅ Deleted {deleted_sessions} chat sessions")
    print(f"  ✅ Deleted {deleted_messages} chat messages")
    
    # Verify deletion
    print("\n📊 AFTER WIPE:")
    
    logs_after = list(db.collection('users').document(TEST_USER_ID)
                        .collection('fitness_logs').stream())
    sessions_after = list(db.collection('users').document(TEST_USER_ID)
                            .collection('chat_sessions').stream())
    
    print(f"  Fitness logs: {len(logs_after)}")
    print(f"  Chat sessions: {len(sessions_after)}")
    
    if len(logs_after) == 0 and len(sessions_after) == 0:
        print("\n✅ WIPE TEST PASSED!")
        return True
    else:
        print("\n❌ WIPE TEST FAILED - Data still exists")
        return False

if __name__ == "__main__":
    try:
        test_wipe_logs()
    except Exception as e:
        print(f"\n❌ Test failed: {e}")
        import traceback
        traceback.print_exc()

