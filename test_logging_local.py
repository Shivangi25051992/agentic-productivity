#!/usr/bin/env python3
"""
Local test script to verify food logging is working correctly
Tests the complete flow: Chat → Parse → Save to Firestore → Retrieve
"""

import os
import sys
import requests
import json
from datetime import datetime, timezone

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Load environment variables
from dotenv import load_dotenv
load_dotenv()
load_dotenv('.env.local', override=True)

# Test configuration
BASE_URL = "http://localhost:8000"
TEST_USER_EMAIL = "alice.test@aiproductivity.app"
TEST_USER_PASSWORD = "test123"  # Replace with actual password

def print_section(title):
    print(f"\n{'='*60}")
    print(f"  {title}")
    print(f"{'='*60}\n")

def test_login():
    """Test 1: Login and get auth token"""
    print_section("TEST 1: Login")
    
    # For testing, we'll use Firebase ID token
    # In production, you'd get this from Firebase Auth SDK
    print("⚠️  Note: Using manual Firebase ID token for testing")
    print("Please provide a valid Firebase ID token for testing:")
    token = input("Token: ").strip()
    
    if not token:
        print("❌ No token provided. Skipping auth tests.")
        return None
    
    return token

def test_chat_endpoint(token, user_input):
    """Test 2: Send message to chat endpoint"""
    print_section(f"TEST 2: Chat Endpoint - '{user_input}'")
    
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }
    
    payload = {
        "user_input": user_input,
        "type": "auto"
    }
    
    print(f"📤 Sending: {user_input}")
    
    try:
        response = requests.post(
            f"{BASE_URL}/chat",
            headers=headers,
            json=payload,
            timeout=30
        )
        
        print(f"Status Code: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Response received:")
            print(f"   Message: {data.get('message', '')[:100]}...")
            print(f"   Items: {len(data.get('items', []))}")
            print(f"   Needs Clarification: {data.get('needs_clarification', False)}")
            return data
        else:
            print(f"❌ Error: {response.status_code}")
            print(f"   Response: {response.text}")
            return None
            
    except Exception as e:
        print(f"❌ Exception: {type(e).__name__}: {str(e)}")
        return None

def test_firestore_direct():
    """Test 3: Check Firestore directly"""
    print_section("TEST 3: Firestore Direct Check")
    
    try:
        from google.cloud import firestore
        
        project = os.getenv("GOOGLE_CLOUD_PROJECT", "productivityai-mvp")
        print(f"Project: {project}")
        
        db = firestore.Client(project=project)
        
        # Check if we're using new structure
        print("\n🔍 Checking for fitness logs...")
        
        # Try new structure first
        print("\n1. Checking NEW structure (users/{userId}/fitness_logs)...")
        users_ref = db.collection('users')
        users = list(users_ref.limit(5).stream())
        
        if users:
            print(f"   Found {len(users)} users")
            for user_doc in users:
                user_id = user_doc.id
                print(f"\n   User: {user_id}")
                
                # Check fitness_logs subcollection
                logs_ref = user_doc.reference.collection('fitness_logs')
                logs = list(logs_ref.order_by('timestamp', direction=firestore.Query.DESCENDING).limit(5).stream())
                
                if logs:
                    print(f"   ✅ Found {len(logs)} fitness logs:")
                    for log in logs:
                        log_data = log.to_dict()
                        print(f"      - {log.id}: {log_data.get('content', 'N/A')} ({log_data.get('calories', 0)} cal)")
                else:
                    print(f"   ⚠️  No fitness logs found in subcollection")
        else:
            print("   ⚠️  No users found")
        
        # Try old structure
        print("\n2. Checking OLD structure (fitness_logs)...")
        old_logs_ref = db.collection('fitness_logs')
        old_logs = list(old_logs_ref.order_by('timestamp', direction=firestore.Query.DESCENDING).limit(5).stream())
        
        if old_logs:
            print(f"   ✅ Found {len(old_logs)} logs in old structure:")
            for log in old_logs:
                log_data = log.to_dict()
                print(f"      - {log.id}: {log_data.get('content', 'N/A')} ({log_data.get('calories', 0)} cal)")
        else:
            print(f"   ⚠️  No logs in old structure")
        
        return True
        
    except Exception as e:
        print(f"❌ Firestore check failed: {type(e).__name__}: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

def test_get_daily_stats(token):
    """Test 4: Get daily stats from API"""
    print_section("TEST 4: Get Daily Stats")
    
    headers = {
        "Authorization": f"Bearer {token}",
    }
    
    try:
        response = requests.get(
            f"{BASE_URL}/fitness/daily-stats",
            headers=headers,
            timeout=10
        )
        
        print(f"Status Code: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Daily stats received:")
            print(f"   Calories: {data.get('calories_consumed', 0)} / {data.get('calories_goal', 0)}")
            print(f"   Protein: {data.get('protein_g', 0)}g")
            print(f"   Activities: {len(data.get('activities', []))}")
            
            # Print activities
            activities = data.get('activities', [])
            if activities:
                print(f"\n   Recent activities:")
                for act in activities[:5]:
                    print(f"      - {act.get('type', 'unknown')}: {act.get('content', 'N/A')}")
            
            return data
        else:
            print(f"❌ Error: {response.status_code}")
            print(f"   Response: {response.text}")
            return None
            
    except Exception as e:
        print(f"❌ Exception: {type(e).__name__}: {str(e)}")
        return None

def main():
    print("""
╔════════════════════════════════════════════════════════════╗
║                                                            ║
║         🧪 LOCAL FOOD LOGGING TEST SUITE                  ║
║                                                            ║
╚════════════════════════════════════════════════════════════╝
    """)
    
    # Check if backend is running
    try:
        response = requests.get(f"{BASE_URL}/health", timeout=5)
        if response.status_code == 200:
            print("✅ Backend is running")
        else:
            print("❌ Backend returned unexpected status")
            return
    except:
        print("❌ Backend is not running. Please start it with:")
        print("   python -m uvicorn app.main:app --reload")
        return
    
    # Test 1: Login (get token)
    token = test_login()
    
    if not token:
        print("\n⚠️  Skipping API tests (no auth token)")
        print("   Running Firestore direct check only...")
        test_firestore_direct()
        return
    
    # Test 2: Send chat message
    test_inputs = [
        "2 eggs and 1 apple for breakfast",
        "chicken breast and rice for lunch",
        "ran 5km"
    ]
    
    for user_input in test_inputs:
        chat_response = test_chat_endpoint(token, user_input)
        if chat_response:
            print(f"✅ Chat response OK")
        else:
            print(f"❌ Chat response failed")
    
    # Test 3: Check Firestore directly
    test_firestore_direct()
    
    # Test 4: Get daily stats
    test_get_daily_stats(token)
    
    print_section("SUMMARY")
    print("✅ Tests complete!")
    print("\nIf you see fitness logs in Firestore but not in daily stats,")
    print("the issue is in the frontend data fetching logic.")
    print("\nIf you don't see logs in Firestore at all,")
    print("the issue is in the backend save logic.")

if __name__ == "__main__":
    main()

