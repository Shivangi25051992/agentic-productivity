#!/usr/bin/env python3
"""
Comprehensive Automated Feature Tests
Tests all existing and new features to ensure no regressions
"""
import os
import sys
import json
import requests
import time
from datetime import datetime
from test_user_setup import setup_test_user

BACKEND_URL = os.getenv("BACKEND_URL", "http://localhost:8000")

class FeatureTester:
    def __init__(self, test_user):
        self.user = test_user
        self.test_results = []
        self.passed = 0
        self.failed = 0
    
    def test(self, name, func):
        """Run a test and record result"""
        print(f"\n{'='*80}")
        print(f"🧪 TEST: {name}")
        print(f"{'='*80}")
        
        try:
            start = time.time()
            result = func()
            duration = time.time() - start
            
            if result:
                print(f"✅ PASSED ({duration:.2f}s)")
                self.passed += 1
                self.test_results.append({
                    "name": name,
                    "status": "PASSED",
                    "duration": duration
                })
            else:
                print(f"❌ FAILED ({duration:.2f}s)")
                self.failed += 1
                self.test_results.append({
                    "name": name,
                    "status": "FAILED",
                    "duration": duration
                })
            
            return result
        except Exception as e:
            print(f"❌ ERROR: {e}")
            self.failed += 1
            self.test_results.append({
                "name": name,
                "status": "ERROR",
                "error": str(e)
            })
            return False
    
    def chat(self, message):
        """Send chat message"""
        response = requests.post(
            f"{BACKEND_URL}/chat",
            headers={
                "Authorization": f"Bearer {self.user.id_token}",
                "Content-Type": "application/json"
            },
            json={"user_input": message}
        )
        return response
    
    # ========== EXISTING FEATURE TESTS (MUST PASS) ==========
    
    def test_meal_logging(self):
        """Test: Meal logging still works"""
        print("📝 Logging meal: '2 eggs for breakfast'")
        
        response = self.chat("2 eggs for breakfast")
        
        if response.status_code != 200:
            print(f"❌ API returned {response.status_code}")
            return False
        
        data = response.json()
        items = data.get("items", [])
        
        if not items:
            print(f"❌ No items returned")
            return False
        
        meal_item = items[0]
        if meal_item.get("category") != "meal":
            print(f"❌ Category is not 'meal': {meal_item.get('category')}")
            return False
        
        if "calories" not in meal_item.get("data", {}):
            print(f"❌ No calories in response")
            return False
        
        print(f"✅ Meal logged: {meal_item.get('summary')}")
        print(f"   Calories: {meal_item.get('data', {}).get('calories')}")
        print(f"   Meal type: {meal_item.get('data', {}).get('meal_type')}")
        
        return True
    
    def test_workout_logging(self):
        """Test: Workout logging still works"""
        print("📝 Logging workout: 'ran 5km'")
        
        response = self.chat("ran 5km")
        
        if response.status_code != 200:
            print(f"❌ API returned {response.status_code}")
            return False
        
        data = response.json()
        items = data.get("items", [])
        
        if not items:
            print(f"❌ No items returned")
            return False
        
        workout_item = items[0]
        if workout_item.get("category") != "workout":
            print(f"❌ Category is not 'workout': {workout_item.get('category')}")
            return False
        
        print(f"✅ Workout logged: {workout_item.get('summary')}")
        print(f"   Activity: {workout_item.get('data', {}).get('activity_type')}")
        
        return True
    
    def test_task_creation(self):
        """Test: Task creation still works"""
        print("📝 Creating task: 'remind me to call doctor'")
        
        response = self.chat("remind me to call doctor")
        
        if response.status_code != 200:
            print(f"❌ API returned {response.status_code}")
            return False
        
        data = response.json()
        items = data.get("items", [])
        
        if not items:
            print(f"❌ No items returned")
            return False
        
        task_item = items[0]
        if task_item.get("category") not in ["task", "reminder"]:
            print(f"❌ Category is not 'task' or 'reminder': {task_item.get('category')}")
            return False
        
        print(f"✅ Task created: {task_item.get('summary')}")
        
        return True
    
    def test_multi_item_meal(self):
        """Test: Multi-item meal parsing still works"""
        print("📝 Logging multi-item meal: '2 eggs and toast for breakfast'")
        
        response = self.chat("2 eggs and toast for breakfast")
        
        if response.status_code != 200:
            print(f"❌ API returned {response.status_code}")
            return False
        
        data = response.json()
        items = data.get("items", [])
        
        if not items:
            print(f"❌ No items returned")
            return False
        
        # Should have at least one meal item
        meal_items = [i for i in items if i.get("category") == "meal"]
        if not meal_items:
            print(f"❌ No meal items found")
            return False
        
        print(f"✅ Multi-item meal logged: {meal_items[0].get('summary')}")
        
        return True
    
    # ========== NEW FEATURE TESTS ==========
    
    def test_water_logging(self):
        """Test: Water logging works"""
        print("📝 Logging water: 'drank 2 glasses of water'")
        
        response = self.chat("drank 2 glasses of water")
        
        if response.status_code != 200:
            print(f"❌ API returned {response.status_code}")
            return False
        
        data = response.json()
        items = data.get("items", [])
        
        if not items:
            print(f"❌ No items returned")
            return False
        
        water_item = items[0]
        if water_item.get("category") != "water":
            print(f"❌ Category is not 'water': {water_item.get('category')}")
            return False
        
        quantity_ml = water_item.get("data", {}).get("quantity_ml")
        if not quantity_ml:
            print(f"❌ No quantity_ml in response")
            return False
        
        print(f"✅ Water logged: {water_item.get('summary')}")
        print(f"   Quantity: {quantity_ml}ml")
        
        return True
    
    def test_supplement_logging(self):
        """Test: Supplement logging works"""
        print("📝 Logging supplement: 'took multivitamin'")
        
        response = self.chat("took multivitamin")
        
        if response.status_code != 200:
            print(f"❌ API returned {response.status_code}")
            return False
        
        data = response.json()
        items = data.get("items", [])
        
        if not items:
            print(f"❌ No items returned")
            return False
        
        supplement_item = items[0]
        if supplement_item.get("category") != "supplement":
            print(f"❌ Category is not 'supplement': {supplement_item.get('category')}")
            return False
        
        supplement_name = supplement_item.get("data", {}).get("supplement_name")
        if not supplement_name:
            print(f"❌ No supplement_name in response")
            return False
        
        print(f"✅ Supplement logged: {supplement_item.get('summary')}")
        print(f"   Name: {supplement_name}")
        
        return True
    
    def test_mixed_input(self):
        """Test: Mixed input (meal + workout + water + supplement)"""
        print("📝 Logging mixed: '2 eggs, ran 5km, drank water, took vitamin d'")
        
        response = self.chat("2 eggs for breakfast, ran 5km, drank 2 glasses of water, took vitamin d")
        
        if response.status_code != 200:
            print(f"❌ API returned {response.status_code}")
            return False
        
        data = response.json()
        items = data.get("items", [])
        
        if len(items) < 4:
            print(f"❌ Expected 4 items, got {len(items)}")
            return False
        
        categories = [i.get("category") for i in items]
        expected = ["meal", "workout", "water", "supplement"]
        
        for exp in expected:
            if exp not in categories:
                print(f"❌ Missing category: {exp}")
                return False
        
        print(f"✅ Mixed input parsed correctly")
        print(f"   Categories: {categories}")
        
        return True
    
    def test_profile_update(self):
        """Test: Profile update works"""
        print("📝 Updating profile weight to 74.5kg")
        
        response = requests.put(
            f"{BACKEND_URL}/profile/me",
            headers={
                "Authorization": f"Bearer {self.user.id_token}",
                "Content-Type": "application/json"
            },
            json={"weight_kg": 74.5}
        )
        
        if response.status_code != 200:
            print(f"❌ API returned {response.status_code}")
            return False
        
        data = response.json()
        profile = data.get("profile", {})
        
        if profile.get("weight_kg") != 74.5:
            print(f"❌ Weight not updated: {profile.get('weight_kg')}")
            return False
        
        print(f"✅ Profile updated successfully")
        print(f"   New weight: {profile.get('weight_kg')}kg")
        
        return True
    
    def test_timezone_in_profile(self):
        """Test: Timezone stored in profile"""
        print("📝 Checking timezone in profile")
        
        response = requests.get(
            f"{BACKEND_URL}/profile/me",
            headers={"Authorization": f"Bearer {self.user.id_token}"}
        )
        
        if response.status_code != 200:
            print(f"❌ API returned {response.status_code}")
            return False
        
        data = response.json()
        profile = data.get("profile", {})
        timezone = profile.get("timezone")
        
        if not timezone:
            print(f"❌ No timezone in profile")
            return False
        
        print(f"✅ Timezone found in profile: {timezone}")
        
        return True
    
    def generate_report(self):
        """Generate test report"""
        print("\n" + "=" * 80)
        print("📊 TEST REPORT")
        print("=" * 80)
        print(f"Total Tests: {self.passed + self.failed}")
        print(f"✅ Passed: {self.passed}")
        print(f"❌ Failed: {self.failed}")
        print(f"Success Rate: {(self.passed / (self.passed + self.failed) * 100):.1f}%")
        print("=" * 80)
        
        if self.failed > 0:
            print("\n❌ FAILED TESTS:")
            for result in self.test_results:
                if result["status"] in ["FAILED", "ERROR"]:
                    print(f"   - {result['name']}")
        
        # Save report
        report = {
            "timestamp": datetime.now().isoformat(),
            "total": self.passed + self.failed,
            "passed": self.passed,
            "failed": self.failed,
            "success_rate": (self.passed / (self.passed + self.failed) * 100) if (self.passed + self.failed) > 0 else 0,
            "tests": self.test_results
        }
        
        os.makedirs("test_automation/reports", exist_ok=True)
        report_file = f"test_automation/reports/test_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        with open(report_file, "w") as f:
            json.dump(report, f, indent=2)
        
        print(f"\n💾 Report saved: {report_file}")
        
        return self.failed == 0

def run_all_tests():
    """Main test runner"""
    print("=" * 80)
    print("🤖 AUTOMATED FEATURE TESTING")
    print("=" * 80)
    print()
    
    # Setup test user
    test_user = setup_test_user()
    
    # Create tester
    tester = FeatureTester(test_user)
    
    # Run all tests
    print("\n" + "=" * 80)
    print("🚀 RUNNING TESTS")
    print("=" * 80)
    
    # CRITICAL: Test existing features first (MUST PASS)
    tester.test("Meal Logging (CRITICAL)", tester.test_meal_logging)
    tester.test("Workout Logging (CRITICAL)", tester.test_workout_logging)
    tester.test("Task Creation (CRITICAL)", tester.test_task_creation)
    tester.test("Multi-Item Meal (CRITICAL)", tester.test_multi_item_meal)
    tester.test("Profile Update (CRITICAL)", tester.test_profile_update)
    
    # Test new features
    tester.test("Timezone in Profile (NEW)", tester.test_timezone_in_profile)
    tester.test("Water Logging (NEW)", tester.test_water_logging)
    tester.test("Supplement Logging (NEW)", tester.test_supplement_logging)
    tester.test("Mixed Input (NEW)", tester.test_mixed_input)
    
    # Generate report
    success = tester.generate_report()
    
    if success:
        print("\n✅ ALL TESTS PASSED - SAFE TO DEPLOY")
        sys.exit(0)
    else:
        print("\n❌ SOME TESTS FAILED - DO NOT DEPLOY")
        sys.exit(1)

if __name__ == "__main__":
    run_all_tests()

