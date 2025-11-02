#!/usr/bin/env python3
"""
Simple automated tests - sends messages directly to backend
User verifies results in UI
"""

import requests
import time
from datetime import datetime

BASE_URL = "http://localhost:8000"

# Test scenarios
TEST_SCENARIOS = [
    {
        "name": "Breakfast Classification",
        "input": "2 eggs for breakfast",
        "expected": ["breakfast", "eggs", "140", "kcal"],
        "not_expected": ["dinner", "**"]
    },
    {
        "name": "Multi-line Workout + Supplement",
        "input": "ran 5km\n1 multivitamin",
        "expected": ["5", "km", "run", "multivitamin", "Exercise"],
        "not_expected": ["dinner", "**"]
    },
    {
        "name": "Lunch with Details",
        "input": "chicken breast with rice and broccoli for lunch",
        "expected": ["lunch", "chicken", "rice", "broccoli"],
        "not_expected": ["breakfast", "dinner", "**"]
    },
    {
        "name": "Chocolate Bar (Smart Assumption)",
        "input": "chocolate bar",
        "expected": ["chocolate", "200", "kcal"],
        "not_expected": ["0 kcal", "**"]
    },
    {
        "name": "Dinner Explicit",
        "input": "salmon with vegetables for dinner",
        "expected": ["dinner", "salmon", "vegetables"],
        "not_expected": ["breakfast", "lunch", "**"]
    },
    {
        "name": "Workout Only",
        "input": "30 minutes yoga",
        "expected": ["yoga", "30", "Exercise"],
        "not_expected": ["Food", "meal", "**"]
    },
    {
        "name": "Task/Reminder",
        "input": "remind me to call doctor at 3pm",
        "expected": ["doctor", "3pm"],
        "not_expected": ["**"]
    },
    {
        "name": "Complex Multi-Category",
        "input": "oatmeal for breakfast\nwalked 3km\nprotein shake\ncall mom at 5pm",
        "expected": ["oatmeal", "breakfast", "walked", "3", "km", "protein", "mom"],
        "not_expected": ["**"]
    }
]

def get_token_from_env():
    """Try to get token from environment or file"""
    import os
    
    # Try environment variable
    token = os.environ.get("ALICE_TOKEN")
    if token:
        return token
    
    # Try reading from a token file
    token_file = "/Users/pchintanwar/Documents/Projects-AIProductivity/agentic-productivity/.alice_token"
    try:
        with open(token_file, 'r') as f:
            token = f.read().strip()
            if token:
                return token
    except:
        pass
    
    return None

def send_message_no_auth(message):
    """
    Send message without auth - for testing backend directly
    This will fail with 401, but we can see if the endpoint is working
    """
    try:
        response = requests.post(
            f"{BASE_URL}/chat",
            json={"text": message, "type": "auto"},
            timeout=30
        )
        return response.status_code, response.text
    except Exception as e:
        return None, str(e)

def main():
    print("=" * 70)
    print("🧪 AUTOMATED TEST RUNNER - ALICE'S ACCOUNT")
    print("=" * 70)
    print(f"Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"Backend: {BASE_URL}")
    print(f"Frontend: http://localhost:3000")
    print("=" * 70)
    print()
    
    # Check if we have a token
    token = get_token_from_env()
    
    if not token:
        print("⚠️  No authentication token found")
        print("⚠️  Tests will be sent to backend, but you need to be logged in via UI")
        print()
        print("📋 INSTRUCTIONS:")
        print("1. Open http://localhost:3000 in your browser")
        print("2. Login as: alice.test@aiproductivity.app")
        print("3. Open browser DevTools (F12)")
        print("4. Go to 'Assistant' tab in the app")
        print("5. Type each test message below manually:")
        print()
        
        for i, scenario in enumerate(TEST_SCENARIOS, 1):
            print(f"   Test {i}: {scenario['name']}")
            print(f"   Input: {scenario['input']}")
            print()
        
        print("\n6. After sending all messages:")
        print("   ✅ Check for duplication")
        print("   ✅ Check meal types (breakfast/lunch/dinner)")
        print("   ✅ Check no ** asterisks")
        print("   ✅ Navigate to Home → Back to Assistant")
        print("   ✅ Verify chat history persists")
        print()
        
        # Try to test backend connectivity at least
        print("🔍 Testing backend connectivity...")
        status, response = send_message_no_auth("test")
        
        if status == 401:
            print("✅ Backend is running (returned 401 Unauthorized as expected)")
        elif status == 403:
            print("✅ Backend is running (returned 403 Forbidden)")
        elif status:
            print(f"⚠️  Backend returned: {status}")
        else:
            print(f"❌ Backend connection failed: {response}")
        
        print("\n" + "=" * 70)
        print("📝 MANUAL TEST CHECKLIST")
        print("=" * 70)
        print()
        
        for i, scenario in enumerate(TEST_SCENARIOS, 1):
            print(f"□ Test {i}: {scenario['name']}")
            print(f"  Input: '{scenario['input']}'")
            print(f"  Expected to see: {', '.join(scenario['expected'][:3])}")
            print(f"  Should NOT see: {', '.join(scenario['not_expected'][:2])}")
            print()
        
        print("□ Chat Persistence Test:")
        print("  1. Navigate to Home page")
        print("  2. Navigate back to Assistant")
        print("  3. All 8 messages should still be visible")
        print()
        
        print("=" * 70)
        print("✅ TEST SCENARIOS READY")
        print("=" * 70)
        print("\n💡 Please run these tests manually in the UI and report results!")
        
    else:
        print("✅ Token found, running automated tests...")
        print()
        
        results = []
        
        for i, scenario in enumerate(TEST_SCENARIOS, 1):
            print(f"\n{'=' * 70}")
            print(f"TEST {i}: {scenario['name']}")
            print(f"{'=' * 70}")
            print(f"Input: '{scenario['input']}'")
            
            try:
                response = requests.post(
                    f"{BASE_URL}/chat",
                    headers={"Authorization": f"Bearer {token}"},
                    json={"text": scenario['input'], "type": "auto"},
                    timeout=30
                )
                
                if response.status_code == 200:
                    data = response.json()
                    message = data.get("message", "")
                    
                    # Check expectations
                    passed = True
                    for expected in scenario['expected']:
                        if expected.lower() not in message.lower():
                            print(f"  ❌ Missing expected: '{expected}'")
                            passed = False
                    
                    for not_expected in scenario['not_expected']:
                        if not_expected in message:
                            print(f"  ❌ Found unexpected: '{not_expected}'")
                            passed = False
                    
                    if passed:
                        print(f"  ✅ PASSED")
                    
                    # Show preview
                    preview = message[:200].replace('\n', ' ')
                    print(f"  Preview: {preview}...")
                    
                    results.append((scenario['name'], passed))
                else:
                    print(f"  ❌ Failed: {response.status_code}")
                    results.append((scenario['name'], False))
                
                time.sleep(2)
                
            except Exception as e:
                print(f"  ❌ Error: {e}")
                results.append((scenario['name'], False))
        
        # Summary
        print(f"\n{'=' * 70}")
        print("📊 TEST RESULTS SUMMARY")
        print(f"{'=' * 70}")
        
        passed = sum(1 for _, p in results if p)
        total = len(results)
        
        for name, p in results:
            print(f"  {'✅' if p else '❌'} {name}")
        
        print(f"\n  Total: {passed}/{total} passed")
        print(f"{'=' * 70}")

if __name__ == "__main__":
    main()

