#!/usr/bin/env python3
"""
7-Day Diet Simulation with 100 User Personas
Tests chat history, clarification, accuracy, and data persistence
"""

import sys
import os
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

import json
import random
from datetime import datetime, timedelta
from typing import List, Dict
import requests
from dotenv import load_dotenv
from tests.firebase_test_helper import create_test_user_with_token

load_dotenv()
load_dotenv('.env.local', override=True)

# API Base URL
API_BASE = "http://localhost:8000"

class UserPersona:
    """Represents a user with specific goals and diet patterns"""
    
    def __init__(self, user_id: int, goal: str, age: int, gender: str, weight_kg: float, height_cm: float):
        self.user_id = user_id
        self.goal = goal  # lose_weight, gain_muscle, maintain, improve_fitness
        self.age = age
        self.gender = gender
        self.weight_kg = weight_kg
        self.height_cm = height_cm
        self.chat_history = []
        self.logged_meals = []
        self.total_calories = 0
        self.daily_calories = {}
        self.auth_token = None
        self.email = f"testuser{user_id}@simulation.test"
        self.password = "TestPass123!"
        
    def __repr__(self):
        return f"User{self.user_id}({self.goal}, {self.age}y, {self.gender}, {self.weight_kg}kg)"

class DietSimulator:
    """Simulates 7 days of diet logging for multiple users"""
    
    def __init__(self):
        self.users = []
        self.test_results = []
        self.errors = []
        
    def generate_personas(self, count: int = 100):
        """Generate diverse user personas"""
        goals = ['lose_weight', 'gain_muscle', 'maintain', 'improve_fitness']
        genders = ['male', 'female']
        
        for i in range(count):
            goal = random.choice(goals)
            gender = random.choice(genders)
            age = random.randint(18, 65)
            
            # Weight based on goal
            if goal == 'lose_weight':
                weight = random.uniform(75, 120)  # Overweight
            elif goal == 'gain_muscle':
                weight = random.uniform(55, 75)   # Lean
            else:
                weight = random.uniform(60, 85)   # Normal
            
            height = random.uniform(150, 190) if gender == 'male' else random.uniform(145, 175)
            
            user = UserPersona(i+1, goal, age, gender, weight, height)
            self.users.append(user)
        
        print(f"✅ Generated {count} user personas")
        return self.users
    
    def get_meal_pattern(self, user: UserPersona, day: int, meal_type: str) -> List[str]:
        """Generate realistic meal inputs based on user goal"""
        
        # Meal patterns by goal
        patterns = {
            'lose_weight': {
                'breakfast': [
                    'eggs',
                    '2 eggs',
                    'egg whites',
                    'oatmeal',
                    'greek yogurt',
                    'avocado toast'
                ],
                'lunch': [
                    'chicken salad',
                    'grilled chicken with vegetables',
                    'tuna salad',
                    'quinoa bowl',
                    'tofu stir fry'
                ],
                'snack': [
                    'apple',
                    'almonds',
                    'protein shake',
                    'carrots with hummus',
                    'greek yogurt'
                ],
                'dinner': [
                    'grilled fish with asparagus',
                    'chicken breast with broccoli',
                    'salmon with vegetables',
                    'turkey with green beans'
                ]
            },
            'gain_muscle': {
                'breakfast': [
                    '4 eggs with toast',
                    '3 eggs and oatmeal',
                    'protein pancakes',
                    'egg sandwich with cheese'
                ],
                'lunch': [
                    'chicken breast with rice',
                    'beef with sweet potato',
                    'salmon with quinoa',
                    'turkey with pasta'
                ],
                'snack': [
                    'protein shake',
                    'peanut butter sandwich',
                    'protein bar',
                    'banana with peanut butter'
                ],
                'dinner': [
                    'steak with potatoes',
                    'chicken with rice and beans',
                    'fish with pasta',
                    'lamb with vegetables'
                ]
            },
            'maintain': {
                'breakfast': [
                    '2 eggs with toast',
                    'oatmeal with fruits',
                    'yogurt with granola'
                ],
                'lunch': [
                    'chicken sandwich',
                    'pasta with vegetables',
                    'rice bowl with chicken'
                ],
                'snack': [
                    'fruits',
                    'nuts',
                    'protein bar'
                ],
                'dinner': [
                    'chicken with rice',
                    'fish with vegetables',
                    'pasta with sauce'
                ]
            },
            'improve_fitness': {
                'breakfast': [
                    '2 eggs and avocado',
                    'smoothie bowl',
                    'protein oatmeal'
                ],
                'lunch': [
                    'chicken wrap',
                    'salmon salad',
                    'quinoa bowl'
                ],
                'snack': [
                    'protein shake',
                    'energy balls',
                    'trail mix'
                ],
                'dinner': [
                    'grilled chicken with vegetables',
                    'fish with quinoa',
                    'tofu stir fry'
                ]
            }
        }
        
        goal_patterns = patterns.get(user.goal, patterns['maintain'])
        meal_options = goal_patterns.get(meal_type, ['eggs'])
        
        return random.sample(meal_options, min(2, len(meal_options)))
    
    def authenticate_user(self, user: UserPersona) -> bool:
        """Authenticate user using Firebase Admin SDK"""
        try:
            # Create user with Firebase Admin SDK and get custom token
            user_data = create_test_user_with_token(
                email=user.email,
                password=user.password,
                display_name=f"Test User {user.user_id}"
            )
            
            # Use the ID token for API calls
            user.auth_token = user_data['id_token']
            return True
            
        except Exception as e:
            print(f"❌ Auth error for {user.email}: {e}")
            return False
    
    def test_chat_interaction(self, user: UserPersona, input_text: str, day: int, meal_type: str) -> Dict:
        """Test a single chat interaction"""
        
        test_case = {
            'user': str(user),
            'day': day,
            'meal_type': meal_type,
            'input': input_text,
            'timestamp': datetime.now().isoformat(),
            'expected': {},
            'actual': {},
            'passed': False,
            'errors': []
        }
        
        # Ensure user is authenticated
        if not user.auth_token:
            if not self.authenticate_user(user):
                test_case['errors'].append("Failed to authenticate user")
                return test_case
        
        try:
            # Send to chat endpoint with auth
            headers = {"Authorization": f"Bearer {user.auth_token}"}
            response = requests.post(
                f"{API_BASE}/chat",
                json={"user_input": input_text},
                headers=headers,
                timeout=10
            )
            
            if response.status_code != 200:
                test_case['errors'].append(f"HTTP {response.status_code}: {response.text}")
                return test_case
            
            result = response.json()
            test_case['actual'] = result
            
            # Check response structure
            if 'items' not in result:
                test_case['errors'].append("Missing 'items' in response")
            
            if 'message' not in result:
                test_case['errors'].append("Missing 'message' in response")
            
            # Check if clarification is needed
            needs_clarification = result.get('needs_clarification', False)
            clarification_question = result.get('clarification_question')
            
            if needs_clarification:
                test_case['expected']['needs_clarification'] = True
                test_case['expected']['has_question'] = True
                
                # Validate clarification
                if not clarification_question:
                    test_case['errors'].append("Clarification needed but no question provided")
                else:
                    # Store in chat history
                    user.chat_history.append({
                        'role': 'user',
                        'content': input_text,
                        'timestamp': datetime.now().isoformat()
                    })
                    user.chat_history.append({
                        'role': 'assistant',
                        'content': clarification_question,
                        'timestamp': datetime.now().isoformat()
                    })
            else:
                # Check logged items
                items = result.get('items', [])
                if items:
                    for item in items:
                        if item.get('category') == 'meal':
                            calories = item.get('data', {}).get('calories', 0)
                            test_case['expected']['calories'] = f"> 0"
                            test_case['actual']['calories'] = calories
                            
                            # Validate calories
                            if calories <= 0:
                                test_case['errors'].append(f"Invalid calories: {calories}")
                            
                            # Store in user's log
                            user.logged_meals.append({
                                'day': day,
                                'meal_type': meal_type,
                                'input': input_text,
                                'calories': calories,
                                'data': item.get('data', {})
                            })
                            user.total_calories += calories
                            
                            # Track daily calories
                            if day not in user.daily_calories:
                                user.daily_calories[day] = 0
                            user.daily_calories[day] += calories
                
                # Store in chat history
                user.chat_history.append({
                    'role': 'user',
                    'content': input_text,
                    'timestamp': datetime.now().isoformat()
                })
                user.chat_history.append({
                    'role': 'assistant',
                    'content': result.get('message', ''),
                    'timestamp': datetime.now().isoformat()
                })
            
            # Test passed if no errors
            test_case['passed'] = len(test_case['errors']) == 0
            
        except requests.exceptions.Timeout:
            test_case['errors'].append("Request timeout")
        except requests.exceptions.ConnectionError:
            test_case['errors'].append("Connection error - is backend running?")
        except Exception as e:
            test_case['errors'].append(f"Exception: {str(e)}")
        
        return test_case
    
    def simulate_7_days(self, user: UserPersona) -> List[Dict]:
        """Simulate 7 days of diet logging for one user"""
        
        results = []
        
        for day in range(1, 8):
            # Breakfast
            breakfast_inputs = self.get_meal_pattern(user, day, 'breakfast')
            for input_text in breakfast_inputs:
                result = self.test_chat_interaction(user, input_text, day, 'breakfast')
                results.append(result)
            
            # Lunch
            lunch_inputs = self.get_meal_pattern(user, day, 'lunch')
            for input_text in lunch_inputs:
                result = self.test_chat_interaction(user, input_text, day, 'lunch')
                results.append(result)
            
            # Snack
            if random.random() > 0.3:  # 70% chance of snack
                snack_inputs = self.get_meal_pattern(user, day, 'snack')
                for input_text in snack_inputs[:1]:  # Just one snack
                    result = self.test_chat_interaction(user, input_text, day, 'snack')
                    results.append(result)
            
            # Dinner
            dinner_inputs = self.get_meal_pattern(user, day, 'dinner')
            for input_text in dinner_inputs:
                result = self.test_chat_interaction(user, input_text, day, 'dinner')
                results.append(result)
        
        return results
    
    def run_full_simulation(self, num_users: int = 100):
        """Run 7-day simulation for all users"""
        
        print(f"\n{'='*80}")
        print(f"🚀 STARTING 7-DAY SIMULATION FOR {num_users} USERS")
        print(f"{'='*80}\n")
        
        # Generate personas
        self.generate_personas(num_users)
        
        # Run simulation for each user
        for i, user in enumerate(self.users, 1):
            print(f"\n📊 User {i}/{num_users}: {user}")
            results = self.simulate_7_days(user)
            self.test_results.extend(results)
            
            # Summary for this user
            passed = sum(1 for r in results if r['passed'])
            failed = len(results) - passed
            print(f"  ✅ Passed: {passed}/{len(results)}")
            print(f"  ❌ Failed: {failed}/{len(results)}")
            print(f"  🍽️  Total meals logged: {len(user.logged_meals)}")
            print(f"  🔥 Total calories: {user.total_calories:.0f} kcal")
            print(f"  💬 Chat history: {len(user.chat_history)} messages")
        
        # Generate report
        self.generate_report()
    
    def generate_report(self):
        """Generate comprehensive test report"""
        
        total_tests = len(self.test_results)
        passed = sum(1 for r in self.test_results if r['passed'])
        failed = total_tests - passed
        
        print(f"\n{'='*80}")
        print(f"📊 SIMULATION REPORT")
        print(f"{'='*80}\n")
        
        print(f"Total Users: {len(self.users)}")
        print(f"Total Tests: {total_tests}")
        print(f"✅ Passed: {passed} ({passed/total_tests*100:.1f}%)")
        print(f"❌ Failed: {failed} ({failed/total_tests*100:.1f}%)")
        
        # Error analysis
        if failed > 0:
            print(f"\n🐛 ERROR ANALYSIS:")
            error_types = {}
            for result in self.test_results:
                if not result['passed']:
                    for error in result['errors']:
                        error_types[error] = error_types.get(error, 0) + 1
            
            for error, count in sorted(error_types.items(), key=lambda x: x[1], reverse=True):
                print(f"  - {error}: {count} occurrences")
        
        # User statistics
        print(f"\n📈 USER STATISTICS:")
        for goal in ['lose_weight', 'gain_muscle', 'maintain', 'improve_fitness']:
            goal_users = [u for u in self.users if u.goal == goal]
            if goal_users:
                avg_calories = sum(u.total_calories for u in goal_users) / len(goal_users)
                avg_meals = sum(len(u.logged_meals) for u in goal_users) / len(goal_users)
                print(f"  {goal}: {len(goal_users)} users, avg {avg_calories:.0f} kcal/week, {avg_meals:.0f} meals")
        
        # Save detailed report
        report_file = "tests/simulation_report.json"
        with open(report_file, 'w') as f:
            json.dump({
                'summary': {
                    'total_users': len(self.users),
                    'total_tests': total_tests,
                    'passed': passed,
                    'failed': failed,
                    'pass_rate': passed/total_tests*100
                },
                'users': [
                    {
                        'user_id': u.user_id,
                        'goal': u.goal,
                        'total_calories': u.total_calories,
                        'daily_calories': u.daily_calories,
                        'meals_logged': len(u.logged_meals),
                        'chat_messages': len(u.chat_history)
                    }
                    for u in self.users
                ],
                'test_results': self.test_results
            }, f, indent=2)
        
        print(f"\n💾 Detailed report saved to: {report_file}")
        print(f"\n{'='*80}\n")


if __name__ == "__main__":
    simulator = DietSimulator()
    
    # Run simulation
    # Start with 10 users for testing, then scale to 100
    num_users = 10  # Change to 100 for full simulation
    
    simulator.run_full_simulation(num_users)

