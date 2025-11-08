"""
Check Meal Plans in Firestore
==============================
Quick script to see what meal plans exist for a user
"""

import os
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from dotenv import load_dotenv
load_dotenv()
load_dotenv('.env.local', override=True)

from google.cloud import firestore

def check_meal_plans():
    project = os.getenv("GOOGLE_CLOUD_PROJECT")
    db = firestore.Client(project=project)
    
    # Your user ID
    user_id = "ACjSKgsfS0NkgSQYCvAEtnRvMO43"
    
    print("=" * 70)
    print(f"Checking meal plans for user: {user_id}")
    print("=" * 70)
    
    # Get all meal plans for this user
    plans = db.collection('meal_plans').where('user_id', '==', user_id).stream()
    
    plan_list = []
    for plan in plans:
        plan_data = plan.to_dict()
        plan_list.append({
            'id': plan.id,
            'data': plan_data
        })
    
    if not plan_list:
        print("\n❌ No meal plans found for this user!")
        return
    
    print(f"\n✅ Found {len(plan_list)} meal plan(s):\n")
    
    for i, plan in enumerate(plan_list, 1):
        print(f"Plan {i}:")
        print(f"  ID: {plan['id']}")
        print(f"  Week Start: {plan['data'].get('week_start_date', 'N/A')}")
        print(f"  Week End: {plan['data'].get('week_end_date', 'N/A')}")
        print(f"  Active: {plan['data'].get('is_active', 'N/A')}")
        print(f"  Dietary Prefs: {plan['data'].get('dietary_preferences', [])}")
        print(f"  Created By AI: {plan['data'].get('created_by_ai', 'N/A')}")
        print(f"  Meals Count: {len(plan['data'].get('meals', []))}")
        
        # Show first 3 meals
        meals = plan['data'].get('meals', [])
        if meals:
            print(f"  First 3 meals:")
            for j, meal in enumerate(meals[:3], 1):
                meal_name = meal.get('recipe_name', 'Unknown')
                meal_type = meal.get('meal_type', 'Unknown')
                print(f"    {j}. {meal_type}: {meal_name}")
        
        print()
    
    # Check for the specific ID mentioned
    specific_id = "c4a3b782-dfe3-4c91-87de-1a09c62ccce1"
    print(f"Checking for specific plan ID: {specific_id}")
    
    found = any(plan['id'] == specific_id for plan in plan_list)
    if found:
        print(f"  ✅ Found!")
    else:
        print(f"  ❌ NOT found in database")
    
    print("\n" + "=" * 70)

if __name__ == "__main__":
    check_meal_plans()


