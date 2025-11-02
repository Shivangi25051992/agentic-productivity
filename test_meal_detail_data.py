"""
Test to verify meal detail data structure
"""
import requests
import json

# Test user credentials
EMAIL = "alice.test@aiproductivity.app"
PASSWORD = "TestPass123!"
BASE_URL = "http://localhost:8000"

def test_meal_detail_data():
    print("=" * 80)
    print("🧪 TESTING MEAL DETAIL DATA STRUCTURE")
    print("=" * 80)
    
    # 1. Login
    print("\n1. Logging in...")
    login_response = requests.post(
        f"{BASE_URL}/auth/login",
        json={"email": EMAIL, "password": PASSWORD}
    )
    
    if login_response.status_code != 200:
        print(f"❌ Login failed: {login_response.status_code}")
        print(login_response.text)
        return
    
    token = login_response.json()["id_token"]
    headers = {"Authorization": f"Bearer {token}"}
    print("✅ Logged in successfully")
    
    # 2. Get dashboard data
    print("\n2. Fetching dashboard data...")
    dashboard_response = requests.get(
        f"{BASE_URL}/dashboard",
        headers=headers
    )
    
    if dashboard_response.status_code != 200:
        print(f"❌ Dashboard fetch failed: {dashboard_response.status_code}")
        print(dashboard_response.text)
        return
    
    dashboard_data = dashboard_response.json()
    print("✅ Dashboard data fetched")
    
    # 3. Check activities structure
    print("\n3. Analyzing activities structure...")
    activities = dashboard_data.get("activities", [])
    print(f"Total activities: {len(activities)}")
    
    # Group by meal type
    meals_by_type = {}
    for activity in activities:
        if activity.get("type") == "meal":
            meal_type = activity.get("data", {}).get("meal_type", "other")
            if meal_type not in meals_by_type:
                meals_by_type[meal_type] = []
            meals_by_type[meal_type].append(activity)
    
    print(f"\nMeals by type:")
    for meal_type, meals in meals_by_type.items():
        print(f"  {meal_type}: {len(meals)} items")
    
    # 4. Show sample meal data
    if activities:
        print("\n4. Sample meal activity structure:")
        sample = activities[0]
        print(json.dumps(sample, indent=2, default=str))
        
        # Check required fields
        print("\n5. Checking required fields for meal detail view:")
        required_fields = ["type", "timestamp", "data"]
        data_fields = ["description", "calories", "protein_g", "carbs_g", "fat_g", "fiber_g", "meal_type"]
        
        for field in required_fields:
            if field in sample:
                print(f"  ✅ {field}: {type(sample[field]).__name__}")
            else:
                print(f"  ❌ {field}: MISSING")
        
        if "data" in sample:
            data = sample["data"]
            print("\n  Data fields:")
            for field in data_fields:
                if field in data:
                    print(f"    ✅ {field}: {data[field]}")
                else:
                    print(f"    ❌ {field}: MISSING")
    else:
        print("\n❌ No activities found. Please log some meals first.")
    
    print("\n" + "=" * 80)
    print("✅ TEST COMPLETE")
    print("=" * 80)

if __name__ == "__main__":
    test_meal_detail_data()


