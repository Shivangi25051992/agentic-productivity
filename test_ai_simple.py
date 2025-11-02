#!/usr/bin/env python3
"""
Simple AI Test - Direct Chat Endpoint Testing
Uses Firebase Admin SDK to create a custom token for testing
"""

import requests
import json
import time
from datetime import datetime
import sys
import os

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app.services.auth import create_custom_token_for_testing

BASE_URL = "http://localhost:8000"
TEST_EMAIL = "alice.test@aiproductivity.app"

def get_test_token() -> str:
    """Get a test token using Firebase Admin SDK"""
    print("🔐 Creating test token...")
    try:
        token = create_custom_token_for_testing(TEST_EMAIL)
        print("✅ Token created successfully")
        return token
    except Exception as e:
        print(f"❌ Failed to create token: {e}")
        sys.exit(1)

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
            print(f"\n⏱️  Response Time: {elapsed:.2f}s")
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
                            print(f"       ⚠️  ESTIMATED VALUES")
                    
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
    print("🚀 Starting AI Test Suite")
    print(f"⏰ Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    token = get_test_token()
    
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
    
    results = []
    for user_input, test_name in test_cases:
        success = test_chat(token, user_input, test_name)
        results.append({"test": test_name, "input": user_input, "success": success})
        time.sleep(2)  # Rate limiting to avoid overwhelming OpenAI
    
    # Summary
    print("\n" + "="*80)
    print("📊 TEST SUMMARY")
    print("="*80)
    
    total = len(results)
    successful = sum(1 for r in results if r['success'])
    
    print(f"\nTotal Tests: {total}")
    print(f"✅ Successful: {successful}")
    print(f"❌ Failed: {total - successful}")
    print(f"📈 Success Rate: {(successful/total*100):.1f}%")
    
    print("\n📋 Detailed Results:")
    for i, r in enumerate(results, 1):
        status = "✅" if r['success'] else "❌"
        print(f"{i:2d}. {status} {r['test']}")
    
    print("\n" + "="*80)
    print("🎉 Test Suite Complete!")
    print("="*80)

if __name__ == "__main__":
    main()


