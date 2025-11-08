"""Check the latest meal plan in Firestore"""
import os
from google.cloud import firestore
from dotenv import load_dotenv
from datetime import datetime

load_dotenv()
load_dotenv('.env.local', override=True)

# Initialize Firestore
db = firestore.Client(project=os.getenv("GOOGLE_CLOUD_PROJECT"))

user_id = "ACjSKgsfS0NkgSQYCvAEtnRvMO43"

print(f"🔍 Checking meal plans for user: {user_id}")
print("=" * 80)

# Query user's meal plans
plans_ref = db.collection('users').document(user_id).collection('meal_plans')
plans = plans_ref.order_by('created_at', direction=firestore.Query.DESCENDING).limit(3).stream()

plan_count = 0
for plan_doc in plans:
    plan_count += 1
    plan_data = plan_doc.to_dict()
    
    print(f"\n📋 Plan #{plan_count}: {plan_doc.id}")
    print(f"   Week: {plan_data.get('week_start_date')} to {plan_data.get('week_end_date')}")
    print(f"   Active: {plan_data.get('is_active', 'N/A')}")
    print(f"   Created: {plan_data.get('created_at', 'N/A')}")
    print(f"   Dietary Prefs: {plan_data.get('dietary_preferences', [])}")
    print(f"   Calorie Target: {plan_data.get('daily_calorie_target', 'N/A')}")
    print(f"   Protein Target: {plan_data.get('daily_protein_target', 'N/A')}")
    
    meals = plan_data.get('meals', [])
    print(f"   Total Meals: {len(meals)}")
    
    if meals:
        # Show first 3 meals
        print(f"\n   📝 Sample meals:")
        for i, meal in enumerate(meals[:3]):
            print(f"      {i+1}. {meal.get('day', 'N/A')} - {meal.get('meal_type', 'N/A')}: {meal.get('recipe_name', 'N/A')}")
            print(f"         Calories: {meal.get('calories', 0)} kcal, Protein: {meal.get('protein_g', 0)}g")
        
        # Calculate daily totals
        meals_by_day = {}
        for meal in meals:
            day = meal.get('day', 'unknown')
            if day not in meals_by_day:
                meals_by_day[day] = {'count': 0, 'calories': 0, 'protein': 0}
            meals_by_day[day]['count'] += 1
            meals_by_day[day]['calories'] += meal.get('calories', 0)
            meals_by_day[day]['protein'] += meal.get('protein_g', 0)
        
        print(f"\n   📊 Meals per day:")
        for day, stats in meals_by_day.items():
            print(f"      {day}: {stats['count']} meals, {stats['calories']} kcal, {stats['protein']:.1f}g protein")

if plan_count == 0:
    print("❌ No meal plans found!")
else:
    print(f"\n✅ Found {plan_count} meal plans")


