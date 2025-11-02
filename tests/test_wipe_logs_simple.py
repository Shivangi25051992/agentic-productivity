#!/usr/bin/env python3
"""
Simple automated test for wipe logs feature
Requires: Backend running on port 8000
"""
import os
import sys
import requests

API_BASE = "http://localhost:8000"

def test_wipe_endpoint():
    """Test that the wipe endpoint exists and returns proper structure"""
    print("=" * 80)
    print("AUTOMATED TEST: Wipe Logs Endpoint")
    print("=" * 80)
    
    print("\n[TEST] Checking DELETE /user/wipe-logs endpoint...")
    print("  Note: This will return 401 without auth, but confirms endpoint exists")
    
    # Test without auth (should return 401)
    resp = requests.delete(f"{API_BASE}/user/wipe-logs")
    
    if resp.status_code == 401:
        print("  ✅ Endpoint exists and requires authentication (401)")
        print("  ✅ Method: DELETE")
        print("  ✅ Path: /user/wipe-logs")
        return True
    elif resp.status_code == 405:
        print(f"  ❌ Wrong HTTP method (405 Method Not Allowed)")
        print(f"     The endpoint may be expecting GET instead of DELETE")
        return False
    elif resp.status_code == 404:
        print(f"  ❌ Endpoint not found (404)")
        return False
    else:
        print(f"  ⚠️  Unexpected status: {resp.status_code}")
        print(f"     Response: {resp.text}")
        return False

def test_frontend_api_service():
    """Verify ApiService has delete method"""
    print("\n[TEST] Checking Flutter ApiService...")
    
    api_service_path = "/Users/pchintanwar/Documents/Projects-AIProductivity/agentic-productivity/flutter_app/lib/services/api_service.dart"
    
    if not os.path.exists(api_service_path):
        print("  ❌ ApiService file not found")
        return False
    
    with open(api_service_path, 'r') as f:
        content = f.read()
    
    if 'Future<Map<String, dynamic>> delete(String path)' in content:
        print("  ✅ ApiService has delete() method")
    else:
        print("  ❌ ApiService missing delete() method")
        return False
    
    return True

def test_settings_screen():
    """Verify settings screen uses correct API call"""
    print("\n[TEST] Checking Settings Screen...")
    
    settings_path = "/Users/pchintanwar/Documents/Projects-AIProductivity/agentic-productivity/flutter_app/lib/screens/settings/settings_screen.dart"
    
    if not os.path.exists(settings_path):
        print("  ❌ Settings screen file not found")
        return False
    
    with open(settings_path, 'r') as f:
        content = f.read()
    
    if 'Wipe All My Logs' in content:
        print("  ✅ 'Wipe All My Logs' button exists")
    else:
        print("  ❌ 'Wipe All My Logs' button not found")
        return False
    
    if 'api.delete(\'/user/wipe-logs\')' in content:
        print("  ✅ Uses correct API method: api.delete()")
    elif 'api.get(\'/user/wipe-logs\')' in content:
        print("  ❌ Uses wrong API method: api.get() (should be delete())")
        return False
    else:
        print("  ⚠️  Could not find API call")
        return False
    
    return True

if __name__ == "__main__":
    print("\n🤖 Running automated tests for Wipe Logs feature...\n")
    
    results = []
    
    try:
        results.append(("Backend Endpoint", test_wipe_endpoint()))
    except Exception as e:
        print(f"  ❌ Backend test failed: {e}")
        results.append(("Backend Endpoint", False))
    
    try:
        results.append(("ApiService", test_frontend_api_service()))
    except Exception as e:
        print(f"  ❌ ApiService test failed: {e}")
        results.append(("ApiService", False))
    
    try:
        results.append(("Settings Screen", test_settings_screen()))
    except Exception as e:
        print(f"  ❌ Settings screen test failed: {e}")
        results.append(("Settings Screen", False))
    
    print("\n" + "=" * 80)
    print("TEST SUMMARY")
    print("=" * 80)
    for name, passed in results:
        status = "✅ PASS" if passed else "❌ FAIL"
        print(f"{status:10} {name}")
    
    all_passed = all(result[1] for result in results)
    
    if all_passed:
        print("\n✅ ALL TESTS PASSED - Feature is ready for manual testing!")
    else:
        print("\n❌ SOME TESTS FAILED - Fix issues before manual testing")
    
    print("=" * 80)
    sys.exit(0 if all_passed else 1)


