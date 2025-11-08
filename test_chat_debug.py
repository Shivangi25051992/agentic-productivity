#!/usr/bin/env python3
"""
Quick script to test the /chat endpoint and see what error occurs
"""
import requests
import json

# Test the chat endpoint
url = "http://localhost:8000/chat"
headers = {
    "Content-Type": "application/json",
}
data = {
    "user_input": "2 eggs"
}

print("🧪 Testing /chat endpoint...")
print(f"URL: {url}")
print(f"Data: {data}")
print("\n" + "="*50 + "\n")

try:
    response = requests.post(url, json=data, headers=headers, timeout=30)
    print(f"Status Code: {response.status_code}")
    print(f"Response: {json.dumps(response.json(), indent=2)}")
except requests.exceptions.Timeout:
    print("❌ ERROR: Request timed out (30s)")
except requests.exceptions.ConnectionError as e:
    print(f"❌ ERROR: Connection error: {e}")
except Exception as e:
    print(f"❌ ERROR: {type(e).__name__}: {e}")
    if hasattr(e, 'response'):
        print(f"Response text: {e.response.text}")




