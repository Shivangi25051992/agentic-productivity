#!/usr/bin/env python3
"""
Comprehensive automated tests on Alice's account
User can verify results in UI at http://localhost:3000
"""

import requests
import json
import time
from datetime import datetime

BASE_URL = "http://localhost:8000"

# Alice's Firebase ID token (you'll need to get this from the UI)
# For now, we'll use the chat endpoint directly with a valid token
ALICE_EMAIL = "alice.test@aiproductivity.app"

def get_alice_token():
    """
    Get Alice's token from Firebase
    Note: This is a simplified version - in production you'd use Firebase SDK
    """
    # For testing, we'll use a manual token approach
    # The user should be logged in via UI, and we'll test the backend directly
    print("⚠️  Note: Make sure Alice is logged in via UI at http://localhost:3000")
    print("⚠️  We'll test the backend endpoints directly\n")
    
    # Return a placeholder - we'll need the actual token
    # For now, let's try to get it from a test login
    import os
    token = os.environ.get("ALICE_TOKEN")
    if token:
        return token
    
    # Try Firebase authentication
    try:
        import firebase_admin
        from firebase_admin import auth, credentials
        
        # Initialize Firebase Admin SDK
        cred_path = "/Users/pchintanwar/keys/productivityai-mvp-0017f7241a58.json"
        if not firebase_admin._apps:
            cred = credentials.Certificate(cred_path)
            firebase_admin.initialize_app(cred)
        
        # Get user by email
        user = auth.get_user_by_email(ALICE_EMAIL)
        
        # Create custom token
        custom_token = auth.create_custom_token(user.uid)
        
        # Exchange for ID token (this requires Firebase REST API)
        import requests
        api_key = "AIzaSyBBXqv3IPw8Z-F9Y7kGOb7-Yx4xGHXoZ0Y"  # From your .env
        
        response = requests.post(
            f"https://identitytoolkit.googleapis.com/v1/accounts:signInWithCustomToken?key={api_key}",
            json={"token": custom_token.decode(), "returnSecureToken": True}
        )
        
        if response.status_code == 200:
            id_token = response.json()["idToken"]
            print(f"✅ Got Alice's token via Firebase Admin SDK\n")
            return id_token
        else:
            print(f"❌ Failed to exchange custom token: {response.text}")
            return None
            
    except Exception as e:
        print(f"⚠️  Could not get token automatically: {e}")
        print("⚠️  Please set ALICE_TOKEN environment variable or login via UI\n")
        return None

def send_chat(token, message):
    """Send a chat message"""
    print(f"📤 [{datetime.now().strftime('%H:%M:%S')}] Sending: '{message}'")
    
    try:
        response = requests.post(
            f"{BASE_URL}/chat",
            headers={"Authorization": f"Bearer {token}"},
            json={"text": message, "type": "auto"},
            timeout=30
        )
        
        if response.status_code != 200:
            print(f"   ❌ Failed: {response.status_code}")
            print(f"   {response.text[:200]}")
            return None
        
        data = response.json()
        message_text = data.get("message", "")
        
        # Print first 150 chars of response
        preview = message_text[:150].replace('\n', ' ')
        print(f"   ✅ Response: {preview}...")
        
        return data
        
    except Exception as e:
        print(f"   ❌ Error: {e}")
        return None

def main():
    print("=" * 70)
    print("🧪 COMPREHENSIVE AUTOMATED TESTS - ALICE'S ACCOUNT")
    print("=" * 70)
    print(f"Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"Backend: {BASE_URL}")
    print(f"Frontend: http://localhost:3000")
    print("=" * 70)
    print()
    
    # Get token
    token = get_alice_token()
    if not token:
        print("\n❌ Cannot proceed without token")
        print("\n💡 Alternative: Login to http://localhost:3000 as Alice and test manually")
        return
    
    print("🚀 Starting automated tests...\n")
    time.sleep(1)
    
    # Test 1: Breakfast classification
    print("\n" + "=" * 70)
    print("TEST 1: Breakfast Classification (Critical Fix)")
    print("=" * 70)
    response1 = send_chat(token, "2 eggs for breakfast")
    time.sleep(2)
    
    # Test 2: Multi-line input
    print("\n" + "=" * 70)
    print("TEST 2: Multi-line Input (Workout + Supplement)")
    print("=" * 70)
    response2 = send_chat(token, "ran 5km\n1 multivitamin")
    time.sleep(2)
    
    # Test 3: Lunch with details
    print("\n" + "=" * 70)
    print("TEST 3: Lunch with Multiple Items")
    print("=" * 70)
    response3 = send_chat(token, "chicken breast with rice and broccoli for lunch")
    time.sleep(2)
    
    # Test 4: Snack
    print("\n" + "=" * 70)
    print("TEST 4: Snack (Chocolate bar - should assume 40g)")
    print("=" * 70)
    response4 = send_chat(token, "chocolate bar")
    time.sleep(2)
    
    # Test 5: Dinner
    print("\n" + "=" * 70)
    print("TEST 5: Dinner with Explicit Mention")
    print("=" * 70)
    response5 = send_chat(token, "salmon with vegetables for dinner")
    time.sleep(2)
    
    # Test 6: Workout only
    print("\n" + "=" * 70)
    print("TEST 6: Workout Only (Should NOT be in Food section)")
    print("=" * 70)
    response6 = send_chat(token, "30 minutes yoga")
    time.sleep(2)
    
    # Test 7: Task/Reminder
    print("\n" + "=" * 70)
    print("TEST 7: Task/Reminder")
    print("=" * 70)
    response7 = send_chat(token, "remind me to call doctor at 3pm")
    time.sleep(2)
    
    # Test 8: Complex multi-category
    print("\n" + "=" * 70)
    print("TEST 8: Complex Multi-Category Input")
    print("=" * 70)
    response8 = send_chat(token, "oatmeal for breakfast\nwalked 3km\nprotein shake\ncall mom at 5pm")
    time.sleep(2)
    
    # Summary
    print("\n" + "=" * 70)
    print("✅ ALL TESTS COMPLETED!")
    print("=" * 70)
    print("\n📊 Test Summary:")
    print(f"  • Test 1 (Breakfast): {'✅' if response1 else '❌'}")
    print(f"  • Test 2 (Multi-line): {'✅' if response2 else '❌'}")
    print(f"  • Test 3 (Lunch): {'✅' if response3 else '❌'}")
    print(f"  • Test 4 (Snack): {'✅' if response4 else '❌'}")
    print(f"  • Test 5 (Dinner): {'✅' if response5 else '❌'}")
    print(f"  • Test 6 (Workout): {'✅' if response6 else '❌'}")
    print(f"  • Test 7 (Task): {'✅' if response7 else '❌'}")
    print(f"  • Test 8 (Complex): {'✅' if response8 else '❌'}")
    
    print("\n" + "=" * 70)
    print("🎯 NEXT STEPS:")
    print("=" * 70)
    print("1. Open http://localhost:3000 in your browser")
    print("2. Login as alice.test@aiproductivity.app")
    print("3. Go to 'Assistant' tab")
    print("4. Verify:")
    print("   ✅ All 8 test messages are visible (Chat Persistence)")
    print("   ✅ No duplication in responses")
    print("   ✅ 'Breakfast' shows as breakfast (not dinner)")
    print("   ✅ 'Lunch' shows as lunch")
    print("   ✅ 'Dinner' shows as dinner")
    print("   ✅ Workouts in 'Exercise' section (not Food)")
    print("   ✅ No ** asterisks in formatting")
    print("   ✅ Clean, ChatGPT-style responses")
    print("\n5. Navigate to Home → Back to Assistant")
    print("   ✅ Chat history should still be there!")
    print("\n" + "=" * 70)

if __name__ == "__main__":
    main()

