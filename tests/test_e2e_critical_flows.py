"""
Comprehensive End-to-End Regression Tests
Tests all critical user workflows with locked test data and expected outcomes
"""

import pytest
import requests
import time
import json
from typing import Dict, List, Any, Optional
from datetime import datetime
import sys
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from tests.firebase_test_helper import create_test_user_with_token, delete_test_user

# ============================================================================
# TEST CONFIGURATION
# ============================================================================

API_BASE = "http://localhost:8000"
FRONTEND_BASE = "http://localhost:8080"
TIMEOUT = 10

# Locked test data with expected outcomes
TEST_USERS = {
    "new_user": {
        "email": "e2e_test_new@regression.test",
        "password": "TestPass123!",
        "name": "E2E Test User",
        "expected_uid_format": "^[a-zA-Z0-9]{28}$"
    },
    "returning_user": {
        "email": "e2e_test_returning@regression.test",
        "password": "TestPass123!",
        "name": "Returning User",
    }
}

ONBOARDING_DATA = {
    "basic_info": {
        "height_cm": 170,
        "weight_kg": 70,
        "age": 30,
        "gender": "male",
        "expected_bmi": 24.2,
        "expected_bmi_category": "Normal"
    },
    "fitness_goal": {
        "goal": "lose_weight",
        "target_weight_kg": 65,
        "activity_level": "moderately_active",
        "expected_daily_calories": 1800,  # Approximate
        "expected_protein_g": 135,  # 30% of calories
        "expected_carbs_g": 180,  # 40% of calories
        "expected_fat_g": 60  # 30% of calories
    }
}

MEAL_LOG_TESTS = [
    {
        "input": "2 eggs",
        "expected_items": 1,
        "expected_category": "meal",
        "expected_calories": 140,
        "expected_protein_g": 12,
        "tolerance_percent": 10  # Allow 10% variance
    },
    {
        "input": "2 eggs, 1 bowl rice, 5 pistachios",
        "expected_items": 3,
        "expected_total_calories": 455,  # 140 + 300 + 15
        "tolerance_percent": 15
    },
    {
        "input": "100g chicken breast",
        "expected_items": 1,
        "expected_calories": 165,
        "expected_protein_g": 31,
        "tolerance_percent": 10
    },
    {
        "input": "eggs",  # Ambiguous - should ask for clarification
        "expected_clarification": True,
        "expected_question_contains": ["how many", "quantity"]
    }
]

# ============================================================================
# TEST UTILITIES
# ============================================================================

class TestSession:
    """Manages test session state"""
    def __init__(self, email: str, password: str, name: str):
        self.email = email
        self.password = password
        self.name = name
        self.auth_token: Optional[str] = None
        self.user_id: Optional[str] = None
        self.profile_id: Optional[str] = None
        self.test_results: List[Dict] = []
        
    def log_result(self, test_name: str, passed: bool, details: Dict = None):
        """Log test result"""
        self.test_results.append({
            "test": test_name,
            "passed": passed,
            "timestamp": datetime.now().isoformat(),
            "details": details or {}
        })
        
    def get_auth_headers(self) -> Dict[str, str]:
        """Get authorization headers"""
        if not self.auth_token:
            raise ValueError("No auth token available")
        return {"Authorization": f"Bearer {self.auth_token}"}


def assert_within_tolerance(actual: float, expected: float, tolerance_percent: float, field_name: str):
    """Assert value is within tolerance"""
    tolerance = expected * (tolerance_percent / 100)
    min_val = expected - tolerance
    max_val = expected + tolerance
    assert min_val <= actual <= max_val, \
        f"{field_name}: expected {expected} ±{tolerance_percent}%, got {actual} (range: {min_val:.1f}-{max_val:.1f})"


def wait_for_service(url: str, max_retries: int = 30, delay: float = 1.0) -> bool:
    """Wait for service to be ready"""
    for i in range(max_retries):
        try:
            response = requests.get(url, timeout=2)
            if response.status_code == 200:
                return True
        except requests.exceptions.RequestException:
            pass
        time.sleep(delay)
    return False


# ============================================================================
# FIXTURES
# ============================================================================

@pytest.fixture(scope="session", autouse=True)
def check_services():
    """Ensure backend and frontend are running"""
    print("\n🔍 Checking services...")
    
    # Check backend
    if not wait_for_service(f"{API_BASE}/health", max_retries=10):
        pytest.fail(f"❌ Backend not running at {API_BASE}")
    print(f"✅ Backend: {API_BASE}")
    
    # Check frontend
    if not wait_for_service(FRONTEND_BASE, max_retries=10):
        pytest.fail(f"❌ Frontend not running at {FRONTEND_BASE}")
    print(f"✅ Frontend: {FRONTEND_BASE}")


@pytest.fixture(scope="function")
def new_user_session():
    """Create a fresh test user session"""
    user_data = TEST_USERS["new_user"]
    email = f"test_{int(time.time())}@regression.test"
    
    session = TestSession(email, user_data["password"], user_data["name"])
    
    # Create user
    try:
        user_info = create_test_user_with_token(email, user_data["password"], user_data["name"])
        session.auth_token = user_info["id_token"]
        session.user_id = user_info["uid"]
    except Exception as e:
        pytest.fail(f"Failed to create test user: {e}")
    
    yield session
    
    # Cleanup
    try:
        delete_test_user(email)
    except Exception:
        pass


# ============================================================================
# TEST SUITE: CRITICAL FLOWS
# ============================================================================

class TestCriticalFlows:
    """End-to-end tests for all critical user workflows"""
    
    # ------------------------------------------------------------------------
    # FLOW 1: Signup → Onboarding → Dashboard
    # ------------------------------------------------------------------------
    
    def test_01_complete_onboarding_flow(self, new_user_session: TestSession):
        """
        Test complete onboarding flow:
        1. User signs up
        2. Completes basic info
        3. Selects fitness goal
        4. Gets personalized plan
        5. Lands on dashboard
        """
        session = new_user_session
        
        # Step 1: Create profile with basic info
        profile_data = {
            "name": session.name,
            "gender": ONBOARDING_DATA["basic_info"]["gender"],
            "age": ONBOARDING_DATA["basic_info"]["age"],
            "height_cm": ONBOARDING_DATA["basic_info"]["height_cm"],
            "weight_kg": ONBOARDING_DATA["basic_info"]["weight_kg"],
            "fitness_goal": ONBOARDING_DATA["fitness_goal"]["goal"],
            "target_weight_kg": ONBOARDING_DATA["fitness_goal"]["target_weight_kg"],
            "activity_level": ONBOARDING_DATA["fitness_goal"]["activity_level"]
        }
        
        response = requests.post(
            f"{API_BASE}/profile/create",
            json=profile_data,
            headers=session.get_auth_headers(),
            timeout=TIMEOUT
        )
        
        assert response.status_code == 200, f"Profile creation failed: {response.text}"
        profile = response.json()
        
        # Verify BMI calculation
        expected_bmi = ONBOARDING_DATA["basic_info"]["expected_bmi"]
        actual_bmi = profile["profile"]["bmi"]
        assert_within_tolerance(actual_bmi, expected_bmi, 1, "BMI")
        
        # Verify goals were calculated
        assert "daily_goals" in profile, "Missing daily_goals"
        goals = profile["daily_goals"]
        
        # Verify calorie goal (with tolerance for different formulas)
        expected_cal = ONBOARDING_DATA["fitness_goal"]["expected_daily_calories"]
        assert_within_tolerance(goals["calories"], expected_cal, 20, "Daily calories")
        
        # Verify macro distribution
        assert goals["proteinG"] > 0, "Protein goal not set"
        assert goals["carbsG"] > 0, "Carbs goal not set"
        assert goals["fatG"] > 0, "Fat goal not set"
        
        session.profile_id = profile["profile"]["user_id"]
        session.log_result("onboarding_flow", True, {"profile_id": session.profile_id})
    
    # ------------------------------------------------------------------------
    # FLOW 2: Chat → Log Single Meal → Dashboard Update
    # ------------------------------------------------------------------------
    
    def test_02_log_single_meal_and_verify_dashboard(self, new_user_session: TestSession):
        """
        Test meal logging flow:
        1. Complete onboarding
        2. Log a single meal via chat
        3. Verify dashboard updates correctly
        """
        session = new_user_session
        
        # Complete onboarding first
        self.test_01_complete_onboarding_flow(session)
        
        # Log a meal
        test_meal = MEAL_LOG_TESTS[0]  # "2 eggs"
        
        response = requests.post(
            f"{API_BASE}/chat",
            json={"user_input": test_meal["input"]},
            headers=session.get_auth_headers(),
            timeout=TIMEOUT
        )
        
        assert response.status_code == 200, f"Chat failed: {response.text}"
        chat_response = response.json()
        
        # Verify response structure
        assert "items" in chat_response, "Missing items in response"
        assert len(chat_response["items"]) == test_meal["expected_items"], \
            f"Expected {test_meal['expected_items']} items, got {len(chat_response['items'])}"
        
        # Verify meal data
        meal_item = chat_response["items"][0]
        assert meal_item["category"] == test_meal["expected_category"]
        
        meal_data = meal_item["data"]
        assert_within_tolerance(
            meal_data["calories"],
            test_meal["expected_calories"],
            test_meal["tolerance_percent"],
            "Calories"
        )
        assert_within_tolerance(
            meal_data["protein_g"],
            test_meal["expected_protein_g"],
            test_meal["tolerance_percent"],
            "Protein"
        )
        
        # Verify dashboard updates
        time.sleep(1)  # Give backend time to process
        
        dashboard_response = requests.get(
            f"{API_BASE}/dashboard",
            headers=session.get_auth_headers(),
            timeout=TIMEOUT
        )
        
        assert dashboard_response.status_code == 200, f"Dashboard fetch failed: {dashboard_response.text}"
        dashboard = dashboard_response.json()
        
        # Verify calories are tracked
        assert dashboard["calories_consumed"] == test_meal["expected_calories"], \
            f"Dashboard calories mismatch: expected {test_meal['expected_calories']}, got {dashboard['calories_consumed']}"
        
        session.log_result("single_meal_log", True, {
            "meal": test_meal["input"],
            "calories_logged": meal_data["calories"]
        })
    
    # ------------------------------------------------------------------------
    # FLOW 3: Multi-Food Entry
    # ------------------------------------------------------------------------
    
    def test_03_log_multi_food_entry(self, new_user_session: TestSession):
        """
        Test multi-food parsing:
        1. Log multiple foods in one message
        2. Verify each food is parsed separately
        3. Verify total calories are correct
        """
        session = new_user_session
        
        # Complete onboarding
        self.test_01_complete_onboarding_flow(session)
        
        # Log multi-food
        test_meal = MEAL_LOG_TESTS[1]  # "2 eggs, 1 bowl rice, 5 pistachios"
        
        response = requests.post(
            f"{API_BASE}/chat",
            json={"user_input": test_meal["input"]},
            headers=session.get_auth_headers(),
            timeout=TIMEOUT
        )
        
        assert response.status_code == 200, f"Multi-food chat failed: {response.text}"
        chat_response = response.json()
        
        # Verify multiple items
        assert len(chat_response["items"]) == test_meal["expected_items"], \
            f"Expected {test_meal['expected_items']} items, got {len(chat_response['items'])}"
        
        # Calculate total calories
        total_calories = sum(item["data"]["calories"] for item in chat_response["items"])
        
        assert_within_tolerance(
            total_calories,
            test_meal["expected_total_calories"],
            test_meal["tolerance_percent"],
            "Total calories"
        )
        
        session.log_result("multi_food_log", True, {
            "input": test_meal["input"],
            "items_parsed": len(chat_response["items"]),
            "total_calories": total_calories
        })
    
    # ------------------------------------------------------------------------
    # FLOW 4: Clarification Handling
    # ------------------------------------------------------------------------
    
    def test_04_clarification_for_ambiguous_input(self, new_user_session: TestSession):
        """
        Test clarification flow:
        1. Send ambiguous input (e.g., "eggs" without quantity)
        2. Verify system asks for clarification
        3. Provide clarification
        4. Verify meal is logged correctly
        """
        session = new_user_session
        
        # Complete onboarding
        self.test_01_complete_onboarding_flow(session)
        
        # Send ambiguous input
        test_meal = MEAL_LOG_TESTS[3]  # "eggs"
        
        response = requests.post(
            f"{API_BASE}/chat",
            json={"user_input": test_meal["input"]},
            headers=session.get_auth_headers(),
            timeout=TIMEOUT
        )
        
        assert response.status_code == 200, f"Chat failed: {response.text}"
        chat_response = response.json()
        
        # Verify clarification is requested
        if test_meal.get("expected_clarification"):
            assert chat_response.get("needs_clarification") == True, \
                "Expected clarification request"
            
            clarification_msg = chat_response.get("message", "").lower()
            assert any(keyword in clarification_msg for keyword in test_meal["expected_question_contains"]), \
                f"Clarification message doesn't contain expected keywords: {clarification_msg}"
            
            session.log_result("clarification_request", True, {
                "input": test_meal["input"],
                "clarification_message": clarification_msg
            })
        
        # Provide clarification
        response2 = requests.post(
            f"{API_BASE}/chat",
            json={"user_input": "2 eggs"},
            headers=session.get_auth_headers(),
            timeout=TIMEOUT
        )
        
        assert response2.status_code == 200, f"Clarification response failed: {response2.text}"
        chat_response2 = response2.json()
        
        # Verify meal is now logged
        assert len(chat_response2["items"]) == 1, "Expected 1 meal item after clarification"
        assert chat_response2["items"][0]["data"]["calories"] == 140, "Calories mismatch after clarification"
        
        session.log_result("clarification_resolution", True)
    
    # ------------------------------------------------------------------------
    # FLOW 5: Chat History Persistence
    # ------------------------------------------------------------------------
    
    def test_05_chat_history_persistence(self, new_user_session: TestSession):
        """
        Test chat history:
        1. Log multiple meals
        2. Fetch chat history
        3. Verify all messages are saved
        4. Verify metadata is correct
        """
        session = new_user_session
        
        # Complete onboarding
        self.test_01_complete_onboarding_flow(session)
        
        # Log 3 meals
        meals = ["2 eggs", "1 bowl rice", "100g chicken breast"]
        
        for meal in meals:
            response = requests.post(
                f"{API_BASE}/chat",
                json={"user_input": meal},
                headers=session.get_auth_headers(),
                timeout=TIMEOUT
            )
            assert response.status_code == 200, f"Chat failed for {meal}: {response.text}"
            time.sleep(0.5)
        
        # Fetch chat history
        history_response = requests.get(
            f"{API_BASE}/chat/history?limit=100",
            headers=session.get_auth_headers(),
            timeout=TIMEOUT
        )
        
        assert history_response.status_code == 200, f"Chat history fetch failed: {history_response.text}"
        history = history_response.json()
        
        # Verify messages are saved
        assert "messages" in history, "Missing messages in history"
        assert len(history["messages"]) >= len(meals) * 2, \
            f"Expected at least {len(meals) * 2} messages (user + AI), got {len(history['messages'])}"
        
        # Verify user messages are present
        user_messages = [msg for msg in history["messages"] if msg.get("role") == "user"]
        assert len(user_messages) >= len(meals), \
            f"Expected at least {len(meals)} user messages, got {len(user_messages)}"
        
        session.log_result("chat_history", True, {
            "total_messages": len(history["messages"]),
            "user_messages": len(user_messages)
        })
    
    # ------------------------------------------------------------------------
    # FLOW 6: Error Handling
    # ------------------------------------------------------------------------
    
    def test_06_invalid_auth_token(self):
        """Test that invalid auth tokens are rejected"""
        response = requests.post(
            f"{API_BASE}/chat",
            json={"user_input": "test"},
            headers={"Authorization": "Bearer invalid_token_12345"},
            timeout=TIMEOUT
        )
        
        assert response.status_code == 401, f"Expected 401, got {response.status_code}"
    
    def test_07_missing_auth_token(self):
        """Test that missing auth tokens are rejected"""
        response = requests.post(
            f"{API_BASE}/chat",
            json={"user_input": "test"},
            timeout=TIMEOUT
        )
        
        assert response.status_code == 401, f"Expected 401, got {response.status_code}"
    
    def test_08_invalid_profile_data(self, new_user_session: TestSession):
        """Test that invalid profile data is rejected"""
        session = new_user_session
        
        # Try to create profile with invalid data
        invalid_data = {
            "name": "Test",
            "age": -5,  # Invalid age
            "height_cm": 300,  # Invalid height
            "weight_kg": 500,  # Invalid weight
        }
        
        response = requests.post(
            f"{API_BASE}/profile/create",
            json=invalid_data,
            headers=session.get_auth_headers(),
            timeout=TIMEOUT
        )
        
        assert response.status_code in [400, 422], \
            f"Expected 400/422 for invalid data, got {response.status_code}"


# ============================================================================
# PERFORMANCE BENCHMARKS
# ============================================================================

class TestPerformance:
    """Performance regression tests"""
    
    def test_chat_response_time(self, new_user_session: TestSession):
        """Verify chat response time is under 2 seconds"""
        session = new_user_session
        
        # Complete onboarding
        TestCriticalFlows().test_01_complete_onboarding_flow(session)
        
        # Test response time
        start = time.time()
        response = requests.post(
            f"{API_BASE}/chat",
            json={"user_input": "2 eggs"},
            headers=session.get_auth_headers(),
            timeout=TIMEOUT
        )
        elapsed = time.time() - start
        
        assert response.status_code == 200, f"Chat failed: {response.text}"
        assert elapsed < 2.0, f"Chat response too slow: {elapsed:.2f}s (expected < 2s)"
    
    def test_dashboard_load_time(self, new_user_session: TestSession):
        """Verify dashboard loads in under 1 second"""
        session = new_user_session
        
        # Complete onboarding
        TestCriticalFlows().test_01_complete_onboarding_flow(session)
        
        # Test load time
        start = time.time()
        response = requests.get(
            f"{API_BASE}/dashboard",
            headers=session.get_auth_headers(),
            timeout=TIMEOUT
        )
        elapsed = time.time() - start
        
        assert response.status_code == 200, f"Dashboard fetch failed: {response.text}"
        assert elapsed < 1.0, f"Dashboard load too slow: {elapsed:.2f}s (expected < 1s)"


# ============================================================================
# MAIN EXECUTION
# ============================================================================

if __name__ == "__main__":
    # Run tests with verbose output
    pytest.main([__file__, "-v", "-s", "--tb=short"])


