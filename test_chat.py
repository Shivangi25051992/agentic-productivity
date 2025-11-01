import requests
import json

# Test the chat endpoint
url = "http://localhost:8000/chat"
payload = {
    "user_input": "i ate 2 eggs in the morning, 1 bowl of rice and 1 bowl of curd during day time, 5 pistachios during afternoon, 200gm of spinach, 1 bowl of rice in the evening"
}

# Note: This will fail without auth token, but we can see the response
try:
    response = requests.post(url, json=payload)
    print(f"Status: {response.status_code}")
    print(f"Response: {json.dumps(response.json(), indent=2)}")
except Exception as e:
    print(f"Error: {e}")
    print(f"Response text: {response.text if 'response' in locals() else 'No response'}")
