"""
Meal Planning Feature - Comprehensive Test Script
Tests meal plan generation, retrieval, and grocery list features
"""

import requests
import json
from datetime import date, datetime, timedelta
from typing import Dict, Any
import time

# Configuration
BASE_URL = "http://localhost:8000"
HEADERS = {
    "Content-Type": "application/json"
}

# ANSI color codes for pretty output
class Colors:
    GREEN = '\033[92m'
    RED = '\033[91m'
    YELLOW = '\033[93m'
    BLUE = '\033[94m'
    MAGENTA = '\033[95m'
    CYAN = '\033[96m'
    WHITE = '\033[97m'
    BOLD = '\033[1m'
    END = '\033[0m'

def print_header(text: str):
    print(f"\n{Colors.BOLD}{Colors.CYAN}{'=' * 80}{Colors.END}")
    print(f"{Colors.BOLD}{Colors.CYAN}{text.center(80)}{Colors.END}")
    print(f"{Colors.BOLD}{Colors.CYAN}{'=' * 80}{Colors.END}\n")

def print_success(text: str):
    print(f"{Colors.GREEN}✓ {text}{Colors.END}")

def print_error(text: str):
    print(f"{Colors.RED}✗ {text}{Colors.END}")

def print_info(text: str):
    print(f"{Colors.BLUE}ℹ {text}{Colors.END}")

def print_warning(text: str):
    print(f"{Colors.YELLOW}⚠ {text}{Colors.END}")

def print_json(data: Any, title: str = "Response"):
    print(f"{Colors.MAGENTA}{title}:{Colors.END}")
    print(json.dumps(data, indent=2))

# ============================================================================
# AUTHENTICATION
# ============================================================================

def get_auth_token() -> str:
    """Login and get authentication token"""
    print_header("AUTHENTICATION")
    
    # Try to login with test credentials
    login_data = {
        "email": "test@example.com",
        "password": "testpassword123"
    }
    
    print_info(f"Attempting login with: {login_data['email']}")
    
    try:
        response = requests.post(
            f"{BASE_URL}/auth/login",
            json=login_data,
            headers=HEADERS
        )
        
        if response.status_code == 200:
            token = response.json()["access_token"]
            print_success(f"Login successful! Token: {token[:20]}...")
            return token
        else:
            print_warning(f"Login failed (status {response.status_code}), trying registration...")
            
            # Try to register
            register_data = {
                "email": login_data["email"],
                "password": login_data["password"],
                "name": "Test User"
            }
            
            response = requests.post(
                f"{BASE_URL}/auth/register",
                json=register_data,
                headers=HEADERS
            )
            
            if response.status_code in [200, 201]:
                # Now login
                response = requests.post(
                    f"{BASE_URL}/auth/login",
                    json=login_data,
                    headers=HEADERS
                )
                token = response.json()["access_token"]
                print_success(f"Registration and login successful! Token: {token[:20]}...")
                return token
            else:
                print_error(f"Registration failed: {response.text}")
                raise Exception("Authentication failed")
                
    except Exception as e:
        print_error(f"Authentication error: {str(e)}")
        raise

# ============================================================================
# MEAL PLANNING TESTS
# ============================================================================

def test_health_check():
    """Test API health"""
    print_header("HEALTH CHECK")
    
    response = requests.get(f"{BASE_URL}/health")
    
    if response.status_code == 200:
        print_success("Backend is healthy!")
        print_json(response.json(), "Health Status")
        return True
    else:
        print_error(f"Health check failed: {response.status_code}")
        return False

def test_generate_meal_plan(token: str) -> Dict[str, Any]:
    """Test AI meal plan generation"""
    print_header("GENERATE MEAL PLAN")
    
    # Generate meal plan for the current week
    start_date = date.today()
    
    request_data = {
        "start_date": start_date.isoformat(),
        "num_days": 7,
        "daily_calories": 2000,
        "daily_protein": 150,
        "dietary_preferences": ["high_protein", "low_carb"],
        "prep_time_preference": "medium",
        "num_people": 1,
        "avoid_ingredients": ["mushrooms"]
    }
    
    print_info("Generating meal plan with preferences:")
    print_json(request_data, "Request")
    
    print_warning("This may take 30-60 seconds as AI generates the meal plan...")
    
    try:
        headers = HEADERS.copy()
        headers["Authorization"] = f"Bearer {token}"
        
        response = requests.post(
            f"{BASE_URL}/meal-planning/meal-plans/generate",
            json=request_data,
            headers=headers,
            timeout=120  # 2 minute timeout
        )
        
        if response.status_code in [200, 201]:
            meal_plan = response.json()
            print_success("Meal plan generated successfully!")
            print_json(meal_plan, "Generated Meal Plan")
            
            # Print summary
            print(f"\n{Colors.BOLD}Meal Plan Summary:{Colors.END}")
            print(f"  Plan ID: {meal_plan.get('id', 'N/A')}")
            print(f"  Week of: {meal_plan.get('start_date', 'N/A')}")
            print(f"  Days: {len(meal_plan.get('meals', []))} days planned")
            
            # Count meals
            total_meals = 0
            for day_meals in meal_plan.get('meals', []):
                total_meals += len(day_meals.get('meals', []))
            print(f"  Total meals: {total_meals}")
            
            return meal_plan
        else:
            print_error(f"Failed to generate meal plan: {response.status_code}")
            print_error(f"Error: {response.text}")
            return None
            
    except requests.Timeout:
        print_error("Request timed out - AI generation took too long")
        return None
    except Exception as e:
        print_error(f"Error generating meal plan: {str(e)}")
        return None

def test_get_meal_plans(token: str):
    """Test retrieving meal plans"""
    print_header("GET MEAL PLANS")
    
    headers = HEADERS.copy()
    headers["Authorization"] = f"Bearer {token}"
    
    # Get current week's meal plan
    start_date = date.today()
    end_date = start_date + timedelta(days=7)
    
    print_info(f"Fetching meal plans from {start_date} to {end_date}")
    
    try:
        response = requests.get(
            f"{BASE_URL}/meal-planning/meal-plans",
            params={
                "start_date": start_date.isoformat(),
                "end_date": end_date.isoformat()
            },
            headers=headers
        )
        
        if response.status_code == 200:
            meal_plans = response.json()
            print_success(f"Retrieved {len(meal_plans)} meal plan(s)")
            
            if meal_plans:
                print_json(meal_plans[0], "First Meal Plan")
                return meal_plans[0]
            else:
                print_warning("No meal plans found for this week")
                return None
        else:
            print_error(f"Failed to get meal plans: {response.status_code}")
            print_error(f"Error: {response.text}")
            return None
            
    except Exception as e:
        print_error(f"Error getting meal plans: {str(e)}")
        return None

def test_get_specific_day_meals(token: str, target_date: date = None):
    """Test getting meals for a specific day"""
    print_header("GET SPECIFIC DAY MEALS")
    
    if target_date is None:
        target_date = date.today()
    
    headers = HEADERS.copy()
    headers["Authorization"] = f"Bearer {token}"
    
    print_info(f"Fetching meals for {target_date}")
    
    try:
        response = requests.get(
            f"{BASE_URL}/meal-planning/meals/by-date/{target_date.isoformat()}",
            headers=headers
        )
        
        if response.status_code == 200:
            meals = response.json()
            print_success(f"Retrieved {len(meals)} meal(s) for {target_date}")
            
            if meals:
                print_json(meals, f"Meals for {target_date}")
                
                # Print meal summary
                print(f"\n{Colors.BOLD}Daily Meal Summary:{Colors.END}")
                total_calories = 0
                total_protein = 0
                
                for meal in meals:
                    meal_type = meal.get('meal_type', 'Unknown')
                    recipe = meal.get('recipe', {})
                    recipe_name = recipe.get('name', 'Unknown')
                    nutrition = recipe.get('nutrition', {})
                    calories = nutrition.get('calories', 0)
                    protein = nutrition.get('protein', 0)
                    
                    print(f"  {meal_type}: {recipe_name}")
                    print(f"    Calories: {calories} kcal, Protein: {protein}g")
                    
                    total_calories += calories
                    total_protein += protein
                
                print(f"\n{Colors.BOLD}Totals:{Colors.END}")
                print(f"  Calories: {total_calories} kcal")
                print(f"  Protein: {total_protein}g")
                
                return meals
            else:
                print_warning(f"No meals found for {target_date}")
                return None
        else:
            print_error(f"Failed to get meals: {response.status_code}")
            print_error(f"Error: {response.text}")
            return None
            
    except Exception as e:
        print_error(f"Error getting meals: {str(e)}")
        return None

def test_generate_grocery_list(token: str, meal_plan_id: str = None):
    """Test grocery list generation"""
    print_header("GENERATE GROCERY LIST")
    
    headers = HEADERS.copy()
    headers["Authorization"] = f"Bearer {token}"
    
    if meal_plan_id:
        print_info(f"Generating grocery list for meal plan: {meal_plan_id}")
        
        try:
            response = requests.post(
                f"{BASE_URL}/meal-planning/meal-plans/{meal_plan_id}/grocery-list",
                headers=headers
            )
            
            if response.status_code in [200, 201]:
                grocery_list = response.json()
                print_success("Grocery list generated successfully!")
                print_json(grocery_list, "Grocery List")
                
                # Print categorized items
                print(f"\n{Colors.BOLD}Grocery List by Category:{Colors.END}")
                
                items_by_category = {}
                for item in grocery_list.get('items', []):
                    category = item.get('category', 'Uncategorized')
                    if category not in items_by_category:
                        items_by_category[category] = []
                    items_by_category[category].append(item)
                
                for category, items in sorted(items_by_category.items()):
                    print(f"\n  {Colors.BOLD}{category}:{Colors.END}")
                    for item in items:
                        name = item.get('item_name', 'Unknown')
                        quantity = item.get('quantity', 0)
                        unit = item.get('unit', '')
                        checked = item.get('checked', False)
                        status = "✓" if checked else "○"
                        print(f"    {status} {name} - {quantity} {unit}")
                
                print(f"\n{Colors.BOLD}Total Items: {len(grocery_list.get('items', []))}{Colors.END}")
                
                return grocery_list
            else:
                print_error(f"Failed to generate grocery list: {response.status_code}")
                print_error(f"Error: {response.text}")
                return None
                
        except Exception as e:
            print_error(f"Error generating grocery list: {str(e)}")
            return None
    else:
        print_warning("No meal plan ID provided, skipping grocery list generation")
        return None

def test_update_grocery_item(token: str, grocery_list_id: str, item_id: str):
    """Test checking off a grocery item"""
    print_header("UPDATE GROCERY ITEM")
    
    headers = HEADERS.copy()
    headers["Authorization"] = f"Bearer {token}"
    
    print_info(f"Checking off item {item_id} in grocery list {grocery_list_id}")
    
    try:
        # Toggle item to checked
        response = requests.patch(
            f"{BASE_URL}/meal-planning/grocery-lists/{grocery_list_id}/items/{item_id}",
            json={"checked": True},
            headers=headers
        )
        
        if response.status_code == 200:
            updated_item = response.json()
            print_success("Item checked off successfully!")
            print_json(updated_item, "Updated Item")
            return updated_item
        else:
            print_error(f"Failed to update item: {response.status_code}")
            print_error(f"Error: {response.text}")
            return None
            
    except Exception as e:
        print_error(f"Error updating item: {str(e)}")
        return None

# ============================================================================
# MAIN TEST FLOW
# ============================================================================

def run_all_tests():
    """Run all meal planning tests"""
    print_header("MEAL PLANNING FEATURE - COMPREHENSIVE TEST")
    print(f"{Colors.BOLD}Starting tests at {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}{Colors.END}\n")
    
    try:
        # 1. Health check
        if not test_health_check():
            print_error("Backend is not healthy. Aborting tests.")
            return
        
        time.sleep(1)
        
        # 2. Authentication
        token = get_auth_token()
        
        time.sleep(1)
        
        # 3. Generate a new meal plan
        meal_plan = test_generate_meal_plan(token)
        
        if meal_plan:
            meal_plan_id = meal_plan.get('id')
            
            time.sleep(2)
            
            # 4. Retrieve meal plans
            test_get_meal_plans(token)
            
            time.sleep(1)
            
            # 5. Get today's meals
            test_get_specific_day_meals(token, date.today())
            
            time.sleep(1)
            
            # 6. Generate grocery list
            grocery_list = test_generate_grocery_list(token, meal_plan_id)
            
            if grocery_list and grocery_list.get('items'):
                time.sleep(1)
                
                # 7. Check off first item
                first_item = grocery_list['items'][0]
                test_update_grocery_item(
                    token,
                    grocery_list.get('id'),
                    first_item.get('id')
                )
        
        # Test summary
        print_header("TEST SUMMARY")
        print_success("All meal planning tests completed!")
        print_info("Check the output above for detailed results")
        
        print(f"\n{Colors.BOLD}Next Steps:{Colors.END}")
        print("1. Open the app at http://localhost:9000")
        print("2. Navigate to the Plan tab")
        print("3. Click 'Generate Meal Plan' to test the UI")
        print("4. View generated meals in the calendar")
        print("5. Generate and check off grocery items")
        
    except Exception as e:
        print_error(f"Test execution failed: {str(e)}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    run_all_tests()

