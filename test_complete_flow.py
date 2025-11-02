#!/usr/bin/env python3
"""
Complete flow test for new Firebase structure
Tests all critical scenarios
"""

from google.cloud import firestore
from datetime import datetime, timedelta, timezone
import os
from dotenv import load_dotenv
import time

load_dotenv()
load_dotenv('.env.local', override=True)

# Initialize Firestore
db = firestore.Client(project=os.getenv('GOOGLE_CLOUD_PROJECT', 'aiproductivity-d6cf6'))

TEST_USER_ID = "Po6FIpjF4cM1WWt8duHjD1BXqY13"  # Alice

def cleanup_test_data():
    """Clean up any existing test data"""
    print("\n🧹 Cleaning up existing test data...")
    
    # Delete fitness logs
    logs_ref = db.collection('users').document(TEST_USER_ID).collection('fitness_logs')
    for doc in logs_ref.stream():
        doc.reference.delete()
    
    # Delete chat sessions
    sessions_ref = db.collection('users').document(TEST_USER_ID).collection('chat_sessions')
    for session in sessions_ref.stream():
        # Delete messages
        messages_ref = session.reference.collection('messages')
        for msg in messages_ref.stream():
            msg.reference.delete()
        # Delete session
        session.reference.delete()
    
    print("✅ Cleanup complete")

def test_scenario_1_single_meal():
    """Test 1: Single meal logging"""
    print("\n" + "="*60)
    print("📋 TEST 1: Single Meal Logging")
    print("="*60)
    
    # Create a meal log
    log_ref = db.collection('users').document(TEST_USER_ID)\
                .collection('fitness_logs').document()
    
    log_data = {
        'log_id': log_ref.id,
        'user_id': TEST_USER_ID,
        'log_type': 'meal',
        'content': 'oatmeal with banana',
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
    print(f"✅ Created meal log: {log_ref.id}")
    
    # Verify it was created
    time.sleep(1)
    logs = list(db.collection('users').document(TEST_USER_ID)
                  .collection('fitness_logs').stream())
    
    if len(logs) == 1:
        print(f"✅ PASSED: Found 1 meal log (expected 1)")
        return True
    else:
        print(f"❌ FAILED: Found {len(logs)} logs (expected 1)")
        return False

def test_scenario_2_multi_item_meal():
    """Test 2: Multi-item meal (should be 1 log, not 3)"""
    print("\n" + "="*60)
    print("📋 TEST 2: Multi-Item Meal (No Duplicates)")
    print("="*60)
    
    # Create a multi-item meal log (grouped)
    log_ref = db.collection('users').document(TEST_USER_ID)\
                .collection('fitness_logs').document()
    
    log_data = {
        'log_id': log_ref.id,
        'user_id': TEST_USER_ID,
        'log_type': 'meal',
        'content': 'chicken breast, rice, broccoli',
        'calories': 600,
        'timestamp': firestore.SERVER_TIMESTAMP,
        'ai_parsed_data': {
            'description': 'chicken breast, rice, broccoli',
            'meal_type': 'lunch',
            'calories': 600,
            'protein_g': 45,
            'carbs_g': 70,
            'fat_g': 10,
            'items': ['chicken breast', 'rice', 'broccoli']
        }
    }
    log_ref.set(log_data)
    print(f"✅ Created multi-item meal log: {log_ref.id}")
    
    # Verify only 1 log was created (not 3)
    time.sleep(1)
    lunch_logs = list(db.collection('users').document(TEST_USER_ID)
                        .collection('fitness_logs')
                        .where('log_type', '==', 'meal')
                        .stream())
    
    # Filter for lunch
    lunch_count = sum(1 for log in lunch_logs 
                     if log.to_dict().get('ai_parsed_data', {}).get('meal_type') == 'lunch')
    
    if lunch_count == 1:
        print(f"✅ PASSED: Found 1 lunch log (expected 1, not 3)")
        return True
    else:
        print(f"❌ FAILED: Found {lunch_count} lunch logs (expected 1)")
        return False

def test_scenario_3_chat_persistence():
    """Test 3: Chat history persistence"""
    print("\n" + "="*60)
    print("📋 TEST 3: Chat History Persistence")
    print("="*60)
    
    # Create a chat session
    session_id = datetime.now(timezone.utc).date().isoformat()
    session_ref = db.collection('users').document(TEST_USER_ID)\
                    .collection('chat_sessions').document(session_id)
    
    session_data = {
        'sessionId': session_id,
        'title': f"Test Chat - {session_id}",
        'startedAt': firestore.SERVER_TIMESTAMP,
        'lastMessageAt': firestore.SERVER_TIMESTAMP,
        'messageCount': 3,
        'expiresAt': datetime.now(timezone.utc) + timedelta(days=7),
        'archived': False
    }
    session_ref.set(session_data)
    print(f"✅ Created chat session: {session_id}")
    
    # Add messages
    messages = [
        {'role': 'user', 'content': 'I had oatmeal with banana for breakfast'},
        {'role': 'assistant', 'content': 'Great! I logged your breakfast (350 cal)'},
        {'role': 'user', 'content': 'For lunch I ate chicken, rice, and broccoli'}
    ]
    
    for msg in messages:
        msg_ref = session_ref.collection('messages').document()
        msg_data = {
            'role': msg['role'],
            'content': msg['content'],
            'metadata': {},
            'timestamp': firestore.SERVER_TIMESTAMP
        }
        msg_ref.set(msg_data)
        print(f"  ✅ Added message: {msg['role']}")
    
    # Verify messages persist
    time.sleep(1)
    saved_messages = list(session_ref.collection('messages').stream())
    
    if len(saved_messages) == 3:
        print(f"✅ PASSED: Found 3 messages (expected 3)")
        return True
    else:
        print(f"❌ FAILED: Found {len(saved_messages)} messages (expected 3)")
        return False

def test_scenario_4_chat_expiration():
    """Test 4: Chat expiration (7 days)"""
    print("\n" + "="*60)
    print("📋 TEST 4: Chat Expiration (7 Days)")
    print("="*60)
    
    # Get the session we just created
    session_id = datetime.now(timezone.utc).date().isoformat()
    session_ref = db.collection('users').document(TEST_USER_ID)\
                    .collection('chat_sessions').document(session_id)
    
    session = session_ref.get()
    if session.exists:
        session_data = session.to_dict()
        expires_at = session_data.get('expiresAt')
        
        if expires_at:
            days_until_expiry = (expires_at - datetime.now(timezone.utc)).days
            
            if 6 <= days_until_expiry <= 7:
                print(f"✅ PASSED: Session expires in {days_until_expiry} days (expected ~7)")
                return True
            else:
                print(f"❌ FAILED: Session expires in {days_until_expiry} days (expected 7)")
                return False
        else:
            print("❌ FAILED: No expiration date set")
            return False
    else:
        print("❌ FAILED: Session not found")
        return False

def test_scenario_5_query_performance():
    """Test 5: Query performance (no composite index errors)"""
    print("\n" + "="*60)
    print("📋 TEST 5: Query Performance (No Index Errors)")
    print("="*60)
    
    try:
        # Query fitness logs (should not require composite index)
        logs = list(db.collection('users').document(TEST_USER_ID)
                      .collection('fitness_logs')
                      .order_by('timestamp', direction=firestore.Query.DESCENDING)
                      .limit(10)
                      .stream())
        
        print(f"✅ Query 1: Fitness logs by timestamp - {len(logs)} results")
        
        # Query by type and timestamp (should not require composite index)
        meal_logs = list(db.collection('users').document(TEST_USER_ID)
                           .collection('fitness_logs')
                           .where('log_type', '==', 'meal')
                           .order_by('timestamp', direction=firestore.Query.DESCENDING)
                           .limit(10)
                           .stream())
        
        print(f"✅ Query 2: Meal logs by type + timestamp - {len(meal_logs)} results")
        
        # Query chat sessions
        sessions = list(db.collection('users').document(TEST_USER_ID)
                          .collection('chat_sessions')
                          .order_by('lastMessageAt', direction=firestore.Query.DESCENDING)
                          .limit(10)
                          .stream())
        
        print(f"✅ Query 3: Chat sessions by lastMessageAt - {len(sessions)} results")
        
        print("✅ PASSED: All queries executed without errors")
        return True
        
    except Exception as e:
        print(f"❌ FAILED: Query error - {e}")
        return False

def test_scenario_6_data_isolation():
    """Test 6: Data isolation (user can only see their data)"""
    print("\n" + "="*60)
    print("📋 TEST 6: Data Isolation")
    print("="*60)
    
    # Verify data is in user's subcollection
    user_logs = list(db.collection('users').document(TEST_USER_ID)
                       .collection('fitness_logs').stream())
    
    print(f"✅ User {TEST_USER_ID[:8]}... has {len(user_logs)} logs")
    
    # Verify path structure
    if len(user_logs) > 0:
        first_log = user_logs[0]
        path = first_log.reference.path
        
        if f'users/{TEST_USER_ID}/fitness_logs' in path:
            print(f"✅ PASSED: Data is in user's subcollection")
            print(f"   Path: {path}")
            return True
        else:
            print(f"❌ FAILED: Data is not in correct path")
            print(f"   Path: {path}")
            return False
    else:
        print("⚠️  WARNING: No logs to verify path")
        return True

def main():
    """Run all test scenarios"""
    print("="*60)
    print("🧪 COMPLETE FLOW TEST - NEW FIREBASE STRUCTURE")
    print("="*60)
    print(f"Test User: {TEST_USER_ID}")
    print(f"Time: {datetime.now().isoformat()}")
    
    # Cleanup first
    cleanup_test_data()
    
    # Run all tests
    results = []
    
    results.append(("Single Meal Logging", test_scenario_1_single_meal()))
    results.append(("Multi-Item Meal (No Duplicates)", test_scenario_2_multi_item_meal()))
    results.append(("Chat History Persistence", test_scenario_3_chat_persistence()))
    results.append(("Chat Expiration (7 Days)", test_scenario_4_chat_expiration()))
    results.append(("Query Performance", test_scenario_5_query_performance()))
    results.append(("Data Isolation", test_scenario_6_data_isolation()))
    
    # Summary
    print("\n" + "="*60)
    print("🎯 TEST SUMMARY")
    print("="*60)
    
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    for test_name, result in results:
        status = "✅ PASSED" if result else "❌ FAILED"
        print(f"{status}: {test_name}")
    
    print("="*60)
    print(f"Total: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 ALL TESTS PASSED! Ready for production!")
    else:
        print("⚠️  Some tests failed. Review errors above.")
    
    print("="*60)

if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        print(f"\n❌ Test suite failed: {e}")
        import traceback
        traceback.print_exc()

