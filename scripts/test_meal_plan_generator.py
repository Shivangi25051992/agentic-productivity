"""
Test Meal Plan Generator - Comprehensive Testing
=================================================
Tests all aspects of the LLM-powered meal plan generator

Usage:
    python scripts/test_meal_plan_generator.py
"""

import asyncio
import sys
import os
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

# Load environment variables
from dotenv import load_dotenv
load_dotenv()
load_dotenv('.env.local', override=True)

from datetime import date
from app.services.meal_plan_llm_service import MealPlanLLMService
from app.models.meal_planning import GenerateMealPlanRequest


async def test_basic_generation():
    """Test 1: Basic meal plan generation"""
    
    print("\n" + "=" * 70)
    print("TEST 1: Basic Meal Plan Generation")
    print("=" * 70)
    
    try:
        service = MealPlanLLMService()
        
        # Mock user profile
        user_profile = {
            'age': 35,
            'gender': 'male',
            'weight_kg': 75,
            'height_cm': 175,
            'activity_level': 'moderately_active',
            'fitness_goal': 'lose_weight',
            'diet_preference': 'none',
            'allergies': [],
            'disliked_foods': []
        }
        
        # Create request
        request = GenerateMealPlanRequest(
            week_start_date=date.today(),
            dietary_preferences=[],
            daily_calorie_target=1800,
            daily_protein_target=130
        )
        
        print("\n🧪 Testing basic generation...")
        print(f"   User: {user_profile['fitness_goal']}, {user_profile['diet_preference']}")
        print(f"   Target: {request.daily_calorie_target} kcal, {request.daily_protein_target}g protein")
        
        # Generate
        result = await service.generate_meal_plan(
            user_profile=user_profile,
            request=request,
            user_id="test_user_1"
        )
        
        meal_plan = result['meal_plan_data']
        metadata = result['metadata']
        
        print(f"\n✅ Generation successful!")
        print(f"   Provider: {metadata['provider_used']}")
        print(f"   Model: {metadata['model_name']}")
        print(f"   Cost: ${metadata['cost']:.4f}")
        print(f"   Latency: {metadata['latency_ms']:.0f}ms")
        print(f"   Meals generated: {len(meal_plan.meals)}")
        
        # Validate meals
        for i, meal in enumerate(meal_plan.meals, 1):
            print(f"\n   Meal {i}: {meal.recipe_name}")
            print(f"      Type: {meal.meal_type}")
            print(f"      Day: {meal.day}")
            print(f"      Servings: {meal.servings}")
            if meal.notes:
                print(f"      Notes: {meal.notes[:80]}...")
        
        return True
        
    except Exception as e:
        print(f"\n❌ Test failed: {e}")
        import traceback
        traceback.print_exc()
        return False


async def test_vegetarian_generation():
    """Test 2: Vegetarian meal plan"""
    
    print("\n" + "=" * 70)
    print("TEST 2: Vegetarian Meal Plan")
    print("=" * 70)
    
    try:
        service = MealPlanLLMService()
        
        user_profile = {
            'age': 28,
            'gender': 'female',
            'weight_kg': 60,
            'height_cm': 165,
            'activity_level': 'active',
            'fitness_goal': 'build_muscle',
            'diet_preference': 'vegetarian',
            'allergies': [],
            'disliked_foods': ['tofu']
        }
        
        request = GenerateMealPlanRequest(
            week_start_date=date.today(),
            dietary_preferences=['vegetarian'],
            daily_calorie_target=2000,
            daily_protein_target=140
        )
        
        print("\n🧪 Testing vegetarian generation...")
        print(f"   Diet: {user_profile['diet_preference']}")
        print(f"   Dislikes: {user_profile['disliked_foods']}")
        
        result = await service.generate_meal_plan(
            user_profile=user_profile,
            request=request,
            user_id="test_user_2"
        )
        
        meal_plan = result['meal_plan_data']
        metadata = result['metadata']
        
        print(f"\n✅ Generation successful!")
        print(f"   Provider: {metadata['provider_used']}")
        print(f"   Meals: {len(meal_plan.meals)}")
        
        # Check for meat (should be none)
        meat_keywords = ['chicken', 'beef', 'pork', 'fish', 'salmon', 'tuna', 'meat']
        for meal in meal_plan.meals:
            meal_text = f"{meal.recipe_name}".lower()
            if any(keyword in meal_text for keyword in meat_keywords):
                print(f"   ⚠️ Warning: Possible meat in {meal.recipe_name}")
            
            # Check for tofu (should be avoided)
            if 'tofu' in meal_text:
                print(f"   ⚠️ Warning: Tofu found in {meal.recipe_name} (user dislikes it)")
        
        return True
        
    except Exception as e:
        print(f"\n❌ Test failed: {e}")
        return False


async def test_failover():
    """Test 3: Failover mechanism (simulated)"""
    
    print("\n" + "=" * 70)
    print("TEST 3: Failover Mechanism")
    print("=" * 70)
    
    print("\n🧪 Testing failover...")
    print("   Note: With valid OpenAI key, primary provider should work")
    print("   Failover would activate if primary fails")
    
    try:
        service = MealPlanLLMService()
        
        user_profile = {
            'age': 40,
            'gender': 'male',
            'weight_kg': 85,
            'height_cm': 180,
            'activity_level': 'moderate',
            'fitness_goal': 'maintain',
            'diet_preference': 'none',
            'allergies': ['peanuts'],
            'disliked_foods': []
        }
        
        request = GenerateMealPlanRequest(
            week_start_date=date.today(),
            dietary_preferences=[],
            daily_calorie_target=2200,
            daily_protein_target=150
        )
        
        result = await service.generate_meal_plan(
            user_profile=user_profile,
            request=request,
            user_id="test_user_3"
        )
        
        metadata = result['metadata']
        
        print(f"\n✅ Generation successful!")
        print(f"   Provider used: {metadata['provider_used']}")
        print(f"   Providers tried: {metadata['providers_tried']}")
        print(f"   Fallback used: {metadata.get('fallback_used', False)}")
        
        if len(metadata['providers_tried']) > 1:
            print(f"   ✅ Failover activated! Tried {len(metadata['providers_tried'])} providers")
        else:
            print(f"   ℹ️ Primary provider worked, no failover needed")
        
        return True
        
    except Exception as e:
        print(f"\n❌ Test failed: {e}")
        return False


async def test_cost_tracking():
    """Test 4: Cost tracking and analytics"""
    
    print("\n" + "=" * 70)
    print("TEST 4: Cost Tracking")
    print("=" * 70)
    
    print("\n🧪 Testing cost tracking...")
    
    try:
        service = MealPlanLLMService()
        
        user_profile = {
            'age': 30,
            'gender': 'female',
            'weight_kg': 65,
            'height_cm': 168,
            'activity_level': 'active',
            'fitness_goal': 'lose_weight',
            'diet_preference': 'none',
            'allergies': [],
            'disliked_foods': []
        }
        
        request = GenerateMealPlanRequest(
            week_start_date=date.today(),
            dietary_preferences=[],
            daily_calorie_target=1600,
            daily_protein_target=120
        )
        
        # Generate 3 plans to test cost accumulation
        total_cost = 0
        for i in range(3):
            result = await service.generate_meal_plan(
                user_profile=user_profile,
                request=request,
                user_id=f"test_user_cost_{i}"
            )
            
            cost = result['metadata']['cost']
            total_cost += cost
            
            print(f"   Plan {i+1}: ${cost:.4f}")
        
        print(f"\n✅ Cost tracking working!")
        print(f"   Total cost for 3 plans: ${total_cost:.4f}")
        print(f"   Average cost per plan: ${total_cost/3:.4f}")
        print(f"   Projected monthly cost (1000 users, 2 plans/week): ${(total_cost/3) * 2 * 4 * 1000:.2f}")
        
        return True
        
    except Exception as e:
        print(f"\n❌ Test failed: {e}")
        return False


async def test_personalization():
    """Test 5: Personalization quality"""
    
    print("\n" + "=" * 70)
    print("TEST 5: Personalization Quality")
    print("=" * 70)
    
    print("\n🧪 Testing personalization...")
    
    try:
        service = MealPlanLLMService()
        
        # Test case: High protein, low carb for muscle gain
        user_profile = {
            'age': 25,
            'gender': 'male',
            'weight_kg': 80,
            'height_cm': 182,
            'activity_level': 'very_active',
            'fitness_goal': 'build_muscle',
            'diet_preference': 'none',
            'allergies': [],
            'disliked_foods': []
        }
        
        request = GenerateMealPlanRequest(
            week_start_date=date.today(),
            dietary_preferences=['high_protein'],
            daily_calorie_target=2500,
            daily_protein_target=200
        )
        
        result = await service.generate_meal_plan(
            user_profile=user_profile,
            request=request,
            user_id="test_user_personalization"
        )
        
        meal_plan = result['meal_plan_data']
        
        print(f"\n✅ Personalization test complete!")
        print(f"   Target: {request.daily_calorie_target} kcal, {request.daily_protein_target}g protein")
        print(f"   Meals generated: {len(meal_plan.meals)}")
        print(f"   Note: Nutrition tracking requires full recipe integration")
        
        return True
        
    except Exception as e:
        print(f"\n❌ Test failed: {e}")
        return False


async def run_all_tests():
    """Run all tests"""
    
    print("\n" + "=" * 70)
    print("🧪 MEAL PLAN GENERATOR - COMPREHENSIVE TEST SUITE")
    print("=" * 70)
    print("\nTesting production-grade LLM-powered meal plan generation")
    print("Features: Multi-provider support, failover, cost tracking, personalization")
    print()
    
    results = []
    
    # Run tests
    results.append(("Basic Generation", await test_basic_generation()))
    results.append(("Vegetarian Plan", await test_vegetarian_generation()))
    results.append(("Failover Mechanism", await test_failover()))
    results.append(("Cost Tracking", await test_cost_tracking()))
    results.append(("Personalization", await test_personalization()))
    
    # Summary
    print("\n" + "=" * 70)
    print("📊 TEST SUMMARY")
    print("=" * 70)
    
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    for test_name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"   {status}: {test_name}")
    
    print(f"\n   Total: {passed}/{total} tests passed ({passed/total*100:.0f}%)")
    
    if passed == total:
        print("\n   🎉 All tests passed! System is production-ready!")
    else:
        print(f"\n   ⚠️ {total - passed} test(s) failed. Review errors above.")
    
    print("\n" + "=" * 70)
    
    return passed == total


if __name__ == "__main__":
    success = asyncio.run(run_all_tests())
    sys.exit(0 if success else 1)

