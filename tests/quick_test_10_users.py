#!/usr/bin/env python3
"""
Quick Test: 10 Users, 1 Day
Fast validation before running full 7-day simulation
"""

import sys
import os
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

import json
import requests
from datetime import datetime

API_BASE = "http://localhost:8000"

def load_test_users():
    """Load pre-created test users"""
    with open('tests/test_users.json', 'r') as f:
        return json.load(f)

def test_single_meal(user, meal_input):
    """Test a single meal log"""
    # Recreate full token (we truncated it in storage)
    from tests.firebase_test_helper import create_test_user_with_token
    user_data = create_test_user_with_token(
        user['email'],
        "TestPass123!",
        f"Test User {user['user_id']}"
    )
    
    headers = {"Authorization": f"Bearer {user_data['id_token']}"}
    
    try:
        response = requests.post(
            f"{API_BASE}/chat",
            json={"user_input": meal_input},
            headers=headers,
            timeout=10
        )
        
        if response.status_code == 200:
            result = response.json()
            items = result.get('items', [])
            if items and items[0].get('category') == 'meal':
                calories = items[0].get('data', {}).get('calories', 0)
                return {'success': True, 'calories': calories, 'message': result.get('message')}
        
        return {'success': False, 'error': f"HTTP {response.status_code}"}
    
    except Exception as e:
        return {'success': False, 'error': str(e)}

def main():
    print(f"\n{'='*80}")
    print(f"🧪 QUICK TEST: 10 Users, 1 Day")
    print(f"{'='*80}\n")
    
    users = load_test_users()
    print(f"✅ Loaded {len(users)} users\n")
    
    # Test meals for each goal type
    test_meals = {
        'lose_weight': '2 eggs',
        'gain_muscle': 'chicken breast with rice',
        'maintain': 'oatmeal',
        'improve_fitness': 'protein shake'
    }
    
    results = []
    
    for i, user in enumerate(users, 1):
        goal = user['goal']
        meal = test_meals.get(goal, '2 eggs')
        
        print(f"👤 User {i}/10: {user['email']} ({goal})")
        print(f"   Testing: '{meal}'...")
        
        result = test_single_meal(user, meal)
        
        if result['success']:
            print(f"   ✅ SUCCESS: {result['calories']} cal logged")
            print(f"   💬 {result['message'][:60]}...")
        else:
            print(f"   ❌ FAILED: {result['error']}")
        
        results.append({
            'user_id': user['user_id'],
            'goal': goal,
            'meal': meal,
            'result': result
        })
        print()
    
    # Summary
    successful = sum(1 for r in results if r['result']['success'])
    failed = len(results) - successful
    
    print(f"{'='*80}")
    print(f"📊 QUICK TEST RESULTS")
    print(f"{'='*80}")
    print(f"✅ Successful: {successful}/10")
    print(f"❌ Failed: {failed}/10")
    print(f"📈 Success Rate: {successful/10*100:.0f}%")
    
    if successful > 0:
        total_calories = sum(r['result'].get('calories', 0) for r in results if r['result']['success'])
        print(f"🔥 Total Calories Logged: {total_calories} kcal")
    
    print(f"{'='*80}\n")
    
    # Save results
    with open('tests/quick_test_results.json', 'w') as f:
        json.dump(results, f, indent=2)
    
    print(f"💾 Results saved to: tests/quick_test_results.json\n")
    
    return successful == 10

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)


