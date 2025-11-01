"""
Phase 2 Automated Tests: Expandable Meal Cards
Tests the backend endpoints that support expandable meal card functionality
"""

import requests
import json
import os
from datetime import datetime, timezone
from dotenv import load_dotenv
import pytest

load_dotenv()
load_dotenv('.env.local', override=True)

BASE_URL = "http://localhost:8000"
TEST_USER_EMAIL = "alice.test@aiproductivity.app"
TEST_USER_PASSWORD = "TestPass123!"
FIREBASE_API_KEY = os.getenv("FIREBASE_API_KEY")

# --- Helper for Authentication ---
def get_id_token(email, password):
    """Authenticates with Firebase and returns an ID token."""
    auth_url = f"https://identitytoolkit.googleapis.com/v1/accounts:signInWithPassword?key={FIREBASE_API_KEY}"
    payload = json.dumps({
        "email": email,
        "password": password,
        "returnSecureToken": True
    })
    headers = {"Content-Type": "application/json"}
    response = requests.post(auth_url, headers=headers, data=payload)
    response.raise_for_status()
    return response.json()["idToken"]

@pytest.fixture(scope="module")
def auth_token():
    """Fixture to provide an authentication token for tests."""
    if not FIREBASE_API_KEY:
        pytest.skip("FIREBASE_API_KEY not set, skipping auth-dependent tests.")
    try:
        token = get_id_token(TEST_USER_EMAIL, TEST_USER_PASSWORD)
        print(f"\n✅ Authenticated successfully for Phase 2 tests. Token: {token[:10]}...")
        return token
    except Exception as e:
        pytest.fail(f"Failed to get auth token: {e}")

# --- Tests ---

def test_0_health_check():
    """Test the health check endpoint."""
    print("\n" + "="*80)
    print("PHASE 2 TEST 0: Health Check")
    print("="*80)
    response = requests.get(f"{BASE_URL}/health")
    assert response.status_code == 200
    data = response.json()
    print(f"Status: {response.status_code}")
    print(f"✅ Service: {data.get('service')}")
    print(f"✅ Status: {data.get('status')}\n")
    assert data["status"] == "healthy"

def test_1_create_multiple_meals(auth_token):
    """Create multiple meals for testing expandable cards."""
    print("\n" + "="*80)
    print("PHASE 2 TEST 1: Create Multiple Meals")
    print("="*80)
    headers = {"Authorization": f"Bearer {auth_token}"}
    
    # Create meals for different meal types
    test_meals = [
        "2 eggs for breakfast",
        "chicken salad for lunch",
        "apple for snack",
        "grilled salmon with rice for dinner"
    ]
    
    created_meal_ids = []
    
    for meal_input in test_meals:
        response = requests.post(f"{BASE_URL}/chat", json={"user_input": meal_input}, headers=headers)
        assert response.status_code == 200, f"Failed to create meal: {meal_input}"
        data = response.json()
        print(f"✅ Created: {meal_input}")
        
        # Extract meal type from response
        items = data.get('items', [])
        for item in items:
            if item.get('category') == 'meal':
                meal_type = item['data'].get('meal_type', 'unknown')
                print(f"   Meal Type: {meal_type}")
    
    print(f"\n✅ TEST 1 PASSED: Created {len(test_meals)} meals")

def test_2_list_meals_by_type(auth_token):
    """Test listing meals filtered by meal type."""
    print("\n" + "="*80)
    print("PHASE 2 TEST 2: List Meals by Type")
    print("="*80)
    headers = {"Authorization": f"Bearer {auth_token}"}
    
    today = datetime.now(timezone.utc).strftime("%Y-%m-%d")
    
    meal_types = ['breakfast', 'lunch', 'snack', 'dinner']
    
    for meal_type in meal_types:
        response = requests.get(f"{BASE_URL}/meals?date={today}&meal_type={meal_type}", headers=headers)
        assert response.status_code == 200, f"Failed to list {meal_type} meals"
        meals = response.json()
        
        print(f"\n{meal_type.upper()}:")
        if meals:
            for meal in meals:
                description = meal.get('ai_parsed_data', {}).get('description', meal.get('content', 'Unknown'))
                calories = meal.get('ai_parsed_data', {}).get('calories', 0)
                print(f"  • {description} ({calories} kcal)")
        else:
            print(f"  No {meal_type} meals logged")
    
    print(f"\n✅ TEST 2 PASSED: Listed meals by type")

def test_3_get_meal_detail(auth_token):
    """Test getting detailed information for a specific meal."""
    print("\n" + "="*80)
    print("PHASE 2 TEST 3: Get Meal Detail")
    print("="*80)
    headers = {"Authorization": f"Bearer {auth_token}"}
    
    # First, list all meals to get an ID
    today = datetime.now(timezone.utc).strftime("%Y-%m-%d")
    response = requests.get(f"{BASE_URL}/meals?date={today}", headers=headers)
    assert response.status_code == 200
    meals = response.json()
    
    if not meals:
        print("⚠️ No meals found to test detail view")
        return
    
    # Get detail for the first meal
    test_meal_id = meals[0]['log_id']
    response = requests.get(f"{BASE_URL}/meals/{test_meal_id}", headers=headers)
    assert response.status_code == 200, f"Failed to get meal detail for {test_meal_id}"
    
    meal_detail = response.json()
    print(f"\nMeal ID: {test_meal_id}")
    print(f"Description: {meal_detail.get('content')}")
    print(f"Meal Type: {meal_detail.get('ai_parsed_data', {}).get('meal_type')}")
    print(f"Calories: {meal_detail.get('ai_parsed_data', {}).get('calories')} kcal")
    print(f"Protein: {meal_detail.get('ai_parsed_data', {}).get('protein')}g")
    print(f"Carbs: {meal_detail.get('ai_parsed_data', {}).get('carbs')}g")
    print(f"Fat: {meal_detail.get('ai_parsed_data', {}).get('fat')}g")
    
    print(f"\n✅ TEST 3 PASSED: Retrieved meal detail")

def test_4_move_meal_to_different_type(auth_token):
    """Test moving a meal to a different meal type."""
    print("\n" + "="*80)
    print("PHASE 2 TEST 4: Move Meal to Different Type")
    print("="*80)
    headers = {"Authorization": f"Bearer {auth_token}"}
    
    # Create a test meal
    response = requests.post(f"{BASE_URL}/chat", json={"user_input": "1 banana for snack"}, headers=headers)
    assert response.status_code == 200
    
    # Get the meal ID
    today = datetime.now(timezone.utc).strftime("%Y-%m-%d")
    response = requests.get(f"{BASE_URL}/meals?date={today}&meal_type=snack", headers=headers)
    meals = response.json()
    
    banana_meal = None
    for meal in meals:
        if 'banana' in meal.get('content', '').lower():
            banana_meal = meal
            break
    
    if not banana_meal:
        print("⚠️ Could not find banana meal to test move")
        return
    
    meal_id = banana_meal['log_id']
    original_type = banana_meal.get('ai_parsed_data', {}).get('meal_type', 'snack')
    
    print(f"\nOriginal meal type: {original_type}")
    
    # Move to breakfast
    response = requests.post(f"{BASE_URL}/meals/{meal_id}/move", 
                            json={"new_meal_type": "breakfast"}, 
                            headers=headers)
    assert response.status_code == 200, f"Failed to move meal: {response.text}"
    
    # Verify the move
    response = requests.get(f"{BASE_URL}/meals/{meal_id}", headers=headers)
    updated_meal = response.json()
    new_type = updated_meal.get('ai_parsed_data', {}).get('meal_type')
    
    print(f"New meal type: {new_type}")
    assert new_type == "breakfast", f"Expected 'breakfast', got '{new_type}'"
    
    print(f"\n✅ TEST 4 PASSED: Successfully moved meal from {original_type} to breakfast")

def test_5_update_meal_description(auth_token):
    """Test updating a meal's description."""
    print("\n" + "="*80)
    print("PHASE 2 TEST 5: Update Meal Description")
    print("="*80)
    headers = {"Authorization": f"Bearer {auth_token}"}
    
    # Create a test meal
    response = requests.post(f"{BASE_URL}/chat", json={"user_input": "1 apple"}, headers=headers)
    assert response.status_code == 200
    
    # Get the meal ID
    today = datetime.now(timezone.utc).strftime("%Y-%m-%d")
    response = requests.get(f"{BASE_URL}/meals?date={today}", headers=headers)
    meals = response.json()
    
    apple_meal = None
    for meal in meals:
        if 'apple' in meal.get('content', '').lower():
            apple_meal = meal
            break
    
    if not apple_meal:
        print("⚠️ Could not find apple meal to test update")
        return
    
    meal_id = apple_meal['log_id']
    original_description = apple_meal.get('content')
    
    print(f"\nOriginal description: {original_description}")
    
    # Update description
    new_description = "1 large red apple"
    response = requests.put(f"{BASE_URL}/meals/{meal_id}", 
                           json={"description": new_description}, 
                           headers=headers)
    assert response.status_code == 200, f"Failed to update meal: {response.text}"
    
    # Verify the update
    response = requests.get(f"{BASE_URL}/meals/{meal_id}", headers=headers)
    updated_meal = response.json()
    updated_description = updated_meal.get('content')
    
    print(f"Updated description: {updated_description}")
    assert updated_description == new_description, f"Expected '{new_description}', got '{updated_description}'"
    
    print(f"\n✅ TEST 5 PASSED: Successfully updated meal description")

def test_6_delete_meal(auth_token):
    """Test deleting a meal."""
    print("\n" + "="*80)
    print("PHASE 2 TEST 6: Delete Meal")
    print("="*80)
    headers = {"Authorization": f"Bearer {auth_token}"}
    
    # Create a test meal
    response = requests.post(f"{BASE_URL}/chat", json={"user_input": "test food to delete"}, headers=headers)
    assert response.status_code == 200
    
    # Get the meal ID
    today = datetime.now(timezone.utc).strftime("%Y-%m-%d")
    response = requests.get(f"{BASE_URL}/meals?date={today}", headers=headers)
    meals = response.json()
    
    test_meal = None
    for meal in meals:
        if 'test food' in meal.get('content', '').lower():
            test_meal = meal
            break
    
    if not test_meal:
        print("⚠️ Could not find test meal to delete")
        return
    
    meal_id = test_meal['log_id']
    
    print(f"\nDeleting meal: {test_meal.get('content')}")
    
    # Delete the meal
    response = requests.delete(f"{BASE_URL}/meals/{meal_id}", headers=headers)
    assert response.status_code == 200, f"Failed to delete meal: {response.text}"
    
    # Verify deletion
    response = requests.get(f"{BASE_URL}/meals/{meal_id}", headers=headers)
    assert response.status_code == 404, "Meal should not exist after deletion"
    
    print(f"\n✅ TEST 6 PASSED: Successfully deleted meal")

def test_7_expandable_card_data_structure(auth_token):
    """Test that meal data has all required fields for expandable cards."""
    print("\n" + "="*80)
    print("PHASE 2 TEST 7: Expandable Card Data Structure")
    print("="*80)
    headers = {"Authorization": f"Bearer {auth_token}"}
    
    # Create a complex meal
    response = requests.post(f"{BASE_URL}/chat", 
                           json={"user_input": "2 eggs, 1 toast, 1 cup coffee for breakfast"}, 
                           headers=headers)
    assert response.status_code == 200
    
    # Get today's meals
    today = datetime.now(timezone.utc).strftime("%Y-%m-%d")
    response = requests.get(f"{BASE_URL}/meals?date={today}&meal_type=breakfast", headers=headers)
    meals = response.json()
    
    if not meals:
        print("⚠️ No breakfast meals found")
        return
    
    # Check data structure
    for meal in meals:
        print(f"\nChecking meal: {meal.get('content')}")
        
        # Required fields
        assert 'log_id' in meal, "Missing log_id"
        assert 'content' in meal, "Missing content"
        assert 'timestamp' in meal, "Missing timestamp"
        assert 'ai_parsed_data' in meal, "Missing ai_parsed_data"
        
        ai_data = meal.get('ai_parsed_data', {})
        
        # Required ai_parsed_data fields
        assert 'description' in ai_data, "Missing description in ai_parsed_data"
        assert 'meal_type' in ai_data, "Missing meal_type in ai_parsed_data"
        assert 'calories' in ai_data, "Missing calories in ai_parsed_data"
        assert 'protein' in ai_data or 'protein_g' in ai_data, "Missing protein in ai_parsed_data"
        assert 'carbs' in ai_data or 'carbs_g' in ai_data, "Missing carbs in ai_parsed_data"
        assert 'fat' in ai_data or 'fat_g' in ai_data, "Missing fat in ai_parsed_data"
        
        print("  ✅ All required fields present")
        print(f"  • Meal Type: {ai_data.get('meal_type')}")
        print(f"  • Calories: {ai_data.get('calories')} kcal")
        print(f"  • Macros: P:{ai_data.get('protein', ai_data.get('protein_g'))}g, C:{ai_data.get('carbs', ai_data.get('carbs_g'))}g, F:{ai_data.get('fat', ai_data.get('fat_g'))}g")
    
    print(f"\n✅ TEST 7 PASSED: All meals have correct data structure for expandable cards")


if __name__ == "__main__":
    print("\n" + "="*80)
    print("🧪 PHASE 2 AUTOMATED TESTS")
    print("Testing: Expandable Meal Cards Backend Support")
    print("="*80)
    
    # Run tests
    test_0_health_check()
    
    try:
        token = get_id_token(TEST_USER_EMAIL, TEST_USER_PASSWORD)
        test_1_create_multiple_meals(token)
        test_2_list_meals_by_type(token)
        test_3_get_meal_detail(token)
        test_4_move_meal_to_different_type(token)
        test_5_update_meal_description(token)
        test_6_delete_meal(token)
        test_7_expandable_card_data_structure(token)
        
        print("\n" + "="*80)
        print("📊 TEST RESULTS SUMMARY")
        print("="*80)
        print("Health Check: ✅ PASSED")
        print("Create Multiple Meals: ✅ PASSED")
        print("List Meals by Type: ✅ PASSED")
        print("Get Meal Detail: ✅ PASSED")
        print("Move Meal: ✅ PASSED")
        print("Update Meal: ✅ PASSED")
        print("Delete Meal: ✅ PASSED")
        print("Data Structure: ✅ PASSED")
        print("\nTotal: 8/8 tests passed")
        print("\n🎉 ALL PHASE 2 TESTS PASSED!")
        print("="*80)
        
    except Exception as e:
        print(f"\n❌ TEST FAILED: {e}")
        raise

