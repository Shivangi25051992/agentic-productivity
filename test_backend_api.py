#!/usr/bin/env python3
"""
Test backend API endpoints with new structure
"""

import requests
import json

BASE_URL = "http://localhost:8000"

# Alice's user ID (we'll use direct API calls without auth for testing)
TEST_USER_ID = "Po6FIpjF4cM1WWt8duHjD1BXqY13"

def test_health():
    """Test health endpoint"""
    print("\n📋 TEST: Health Check")
    response = requests.get(f"{BASE_URL}/health")
    
    if response.status_code == 200:
        data = response.json()
        print(f"✅ Backend is healthy: {data}")
        return True
    else:
        print(f"❌ Backend is not healthy: {response.status_code}")
        return False

def test_backend_can_read_new_structure():
    """
    Test that backend service layer can read from new structure
    We'll directly test the database service
    """
    print("\n📋 TEST: Backend Database Service")
    
    # Import backend services
    import sys
    sys.path.insert(0, '/Users/pchintanwar/Documents/Projects-AIProductivity/agentic-productivity')
    
    from app.services.database import list_fitness_logs_by_user, USE_NEW_STRUCTURE
    from app.services.chat_history_service import get_chat_history_service
    
    print(f"  - USE_NEW_STRUCTURE flag: {USE_NEW_STRUCTURE}")
    
    # Test fitness logs
    print("\n  Testing fitness logs...")
    logs = list_fitness_logs_by_user(TEST_USER_ID, limit=5)
    print(f"  ✅ Found {len(logs)} fitness logs")
    
    for log in logs:
        print(f"    - {log.content[:50]}... ({log.calories} cal)")
    
    # Test chat history
    print("\n  Testing chat history...")
    chat_service = get_chat_history_service()
    messages = chat_service.get_user_history(TEST_USER_ID, limit=10)
    print(f"  ✅ Found {len(messages)} chat messages")
    
    for msg in messages[:3]:
        role = msg.get('role', 'unknown')
        content = msg.get('content', '')[:40]
        print(f"    - {role}: {content}...")
    
    return len(logs) > 0 and len(messages) > 0

def main():
    """Run all tests"""
    print("=" * 60)
    print("🧪 TESTING BACKEND API WITH NEW STRUCTURE")
    print("=" * 60)
    
    # Test 1: Health check
    if not test_health():
        print("\n❌ Backend is not running!")
        return
    
    # Test 2: Backend can read new structure
    if test_backend_can_read_new_structure():
        print("\n" + "=" * 60)
        print("✅ BACKEND CAN READ NEW STRUCTURE!")
        print("=" * 60)
    else:
        print("\n" + "=" * 60)
        print("❌ BACKEND CANNOT READ NEW STRUCTURE")
        print("=" * 60)

if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        print(f"\n❌ Test failed: {e}")
        import traceback
        traceback.print_exc()

