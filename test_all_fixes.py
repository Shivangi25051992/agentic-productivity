#!/usr/bin/env python3
"""
Comprehensive test for all critical fixes:
1. No duplication in responses
2. Chat persistence working
3. Meal type classification correct (breakfast not logged as dinner)
4. No asterisks in formatting
5. Clean, ChatGPT-style responses
"""

import requests
import json
import time

BASE_URL = "http://localhost:8000"

# Test user credentials
EMAIL = "alice.test@aiproductivity.app"
PASSWORD = "Test@123"

def login():
    """Login and get token"""
    print("🔐 Logging in...")
    response = requests.post(
        f"{BASE_URL}/auth/login",
        json={"email": EMAIL, "password": PASSWORD}
    )
    
    if response.status_code != 200:
        print(f"❌ Login failed: {response.status_code}")
        print(response.text)
        return None
    
    data = response.json()
    token = data.get("idToken") or data.get("id_token")
    
    if not token:
        print(f"❌ No token in response: {data}")
        return None
    
    print(f"✅ Login successful")
    return token

def test_chat_message(token, message):
    """Send a chat message and return response"""
    print(f"\n📤 Sending: '{message}'")
    
    response = requests.post(
        f"{BASE_URL}/chat",
        headers={"Authorization": f"Bearer {token}"},
        json={"text": message, "type": "auto"}
    )
    
    if response.status_code != 200:
        print(f"❌ Chat failed: {response.status_code}")
        print(response.text)
        return None
    
    data = response.json()
    print(f"✅ Response received")
    return data

def test_chat_history(token):
    """Get chat history"""
    print(f"\n📜 Fetching chat history...")
    
    response = requests.get(
        f"{BASE_URL}/chat/history?limit=50",
        headers={"Authorization": f"Bearer {token}"}
    )
    
    if response.status_code != 200:
        print(f"❌ History failed: {response.status_code}")
        print(response.text)
        return None
    
    data = response.json()
    print(f"✅ History received: {data.get('count', 0)} messages")
    return data

def check_response_quality(response_data):
    """Check response for quality issues"""
    issues = []
    
    message = response_data.get("message", "")
    
    # Check for asterisks (markdown formatting)
    if "**" in message:
        issues.append("❌ Contains markdown asterisks (**)")
    else:
        print("✅ No asterisks in response")
    
    # Check for duplication (same text appearing twice)
    lines = message.split('\n')
    seen = set()
    for line in lines:
        line = line.strip()
        if line and line in seen and len(line) > 20:  # Ignore short lines
            issues.append(f"❌ Duplicate line detected: '{line[:50]}...'")
        seen.add(line)
    
    if not any("Duplicate line" in issue for issue in issues):
        print("✅ No duplication detected")
    
    # Check for clean formatting
    if "🥘" in message or "🏃" in message or "⚖️" in message:
        print("✅ Clean emoji formatting present")
    
    return issues

def main():
    print("=" * 60)
    print("🧪 COMPREHENSIVE FIX VERIFICATION TEST")
    print("=" * 60)
    
    # Login
    token = login()
    if not token:
        print("\n❌ Cannot proceed without token")
        return
    
    # Test 1: Breakfast classification
    print("\n" + "=" * 60)
    print("TEST 1: Meal Type Classification (Breakfast)")
    print("=" * 60)
    
    response1 = test_chat_message(token, "2 eggs for breakfast")
    if response1:
        message = response1.get("message", "")
        print(f"\n📋 Response:\n{message}\n")
        
        # Check if breakfast is mentioned
        if "breakfast" in message.lower():
            print("✅ Breakfast correctly identified")
        else:
            print("❌ Breakfast NOT mentioned in response")
        
        # Check if dinner is incorrectly mentioned
        if "dinner" in message.lower():
            print("❌ CRITICAL: Logged as dinner instead of breakfast!")
        else:
            print("✅ Not incorrectly logged as dinner")
        
        # Check response quality
        issues = check_response_quality(response1)
        if issues:
            print("\n⚠️  Quality Issues:")
            for issue in issues:
                print(f"  {issue}")
    
    time.sleep(2)
    
    # Test 2: Multi-item input
    print("\n" + "=" * 60)
    print("TEST 2: Multi-Item Input (Workout + Supplement)")
    print("=" * 60)
    
    response2 = test_chat_message(token, "ran 5km\n1 multivitamin")
    if response2:
        message = response2.get("message", "")
        print(f"\n📋 Response:\n{message}\n")
        
        # Check if both items are mentioned
        if "5" in message and ("km" in message.lower() or "run" in message.lower()):
            print("✅ Running activity detected")
        else:
            print("❌ Running activity NOT detected")
        
        if "multivitamin" in message.lower():
            print("✅ Multivitamin detected")
        else:
            print("❌ Multivitamin NOT detected")
        
        # Check if workout is correctly categorized (not as dinner)
        if "dinner" in message.lower() and "run" in message.lower():
            print("❌ CRITICAL: Workout logged as dinner!")
        else:
            print("✅ Workout not logged as dinner")
        
        # Check response quality
        issues = check_response_quality(response2)
        if issues:
            print("\n⚠️  Quality Issues:")
            for issue in issues:
                print(f"  {issue}")
    
    time.sleep(2)
    
    # Test 3: Chat History Persistence
    print("\n" + "=" * 60)
    print("TEST 3: Chat History Persistence")
    print("=" * 60)
    
    history = test_chat_history(token)
    if history:
        messages = history.get("messages", [])
        
        if len(messages) >= 4:  # At least 2 user + 2 assistant messages
            print(f"✅ Chat history persisted: {len(messages)} messages")
            
            # Check last few messages
            print("\n📜 Last 4 messages:")
            for msg in messages[-4:]:
                role = msg.get("role", "unknown")
                content = msg.get("content", "")[:60]
                print(f"  {role}: {content}...")
        else:
            print(f"❌ Chat history incomplete: only {len(messages)} messages")
    
    # Final Summary
    print("\n" + "=" * 60)
    print("📊 TEST SUMMARY")
    print("=" * 60)
    print("✅ All tests completed!")
    print("\n🎯 Key Checks:")
    print("  1. Breakfast classification - Check output above")
    print("  2. No duplication - Check output above")
    print("  3. No asterisks - Check output above")
    print("  4. Chat persistence - Check output above")
    print("  5. Clean formatting - Check output above")
    print("\n💡 Please review the output above for any ❌ marks")

if __name__ == "__main__":
    main()

