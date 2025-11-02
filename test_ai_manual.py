#!/usr/bin/env python3
"""
Manual AI Test - Requires manual token input
Run this after logging in via the frontend and copying the token from browser dev tools
Or provide a valid Firebase ID token
"""

import requests
import json
import time
from datetime import datetime
import sys

BASE_URL = "http://localhost:8000"

# INSTRUCTIONS:
# 1. Login via the Flutter app
# 2. Open browser dev tools -> Application -> Local Storage
# 3. Find the Firebase auth token
# 4. Paste it below or pass as command line argument

def test_chat(token: str, user_input: str, test_name: str):
    """Send a chat message and print the response"""
    print(f"\n{'='*80}")
    print(f"🧪 TEST: {test_name}")
    print(f"📝 USER INPUT: \"{user_input}\"")
    print(f"{'='*80}")
    
    start_time = time.time()
    
    try:
        response = requests.post(
            f"{BASE_URL}/chat",
            json={"user_input": user_input},
            headers={"Authorization": f"Bearer {token}"},
            timeout=30
        )
        
        elapsed = time.time() - start_time
        
        if response.status_code == 200:
            data = response.json()
            print(f"\n⏱️  Response Time: {elapsed:.2f}s {'⚠️ SLOW' if elapsed > 3 else '✅ FAST'}")
            print(f"\n🤖 AI RESPONSE:")
            print(f"   Message: {data.get('message', 'N/A')}")
            
            if data.get('needs_clarification'):
                print(f"\n❓ NEEDS CLARIFICATION: {data.get('clarification_question', 'N/A')}")
            
            items = data.get('items', [])
            if items:
                print(f"\n📊 PARSED ITEMS ({len(items)}):")
                for i, item in enumerate(items, 1):
                    category = item.get('category', 'unknown')
                    summary = item.get('summary', 'N/A')
                    item_data = item.get('data', {})
                    
                    print(f"\n   [{i}] Category: {category.upper()}")
                    print(f"       Summary: {summary}")
                    
                    if category == 'meal':
                        print(f"       Food: {item_data.get('meal', 'N/A')}")
                        print(f"       Description: {item_data.get('description', 'N/A')}")
                        print(f"       Meal Type: {item_data.get('meal_type', 'N/A')}")
                        print(f"       Quantity: {item_data.get('quantity', 'N/A')}")
                        print(f"       Calories: {item_data.get('calories', 0)} kcal")
                        print(f"       Protein: {item_data.get('protein_g', 0):.1f}g")
                        print(f"       Carbs: {item_data.get('carbs_g', 0):.1f}g")
                        print(f"       Fat: {item_data.get('fat_g', 0):.1f}g")
                        print(f"       Fiber: {item_data.get('fiber_g', 0):.1f}g")
                        if item_data.get('estimated'):
                            print(f"       ⚠️  ESTIMATED VALUES (not from database)")
                        else:
                            print(f"       ✅ FROM DATABASE")
                    
                    elif category == 'workout':
                        print(f"       Exercise: {item_data.get('exercise', 'N/A')}")
                        print(f"       Duration: {item_data.get('duration_minutes', 'N/A')} min")
                        print(f"       Calories Burned: {item_data.get('calories_burned', 0)} kcal")
                        print(f"       Intensity: {item_data.get('intensity', 'N/A')}")
                    
                    elif category == 'task':
                        print(f"       Task: {item_data.get('task', 'N/A')}")
                        print(f"       Priority: {item_data.get('priority', 'N/A')}")
            
            print(f"\n{'='*80}")
            return True
        else:
            print(f"\n❌ ERROR: {response.status_code}")
            print(response.text)
            print(f"{'='*80}")
            return False
    except Exception as e:
        print(f"\n❌ EXCEPTION: {e}")
        print(f"{'='*80}")
        return False

def main():
    print("🚀 AI Test Suite - Testing OpenAI Integration")
    print(f"⏰ Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("\n" + "="*80)
    
    # For testing without auth, we'll use a mock approach
    # In production, you'd get this from Firebase
    print("⚠️  This test requires a valid Firebase ID token")
    print("For now, we'll test the endpoint directly with test scenarios")
    print("="*80)
    
    # Test token - this will fail auth but we can see the response format
    # In real usage, get this from Firebase Auth
    token = "test-token-for-format-check"
    
    # Test cases with various inputs including wrong English
    test_cases = [
        # Food - Correct English
        ("2 eggs for breakfast", "Food - Correct English (Simple)"),
        ("1 bowl of oatmeal with honey", "Food - Correct English (Complex)"),
        
        # Food - Wrong English (typos, grammar errors)
        ("2 egg omlet", "Food - Wrong English (Typo: omlet)"),
        ("i ate 1 banan", "Food - Wrong English (Typo: banan)"),
        ("had some rice and dal", "Food - Wrong English (Informal)"),
        ("eated 2 roti with curry", "Food - Wrong English (Grammar: eated)"),
        
        # Multi-food entries
        ("2 egg omlet + 1 bowl rice + beans curry 100gm + 1.5 litre water", "Multi-Food - Mixed English"),
        
        # Drinks
        ("1 glass of water", "Drink - Water"),
        ("2 cups of coffe", "Drink - Wrong English (coffe)"),
        
        # Supplements/Multivitamins
        ("1 multivitamin tablet", "Supplement - Multivitamin"),
        ("1 omega 3 capsule", "Supplement - Omega 3"),
        ("1 protien shake", "Supplement - Wrong English (protien)"),
        
        # Workouts
        ("ran 5 km", "Workout - Running"),
        ("runing for 20 minuts", "Workout - Wrong English (runing, minuts)"),
        ("walked 10000 steps", "Workout - Steps"),
        
        # Tasks
        ("remind me to call doctor tomorrow", "Task - Reminder"),
        ("todo: buy grocerys", "Task - Wrong English (grocerys)"),
        
        # Edge cases
        ("chocolate bar", "Edge Case - Ambiguous food (should ask for details)"),
        ("v", "Edge Case - Single character (should reject)"),
    ]
    
    print("\n⚠️  NOTE: These tests will fail auth without a valid token")
    print("To run with auth, update the 'token' variable with a valid Firebase ID token\n")
    
    results = []
    for user_input, test_name in test_cases[:3]:  # Just test first 3 for format
        success = test_chat(token, user_input, test_name)
        results.append({"test": test_name, "input": user_input, "success": success})
        if not success:
            print("\n⚠️  Stopping tests - authentication required")
            print("To get a valid token:")
            print("1. Login via the Flutter app (http://localhost:3000)")
            print("2. Open browser dev tools -> Application -> Local Storage")
            print("3. Copy the Firebase auth token")
            print("4. Update this script with the token")
            break
        time.sleep(2)
    
    print("\n" + "="*80)
    print("📊 MANUAL TESTING RECOMMENDED")
    print("="*80)
    print("\nFor comprehensive testing:")
    print("1. Open the app: http://localhost:3000")
    print("2. Login with: alice.test@aiproductivity.app / TestPass123!")
    print("3. Go to Chat Assistant")
    print("4. Test these inputs manually:")
    print("\nTest Inputs:")
    for i, (inp, name) in enumerate(test_cases, 1):
        print(f"  {i:2d}. {inp:50s} // {name}")
    
    print("\n" + "="*80)

if __name__ == "__main__":
    main()


