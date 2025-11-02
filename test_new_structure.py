#!/usr/bin/env python3
"""
Test script to verify new subcollection structure works correctly
Tests: chat history persistence, fitness logs, no duplicates
"""

import requests
import json
from datetime import datetime

BASE_URL = "http://localhost:8000"

# Alice's test credentials
TEST_USER = {
    "email": "alice.test@aiproductivity.app",
    "token": "eyJhbGciOiJSUzI1NiIsImtpZCI6IjZmNzI1NDEwMWY1NmU0MWNmMzVjZTczNTA3NTUzY2ZmZjkyZGM2ZjYiLCJ0eXAiOiJKV1QifQ.eyJpc3MiOiJodHRwczovL3NlY3VyZXRva2VuLmdvb2dsZS5jb20vYWlwcm9kdWN0aXZpdHktZDZjZjYiLCJhdWQiOiJhaXByb2R1Y3Rpdml0eS1kNmNmNiIsImF1dGhfdGltZSI6MTczMDU0NjM3OSwidXNlcl9pZCI6IlBvNkZJcGpGNGNNMVdXdDhkdUhqRDFCWHFZMTMiLCJzdWIiOiJQbzZGSXBqRjRjTTFXV3Q4ZHVIakQxQlhxWTEzIiwiaWF0IjoxNzMwNTQ2Mzc5LCJleHAiOjE3MzA1NDk5NzksImVtYWlsIjoiYWxpY2UudGVzdEBhaXByb2R1Y3Rpdml0eS5hcHAiLCJlbWFpbF92ZXJpZmllZCI6ZmFsc2UsImZpcmViYXNlIjp7ImlkZW50aXRpZXMiOnsiZW1haWwiOlsiYWxpY2UudGVzdEBhaXByb2R1Y3Rpdml0eS5hcHAiXX0sInNpZ25faW5fcHJvdmlkZXIiOiJwYXNzd29yZCJ9fQ.invalid"  # Will be replaced with valid token
}

def get_headers():
    """Get auth headers"""
    return {
        "Authorization": f"Bearer {TEST_USER['token']}",
        "Content-Type": "application/json"
    }

def test_chat_message(message: str):
    """Send a chat message and return response"""
    print(f"\n📤 Sending: '{message}'")
    
    response = requests.post(
        f"{BASE_URL}/chat",
        headers=get_headers(),
        json={"text": message}
    )
    
    if response.status_code == 200:
        data = response.json()
        print(f"✅ Response: {data.get('message', '')[:100]}...")
        return data
    else:
        print(f"❌ Error: {response.status_code} - {response.text}")
        return None

def test_chat_history():
    """Test chat history persistence"""
    print("\n🔍 Testing Chat History...")
    
    response = requests.get(
        f"{BASE_URL}/chat/history?limit=50",
        headers=get_headers()
    )
    
    if response.status_code == 200:
        data = response.json()
        messages = data.get('messages', [])
        print(f"✅ Found {len(messages)} messages in history")
        
        # Show last 3 messages
        for msg in messages[-3:]:
            role = msg.get('role', 'unknown')
            content = msg.get('content', '')[:50]
            print(f"  - {role}: {content}...")
        
        return len(messages)
    else:
        print(f"❌ Error: {response.status_code} - {response.text}")
        return 0

def test_fitness_logs():
    """Test fitness logs (check for duplicates)"""
    print("\n🔍 Testing Fitness Logs...")
    
    response = requests.get(
        f"{BASE_URL}/logs/today",
        headers=get_headers()
    )
    
    if response.status_code == 200:
        data = response.json()
        logs = data.get('logs', [])
        print(f"✅ Found {len(logs)} logs today")
        
        # Check for duplicates
        meal_types = {}
        for log in logs:
            if log.get('log_type') == 'meal':
                meal_type = log.get('ai_parsed_data', {}).get('meal_type', 'unknown')
                meal_types[meal_type] = meal_types.get(meal_type, 0) + 1
        
        print(f"  Meal breakdown: {meal_types}")
        
        # Flag duplicates
        duplicates = {k: v for k, v in meal_types.items() if v > 1}
        if duplicates:
            print(f"⚠️  WARNING: Duplicate meals detected: {duplicates}")
        else:
            print(f"✅ No duplicate meals!")
        
        return logs
    else:
        print(f"❌ Error: {response.status_code} - {response.text}")
        return []

def main():
    """Run all tests"""
    print("=" * 60)
    print("🧪 TESTING NEW SUBCOLLECTION STRUCTURE")
    print("=" * 60)
    
    # Test 1: Send a meal message
    print("\n📋 TEST 1: Send Meal Message")
    test_chat_message("I had oatmeal with banana for breakfast")
    
    # Test 2: Check chat history persists
    print("\n📋 TEST 2: Check Chat History Persistence")
    history_count = test_chat_history()
    
    if history_count > 0:
        print("✅ Chat history is persisting!")
    else:
        print("❌ Chat history NOT persisting!")
    
    # Test 3: Send multi-item meal
    print("\n📋 TEST 3: Send Multi-Item Meal (Check for Duplicates)")
    test_chat_message("For lunch I ate grilled chicken, rice, and broccoli")
    
    # Test 4: Check fitness logs
    print("\n📋 TEST 4: Check Fitness Logs")
    logs = test_fitness_logs()
    
    # Test 5: Send another message and verify history grows
    print("\n📋 TEST 5: Send Another Message")
    test_chat_message("I did 30 minutes of jogging")
    
    print("\n📋 TEST 6: Verify History Grew")
    new_history_count = test_chat_history()
    
    if new_history_count > history_count:
        print(f"✅ History grew from {history_count} to {new_history_count}")
    else:
        print(f"❌ History did NOT grow (was {history_count}, now {new_history_count})")
    
    print("\n" + "=" * 60)
    print("🎯 TEST SUMMARY")
    print("=" * 60)
    print(f"✅ Chat messages sent: 3")
    print(f"✅ Chat history count: {new_history_count}")
    print(f"✅ Fitness logs today: {len(logs)}")
    print("=" * 60)

if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        print(f"\n❌ Test failed with error: {e}")
        import traceback
        traceback.print_exc()

