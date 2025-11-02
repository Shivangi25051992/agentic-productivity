#!/usr/bin/env python3
"""
Comprehensive AI Test Suite
Tests OpenAI integration with various inputs including:
- Food logging (correct and wrong English)
- Workouts
- Tasks
- Drinks
- Supplements/Multivitamins
- Multi-item entries
"""

import requests
import json
import time
from datetime import datetime
from typing import Dict, Any

BASE_URL = "http://localhost:8000"

# Test user credentials
TEST_EMAIL = "alice.test@aiproductivity.app"
TEST_PASSWORD = "TestPass123!"

def login() -> str:
    """Login and get auth token"""
    print("\n🔐 Logging in...")
    response = requests.post(
        f"{BASE_URL}/login",
        json={"email": TEST_EMAIL, "password": TEST_PASSWORD}
    )
    if response.status_code == 200:
        token = response.json()["id_token"]
        print(f"✅ Login successful")
        return token
    else:
        print(f"❌ Login failed: {response.status_code}")
        print(response.text)
        exit(1)

def test_chat(token: str, user_input: str, test_name: str) -> Dict[str, Any]:
    """Send a chat message and return the response"""
    print(f"\n{'='*80}")
    print(f"🧪 TEST: {test_name}")
    print(f"📝 USER INPUT: \"{user_input}\"")
    print(f"{'='*80}")
    
    start_time = time.time()
    
    response = requests.post(
        f"{BASE_URL}/chat",
        json={"user_input": user_input},
        headers={"Authorization": f"Bearer {token}"}
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
                    print(f"       Due: {item_data.get('due_date', 'N/A')}")
        
        print(f"\n{'='*80}")
        return data
    else:
        print(f"\n❌ ERROR: {response.status_code}")
        print(response.text)
        print(f"{'='*80}")
        return {}

def main():
    print("🚀 Starting Comprehensive AI Test Suite")
    print(f"⏰ Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    token = login()
    
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
        ("drinked 1 glass milk", "Food - Wrong English (Grammar: drinked)"),
        
        # Multi-food entries
        ("2 egg omlet + 1 bowl rice + beans curry 100gm + 1.5 litre water", "Multi-Food - Mixed English"),
        ("breakfast: 2 eggs, 1 toast, 1 coffe", "Multi-Food - Wrong English (coffe)"),
        
        # Drinks
        ("1 glass of water", "Drink - Water"),
        ("2 cups of coffe", "Drink - Wrong English (coffe)"),
        ("1 bottle of coke", "Drink - Soda"),
        
        # Supplements/Multivitamins
        ("1 multivitamin tablet", "Supplement - Multivitamin"),
        ("1 omega 3 capsule", "Supplement - Omega 3"),
        ("took 1 vitamin c and 1 probiotic", "Supplement - Multiple"),
        ("1 protien shake", "Supplement - Wrong English (protien)"),
        
        # Workouts
        ("ran 5 km", "Workout - Running"),
        ("30 minutes of yoga", "Workout - Yoga"),
        ("runing for 20 minuts", "Workout - Wrong English (runing, minuts)"),
        ("did workout at gym for 1 hour", "Workout - Generic"),
        ("walked 10000 steps", "Workout - Steps"),
        
        # Tasks
        ("remind me to call doctor tomorrow", "Task - Reminder"),
        ("add task: finish report by friday", "Task - Work"),
        ("todo: buy grocerys", "Task - Wrong English (grocerys)"),
        
        # Edge cases
        ("chocolate bar", "Edge Case - Ambiguous food (should ask for details)"),
        ("had lunch", "Edge Case - Very vague"),
        ("ate something", "Edge Case - No specifics"),
        ("v", "Edge Case - Single character (should reject)"),
        ("", "Edge Case - Empty (should reject)"),
    ]
    
    results = []
    for user_input, test_name in test_cases:
        try:
            result = test_chat(token, user_input, test_name)
            results.append({
                "test": test_name,
                "input": user_input,
                "success": bool(result),
                "needs_clarification": result.get('needs_clarification', False),
                "items_count": len(result.get('items', []))
            })
            time.sleep(1)  # Rate limiting
        except Exception as e:
            print(f"\n❌ Exception: {e}")
            results.append({
                "test": test_name,
                "input": user_input,
                "success": False,
                "error": str(e)
            })
    
    # Summary
    print("\n" + "="*80)
    print("📊 TEST SUMMARY")
    print("="*80)
    
    total = len(results)
    successful = sum(1 for r in results if r.get('success'))
    needs_clarification = sum(1 for r in results if r.get('needs_clarification'))
    
    print(f"\nTotal Tests: {total}")
    print(f"✅ Successful: {successful}")
    print(f"❓ Needs Clarification: {needs_clarification}")
    print(f"❌ Failed: {total - successful}")
    
    print("\n📋 Detailed Results:")
    for i, r in enumerate(results, 1):
        status = "✅" if r.get('success') else "❌"
        clarify = " (needs clarification)" if r.get('needs_clarification') else ""
        items = f" [{r.get('items_count', 0)} items]" if r.get('items_count', 0) > 0 else ""
        print(f"{i:2d}. {status} {r['test']}{clarify}{items}")
        if r.get('error'):
            print(f"    Error: {r['error']}")
    
    print("\n" + "="*80)
    print("🎉 Test Suite Complete!")
    print("="*80)

if __name__ == "__main__":
    main()


