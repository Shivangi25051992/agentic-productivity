#!/usr/bin/env python3
"""
Automated Test User Setup
Creates a dedicated test user for automated testing
"""
import os
import sys
import json
import requests
from datetime import datetime

# Configuration
BACKEND_URL = os.getenv("BACKEND_URL", "http://localhost:8000")
TEST_USER_EMAIL = "test_automation@aiproductivity.app"
TEST_USER_PASSWORD = "TestUser123!@#"
TEST_USER_NAME = "Test Automation User"

# Firebase Web API Key (for authentication)
FIREBASE_API_KEY = os.getenv("FIREBASE_API_KEY", "AIzaSyBLb8tqVHY5KZ9X0YmQKxJ0aVYPUZxQKxY")
FIREBASE_AUTH_URL = f"https://identitytoolkit.googleapis.com/v1/accounts:signInWithPassword?key={FIREBASE_API_KEY}"
FIREBASE_SIGNUP_URL = f"https://identitytoolkit.googleapis.com/v1/accounts:signUp?key={FIREBASE_API_KEY}"

class TestUserManager:
    def __init__(self):
        self.email = TEST_USER_EMAIL
        self.password = TEST_USER_PASSWORD
        self.name = TEST_USER_NAME
        self.id_token = None
        self.user_id = None
        self.profile_created = False
    
    def signup_or_login(self):
        """Try to login, if fails then signup"""
        print(f"🔐 Attempting to login as {self.email}...")
        
        # Try login first
        if self.login():
            print(f"✅ Logged in successfully")
            return True
        
        # If login fails, try signup
        print(f"📝 Login failed, attempting signup...")
        if self.signup():
            print(f"✅ Signed up successfully")
            return True
        
        print(f"❌ Both login and signup failed")
        return False
    
    def login(self):
        """Login with existing user"""
        try:
            response = requests.post(
                FIREBASE_AUTH_URL,
                json={
                    "email": self.email,
                    "password": self.password,
                    "returnSecureToken": True
                }
            )
            
            if response.status_code == 200:
                data = response.json()
                self.id_token = data['idToken']
                self.user_id = data['localId']
                return True
            else:
                return False
        except Exception as e:
            print(f"⚠️  Login error: {e}")
            return False
    
    def signup(self):
        """Create new test user"""
        try:
            response = requests.post(
                FIREBASE_SIGNUP_URL,
                json={
                    "email": self.email,
                    "password": self.password,
                    "returnSecureToken": True
                }
            )
            
            if response.status_code == 200:
                data = response.json()
                self.id_token = data['idToken']
                self.user_id = data['localId']
                return True
            else:
                print(f"❌ Signup failed: {response.text}")
                return False
        except Exception as e:
            print(f"⚠️  Signup error: {e}")
            return False
    
    def complete_onboarding(self):
        """Complete onboarding flow"""
        print(f"🎯 Completing onboarding...")
        
        try:
            response = requests.post(
                f"{BACKEND_URL}/profile/onboard",
                headers={
                    "Authorization": f"Bearer {self.id_token}",
                    "Content-Type": "application/json"
                },
                json={
                    "name": self.name,
                    "gender": "male",
                    "age": 30,
                    "height_cm": 175,
                    "weight_kg": 75.0,
                    "activity_level": "moderately_active",
                    "fitness_goal": "lose_weight",
                    "target_weight_kg": 70.0,
                    "diet_preference": "none",
                    "allergies": [],
                    "disliked_foods": [],
                    "timezone": "America/New_York"
                }
            )
            
            if response.status_code == 200:
                self.profile_created = True
                print(f"✅ Onboarding complete")
                return True
            else:
                print(f"❌ Onboarding failed: {response.status_code} - {response.text}")
                return False
        except Exception as e:
            print(f"⚠️  Onboarding error: {e}")
            return False
    
    def get_profile(self):
        """Get user profile"""
        try:
            response = requests.get(
                f"{BACKEND_URL}/profile/me",
                headers={"Authorization": f"Bearer {self.id_token}"}
            )
            
            if response.status_code == 200:
                return response.json()
            else:
                return None
        except Exception as e:
            print(f"⚠️  Get profile error: {e}")
            return None
    
    def save_credentials(self):
        """Save credentials to file for reuse"""
        credentials = {
            "email": self.email,
            "password": self.password,
            "user_id": self.user_id,
            "id_token": self.id_token,
            "profile_created": self.profile_created,
            "created_at": datetime.now().isoformat()
        }
        
        os.makedirs("test_automation", exist_ok=True)
        with open("test_automation/test_user_credentials.json", "w") as f:
            json.dump(credentials, f, indent=2)
        
        print(f"💾 Credentials saved to test_automation/test_user_credentials.json")
    
    def load_credentials(self):
        """Load credentials from file"""
        try:
            with open("test_automation/test_user_credentials.json", "r") as f:
                credentials = json.load(f)
                self.user_id = credentials.get("user_id")
                self.id_token = credentials.get("id_token")
                self.profile_created = credentials.get("profile_created", False)
                return True
        except FileNotFoundError:
            return False

def setup_test_user():
    """Main setup function"""
    print("=" * 80)
    print("🤖 AUTOMATED TEST USER SETUP")
    print("=" * 80)
    print()
    
    manager = TestUserManager()
    
    # Try to load existing credentials
    if manager.load_credentials():
        print(f"📂 Found existing credentials")
        # Verify token still works
        profile = manager.get_profile()
        if profile:
            print(f"✅ Existing test user is valid")
            print(f"   User ID: {manager.user_id}")
            print(f"   Profile: {profile.get('profile', {}).get('name', 'Unknown')}")
            manager.save_credentials()  # Update timestamp
            return manager
        else:
            print(f"⚠️  Token expired, re-authenticating...")
    
    # Signup or login
    if not manager.signup_or_login():
        print(f"❌ Failed to create/login test user")
        sys.exit(1)
    
    # Check if profile exists
    profile = manager.get_profile()
    if profile and profile.get("profile"):
        print(f"✅ Profile already exists")
        manager.profile_created = True
    else:
        # Complete onboarding
        if not manager.complete_onboarding():
            print(f"❌ Failed to complete onboarding")
            sys.exit(1)
    
    # Save credentials
    manager.save_credentials()
    
    print()
    print("=" * 80)
    print("✅ TEST USER READY")
    print("=" * 80)
    print(f"Email: {manager.email}")
    print(f"User ID: {manager.user_id}")
    print(f"Profile Created: {manager.profile_created}")
    print()
    
    return manager

if __name__ == "__main__":
    setup_test_user()

