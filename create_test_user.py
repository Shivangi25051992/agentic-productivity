#!/usr/bin/env python3
"""
Create test user with realistic data for manual testing
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from datetime import datetime, timedelta
from app.services.database import get_firestore_client
import json

def create_test_user():
    """Create test user with profile and sample data"""
    db = get_firestore_client()
    
    # Test user credentials
    email = "testuser@example.com"
    user_id = "test_user_123"  # Firebase will create this on first login
    
    print("\n" + "="*70)
    print("  CREATING TEST USER WITH DATA")
    print("="*70)
    
    # User profile
    profile = {
        "email": email,
        "name": "Test User",
        "age": 30,
        "gender": "male",
        "height_cm": 175,
        "weight_kg": 75,
        "target_weight_kg": 70,
        "activity_level": "moderately_active",
        "fitness_goal": "lose_weight",
        "daily_goals": {
            "calories": 2000,
            "protein_g": 150,
            "carbs_g": 200,
            "fat_g": 67
        },
        "preferences": {
            "dietary_restrictions": ["none"],
            "favorite_cuisines": ["Indian", "Continental"],
            "meal_reminders": True
        },
        "created_at": datetime.now().isoformat(),
        "profile_complete": True
    }
    
    print(f"\n✅ User Profile:")
    print(f"   Email: {email}")
    print(f"   Password: Test1234!")
    print(f"   Name: {profile['name']}")
    print(f"   Goal: Lose weight (75kg → 70kg)")
    print(f"   Daily Target: {profile['daily_goals']['calories']} cal")
    
    # Save profile (will be created when user signs up)
    # For now, just print the data
    
    # Sample meal logs for the past 3 days
    print(f"\n✅ Sample Meal Logs (Past 3 Days):")
    
    meals_data = []
    
    # Day 1 (2 days ago)
    day1 = datetime.now() - timedelta(days=2)
    meals_data.extend([
        {
            "user_id": user_id,
            "date": day1.strftime("%Y-%m-%d"),
            "meal_type": "breakfast",
            "food": "2 boiled eggs and 2 toast",
            "calories": 320,
            "protein_g": 20,
            "carbs_g": 30,
            "fat_g": 12,
            "logged_at": day1.replace(hour=8, minute=30).isoformat()
        },
        {
            "user_id": user_id,
            "date": day1.strftime("%Y-%m-%d"),
            "meal_type": "lunch",
            "food": "2 rotis with dal and rice",
            "calories": 550,
            "protein_g": 18,
            "carbs_g": 95,
            "fat_g": 8,
            "logged_at": day1.replace(hour=13, minute=0).isoformat()
        },
        {
            "user_id": user_id,
            "date": day1.strftime("%Y-%m-%d"),
            "meal_type": "snack",
            "food": "1 banana and 10 almonds",
            "calories": 175,
            "protein_g": 4,
            "carbs_g": 30,
            "fat_g": 7,
            "logged_at": day1.replace(hour=16, minute=30).isoformat()
        },
        {
            "user_id": user_id,
            "date": day1.strftime("%Y-%m-%d"),
            "meal_type": "dinner",
            "food": "Grilled chicken with vegetables",
            "calories": 450,
            "protein_g": 45,
            "carbs_g": 25,
            "fat_g": 15,
            "logged_at": day1.replace(hour=20, minute=0).isoformat()
        }
    ])
    
    # Day 2 (yesterday)
    day2 = datetime.now() - timedelta(days=1)
    meals_data.extend([
        {
            "user_id": user_id,
            "date": day2.strftime("%Y-%m-%d"),
            "meal_type": "breakfast",
            "food": "1 bowl poha with peanuts",
            "calories": 280,
            "protein_g": 8,
            "carbs_g": 45,
            "fat_g": 7,
            "logged_at": day2.replace(hour=8, minute=0).isoformat()
        },
        {
            "user_id": user_id,
            "date": day2.strftime("%Y-%m-%d"),
            "meal_type": "lunch",
            "food": "Chicken biryani with raita",
            "calories": 650,
            "protein_g": 35,
            "carbs_g": 75,
            "fat_g": 20,
            "logged_at": day2.replace(hour=13, minute=30).isoformat()
        },
        {
            "user_id": user_id,
            "date": day2.strftime("%Y-%m-%d"),
            "meal_type": "snack",
            "food": "1 cup chai with 2 biscuits",
            "calories": 120,
            "protein_g": 2,
            "carbs_g": 20,
            "fat_g": 3,
            "logged_at": day2.replace(hour=17, minute=0).isoformat()
        },
        {
            "user_id": user_id,
            "date": day2.strftime("%Y-%m-%d"),
            "meal_type": "dinner",
            "food": "Dal khichdi with curd",
            "calories": 420,
            "protein_g": 15,
            "carbs_g": 65,
            "fat_g": 10,
            "logged_at": day2.replace(hour=20, minute=30).isoformat()
        }
    ])
    
    # Day 3 (today - morning only)
    day3 = datetime.now()
    meals_data.extend([
        {
            "user_id": user_id,
            "date": day3.strftime("%Y-%m-%d"),
            "meal_type": "breakfast",
            "food": "2 parathas with curd",
            "calories": 450,
            "protein_g": 12,
            "carbs_g": 60,
            "fat_g": 18,
            "logged_at": day3.replace(hour=8, minute=30).isoformat()
        }
    ])
    
    for i, meal in enumerate(meals_data, 1):
        print(f"   {i}. {meal['meal_type'].upper()}: {meal['food']} ({meal['calories']} cal)")
    
    # Calculate totals
    total_calories = sum(m['calories'] for m in meals_data)
    total_protein = sum(m['protein_g'] for m in meals_data)
    
    print(f"\n📊 Total Logged:")
    print(f"   Calories: {total_calories} kcal")
    print(f"   Protein: {total_protein}g")
    print(f"   Meals: {len(meals_data)}")
    
    # Save to JSON for reference
    test_data = {
        "user": {
            "email": email,
            "password": "Test1234!",
            "user_id": user_id,
            "profile": profile
        },
        "meals": meals_data
    }
    
    with open("test_user_data.json", "w") as f:
        json.dump(test_data, f, indent=2)
    
    print(f"\n✅ Test data saved to: test_user_data.json")
    
    print("\n" + "="*70)
    print("  TEST INSTRUCTIONS")
    print("="*70)
    print("\n1. Go to: http://localhost:8080")
    print("\n2. Click 'Sign Up' and create account:")
    print(f"   Email: {email}")
    print("   Password: Test1234!")
    print("\n3. Complete onboarding with these details:")
    print("   - Age: 30")
    print("   - Gender: Male")
    print("   - Height: 175 cm (5'9\")")
    print("   - Weight: 75 kg (165 lb)")
    print("   - Goal: Lose Weight")
    print("   - Activity: Moderately Active")
    print("\n4. Test the Chat Assistant with:")
    print("   ✨ SIMPLE: '2 boiled eggs'")
    print("   ✨ COMPLEX: 'i ate 2 eggs in the morning, 1 bowl of rice and curd for lunch, 5 pistachios afternoon, 200g spinach dinner'")
    print("   ✨ INDIAN: '2 rotis with dal'")
    print("   ✨ MULTI-MEAL: 'breakfast: 2 eggs, lunch: chicken biryani, dinner: dal khichdi'")
    print("\n5. Check Dashboard:")
    print("   - Verify calories update correctly")
    print("   - Check meal breakdown by type")
    print("   - Verify macros are accurate")
    print("\n" + "="*70)
    print("  🎉 READY FOR TESTING!")
    print("="*70 + "\n")

if __name__ == "__main__":
    create_test_user()

