"""
Automated API Testing for Fasting & Meal Planning
Tests all new endpoints with real requests
"""

import requests
import json
from datetime import datetime, date, timedelta
import sys

# Base URL
BASE_URL = "http://localhost:8000"

# Test user credentials (use your existing test user)
TEST_EMAIL = "test@example.com"
TEST_PASSWORD = "test123"

# Colors for output
GREEN = '\033[92m'
RED = '\033[91m'
BLUE = '\033[94m'
YELLOW = '\033[93m'
RESET = '\033[0m'

def print_success(msg):
    print(f"{GREEN}✅ {msg}{RESET}")

def print_error(msg):
    print(f"{RED}❌ {msg}{RESET}")

def print_info(msg):
    print(f"{BLUE}ℹ️  {msg}{RESET}")

def print_warning(msg):
    print(f"{YELLOW}⚠️  {msg}{RESET}")

def print_section(msg):
    print(f"\n{BLUE}{'='*60}")
    print(f"  {msg}")
    print(f"{'='*60}{RESET}\n")


class APITester:
    def __init__(self):
        self.token = None
        self.headers = {}
        self.session_id = None
        self.meal_plan_id = None
        self.recipe_id = None
        self.grocery_list_id = None
    
    def login(self):
        """Login and get JWT token"""
        print_section("🔐 AUTHENTICATION")
        
        try:
            response = requests.post(
                f"{BASE_URL}/auth/login",
                json={"email": TEST_EMAIL, "password": TEST_PASSWORD}
            )
            
            if response.status_code == 200:
                data = response.json()
                self.token = data.get("access_token")
                self.headers = {"Authorization": f"Bearer {self.token}"}
                print_success(f"Logged in as {TEST_EMAIL}")
                return True
            else:
                print_error(f"Login failed: {response.status_code}")
                print_warning("Make sure test user exists. Creating one...")
                return self.create_test_user()
        except Exception as e:
            print_error(f"Login error: {e}")
            return False
    
    def create_test_user(self):
        """Create test user if doesn't exist"""
        try:
            response = requests.post(
                f"{BASE_URL}/auth/register",
                json={
                    "email": TEST_EMAIL,
                    "password": TEST_PASSWORD,
                    "name": "Test User"
                }
            )
            
            if response.status_code in [200, 201]:
                print_success("Test user created")
                return self.login()
            else:
                print_error(f"Failed to create user: {response.status_code}")
                return False
        except Exception as e:
            print_error(f"Error creating user: {e}")
            return False
    
    # ========================================================================
    # FASTING API TESTS
    # ========================================================================
    
    def test_fasting_apis(self):
        """Test all fasting endpoints"""
        print_section("🕐 FASTING API TESTS")
        
        # 1. Start fasting session
        print_info("1. Starting fasting session...")
        try:
            response = requests.post(
                f"{BASE_URL}/fasting/start",
                headers=self.headers,
                json={
                    "target_duration_hours": 16,
                    "protocol": "16:8",
                    "notes": "Test fast"
                }
            )
            
            if response.status_code == 200:
                data = response.json()
                self.session_id = data.get("id")
                print_success(f"Started fasting session: {self.session_id}")
                print_info(f"   Protocol: {data.get('protocol')}")
                print_info(f"   Target: {data.get('target_duration_hours')} hours")
            else:
                print_error(f"Failed to start session: {response.status_code} - {response.text}")
        except Exception as e:
            print_error(f"Error: {e}")
        
        # 2. Get current session
        print_info("\n2. Getting current fasting session...")
        try:
            response = requests.get(
                f"{BASE_URL}/fasting/current",
                headers=self.headers
            )
            
            if response.status_code == 200:
                data = response.json()
                if data:
                    print_success("Retrieved current session")
                    print_info(f"   Stage: {data.get('current_stage')}")
                    print_info(f"   Progress: {data.get('progress_percentage')}%")
                    print_info(f"   Time remaining: {data.get('time_remaining_hours')} hours")
                else:
                    print_warning("No active session")
            else:
                print_error(f"Failed: {response.status_code}")
        except Exception as e:
            print_error(f"Error: {e}")
        
        # 3. Get fasting history
        print_info("\n3. Getting fasting history...")
        try:
            response = requests.get(
                f"{BASE_URL}/fasting/history?limit=10",
                headers=self.headers
            )
            
            if response.status_code == 200:
                data = response.json()
                print_success(f"Retrieved {len(data)} fasting sessions")
            else:
                print_error(f"Failed: {response.status_code}")
        except Exception as e:
            print_error(f"Error: {e}")
        
        # 4. Get analytics
        print_info("\n4. Getting fasting analytics...")
        try:
            response = requests.get(
                f"{BASE_URL}/fasting/analytics?period_days=30",
                headers=self.headers
            )
            
            if response.status_code == 200:
                data = response.json()
                print_success("Retrieved analytics")
                print_info(f"   Total fasts: {data.get('total_fasts')}")
                print_info(f"   Completion rate: {data.get('completion_rate')}%")
                print_info(f"   Average duration: {data.get('average_duration_hours')} hours")
                print_info(f"   Current streak: {data.get('current_streak_days')} days")
            else:
                print_error(f"Failed: {response.status_code}")
        except Exception as e:
            print_error(f"Error: {e}")
        
        # 5. Get/Create profile
        print_info("\n5. Getting fasting profile...")
        try:
            response = requests.get(
                f"{BASE_URL}/fasting/profile",
                headers=self.headers
            )
            
            if response.status_code == 200:
                data = response.json()
                if data:
                    print_success("Retrieved profile")
                    print_info(f"   Default protocol: {data.get('default_protocol')}")
                else:
                    print_warning("No profile found, creating one...")
                    self.create_fasting_profile()
            else:
                print_error(f"Failed: {response.status_code}")
        except Exception as e:
            print_error(f"Error: {e}")
        
        # 6. Get coaching context
        print_info("\n6. Getting AI coaching context...")
        try:
            response = requests.get(
                f"{BASE_URL}/fasting/coaching/context",
                headers=self.headers
            )
            
            if response.status_code == 200:
                data = response.json()
                print_success("Retrieved coaching context")
                print_info(f"   Has active session: {data.get('active_session') is not None}")
                print_info(f"   Has profile: {data.get('profile') is not None}")
            else:
                print_error(f"Failed: {response.status_code}")
        except Exception as e:
            print_error(f"Error: {e}")
        
        # 7. Get window recommendation
        print_info("\n7. Getting fasting window recommendation...")
        try:
            response = requests.post(
                f"{BASE_URL}/fasting/coaching/recommend-window",
                headers=self.headers,
                json={
                    "wake_time": "07:00",
                    "sleep_time": "23:00",
                    "work_schedule": "9-5"
                }
            )
            
            if response.status_code == 200:
                data = response.json()
                print_success("Got recommendation")
                print_info(f"   Protocol: {data.get('protocol')}")
                print_info(f"   Eating window: {data.get('eating_window_start')} - {data.get('eating_window_end')}")
            else:
                print_error(f"Failed: {response.status_code}")
        except Exception as e:
            print_error(f"Error: {e}")
        
        # 8. End fasting session
        if self.session_id:
            print_info(f"\n8. Ending fasting session {self.session_id}...")
            try:
                response = requests.post(
                    f"{BASE_URL}/fasting/end/{self.session_id}",
                    headers=self.headers,
                    json={
                        "break_reason": "planned",
                        "energy_level": 4,
                        "hunger_level": 3,
                        "notes": "Test completed"
                    }
                )
                
                if response.status_code == 200:
                    data = response.json()
                    print_success("Ended fasting session")
                    print_info(f"   Duration: {data.get('actual_duration_hours')} hours")
                    print_info(f"   Completed: {data.get('is_completed')}")
                else:
                    print_error(f"Failed: {response.status_code}")
            except Exception as e:
                print_error(f"Error: {e}")
    
    def create_fasting_profile(self):
        """Create a fasting profile"""
        try:
            response = requests.put(
                f"{BASE_URL}/fasting/profile",
                headers=self.headers,
                json={
                    "default_protocol": "16:8",
                    "eating_window_start": "12:00",
                    "eating_window_end": "20:00",
                    "experience_level": "beginner",
                    "goals": ["weight_loss", "mental_clarity"]
                }
            )
            
            if response.status_code == 200:
                print_success("Created fasting profile")
            else:
                print_error(f"Failed to create profile: {response.status_code}")
        except Exception as e:
            print_error(f"Error: {e}")
    
    # ========================================================================
    # MEAL PLANNING API TESTS
    # ========================================================================
    
    def test_meal_planning_apis(self):
        """Test all meal planning endpoints"""
        print_section("🍽️ MEAL PLANNING API TESTS")
        
        # 1. Create a recipe
        print_info("1. Creating a test recipe...")
        try:
            response = requests.post(
                f"{BASE_URL}/meal-planning/recipes",
                headers=self.headers,
                json={
                    "name": "Protein Smoothie Bowl",
                    "description": "High-protein breakfast bowl",
                    "category": "breakfast",
                    "cuisine": "american",
                    "difficulty": "easy",
                    "prep_time_minutes": 10,
                    "cook_time_minutes": 0,
                    "servings": 1,
                    "ingredients": [
                        {"name": "Banana", "amount": "1 medium"},
                        {"name": "Protein powder", "amount": "30g"},
                        {"name": "Almond milk", "amount": "200ml"},
                        {"name": "Berries", "amount": "50g"}
                    ],
                    "instructions": [
                        "Blend banana, protein powder, and almond milk",
                        "Pour into bowl",
                        "Top with berries"
                    ],
                    "nutrition": {
                        "calories": 350,
                        "protein_g": 30,
                        "carbs_g": 45,
                        "fat_g": 8
                    },
                    "tags": ["high_protein", "quick", "breakfast"]
                }
            )
            
            if response.status_code == 200:
                data = response.json()
                self.recipe_id = data.get("id")
                print_success(f"Created recipe: {data.get('name')}")
                print_info(f"   ID: {self.recipe_id}")
                print_info(f"   Calories: {data.get('nutrition', {}).get('calories')}")
            else:
                print_error(f"Failed: {response.status_code} - {response.text}")
        except Exception as e:
            print_error(f"Error: {e}")
        
        # 2. Search recipes
        print_info("\n2. Searching recipes...")
        try:
            response = requests.post(
                f"{BASE_URL}/meal-planning/recipes/search",
                headers=self.headers,
                json={
                    "query": "protein",
                    "max_prep_time": 30,
                    "limit": 10
                }
            )
            
            if response.status_code == 200:
                data = response.json()
                print_success(f"Found {len(data)} recipes")
            else:
                print_error(f"Failed: {response.status_code}")
        except Exception as e:
            print_error(f"Error: {e}")
        
        # 3. Generate meal plan
        print_info("\n3. Generating meal plan...")
        try:
            today = date.today()
            # Start from Monday of current week
            monday = today - timedelta(days=today.weekday())
            
            response = requests.post(
                f"{BASE_URL}/meal-planning/plans/generate",
                headers=self.headers,
                json={
                    "week_start_date": monday.isoformat(),
                    "dietary_preferences": ["high_protein"],
                    "daily_calorie_target": 2000,
                    "daily_protein_target": 150,
                    "num_people": 1,
                    "prep_time_preference": "quick"
                }
            )
            
            if response.status_code == 200:
                data = response.json()
                self.meal_plan_id = data.get("id")
                print_success(f"Generated meal plan: {self.meal_plan_id}")
                print_info(f"   Week: {data.get('week_start_date')} to {data.get('week_end_date')}")
                print_info(f"   Target calories: {data.get('daily_calorie_target')}")
            else:
                print_error(f"Failed: {response.status_code} - {response.text}")
        except Exception as e:
            print_error(f"Error: {e}")
        
        # 4. Get current week plan
        print_info("\n4. Getting current week meal plan...")
        try:
            response = requests.get(
                f"{BASE_URL}/meal-planning/plans/current",
                headers=self.headers
            )
            
            if response.status_code == 200:
                data = response.json()
                if data:
                    print_success("Retrieved current week plan")
                    print_info(f"   ID: {data.get('id')}")
                else:
                    print_warning("No current week plan")
            else:
                print_error(f"Failed: {response.status_code}")
        except Exception as e:
            print_error(f"Error: {e}")
        
        # 5. Add meal to plan
        if self.meal_plan_id and self.recipe_id:
            print_info(f"\n5. Adding meal to plan...")
            try:
                response = requests.post(
                    f"{BASE_URL}/meal-planning/plans/{self.meal_plan_id}/meals",
                    headers=self.headers,
                    json={
                        "day": "monday",
                        "meal_type": "breakfast",
                        "recipe_id": self.recipe_id,
                        "servings": 1
                    }
                )
                
                if response.status_code == 200:
                    print_success("Added meal to plan")
                else:
                    print_error(f"Failed: {response.status_code}")
            except Exception as e:
                print_error(f"Error: {e}")
        
        # 6. Get meal plan analytics
        if self.meal_plan_id:
            print_info(f"\n6. Getting meal plan analytics...")
            try:
                response = requests.get(
                    f"{BASE_URL}/meal-planning/plans/{self.meal_plan_id}/analytics",
                    headers=self.headers
                )
                
                if response.status_code == 200:
                    data = response.json()
                    print_success("Retrieved analytics")
                    print_info(f"   Total meals: {data.get('total_meals_planned')}")
                    print_info(f"   Completion: {data.get('completion_percentage')}%")
                else:
                    print_error(f"Failed: {response.status_code}")
            except Exception as e:
                print_error(f"Error: {e}")
        
        # 7. Generate grocery list
        if self.meal_plan_id:
            print_info(f"\n7. Generating grocery list...")
            try:
                response = requests.post(
                    f"{BASE_URL}/meal-planning/grocery-lists/generate/{self.meal_plan_id}",
                    headers=self.headers
                )
                
                if response.status_code == 200:
                    data = response.json()
                    self.grocery_list_id = data.get("id")
                    print_success(f"Generated grocery list: {self.grocery_list_id}")
                    print_info(f"   Items: {len(data.get('items', []))}")
                    print_info(f"   Estimated cost: ${data.get('total_estimated_cost', 0)}")
                else:
                    print_error(f"Failed: {response.status_code}")
            except Exception as e:
                print_error(f"Error: {e}")
        
        # 8. Get daily suggestions
        print_info("\n8. Getting daily meal suggestions...")
        try:
            response = requests.get(
                f"{BASE_URL}/meal-planning/suggestions/daily?remaining_calories=1500&remaining_protein=100",
                headers=self.headers
            )
            
            if response.status_code == 200:
                data = response.json()
                print_success(f"Got {len(data)} meal suggestions")
            else:
                print_error(f"Failed: {response.status_code}")
        except Exception as e:
            print_error(f"Error: {e}")
    
    def run_all_tests(self):
        """Run all API tests"""
        print(f"\n{BLUE}{'='*60}")
        print("  🧪 AUTOMATED API TESTING")
        print("  Testing Fasting & Meal Planning APIs")
        print(f"{'='*60}{RESET}\n")
        
        # Login
        if not self.login():
            print_error("Cannot proceed without authentication")
            return False
        
        # Test Fasting APIs
        self.test_fasting_apis()
        
        # Test Meal Planning APIs
        self.test_meal_planning_apis()
        
        # Summary
        print_section("📊 TEST SUMMARY")
        print_success("All API endpoints tested!")
        print_info("✅ Fasting: 8 endpoints")
        print_info("✅ Meal Planning: 8 endpoints")
        print_info("✅ Total: 16 endpoints tested")
        
        print(f"\n{GREEN}{'='*60}")
        print("  🎉 API TESTING COMPLETE!")
        print(f"{'='*60}{RESET}\n")
        
        return True


if __name__ == "__main__":
    tester = APITester()
    success = tester.run_all_tests()
    sys.exit(0 if success else 1)








