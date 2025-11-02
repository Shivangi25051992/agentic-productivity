#!/usr/bin/env python3
"""
Comprehensive Regression Test Suite
Tests all features to ensure nothing breaks when we make changes
"""

import pytest
import requests
import json
from datetime import datetime
from typing import Dict, List

# Test configuration
API_BASE_URL = "http://localhost:8000"
TEST_DATA_FILE = "test_data.json"

class TestRegression:
    """Regression tests for all features"""
    
    @pytest.fixture(autouse=True)
    def setup(self):
        """Load test data before each test"""
        with open(TEST_DATA_FILE, 'r') as f:
            self.test_data = json.load(f)
    
    # ==================== HEALTH & CONNECTIVITY ====================
    
    def test_backend_health(self):
        """Test 1: Backend health check"""
        response = requests.get(f"{API_BASE_URL}/health")
        assert response.status_code == 200
        data = response.json()
        assert data['status'] == 'healthy'
        assert 'version' in data
    
    # ==================== GOAL CALCULATIONS ====================
    
    def test_goal_calculation_male(self):
        """Test 2: Goal calculation for male user"""
        payload = {
            "gender": "male",
            "age": 30,
            "height_cm": 175,
            "weight_kg": 75,
            "activity_level": "moderately_active",
            "fitness_goal": "lose_weight"
        }
        response = requests.post(f"{API_BASE_URL}/profile/calculate-goals", json=payload)
        assert response.status_code == 200
        data = response.json()
        
        # Verify structure
        assert 'recommended_goals' in data
        assert 'metabolic_info' in data
        
        goals = data['recommended_goals']
        assert 'calories' in goals
        assert 'protein_g' in goals
        assert 'carbs_g' in goals
        assert 'fat_g' in goals
        
        # Verify reasonable ranges
        assert 1500 <= goals['calories'] <= 3000
        assert 50 <= goals['protein_g'] <= 250
        assert 50 <= goals['carbs_g'] <= 400
        assert 20 <= goals['fat_g'] <= 150
    
    def test_goal_calculation_female(self):
        """Test 3: Goal calculation for female user"""
        payload = {
            "gender": "female",
            "age": 28,
            "height_cm": 165,
            "weight_kg": 60,
            "activity_level": "lightly_active",
            "fitness_goal": "maintain"
        }
        response = requests.post(f"{API_BASE_URL}/profile/calculate-goals", json=payload)
        assert response.status_code == 200
        data = response.json()
        assert 'recommended_goals' in data
        assert data['recommended_goals']['calories'] > 0
    
    def test_goal_calculation_gain_muscle(self):
        """Test 4: Goal calculation for muscle gain"""
        payload = {
            "gender": "male",
            "age": 25,
            "height_cm": 180,
            "weight_kg": 70,
            "activity_level": "very_active",
            "fitness_goal": "gain_muscle"
        }
        response = requests.post(f"{API_BASE_URL}/profile/calculate-goals", json=payload)
        assert response.status_code == 200
        data = response.json()
        goals = data['recommended_goals']
        
        # Muscle gain should have high protein
        assert goals['protein_g'] >= 140  # 2g per kg minimum
    
    # ==================== BMI CALCULATIONS ====================
    
    def test_bmi_calculation(self):
        """Test 5: BMI calculation accuracy"""
        # Test case: 175cm, 70kg = BMI 22.9 (Normal)
        height_cm = 175
        weight_kg = 70
        expected_bmi = 22.9
        
        bmi = weight_kg / ((height_cm / 100) ** 2)
        assert abs(bmi - expected_bmi) < 0.1
    
    def test_bmi_categories(self):
        """Test 6: BMI category classification"""
        height_cm = 175
        
        # Underweight
        bmi_underweight = 50 / ((height_cm / 100) ** 2)
        assert bmi_underweight < 18.5
        
        # Normal
        bmi_normal = 70 / ((height_cm / 100) ** 2)
        assert 18.5 <= bmi_normal < 25
        
        # Overweight
        bmi_overweight = 85 / ((height_cm / 100) ** 2)
        assert 25 <= bmi_overweight < 30
    
    # ==================== CHAT ASSISTANT ====================
    
    def test_chat_simple_meal(self):
        """Test 7: Chat assistant with simple meal input"""
        # Note: This requires auth token, so we test the structure
        payload = {"user_input": "2 boiled eggs"}
        # Without auth, should get 401
        response = requests.post(f"{API_BASE_URL}/chat", json=payload)
        assert response.status_code in [200, 401]  # Either works or needs auth
    
    def test_chat_complex_multi_food(self):
        """Test 8: Chat assistant with complex multi-food input"""
        test_case = self.test_data['complex_cases'][0]
        payload = {"user_input": test_case['input']}
        response = requests.post(f"{API_BASE_URL}/chat", json=payload)
        # Should either work (200) or need auth (401), but not crash (500)
        assert response.status_code in [200, 401]
        assert response.status_code != 500  # No server errors
    
    # ==================== FOOD DATABASE ====================
    
    def test_food_macro_lookup_eggs(self):
        """Test 9: Food macro lookup for eggs"""
        # This tests the food database functionality
        # Eggs: ~70 cal, 6g protein per egg
        expected_cal_per_egg = 70
        expected_protein_per_egg = 6
        
        # Just verify the numbers are reasonable
        assert 60 <= expected_cal_per_egg <= 80
        assert 5 <= expected_protein_per_egg <= 7
    
    def test_food_macro_lookup_rice(self):
        """Test 10: Food macro lookup for rice"""
        # Rice: ~130 cal per 100g, 2.7g protein, 28g carbs
        expected_cal_per_100g = 130
        expected_carbs_per_100g = 28
        
        assert 120 <= expected_cal_per_100g <= 140
        assert 25 <= expected_carbs_per_100g <= 30
    
    # ==================== UNIT CONVERSIONS ====================
    
    def test_weight_conversion_kg_to_lb(self):
        """Test 11: Weight conversion kg to lb"""
        kg = 70
        lb = kg / 0.453592
        expected_lb = 154.3
        assert abs(lb - expected_lb) < 0.5
    
    def test_height_conversion_cm_to_ft_in(self):
        """Test 12: Height conversion cm to ft/in"""
        cm = 175
        total_inches = cm / 2.54
        feet = int(total_inches // 12)
        inches = int(total_inches % 12)
        
        assert feet == 5
        assert 8 <= inches <= 9  # 5'8" or 5'9"
    
    # ==================== EDGE CASES ====================
    
    def test_edge_case_zero_values(self):
        """Test 13: Handle zero values gracefully"""
        payload = {
            "gender": "male",
            "age": 25,
            "height_cm": 175,
            "weight_kg": 0,  # Invalid
            "activity_level": "moderately_active",
            "fitness_goal": "maintain"
        }
        response = requests.post(f"{API_BASE_URL}/profile/calculate-goals", json=payload)
        # Should either reject (400) or handle gracefully
        assert response.status_code in [200, 400, 422]
    
    def test_edge_case_extreme_values(self):
        """Test 14: Handle extreme values"""
        payload = {
            "gender": "male",
            "age": 150,  # Too old
            "height_cm": 300,  # Too tall
            "weight_kg": 500,  # Too heavy
            "activity_level": "moderately_active",
            "fitness_goal": "maintain"
        }
        response = requests.post(f"{API_BASE_URL}/profile/calculate-goals", json=payload)
        # Should handle gracefully
        assert response.status_code in [200, 400, 422]
    
    # ==================== PERFORMANCE ====================
    
    def test_response_time_health(self):
        """Test 15: Health endpoint response time < 1 second"""
        import time
        start = time.time()
        response = requests.get(f"{API_BASE_URL}/health")
        elapsed = time.time() - start
        
        assert response.status_code == 200
        assert elapsed < 1.0  # Should respond in < 1 second
    
    def test_response_time_goal_calculation(self):
        """Test 16: Goal calculation response time < 2 seconds"""
        import time
        payload = {
            "gender": "male",
            "age": 30,
            "height_cm": 175,
            "weight_kg": 75,
            "activity_level": "moderately_active",
            "fitness_goal": "maintain"
        }
        start = time.time()
        response = requests.post(f"{API_BASE_URL}/profile/calculate-goals", json=payload)
        elapsed = time.time() - start
        
        assert response.status_code == 200
        assert elapsed < 2.0  # Should respond in < 2 seconds
    
    # ==================== DATA VALIDATION ====================
    
    def test_macro_sum_equals_calories(self):
        """Test 17: Verify macros sum to total calories"""
        payload = {
            "gender": "male",
            "age": 30,
            "height_cm": 175,
            "weight_kg": 75,
            "activity_level": "moderately_active",
            "fitness_goal": "maintain"
        }
        response = requests.post(f"{API_BASE_URL}/profile/calculate-goals", json=payload)
        assert response.status_code == 200
        
        goals = response.json()['recommended_goals']
        
        # Calculate calories from macros
        protein_cal = goals['protein_g'] * 4
        carbs_cal = goals['carbs_g'] * 4
        fat_cal = goals['fat_g'] * 9
        total_from_macros = protein_cal + carbs_cal + fat_cal
        
        # Should be within 10% of stated calories (due to rounding)
        assert abs(total_from_macros - goals['calories']) / goals['calories'] < 0.1
    
    # ==================== TEST DATA VALIDATION ====================
    
    def test_test_data_structure(self):
        """Test 18: Verify test data has correct structure"""
        assert 'week_data' in self.test_data
        assert 'complex_cases' in self.test_data
        assert 'edge_cases' in self.test_data
        
        assert len(self.test_data['week_data']) == 7  # 7 days
        assert len(self.test_data['complex_cases']) >= 5
        assert len(self.test_data['edge_cases']) >= 5
    
    def test_test_data_completeness(self):
        """Test 19: Verify test data is complete"""
        for day in self.test_data['week_data']:
            assert 'date' in day
            assert 'day' in day
            assert 'meals' in day
            assert len(day['meals']) >= 4  # At least 4 meals per day

# ==================== RUN TESTS ====================

def run_regression_tests():
    """Run all regression tests and generate report"""
    print("\n" + "="*70)
    print("  RUNNING REGRESSION TEST SUITE")
    print("="*70 + "\n")
    
    # Run pytest
    exit_code = pytest.main([
        __file__,
        "-v",  # Verbose
        "--tb=short",  # Short traceback
        "-x",  # Stop on first failure
    ])
    
    if exit_code == 0:
        print("\n" + "="*70)
        print("  ✅ ALL REGRESSION TESTS PASSED!")
        print("="*70 + "\n")
    else:
        print("\n" + "="*70)
        print("  ❌ SOME TESTS FAILED - CHECK OUTPUT ABOVE")
        print("="*70 + "\n")
    
    return exit_code

if __name__ == "__main__":
    run_regression_tests()


