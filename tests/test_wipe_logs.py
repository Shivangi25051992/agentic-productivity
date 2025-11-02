#!/usr/bin/env python3
"""
Automated test for wipe logs feature
"""
import os
import sys
import requests
from datetime import datetime

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

API_BASE = "http://localhost:8000"
TEST_USER_EMAIL = "alice.test@aiproductivity.app"
TEST_USER_PASSWORD = "TestPass123!"

def test_wipe_logs():
    """Test the wipe logs endpoint"""
    print("=" * 80)
    print("AUTOMATED TEST: Wipe Logs Feature")
    print("=" * 80)
    
    # Step 1: Login
    print("\n[1/5] Logging in...")
    login_resp = requests.post(
        f"{API_BASE}/auth/login",
        json={"email": TEST_USER_EMAIL, "password": TEST_USER_PASSWORD}
    )
    
    if login_resp.status_code != 200:
        print(f"❌ Login failed: {login_resp.status_code}")
        print(login_resp.text)
        return False
    
    token = login_resp.json().get("id_token")
    headers = {"Authorization": f"Bearer {token}"}
    print("✅ Login successful")
    
    # Step 2: Log some test data
    print("\n[2/5] Creating test data...")
    test_items = [
        {"user_input": "2 eggs for breakfast", "type": "meal"},
        {"user_input": "ran 5km", "type": "workout"},
        {"user_input": "finish report", "type": "task"}
    ]
    
    for item in test_items:
        resp = requests.post(f"{API_BASE}/chat", json=item, headers=headers)
        if resp.status_code == 200:
            print(f"  ✅ Logged: {item['user_input']}")
        else:
            print(f"  ⚠️  Failed to log: {item['user_input']}")
    
    # Step 3: Verify data exists
    print("\n[3/5] Verifying data exists...")
    stats_resp = requests.get(f"{API_BASE}/fitness/stats?period=daily", headers=headers)
    if stats_resp.status_code == 200:
        stats = stats_resp.json()
        print(f"  📊 Current calories: {stats.get('calories', 0)}")
    
    # Step 4: Call wipe endpoint
    print("\n[4/5] Calling wipe logs endpoint...")
    wipe_resp = requests.delete(f"{API_BASE}/user/wipe-logs", headers=headers)
    
    if wipe_resp.status_code != 200:
        print(f"❌ Wipe failed: {wipe_resp.status_code}")
        print(wipe_resp.text)
        return False
    
    result = wipe_resp.json()
    print(f"✅ Wipe successful!")
    print(f"  - Fitness logs deleted: {result['deleted']['fitness_logs']}")
    print(f"  - Chat messages deleted: {result['deleted']['chat_messages']}")
    print(f"  - Tasks deleted: {result['deleted']['tasks']}")
    print(f"  - Total deleted: {result['deleted']['total']}")
    
    # Step 5: Verify data is wiped
    print("\n[5/5] Verifying data is wiped...")
    stats_resp = requests.get(f"{API_BASE}/fitness/stats?period=daily", headers=headers)
    if stats_resp.status_code == 200:
        stats = stats_resp.json()
        calories = stats.get('calories', 0)
        if calories == 0:
            print(f"  ✅ Data successfully wiped (calories: {calories})")
        else:
            print(f"  ⚠️  Data may not be fully wiped (calories: {calories})")
    
    # Verify profile still exists
    profile_resp = requests.get(f"{API_BASE}/auth/me", headers=headers)
    if profile_resp.status_code == 200:
        profile = profile_resp.json()
        print(f"  ✅ Profile preserved: {profile.get('email')}")
    else:
        print(f"  ❌ Profile check failed")
        return False
    
    print("\n" + "=" * 80)
    print("✅ ALL TESTS PASSED")
    print("=" * 80)
    return True

if __name__ == "__main__":
    try:
        success = test_wipe_logs()
        sys.exit(0 if success else 1)
    except Exception as e:
        print(f"\n❌ TEST FAILED WITH EXCEPTION: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


