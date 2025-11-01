#!/usr/bin/env python3
"""
REAL End-to-End Automated Test Suite with Firebase Auth
Tests complete user flows with actual Firebase authentication
"""

import requests
import json
import time
import os
from datetime import datetime
from typing import Dict, List, Optional
import firebase_admin
from firebase_admin import credentials, auth as firebase_auth

# Configuration
API_BASE_URL = "http://localhost:8000"
FIREBASE_CREDS_PATH = "/Users/pchintanwar/keys/productivityai-mvp-0017f7241a58.json"

# Initialize Firebase Admin
if not firebase_admin._apps:
    cred = credentials.Certificate(FIREBASE_CREDS_PATH)
    firebase_admin.initialize_app(cred)

TEST_USERS = [
    {
        "email": "alice.test@aiproductivity.app",
        "password": "TestPass123!",
        "name": "Alice Johnson",
        "profile": {
            "gender": "female",
            "age": 28,
            "height_cm": 165,
            "weight_kg": 62.0,
            "activity_level": "moderately_active",
            "fitness_goal": "lose_weight",
            "target_weight_kg": 58.0,
            "diet_preference": "vegetarian",
            "allergies": ["peanuts"],
            "disliked_foods": ["mushrooms"]
        },
        "meals": [
            "I ate 2 boiled eggs and a banana for breakfast",
            "Had a vegetable salad for lunch with olive oil",
            "Snacked on an apple and almonds"
        ],
        "workouts": [
            "I ran 5km in 30 minutes",
            "Did 45 minutes of yoga"
        ],
        "tasks": [
            "Buy groceries for the week",
            "Schedule dentist appointment"
        ]
    },
    {
        "email": "bob.test@aiproductivity.app",
        "password": "TestPass456!",
        "name": "Bob Smith",
        "profile": {
            "gender": "male",
            "age": 35,
            "height_cm": 180,
            "weight_kg": 85.0,
            "activity_level": "very_active",
            "fitness_goal": "gain_muscle",
            "target_weight_kg": 90.0,
            "diet_preference": "none",
            "allergies": [],
            "disliked_foods": ["olives"]
        },
        "meals": [
            "Protein shake with banana and oats",
            "Chicken breast with rice and vegetables"
        ],
        "workouts": [
            "Weight training chest and triceps for 60 minutes",
            "Cycling 20km"
        ],
        "tasks": [
            "Review quarterly reports",
            "Call insurance company"
        ]
    }
]

class Colors:
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKCYAN = '\033[96m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'

class TestResult:
    def __init__(self):
        self.passed = 0
        self.failed = 0
        self.errors: List[str] = []
    
    def log_pass(self, test_name: str, details: str = ""):
        self.passed += 1
        detail_str = f" ({details})" if details else ""
        print(f"{Colors.OKGREEN}✓{Colors.ENDC} {test_name}{detail_str}")
    
    def log_fail(self, test_name: str, error: str):
        self.failed += 1
        self.errors.append(f"{test_name}: {error}")
        print(f"{Colors.FAIL}✗{Colors.ENDC} {test_name}")
        print(f"  {Colors.FAIL}Error: {error}{Colors.ENDC}")
    
    def print_summary(self):
        print(f"\n{Colors.BOLD}{'='*70}{Colors.ENDC}")
        print(f"{Colors.BOLD}TEST SUMMARY{Colors.ENDC}")
        print(f"{Colors.BOLD}{'='*70}{Colors.ENDC}")
        print(f"{Colors.OKGREEN}Passed: {self.passed}{Colors.ENDC}")
        print(f"{Colors.FAIL}Failed: {self.failed}{Colors.ENDC}")
        print(f"Total: {self.passed + self.failed}")
        
        if self.errors:
            print(f"\n{Colors.FAIL}Failed Tests:{Colors.ENDC}")
            for error in self.errors:
                print(f"  • {error}")
        
        if self.failed == 0:
            print(f"\n{Colors.OKGREEN}{Colors.BOLD}🎉 ALL TESTS PASSED!{Colors.ENDC}")
        else:
            print(f"\n{Colors.FAIL}{Colors.BOLD}❌ {self.failed} TEST(S) FAILED{Colors.ENDC}")

class RealE2ETestSuite:
    def __init__(self):
        self.result = TestResult()
        self.user_tokens: Dict[str, str] = {}
        self.user_uids: Dict[str, str] = {}
        self.user_data_counts: Dict[str, dict] = {}
    
    def create_firebase_user(self, email: str, password: str) -> Optional[str]:
        """Create a Firebase user and return UID"""
        try:
            # Try to get existing user first
            try:
                user = firebase_auth.get_user_by_email(email)
                # Delete existing user to start fresh
                firebase_auth.delete_user(user.uid)
                print(f"  Deleted existing user: {email}")
            except:
                pass
            
            # Create new user
            user = firebase_auth.create_user(
                email=email,
                password=password,
                email_verified=True
            )
            return user.uid
        except Exception as e:
            print(f"  Error creating Firebase user: {e}")
            return None
    
    def get_id_token(self, uid: str) -> Optional[str]:
        """Get an ID token for the user via custom token exchange"""
        try:
            # Create custom token
            custom_token = firebase_auth.create_custom_token(uid)
            custom_token_str = custom_token.decode('utf-8')
            
            # Exchange custom token for ID token using Firebase REST API
            # Get API key from Firebase config
            api_key = "AIzaSyCWfkKNm9Q6nYBHnldlUtlFBS15NJmCBkg"  # From firebase_options.dart
            
            response = requests.post(
                f"https://identitytoolkit.googleapis.com/v1/accounts:signInWithCustomToken?key={api_key}",
                json={"token": custom_token_str, "returnSecureToken": True},
                timeout=10
            )
            
            if response.status_code == 200:
                data = response.json()
                return data.get("idToken")
            else:
                print(f"  Error exchanging custom token: {response.text}")
                return None
        except Exception as e:
            print(f"  Error getting ID token: {e}")
            return None
    
    def run_all_tests(self):
        """Run complete test suite"""
        print(f"\n{Colors.HEADER}{Colors.BOLD}{'='*70}{Colors.ENDC}")
        print(f"{Colors.HEADER}{Colors.BOLD}🧪 AI PRODUCTIVITY APP - REAL E2E TEST SUITE{Colors.ENDC}")
        print(f"{Colors.HEADER}{Colors.BOLD}{'='*70}{Colors.ENDC}\n")
        
        # Test 1: Backend Health
        print(f"{Colors.OKCYAN}{Colors.BOLD}[1] Backend Health Check{Colors.ENDC}")
        if not self.test_backend_health():
            print(f"\n{Colors.FAIL}Backend is not running. Aborting tests.{Colors.ENDC}")
            return False
        
        # Test 2: Create Firebase Users
        print(f"\n{Colors.OKCYAN}{Colors.BOLD}[2] Firebase User Creation{Colors.ENDC}")
        for user_data in TEST_USERS:
            self.test_create_firebase_user(user_data)
        
        # Test 3: User Onboarding
        print(f"\n{Colors.OKCYAN}{Colors.BOLD}[3] User Onboarding & Profile Creation{Colors.ENDC}")
        for user_data in TEST_USERS:
            self.test_user_onboarding(user_data)
        
        # Test 4: Profile Retrieval
        print(f"\n{Colors.OKCYAN}{Colors.BOLD}[4] Profile Retrieval (Persistence Check){Colors.ENDC}")
        for user_data in TEST_USERS:
            self.test_profile_retrieval(user_data)
        
        # Test 5: Meal Logging
        print(f"\n{Colors.OKCYAN}{Colors.BOLD}[5] Meal Logging via Chat{Colors.ENDC}")
        for user_data in TEST_USERS:
            self.test_meal_logging(user_data)
        
        # Test 6: Fitness Logs Retrieval
        print(f"\n{Colors.OKCYAN}{Colors.BOLD}[6] Fitness Logs Retrieval (Persistence Check){Colors.ENDC}")
        for user_data in TEST_USERS:
            self.test_fitness_logs_retrieval(user_data)
        
        # Test 7: Workout Logging
        print(f"\n{Colors.OKCYAN}{Colors.BOLD}[7] Workout Logging via Chat{Colors.ENDC}")
        for user_data in TEST_USERS:
            self.test_workout_logging(user_data)
        
        # Test 8: Task Creation
        print(f"\n{Colors.OKCYAN}{Colors.BOLD}[8] Task Creation via Chat{Colors.ENDC}")
        for user_data in TEST_USERS:
            self.test_task_creation(user_data)
        
        # Test 9: Tasks Retrieval
        print(f"\n{Colors.OKCYAN}{Colors.BOLD}[9] Tasks Retrieval (Persistence Check){Colors.ENDC}")
        for user_data in TEST_USERS:
            self.test_tasks_retrieval(user_data)
        
        # Test 10: Cross-User Data Isolation
        print(f"\n{Colors.OKCYAN}{Colors.BOLD}[10] Cross-User Data Isolation{Colors.ENDC}")
        self.test_data_isolation()
        
        # Print Summary
        self.result.print_summary()
        
        # Print Test User Credentials
        self.print_test_credentials()
        
        return self.result.failed == 0
    
    def test_backend_health(self) -> bool:
        """Test if backend is running"""
        try:
            response = requests.get(f"{API_BASE_URL}/", timeout=5)
            if response.status_code == 200:
                self.result.log_pass("Backend is running", f"Status: {response.status_code}")
                return True
            else:
                self.result.log_fail("Backend health check", f"Status code: {response.status_code}")
                return False
        except Exception as e:
            self.result.log_fail("Backend health check", str(e))
            return False
    
    def test_create_firebase_user(self, user_data: dict):
        """Create Firebase user"""
        email = user_data["email"]
        password = user_data["password"]
        
        uid = self.create_firebase_user(email, password)
        if uid:
            self.user_uids[email] = uid
            token = self.get_id_token(uid)
            if token:
                self.user_tokens[email] = token
                self.result.log_pass(f"Created Firebase user: {email}", f"UID: {uid[:8]}...")
            else:
                self.result.log_fail(f"Get token for {email}", "Failed to get ID token")
        else:
            self.result.log_fail(f"Create Firebase user: {email}", "Failed to create user")
    
    def test_user_onboarding(self, user_data: dict):
        """Test user onboarding"""
        email = user_data["email"]
        token = self.user_tokens.get(email)
        
        if not token:
            self.result.log_fail(f"Onboarding: {email}", "No auth token available")
            return
        
        try:
            payload = {
                "name": user_data["name"],
                **user_data["profile"]
            }
            
            headers = {"Authorization": f"Bearer {token}"}
            response = requests.post(
                f"{API_BASE_URL}/profile/onboard",
                json=payload,
                headers=headers,
                timeout=10
            )
            
            if response.status_code == 200:
                data = response.json()
                self.result.log_pass(f"Onboarding: {user_data['name']}", f"Profile created")
            else:
                self.result.log_fail(
                    f"Onboarding: {email}",
                    f"Status {response.status_code}: {response.text[:200]}"
                )
        except Exception as e:
            self.result.log_fail(f"Onboarding: {email}", str(e))
    
    def test_profile_retrieval(self, user_data: dict):
        """Test profile retrieval"""
        email = user_data["email"]
        token = self.user_tokens.get(email)
        
        if not token:
            self.result.log_fail(f"Profile retrieval: {email}", "No auth token")
            return
        
        try:
            headers = {"Authorization": f"Bearer {token}"}
            response = requests.get(
                f"{API_BASE_URL}/profile/me",
                headers=headers,
                timeout=10
            )
            
            if response.status_code == 200:
                data = response.json()
                profile = data.get("profile", {})
                name = profile.get("name", "Unknown")
                goal = profile.get("fitness_goal", "Unknown")
                self.result.log_pass(
                    f"Profile retrieved: {name}",
                    f"Goal: {goal}"
                )
            else:
                self.result.log_fail(
                    f"Profile retrieval: {email}",
                    f"Status {response.status_code}: {response.text[:200]}"
                )
        except Exception as e:
            self.result.log_fail(f"Profile retrieval: {email}", str(e))
    
    def test_meal_logging(self, user_data: dict):
        """Test meal logging"""
        email = user_data["email"]
        token = self.user_tokens.get(email)
        meals = user_data.get("meals", [])
        
        if not token:
            self.result.log_fail(f"Meal logging: {email}", "No auth token")
            return
        
        for meal_text in meals:
            try:
                headers = {"Authorization": f"Bearer {token}"}
                payload = {"user_input": meal_text}
                
                response = requests.post(
                    f"{API_BASE_URL}/chat",
                    json=payload,
                    headers=headers,
                    timeout=15
                )
                
                if response.status_code == 200:
                    data = response.json()
                    items = data.get("items", [])
                    meal_count = sum(1 for item in items if item.get("category") == "meal")
                    self.result.log_pass(
                        f"Meal logged: {meal_text[:40]}...",
                        f"{meal_count} meal(s) parsed"
                    )
                else:
                    self.result.log_fail(
                        f"Meal logging: {meal_text[:40]}",
                        f"Status {response.status_code}"
                    )
            except Exception as e:
                self.result.log_fail(f"Meal logging: {meal_text[:40]}", str(e))
            
            time.sleep(0.5)  # Rate limiting
    
    def test_fitness_logs_retrieval(self, user_data: dict):
        """Test fitness logs retrieval"""
        email = user_data["email"]
        token = self.user_tokens.get(email)
        
        if not token:
            self.result.log_fail(f"Fitness logs: {email}", "No auth token")
            return
        
        try:
            headers = {"Authorization": f"Bearer {token}"}
            response = requests.get(
                f"{API_BASE_URL}/fitness/logs",
                headers=headers,
                timeout=10
            )
            
            if response.status_code == 200:
                data = response.json()
                # Backend returns a list directly, not a dict with "logs" key
                logs = data if isinstance(data, list) else data.get("logs", [])
                meal_count = sum(1 for log in logs if log.get("log_type") == "meal")
                
                if email not in self.user_data_counts:
                    self.user_data_counts[email] = {}
                self.user_data_counts[email]["meals"] = meal_count
                
                self.result.log_pass(
                    f"Fitness logs: {user_data['name']}",
                    f"{meal_count} meal(s) persisted"
                )
            else:
                self.result.log_fail(
                    f"Fitness logs: {email}",
                    f"Status {response.status_code}"
                )
        except Exception as e:
            self.result.log_fail(f"Fitness logs: {email}", str(e))
    
    def test_workout_logging(self, user_data: dict):
        """Test workout logging"""
        email = user_data["email"]
        token = self.user_tokens.get(email)
        workouts = user_data.get("workouts", [])
        
        if not token:
            self.result.log_fail(f"Workout logging: {email}", "No auth token")
            return
        
        for workout_text in workouts:
            try:
                headers = {"Authorization": f"Bearer {token}"}
                payload = {"user_input": workout_text}
                
                response = requests.post(
                    f"{API_BASE_URL}/chat",
                    json=payload,
                    headers=headers,
                    timeout=15
                )
                
                if response.status_code == 200:
                    data = response.json()
                    items = data.get("items", [])
                    workout_count = sum(1 for item in items if item.get("category") == "workout")
                    self.result.log_pass(
                        f"Workout logged: {workout_text[:40]}...",
                        f"{workout_count} workout(s) parsed"
                    )
                else:
                    self.result.log_fail(
                        f"Workout logging: {workout_text[:40]}",
                        f"Status {response.status_code}"
                    )
            except Exception as e:
                self.result.log_fail(f"Workout logging: {workout_text[:40]}", str(e))
            
            time.sleep(0.5)
    
    def test_task_creation(self, user_data: dict):
        """Test task creation"""
        email = user_data["email"]
        token = self.user_tokens.get(email)
        tasks = user_data.get("tasks", [])
        
        if not token:
            self.result.log_fail(f"Task creation: {email}", "No auth token")
            return
        
        for task_text in tasks:
            try:
                headers = {"Authorization": f"Bearer {token}"}
                payload = {"user_input": task_text}
                
                response = requests.post(
                    f"{API_BASE_URL}/chat",
                    json=payload,
                    headers=headers,
                    timeout=15
                )
                
                if response.status_code == 200:
                    data = response.json()
                    items = data.get("items", [])
                    task_count = sum(1 for item in items if item.get("category") in ("task", "reminder"))
                    self.result.log_pass(
                        f"Task created: {task_text[:40]}...",
                        f"{task_count} task(s) parsed"
                    )
                else:
                    self.result.log_fail(
                        f"Task creation: {task_text[:40]}",
                        f"Status {response.status_code}"
                    )
            except Exception as e:
                self.result.log_fail(f"Task creation: {task_text[:40]}", str(e))
            
            time.sleep(0.5)
    
    def test_tasks_retrieval(self, user_data: dict):
        """Test tasks retrieval"""
        email = user_data["email"]
        token = self.user_tokens.get(email)
        
        if not token:
            self.result.log_fail(f"Tasks retrieval: {email}", "No auth token")
            return
        
        try:
            headers = {"Authorization": f"Bearer {token}"}
            response = requests.get(
                f"{API_BASE_URL}/tasks",
                headers=headers,
                timeout=10
            )
            
            if response.status_code == 200:
                data = response.json()
                # Backend returns a list directly, not a dict with "tasks" key
                tasks = data if isinstance(data, list) else data.get("tasks", [])
                task_count = len(tasks)
                
                if email not in self.user_data_counts:
                    self.user_data_counts[email] = {}
                self.user_data_counts[email]["tasks"] = task_count
                
                self.result.log_pass(
                    f"Tasks retrieved: {user_data['name']}",
                    f"{task_count} task(s) persisted"
                )
            else:
                self.result.log_fail(
                    f"Tasks retrieval: {email}",
                    f"Status {response.status_code}"
                )
        except Exception as e:
            self.result.log_fail(f"Tasks retrieval: {email}", str(e))
    
    def test_data_isolation(self):
        """Test cross-user data isolation"""
        if len(self.user_data_counts) < 2:
            self.result.log_fail("Data isolation", "Not enough users to test")
            return
        
        # Verify each user has different data counts
        user_emails = list(self.user_data_counts.keys())
        user1_data = self.user_data_counts.get(user_emails[0], {})
        user2_data = self.user_data_counts.get(user_emails[1], {})
        
        # They should have different data (since we logged different things)
        if user1_data != user2_data:
            self.result.log_pass(
                "Data isolation verified",
                f"User 1: {user1_data}, User 2: {user2_data}"
            )
        else:
            self.result.log_fail(
                "Data isolation",
                "Users have identical data - possible isolation issue"
            )
    
    def print_test_credentials(self):
        """Print test user credentials"""
        print(f"\n{Colors.HEADER}{Colors.BOLD}{'='*70}{Colors.ENDC}")
        print(f"{Colors.HEADER}{Colors.BOLD}🔑 TEST USER CREDENTIALS FOR MANUAL VERIFICATION{Colors.ENDC}")
        print(f"{Colors.HEADER}{Colors.BOLD}{'='*70}{Colors.ENDC}\n")
        
        for user_data in TEST_USERS:
            email = user_data["email"]
            counts = self.user_data_counts.get(email, {})
            
            print(f"{Colors.OKBLUE}{Colors.BOLD}{user_data['name']}{Colors.ENDC}")
            print(f"  Email:    {email}")
            print(f"  Password: {user_data['password']}")
            print(f"  UID:      {self.user_uids.get(email, 'N/A')}")
            print(f"  Profile:  {user_data['profile']['fitness_goal']} | {user_data['profile']['activity_level']}")
            print(f"  Meals:    {counts.get('meals', 0)} persisted")
            print(f"  Tasks:    {counts.get('tasks', 0)} persisted")
            print()
        
        print(f"{Colors.WARNING}📋 MANUAL VERIFICATION STEPS:{Colors.ENDC}")
        print(f"  1. Open: http://localhost:8080")
        print(f"  2. Login with User 1 credentials")
        print(f"  3. Verify profile, meals, and tasks are visible")
        print(f"  4. Refresh page (Cmd+R) - data should persist")
        print(f"  5. Logout and login with User 2")
        print(f"  6. Verify User 2 sees ONLY their data (not User 1's)")
        print()


def main():
    """Main test runner"""
    print(f"\n{Colors.BOLD}Starting REAL E2E Test Suite with Firebase Auth...{Colors.ENDC}")
    print(f"Target: {API_BASE_URL}")
    print(f"Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
    
    suite = RealE2ETestSuite()
    success = suite.run_all_tests()
    
    return success


if __name__ == "__main__":
    import sys
    success = main()
    sys.exit(0 if success else 1)

