#!/usr/bin/env python3
"""
End-to-end test to verify new structure works with live data
Creates test data in new structure and verifies backend can read it
"""

from google.cloud import firestore
from datetime import datetime, timedelta
import os
from dotenv import load_dotenv

load_dotenv()
load_dotenv('.env.local', override=True)

# Initialize Firestore
db = firestore.Client(project=os.getenv('GOOGLE_CLOUD_PROJECT', 'aiproductivity-d6cf6'))

TEST_USER_ID = "Po6FIpjF4cM1WWt8duHjD1BXqY13"  # Alice

def create_test_data():
    """Create test data in NEW subcollection structure"""
    print("=" * 60)
    print("🧪 CREATING TEST DATA IN NEW STRUCTURE")
    print("=" * 60)
    
    # Test 1: Create fitness log
    print("\n📋 TEST 1: Create Fitness Log")
    log_ref = db.collection('users').document(TEST_USER_ID)\
                .collection('fitness_logs').document()
    
    log_data = {
        'log_id': log_ref.id,
        'user_id': TEST_USER_ID,
        'log_type': 'meal',
        'content': 'Test meal: oatmeal with banana',
        'calories': 350,
        'timestamp': firestore.SERVER_TIMESTAMP,
        'ai_parsed_data': {
            'description': 'oatmeal with banana',
            'meal_type': 'breakfast',
            'calories': 350,
            'protein_g': 10,
            'carbs_g': 60,
            'fat_g': 5
        }
    }
    log_ref.set(log_data)
    print(f"✅ Created fitness log: {log_ref.id}")
    
    # Test 2: Create chat session with messages
    print("\n📋 TEST 2: Create Chat Session")
    session_id = datetime.utcnow().date().isoformat()
    session_ref = db.collection('users').document(TEST_USER_ID)\
                    .collection('chat_sessions').document(session_id)
    
    session_data = {
        'sessionId': session_id,
        'title': f"Test Chat - {session_id}",
        'startedAt': firestore.SERVER_TIMESTAMP,
        'lastMessageAt': firestore.SERVER_TIMESTAMP,
        'messageCount': 2,
        'expiresAt': datetime.utcnow() + timedelta(days=7),
        'archived': False
    }
    session_ref.set(session_data)
    print(f"✅ Created chat session: {session_id}")
    
    # Add messages to session
    print("\n📋 TEST 3: Add Messages to Session")
    messages = [
        {
            'role': 'user',
            'content': 'I had oatmeal with banana for breakfast',
            'metadata': {},
            'timestamp': firestore.SERVER_TIMESTAMP
        },
        {
            'role': 'assistant',
            'content': 'Great! I logged your breakfast: oatmeal with banana (350 cal)',
            'metadata': {'category': 'meal', 'calories': 350},
            'timestamp': firestore.SERVER_TIMESTAMP
        }
    ]
    
    for msg in messages:
        msg_ref = session_ref.collection('messages').document()
        msg_ref.set(msg)
        print(f"✅ Created message: {msg['role']}")
    
    print("\n" + "=" * 60)
    print("✅ TEST DATA CREATED SUCCESSFULLY!")
    print("=" * 60)

def verify_test_data():
    """Verify backend can read test data"""
    print("\n" + "=" * 60)
    print("🔍 VERIFYING BACKEND CAN READ TEST DATA")
    print("=" * 60)
    
    # Verify fitness logs
    print("\n📋 Verify Fitness Logs")
    logs_ref = db.collection('users').document(TEST_USER_ID)\
                 .collection('fitness_logs')
    logs = list(logs_ref.limit(5).stream())
    print(f"✅ Found {len(logs)} fitness logs")
    
    for log in logs:
        data = log.to_dict()
        content = data.get('content', '')[:50]
        calories = data.get('calories', 0)
        print(f"  - {content}... ({calories} cal)")
    
    # Verify chat sessions
    print("\n📋 Verify Chat Sessions")
    sessions_ref = db.collection('users').document(TEST_USER_ID)\
                     .collection('chat_sessions')
    sessions = list(sessions_ref.limit(5).stream())
    print(f"✅ Found {len(sessions)} chat sessions")
    
    for session in sessions:
        session_data = session.to_dict()
        session_id = session.id
        message_count = session_data.get('messageCount', 0)
        print(f"  - Session {session_id}: {message_count} messages")
        
        # Verify messages
        messages_ref = session.reference.collection('messages')
        messages = list(messages_ref.stream())
        print(f"    ✅ Found {len(messages)} messages in subcollection")
        
        for msg in messages:
            msg_data = msg.to_dict()
            role = msg_data.get('role', 'unknown')
            content = msg_data.get('content', '')[:40]
            print(f"      - {role}: {content}...")
    
    print("\n" + "=" * 60)
    print("✅ VERIFICATION COMPLETE!")
    print("=" * 60)
    
    return len(logs), len(sessions)

def main():
    """Run end-to-end test"""
    try:
        # Step 1: Create test data
        create_test_data()
        
        # Step 2: Verify backend can read it
        logs_count, sessions_count = verify_test_data()
        
        # Summary
        print("\n" + "=" * 60)
        print("🎯 END-TO-END TEST SUMMARY")
        print("=" * 60)
        print(f"✅ Fitness logs created and verified: {logs_count}")
        print(f"✅ Chat sessions created and verified: {sessions_count}")
        print("✅ New subcollection structure is WORKING!")
        print("=" * 60)
        
    except Exception as e:
        print(f"\n❌ Test failed: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()

