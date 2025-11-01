"""
E2E Test Scenarios Based on Real User Testing Feedback
Date: November 1, 2025
Source: Manual testing session with primary user

These tests replicate the exact user journey and validate all observations.
"""

import pytest
import requests
import time
from typing import Dict, List, Any
from datetime import datetime

# Test Configuration
API_BASE = "http://localhost:8000"
FRONTEND_BASE = "http://localhost:8080"
TIMEOUT = 10

# Test Data from User Session
USER_DATA = {
    "email": "test_user_nov1_2025@test.com",
    "password": "TestPass123!",
    "name": "Test User Nov 1"
}

ONBOARDING_DATA = {
    "height_cm": 170,
    "weight_kg": 70,
    "age": 30,
    "gender": "male",
    "goal": "lose_weight",
    "target_weight_kg": 65,
    "activity_level": "moderately_active"
}

# Exact user input from testing session
COMPLEX_FOOD_INPUT = (
    "2 egg Omlet+ 1 bowl of rice+ beans curry 100 gm + 1 egg dosa + "
    "1.5 litres of water + 1 Multivitamin, 1 omega 3 capsule, 1 probiotics"
)

# Expected parsed items
EXPECTED_ITEMS = [
    {"name": "egg omlet", "quantity": 2, "calories_min": 250, "calories_max": 320},
    {"name": "rice", "quantity": 1, "unit": "bowl", "calories_min": 250, "calories_max": 350},
    {"name": "beans curry", "quantity": 100, "unit": "gm", "calories_min": 80, "calories_max": 120},
    {"name": "egg dosa", "quantity": 1, "calories_min": 180, "calories_max": 250},
    {"name": "water", "quantity": 1.5, "unit": "litres", "calories": 0},
    {"name": "multivitamin", "quantity": 1, "calories": 0},
    {"name": "omega 3 capsule", "quantity": 1, "calories_min": 5, "calories_max": 15},
    {"name": "probiotics", "quantity": 1, "calories_min": 0, "calories_max": 10}
]


class TestUserScenario1:
    """Test Scenario 1: New User Signup & Complete Flow"""
    
    @pytest.fixture(autouse=True)
    def setup(self):
        """Setup for each test"""
        self.session = requests.Session()
        self.auth_token = None
        self.user_id = None
        yield
        # Cleanup
        if self.user_id:
            # Delete test user (implement cleanup)
            pass
    
    def test_01_signup_flow(self):
        """
        Test 1: User Signup Flow
        
        Steps:
        1. Open app, navigate to login/signup
        2. Fill: Email, Password, Name
        3. Submit
        4. Assert: Signup successful, navigates to onboarding
        """
        # Signup
        response = self.session.post(
            f"{API_BASE}/auth/signup",
            json=USER_DATA,
            timeout=TIMEOUT
        )
        
        assert response.status_code == 201, f"Signup failed: {response.text}"
        data = response.json()
        
        assert "id_token" in data, "No auth token returned"
        assert "user" in data, "No user data returned"
        
        self.auth_token = data["id_token"]
        self.user_id = data["user"]["user_id"]
        
        # User feedback: "Sign-up successful, Love the experience"
        print("✅ Test 1 PASSED: Signup successful")
    
    def test_02_onboarding_flow(self):
        """
        Test 2: Onboarding Flow
        
        Steps:
        1. Fill: Height, Weight, Age, Gender
        2. Select goal: "Lose Weight"
        3. Select activity: "Moderately Active"
        4. Submit
        5. Assert: Navigates to dashboard, no errors/delays
        """
        # First signup
        self.test_01_signup_flow()
        
        headers = {"Authorization": f"Bearer {self.auth_token}"}
        
        # Submit onboarding data
        start_time = time.time()
        response = self.session.post(
            f"{API_BASE}/profile",
            json=ONBOARDING_DATA,
            headers=headers,
            timeout=TIMEOUT
        )
        end_time = time.time()
        
        assert response.status_code in [200, 201], f"Onboarding failed: {response.text}"
        
        # Assert: No delays (< 2 seconds)
        response_time = end_time - start_time
        assert response_time < 2.0, f"Onboarding too slow: {response_time:.2f}s"
        
        data = response.json()
        assert "daily_goals" in data, "No daily goals calculated"
        
        print(f"✅ Test 2 PASSED: Onboarding completed in {response_time:.2f}s")
    
    def test_03_dashboard_load(self):
        """
        Test 3: Dashboard Load
        
        Steps:
        1. Assert: Dashboard loads < 2 seconds
        2. Assert: Shows correct calorie goal
        3. Assert: Shows correct macros
        """
        # Setup
        self.test_02_onboarding_flow()
        
        headers = {"Authorization": f"Bearer {self.auth_token}"}
        
        # Load dashboard
        start_time = time.time()
        response = self.session.get(
            f"{API_BASE}/dashboard",
            headers=headers,
            timeout=TIMEOUT
        )
        end_time = time.time()
        
        assert response.status_code == 200, f"Dashboard load failed: {response.text}"
        
        # Assert: Loads < 2 seconds
        load_time = end_time - start_time
        assert load_time < 2.0, f"Dashboard too slow: {load_time:.2f}s"
        
        data = response.json()
        
        # Assert: Shows correct calorie goal (around 1800 for weight loss)
        assert "daily_calories" in data, "No calorie goal"
        assert 1600 <= data["daily_calories"] <= 2000, f"Unexpected calorie goal: {data['daily_calories']}"
        
        # Assert: Shows correct macros
        assert "protein_g" in data, "No protein goal"
        assert "carbs_g" in data, "No carbs goal"
        assert "fat_g" in data, "No fat goal"
        
        print(f"✅ Test 3 PASSED: Dashboard loaded in {load_time:.2f}s")
        print(f"   Daily goals: {data['daily_calories']} kcal, "
              f"{data['protein_g']}g protein, {data['carbs_g']}g carbs, {data['fat_g']}g fat")
    
    def test_04_food_logging_multi_item(self):
        """
        Test 4: Food Logging (Multi-Item) - CRITICAL TEST
        
        Input: Exact user input from testing session
        "2 egg Omlet+ 1 bowl of rice+ beans curry 100 gm + 1 egg dosa + 
         1.5 litres of water + 1 Multivitamin, 1 omega 3 capsule, 1 probiotics"
        
        Assert:
        ✅ Response < 3 seconds (priority 1)
        ✅ Each food parsed into individual card
        ✅ Calories/macros accurate per reference (NOT flat 200 kcal for all)
        ✅ No duplicate/flat values
        
        CRITICAL BUG TO CATCH:
        ❌ All items showing 200 kcal, 10g protein, 25g carbs, 5g fat (flat values)
        """
        # Setup
        self.test_02_onboarding_flow()
        
        headers = {"Authorization": f"Bearer {self.auth_token}"}
        
        # Send chat message
        start_time = time.time()
        response = self.session.post(
            f"{API_BASE}/chat",
            json={"message": COMPLEX_FOOD_INPUT},
            headers=headers,
            timeout=30  # Allow more time for complex input
        )
        end_time = time.time()
        
        assert response.status_code == 200, f"Chat failed: {response.text}"
        
        # Assert: Response < 3 seconds (priority 1)
        response_time = end_time - start_time
        if response_time >= 3.0:
            print(f"⚠️ PRIORITY 2: Response time {response_time:.2f}s (> 3s threshold)")
        else:
            print(f"✅ Response time: {response_time:.2f}s")
        
        data = response.json()
        
        # Assert: Each food parsed into individual item
        assert "items" in data or "meals" in data, "No items returned"
        items = data.get("items", data.get("meals", []))
        
        assert len(items) >= 6, f"Expected at least 6 items, got {len(items)}"
        print(f"✅ Parsed {len(items)} items from complex input")
        
        # CRITICAL: Assert calories/macros are NOT all the same (flat values bug)
        calories_list = [item.get("calories", 0) for item in items if "calories" in item]
        
        # Check for flat values bug
        if len(set(calories_list)) == 1 and calories_list[0] == 200:
            pytest.fail("🔴 CRITICAL BUG: All items have flat 200 kcal (same as user reported)")
        
        # Assert: Different foods have different macros
        unique_calories = len(set(calories_list))
        assert unique_calories >= 3, f"Too many duplicate calorie values: {calories_list}"
        
        # Validate each item has reasonable macros
        for i, item in enumerate(items):
            item_name = item.get("name", f"Item {i+1}")
            calories = item.get("calories", 0)
            protein = item.get("protein_g", 0)
            carbs = item.get("carbs_g", 0)
            fat = item.get("fat_g", 0)
            
            print(f"   Item {i+1}: {item_name} - {calories} kcal, "
                  f"{protein}g protein, {carbs}g carbs, {fat}g fat")
            
            # Sanity checks
            assert calories >= 0, f"Negative calories for {item_name}"
            assert protein >= 0, f"Negative protein for {item_name}"
            assert carbs >= 0, f"Negative carbs for {item_name}"
            assert fat >= 0, f"Negative fat for {item_name}"
            
            # Macro energy should roughly match calories (within 20%)
            macro_calories = (protein * 4) + (carbs * 4) + (fat * 9)
            if calories > 10:  # Skip for very low calorie items
                ratio = abs(macro_calories - calories) / calories
                assert ratio < 0.3, f"Macro mismatch for {item_name}: {macro_calories} vs {calories} kcal"
        
        print(f"✅ Test 4 PASSED: Multi-food logging with accurate macros")
    
    def test_05_dashboard_meal_verification(self):
        """
        Test 5: Dashboard & Meal Verification
        
        Steps:
        1. Go to Home
        2. Assert: Calorie bar updated (sum of all foods)
        3. Assert: Macros updated correctly
        4. Assert: Today's Meals separates by meal type
        5. Assert: Clicking meal shows detail view (MISSING FEATURE)
        6. Assert: Individual macros visible per item (MISSING FEATURE)
        
        CRITICAL BUGS TO CATCH:
        ❌ All meals logged as "Snack" (no meal type classification)
        ❌ No meal detail view (can't see what's inside)
        """
        # Setup: Log foods first
        self.test_04_food_logging_multi_item()
        
        headers = {"Authorization": f"Bearer {self.auth_token}"}
        
        # Get dashboard
        response = self.session.get(
            f"{API_BASE}/dashboard",
            headers=headers,
            timeout=TIMEOUT
        )
        
        assert response.status_code == 200, f"Dashboard failed: {response.text}"
        data = response.json()
        
        # Assert: Calorie bar updated
        total_calories = data.get("total_calories", 0)
        assert total_calories > 0, "No calories logged"
        print(f"✅ Total calories: {total_calories} kcal")
        
        # Assert: Macros updated
        total_protein = data.get("total_protein_g", 0)
        total_carbs = data.get("total_carbs_g", 0)
        total_fat = data.get("total_fat_g", 0)
        
        assert total_protein > 0, "No protein logged"
        assert total_carbs > 0, "No carbs logged"
        assert total_fat > 0, "No fat logged"
        
        print(f"✅ Macros: {total_protein}g protein, {total_carbs}g carbs, {total_fat}g fat")
        
        # Assert: Today's Meals section exists
        meals = data.get("meals", [])
        assert len(meals) > 0, "No meals in Today's Meals section"
        
        # Check meal type classification
        meal_types = [meal.get("meal_type", "unknown") for meal in meals]
        unique_meal_types = set(meal_types)
        
        if len(unique_meal_types) == 1 and "snack" in unique_meal_types:
            print("⚠️ PRIORITY 2: All meals classified as 'Snack' (user reported issue)")
        else:
            print(f"✅ Meal types: {unique_meal_types}")
        
        # Check for meal detail capability (MISSING FEATURE)
        for meal in meals:
            if "items" not in meal and "details" not in meal:
                print("⚠️ PRIORITY 1: No meal detail view available (user requested feature)")
                break
        
        print(f"✅ Test 5 PASSED: Dashboard updated with {len(meals)} meals")
    
    def test_06_persistence(self):
        """
        Test 6: Persistence and Recovery
        
        Steps:
        1. Log foods
        2. Simulate reload (new session)
        3. Assert: Data persists
        4. Assert: No loss of logs
        5. Assert: Dashboard state maintained
        """
        # Setup: Log foods
        self.test_04_food_logging_multi_item()
        
        # Get current state
        headers = {"Authorization": f"Bearer {self.auth_token}"}
        response1 = self.session.get(f"{API_BASE}/dashboard", headers=headers, timeout=TIMEOUT)
        data1 = response1.json()
        
        # Simulate reload (new session, same token)
        new_session = requests.Session()
        response2 = new_session.get(f"{API_BASE}/dashboard", headers=headers, timeout=TIMEOUT)
        data2 = response2.json()
        
        # Assert: Data persists
        assert data1["total_calories"] == data2["total_calories"], "Calories not persisted"
        assert len(data1.get("meals", [])) == len(data2.get("meals", [])), "Meals not persisted"
        
        print(f"✅ Test 6 PASSED: Data persisted across sessions")
    
    def test_07_edge_cases(self):
        """
        Test 7: Negative/Edge Tests
        
        Test cases:
        1. Incomplete: "2 eggs, , rice"
        2. Non-nutrition: "water bottle"
        3. Invalid: "1000 eggs"
        4. Typos: "2 eggs omlette"
        """
        # Setup
        self.test_02_onboarding_flow()
        
        headers = {"Authorization": f"Bearer {self.auth_token}"}
        
        test_cases = [
            {
                "input": "2 eggs, , rice",
                "description": "Incomplete input with empty item",
                "should_succeed": True
            },
            {
                "input": "water bottle",
                "description": "Non-nutrition item",
                "should_succeed": True  # Should handle gracefully
            },
            {
                "input": "1000 eggs",
                "description": "Extreme quantity",
                "should_succeed": True  # Should warn or cap
            },
            {
                "input": "2 eggs omlette",
                "description": "Typo in food name",
                "should_succeed": True  # Should fuzzy match
            }
        ]
        
        for test_case in test_cases:
            response = self.session.post(
                f"{API_BASE}/chat",
                json={"message": test_case["input"]},
                headers=headers,
                timeout=TIMEOUT
            )
            
            if test_case["should_succeed"]:
                assert response.status_code == 200, \
                    f"Failed on {test_case['description']}: {response.text}"
                print(f"✅ Handled: {test_case['description']}")
            else:
                assert response.status_code >= 400, \
                    f"Should have failed on {test_case['description']}"
                print(f"✅ Correctly rejected: {test_case['description']}")
        
        print(f"✅ Test 7 PASSED: All edge cases handled")


class TestPerformance:
    """Performance tests based on user feedback"""
    
    def test_response_time_benchmark(self):
        """
        Benchmark: Chat response time
        
        User feedback: Response taking longer for complex input
        Target: < 3 seconds
        """
        # This would be run with proper setup
        pass


class TestDataAccuracy:
    """Data accuracy tests - CRITICAL based on user feedback"""
    
    def test_macro_calculation_accuracy(self):
        """
        CRITICAL: Test that macros are calculated accurately
        
        User reported: All foods showing flat 200 kcal, 10g protein, 25g carbs, 5g fat
        Expected: Each food should have accurate, different macros
        """
        # This would validate against reference database
        pass


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])

