#!/usr/bin/env python3
"""
Test script to verify water and supplement logging
"""
import requests
import json

# Configuration
BASE_URL = "http://localhost:8000"
TOKEN = "YOUR_TOKEN_HERE"  # Replace with actual token

def test_water_logging():
    """Test water logging via chat endpoint"""
    print("\n🧪 Testing Water Logging...")
    
    response = requests.post(
        f"{BASE_URL}/chat",
        headers={
            "Authorization": f"Bearer {TOKEN}",
            "Content-Type": "application/json"
        },
        json={
            "user_input": "I drank 250ml water"
        }
    )
    
    print(f"Status: {response.status_code}")
    print(f"Response: {json.dumps(response.json(), indent=2)}")
    
    if response.status_code == 200:
        data = response.json()
        print(f"✅ Water logged successfully!")
        print(f"Message: {data.get('message')}")
    else:
        print(f"❌ Failed: {response.text}")

def test_supplement_logging():
    """Test supplement logging via chat endpoint"""
    print("\n🧪 Testing Supplement Logging...")
    
    response = requests.post(
        f"{BASE_URL}/chat",
        headers={
            "Authorization": f"Bearer {TOKEN}",
            "Content-Type": "application/json"
        },
        json={
            "user_input": "I took vitamin D 1000 IU"
        }
    )
    
    print(f"Status: {response.status_code}")
    print(f"Response: {json.dumps(response.json(), indent=2)}")
    
    if response.status_code == 200:
        data = response.json()
        print(f"✅ Supplement logged successfully!")
        print(f"Message: {data.get('message')}")
    else:
        print(f"❌ Failed: {response.text}")

def test_timeline():
    """Test timeline endpoint to see if water/supplements appear"""
    print("\n🧪 Testing Timeline...")
    
    response = requests.get(
        f"{BASE_URL}/timeline",
        headers={
            "Authorization": f"Bearer {TOKEN}"
        },
        params={
            "types": "water,supplement",
            "limit": 10
        }
    )
    
    print(f"Status: {response.status_code}")
    
    if response.status_code == 200:
        data = response.json()
        activities = data.get('activities', [])
        print(f"✅ Found {len(activities)} activities")
        
        for activity in activities:
            print(f"\n  - {activity['type']}: {activity['title']}")
            print(f"    Details: {activity['details']}")
    else:
        print(f"❌ Failed: {response.text}")

if __name__ == "__main__":
    print("=" * 60)
    print("WATER & SUPPLEMENT LOGGING TEST")
    print("=" * 60)
    print("\n⚠️  Before running, update TOKEN variable with your auth token")
    print("    You can get it from browser DevTools > Network > Authorization header")
    print("\n" + "=" * 60)
    
    # Uncomment to run tests
    # test_water_logging()
    # test_supplement_logging()
    # test_timeline()


