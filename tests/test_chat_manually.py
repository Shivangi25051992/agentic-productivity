#!/usr/bin/env python3
"""
Manual Chat Testing Script
Tests chat functionality with existing user credentials
"""

import requests
import json
from datetime import datetime

API_BASE = "http://localhost:8000"

# Existing test user
TEST_USER = {
    "email": "alice.test@aiproductivity.app",
    "password": "TestPass123!"
}

def login():
    """Login and get auth token"""
    response = requests.post(
        f"{API_BASE}/auth/login",
        json=TEST_USER,
        timeout=5
    )
    
    if response.status_code == 200:
        data = response.json()
        token = data.get('token') or data.get('access_token') or data.get('idToken')
        print(f"✅ Logged in as {TEST_USER['email']}")
        return token
    else:
        print(f"❌ Login failed: {response.status_code}")
        print(response.text)
        return None

def test_chat(token, input_text):
    """Test a chat input"""
    print(f"\n{'='*80}")
    print(f"📝 Input: {input_text}")
    print(f"{'='*80}")
    
    headers = {"Authorization": f"Bearer {token}"}
    response = requests.post(
        f"{API_BASE}/chat",
        json={"user_input": input_text},
        headers=headers,
        timeout=10
    )
    
    if response.status_code == 200:
        result = response.json()
        
        # Display response
        print(f"✅ Status: Success")
        print(f"📨 Message: {result.get('message', '')}")
        print(f"❓ Needs Clarification: {result.get('needs_clarification', False)}")
        
        if result.get('clarification_question'):
            print(f"🤔 Question: {result.get('clarification_question')}")
        
        # Display items
        items = result.get('items', [])
        if items:
            print(f"\n📦 Items Logged: {len(items)}")
            for i, item in enumerate(items, 1):
                print(f"\n  Item {i}:")
                print(f"    Category: {item.get('category')}")
                print(f"    Summary: {item.get('summary')}")
                
                data = item.get('data', {})
                if data.get('calories'):
                    print(f"    Calories: {data.get('calories')} kcal")
                if data.get('protein_g'):
                    print(f"    Protein: {data.get('protein_g')}g")
                if data.get('carbs_g'):
                    print(f"    Carbs: {data.get('carbs_g')}g")
                if data.get('fat_g'):
                    print(f"    Fat: {data.get('fat_g')}g")
        
        return result
    else:
        print(f"❌ Error: {response.status_code}")
        print(response.text)
        return None

def get_chat_history(token):
    """Get chat history"""
    print(f"\n{'='*80}")
    print(f"📜 Chat History")
    print(f"{'='*80}")
    
    headers = {"Authorization": f"Bearer {token}"}
    response = requests.get(
        f"{API_BASE}/chat/history?limit=20",
        headers=headers,
        timeout=5
    )
    
    if response.status_code == 200:
        result = response.json()
        messages = result.get('messages', [])
        
        print(f"✅ Found {len(messages)} messages")
        
        for msg in messages[-10:]:  # Show last 10
            role = msg.get('role', 'unknown')
            content = msg.get('content', '')
            timestamp = msg.get('timestamp', '')
            
            if role == 'user':
                print(f"\n👤 USER: {content}")
            else:
                print(f"🤖 AI: {content}")
        
        return messages
    else:
        print(f"❌ Error: {response.status_code}")
        print(response.text)
        return []

def get_chat_stats(token):
    """Get chat statistics"""
    print(f"\n{'='*80}")
    print(f"📊 Chat Statistics")
    print(f"{'='*80}")
    
    headers = {"Authorization": f"Bearer {token}"}
    response = requests.get(
        f"{API_BASE}/chat/stats",
        headers=headers,
        timeout=5
    )
    
    if response.status_code == 200:
        stats = response.json()
        
        print(f"✅ Statistics:")
        print(f"  Total Messages: {stats.get('total_messages', 0)}")
        print(f"  User Messages: {stats.get('user_messages', 0)}")
        print(f"  AI Messages: {stats.get('assistant_messages', 0)}")
        print(f"  Meals Logged: {stats.get('meals_logged', 0)}")
        print(f"  Total Calories: {stats.get('total_calories', 0)} kcal")
        
        return stats
    else:
        print(f"❌ Error: {response.status_code}")
        print(response.text)
        return {}

def main():
    print(f"\n{'='*80}")
    print(f"🧪 MANUAL CHAT TESTING")
    print(f"{'='*80}\n")
    
    # Login
    token = login()
    if not token:
        print("❌ Cannot proceed without authentication")
        return
    
    # Test cases
    test_cases = [
        "eggs",  # Should ask for clarification
        "2 eggs",  # Should log directly
        "2 eggs, 1 bowl rice, 5 pistachios",  # Multi-food
        "chicken breast with vegetables",  # Complex meal
        "oatmeal",  # Single food
        "protein shake",  # Beverage
    ]
    
    print("\n" + "="*80)
    print("🧪 RUNNING TEST CASES")
    print("="*80)
    
    results = []
    for test_input in test_cases:
        result = test_chat(token, test_input)
        results.append({
            'input': test_input,
            'result': result,
            'timestamp': datetime.now().isoformat()
        })
    
    # Get history
    history = get_chat_history(token)
    
    # Get stats
    stats = get_chat_stats(token)
    
    # Summary
    print(f"\n{'='*80}")
    print(f"📊 TEST SUMMARY")
    print(f"{'='*80}")
    
    successful = sum(1 for r in results if r['result'] is not None)
    failed = len(results) - successful
    
    print(f"✅ Successful: {successful}/{len(results)}")
    print(f"❌ Failed: {failed}/{len(results)}")
    print(f"📜 History Messages: {len(history)}")
    print(f"🍽️  Meals Logged: {stats.get('meals_logged', 0)}")
    print(f"🔥 Total Calories: {stats.get('total_calories', 0)} kcal")
    
    # Save results
    with open('tests/manual_test_results.json', 'w') as f:
        json.dump({
            'test_cases': results,
            'history': history,
            'stats': stats,
            'timestamp': datetime.now().isoformat()
        }, f, indent=2)
    
    print(f"\n💾 Results saved to: tests/manual_test_results.json")
    print(f"\n{'='*80}\n")

if __name__ == "__main__":
    main()


