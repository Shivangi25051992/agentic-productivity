#!/usr/bin/env python3
"""
Automated Test Suite for P0 Bug Fixes
Tests system prompt changes to ensure no regression in existing functionality
"""

import os
import sys
import json
import requests
from typing import Dict, Any, List
from datetime import datetime

# Configuration
BACKEND_URL = os.getenv("BACKEND_URL", "https://aiproductivity-backend-rhwrraai2a-uc.a.run.app")
TEST_USER_EMAIL = "shivganga25shingatwar@gmail.com"
TEST_USER_PASSWORD = "Test@1234"

class Colors:
    GREEN = '\033[92m'
    RED = '\033[91m'
    YELLOW = '\033[93m'
    BLUE = '\033[94m'
    RESET = '\033[0m'
    BOLD = '\033[1m'

def print_header(text: str):
    print(f"\n{Colors.BOLD}{Colors.BLUE}{'='*80}{Colors.RESET}")
    print(f"{Colors.BOLD}{Colors.BLUE}{text.center(80)}{Colors.RESET}")
    print(f"{Colors.BOLD}{Colors.BLUE}{'='*80}{Colors.RESET}\n")

def print_test(test_name: str):
    print(f"\n{Colors.BOLD}🧪 Test: {test_name}{Colors.RESET}")

def print_pass(message: str):
    print(f"  {Colors.GREEN}✅ PASS:{Colors.RESET} {message}")

def print_fail(message: str):
    print(f"  {Colors.RED}❌ FAIL:{Colors.RESET} {message}")

def print_warning(message: str):
    print(f"  {Colors.YELLOW}⚠️  WARNING:{Colors.RESET} {message}")

def print_info(message: str):
    print(f"  {Colors.BLUE}ℹ️  INFO:{Colors.RESET} {message}")

# Global test results
test_results = {
    "total": 0,
    "passed": 0,
    "failed": 0,
    "warnings": 0
}

def login() -> str:
    """Login and get auth token"""
    print_info("Logging in...")
    try:
        response = requests.post(
            f"{BACKEND_URL}/auth/login",
            json={"email": TEST_USER_EMAIL, "password": TEST_USER_PASSWORD},
            timeout=10
        )
        if response.status_code == 200:
            token = response.json().get("idToken")
            print_pass(f"Logged in successfully")
            return token
        else:
            print_fail(f"Login failed: {response.status_code}")
            sys.exit(1)
    except Exception as e:
        print_fail(f"Login error: {e}")
        sys.exit(1)

def test_basic_meal_logging(token: str) -> bool:
    """Test: Basic meal logging still works"""
    print_test("Basic Meal Logging - '2 eggs for breakfast'")
    test_results["total"] += 1
    
    try:
        response = requests.post(
            f"{BACKEND_URL}/chat",
            headers={"Authorization": f"Bearer {token}"},
            json={"message": "2 eggs for breakfast"},
            timeout=30
        )
        
        if response.status_code != 200:
            print_fail(f"API returned {response.status_code}")
            test_results["failed"] += 1
            return False
        
        data = response.json()
        
        # Check response structure
        if "response" not in data:
            print_fail("No 'response' field in API response")
            test_results["failed"] += 1
            return False
        
        print_info(f"AI Response: {data['response'][:100]}...")
        
        # Check if meal was logged
        if "items" in data and len(data["items"]) > 0:
            item = data["items"][0]
            print_pass(f"Meal logged: {item.get('summary', 'N/A')}")
            
            # Verify category
            if item.get("category") == "meal":
                print_pass("Category: meal ✓")
            else:
                print_fail(f"Category: {item.get('category')} (expected 'meal')")
                test_results["failed"] += 1
                return False
            
            # Verify meal_type
            meal_type = item.get("data", {}).get("meal_type")
            if meal_type == "breakfast":
                print_pass("Meal type: breakfast ✓")
            else:
                print_fail(f"Meal type: {meal_type} (expected 'breakfast')")
                test_results["failed"] += 1
                return False
            
            # Verify macros exist
            macros = item.get("data", {})
            if all(k in macros for k in ["calories", "protein_g", "carbs_g", "fat_g"]):
                print_pass(f"Macros: {macros['calories']}cal, {macros['protein_g']}g protein ✓")
            else:
                print_fail("Missing macro data")
                test_results["failed"] += 1
                return False
            
            test_results["passed"] += 1
            return True
        else:
            print_fail("No items logged")
            test_results["failed"] += 1
            return False
            
    except Exception as e:
        print_fail(f"Exception: {e}")
        test_results["failed"] += 1
        return False

def test_multiline_logging(token: str) -> bool:
    """Test: Multi-line meal logging"""
    print_test("Multi-line Logging - '2 eggs\\ntoast\\ncoffee'")
    test_results["total"] += 1
    
    try:
        response = requests.post(
            f"{BACKEND_URL}/chat",
            headers={"Authorization": f"Bearer {token}"},
            json={"message": "2 eggs\ntoast\ncoffee"},
            timeout=30
        )
        
        if response.status_code != 200:
            print_fail(f"API returned {response.status_code}")
            test_results["failed"] += 1
            return False
        
        data = response.json()
        
        if "items" in data and len(data["items"]) >= 3:
            print_pass(f"Logged {len(data['items'])} items ✓")
            for item in data["items"]:
                print_info(f"  - {item.get('summary', 'N/A')}")
            test_results["passed"] += 1
            return True
        else:
            print_fail(f"Expected 3 items, got {len(data.get('items', []))}")
            test_results["failed"] += 1
            return False
            
    except Exception as e:
        print_fail(f"Exception: {e}")
        test_results["failed"] += 1
        return False

def test_typo_handling(token: str) -> bool:
    """Test: Typo correction still works"""
    print_test("Typo Handling - 'omlet and banan'")
    test_results["total"] += 1
    
    try:
        response = requests.post(
            f"{BACKEND_URL}/chat",
            headers={"Authorization": f"Bearer {token}"},
            json={"message": "omlet and banan"},
            timeout=30
        )
        
        if response.status_code != 200:
            print_fail(f"API returned {response.status_code}")
            test_results["failed"] += 1
            return False
        
        data = response.json()
        response_text = data.get("response", "").lower()
        
        # Check if AI corrected typos
        if "omelet" in response_text or "omelette" in response_text:
            print_pass("Typo 'omlet' → 'omelet' corrected ✓")
        else:
            print_warning("Typo correction may not have worked")
            test_results["warnings"] += 1
        
        if "banana" in response_text:
            print_pass("Typo 'banan' → 'banana' corrected ✓")
        else:
            print_warning("Typo correction may not have worked")
            test_results["warnings"] += 1
        
        if "items" in data and len(data["items"]) > 0:
            print_pass(f"Items logged: {len(data['items'])} ✓")
            test_results["passed"] += 1
            return True
        else:
            print_fail("No items logged")
            test_results["failed"] += 1
            return False
            
    except Exception as e:
        print_fail(f"Exception: {e}")
        test_results["failed"] += 1
        return False

def test_explicit_meal_type(token: str) -> bool:
    """Test: Explicit meal type is respected"""
    print_test("Explicit Meal Type - '2 eggs for lunch' (should be lunch, not breakfast)")
    test_results["total"] += 1
    
    try:
        response = requests.post(
            f"{BACKEND_URL}/chat",
            headers={"Authorization": f"Bearer {token}"},
            json={"message": "2 eggs for lunch"},
            timeout=30
        )
        
        if response.status_code != 200:
            print_fail(f"API returned {response.status_code}")
            test_results["failed"] += 1
            return False
        
        data = response.json()
        
        if "items" in data and len(data["items"]) > 0:
            meal_type = data["items"][0].get("data", {}).get("meal_type")
            if meal_type == "lunch":
                print_pass("Meal type: lunch ✓ (explicit user input respected)")
                test_results["passed"] += 1
                return True
            else:
                print_fail(f"Meal type: {meal_type} (expected 'lunch')")
                print_fail("AI is NOT respecting explicit user input!")
                test_results["failed"] += 1
                return False
        else:
            print_fail("No items logged")
            test_results["failed"] += 1
            return False
            
    except Exception as e:
        print_fail(f"Exception: {e}")
        test_results["failed"] += 1
        return False

def test_unsupported_feature_diet_plan(token: str) -> bool:
    """Test: AI rejects unsupported feature (diet plan) gracefully"""
    print_test("Unsupported Feature - 'create a diet plan for me'")
    test_results["total"] += 1
    
    try:
        response = requests.post(
            f"{BACKEND_URL}/chat",
            headers={"Authorization": f"Bearer {token}"},
            json={"message": "create a diet plan for me"},
            timeout=30
        )
        
        if response.status_code != 200:
            print_fail(f"API returned {response.status_code}")
            test_results["failed"] += 1
            return False
        
        data = response.json()
        response_text = data.get("response", "").lower()
        
        # Check if AI responds with friendly message
        if "coming soon" in response_text or "not support" in response_text or "right now" in response_text:
            print_pass("AI correctly identifies unsupported feature ✓")
            print_info(f"Response: {data.get('response', '')[:150]}...")
            
            # Verify no items were logged
            if not data.get("items") or len(data.get("items", [])) == 0:
                print_pass("No items logged (correct behavior) ✓")
                test_results["passed"] += 1
                return True
            else:
                print_warning(f"Items logged: {len(data.get('items', []))} (unexpected)")
                test_results["warnings"] += 1
                test_results["passed"] += 1
                return True
        else:
            print_fail("AI may be hallucinating unsupported feature")
            print_info(f"Response: {data.get('response', '')[:150]}...")
            test_results["failed"] += 1
            return False
            
    except Exception as e:
        print_fail(f"Exception: {e}")
        test_results["failed"] += 1
        return False

def test_unsupported_feature_meal_suggestions(token: str) -> bool:
    """Test: AI rejects unsupported feature (meal suggestions) gracefully"""
    print_test("Unsupported Feature - 'suggest meals for today'")
    test_results["total"] += 1
    
    try:
        response = requests.post(
            f"{BACKEND_URL}/chat",
            headers={"Authorization": f"Bearer {token}"},
            json={"message": "suggest meals for today"},
            timeout=30
        )
        
        if response.status_code != 200:
            print_fail(f"API returned {response.status_code}")
            test_results["failed"] += 1
            return False
        
        data = response.json()
        response_text = data.get("response", "").lower()
        
        if "coming soon" in response_text or "not support" in response_text or "right now" in response_text:
            print_pass("AI correctly identifies unsupported feature ✓")
            print_info(f"Response: {data.get('response', '')[:150]}...")
            test_results["passed"] += 1
            return True
        else:
            print_fail("AI may be hallucinating unsupported feature")
            print_info(f"Response: {data.get('response', '')[:150]}...")
            test_results["failed"] += 1
            return False
            
    except Exception as e:
        print_fail(f"Exception: {e}")
        test_results["failed"] += 1
        return False

def test_json_parsing(token: str) -> bool:
    """Test: AI still returns valid JSON structure"""
    print_test("JSON Parsing - Verify response structure")
    test_results["total"] += 1
    
    try:
        response = requests.post(
            f"{BACKEND_URL}/chat",
            headers={"Authorization": f"Bearer {token}"},
            json={"message": "chicken breast 200g"},
            timeout=30
        )
        
        if response.status_code != 200:
            print_fail(f"API returned {response.status_code}")
            test_results["failed"] += 1
            return False
        
        data = response.json()
        
        # Verify expected fields
        required_fields = ["response", "items"]
        for field in required_fields:
            if field in data:
                print_pass(f"Field '{field}' exists ✓")
            else:
                print_fail(f"Missing field '{field}'")
                test_results["failed"] += 1
                return False
        
        # Verify items structure
        if len(data["items"]) > 0:
            item = data["items"][0]
            required_item_fields = ["category", "summary", "data"]
            for field in required_item_fields:
                if field in item:
                    print_pass(f"Item field '{field}' exists ✓")
                else:
                    print_fail(f"Missing item field '{field}'")
                    test_results["failed"] += 1
                    return False
        
        test_results["passed"] += 1
        return True
            
    except Exception as e:
        print_fail(f"Exception: {e}")
        test_results["failed"] += 1
        return False

def test_chat_history_persistence(token: str) -> bool:
    """Test: Chat history still persists"""
    print_test("Chat History Persistence")
    test_results["total"] += 1
    
    try:
        # Get chat history
        response = requests.get(
            f"{BACKEND_URL}/chat/history?limit=10",
            headers={"Authorization": f"Bearer {token}"},
            timeout=10
        )
        
        if response.status_code != 200:
            print_fail(f"API returned {response.status_code}")
            test_results["failed"] += 1
            return False
        
        data = response.json()
        
        if "messages" in data:
            message_count = len(data["messages"])
            print_pass(f"Chat history loaded: {message_count} messages ✓")
            
            if message_count > 0:
                print_info(f"Latest message: {data['messages'][0].get('content', '')[:80]}...")
            
            test_results["passed"] += 1
            return True
        else:
            print_fail("No 'messages' field in response")
            test_results["failed"] += 1
            return False
            
    except Exception as e:
        print_fail(f"Exception: {e}")
        test_results["failed"] += 1
        return False

def print_summary():
    """Print test summary"""
    print_header("TEST SUMMARY")
    
    total = test_results["total"]
    passed = test_results["passed"]
    failed = test_results["failed"]
    warnings = test_results["warnings"]
    
    pass_rate = (passed / total * 100) if total > 0 else 0
    
    print(f"Total Tests:    {total}")
    print(f"{Colors.GREEN}Passed:         {passed}{Colors.RESET}")
    print(f"{Colors.RED}Failed:         {failed}{Colors.RESET}")
    print(f"{Colors.YELLOW}Warnings:       {warnings}{Colors.RESET}")
    print(f"\n{Colors.BOLD}Pass Rate:      {pass_rate:.1f}%{Colors.RESET}")
    
    if failed == 0:
        print(f"\n{Colors.GREEN}{Colors.BOLD}✅ ALL TESTS PASSED! Safe to deploy.{Colors.RESET}")
        return 0
    else:
        print(f"\n{Colors.RED}{Colors.BOLD}❌ TESTS FAILED! DO NOT DEPLOY.{Colors.RESET}")
        return 1

def main():
    print_header("P0 BUG FIXES - AUTOMATED TEST SUITE")
    print(f"Backend URL: {BACKEND_URL}")
    print(f"Test User: {TEST_USER_EMAIL}")
    print(f"Started: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    # Login
    token = login()
    
    # Run tests
    print_header("REGRESSION TESTS - EXISTING FUNCTIONALITY")
    test_basic_meal_logging(token)
    test_multiline_logging(token)
    test_typo_handling(token)
    test_explicit_meal_type(token)
    test_json_parsing(token)
    test_chat_history_persistence(token)
    
    print_header("NEW FUNCTIONALITY TESTS - AI GUARDRAILS")
    test_unsupported_feature_diet_plan(token)
    test_unsupported_feature_meal_suggestions(token)
    
    # Print summary
    exit_code = print_summary()
    
    print(f"\n{Colors.BLUE}Finished: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}{Colors.RESET}\n")
    sys.exit(exit_code)

if __name__ == "__main__":
    main()

