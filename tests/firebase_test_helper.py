"""
Firebase Admin Helper for Testing
Generates custom tokens for test users
"""

import os
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

from dotenv import load_dotenv
import firebase_admin
from firebase_admin import credentials, auth
import time
from functools import wraps

# Load environment variables
load_dotenv()
load_dotenv('.env.local', override=True)

def retry_on_network_error(max_retries=3, initial_delay=1, backoff_factor=2):
    """
    Decorator to retry functions on network/DNS errors
    
    Args:
        max_retries: Maximum number of retry attempts
        initial_delay: Initial delay in seconds
        backoff_factor: Multiplier for delay after each retry
    """
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            delay = initial_delay
            last_exception = None
            
            for attempt in range(max_retries + 1):
                try:
                    return func(*args, **kwargs)
                except Exception as e:
                    last_exception = e
                    error_str = str(e).lower()
                    
                    # Check if it's a network/DNS error
                    is_network_error = any(keyword in error_str for keyword in [
                        'dns', 'timeout', 'unavailable', 'connection', 
                        'network', 'firestore.googleapis.com'
                    ])
                    
                    if not is_network_error or attempt == max_retries:
                        # Not a network error or final attempt - raise
                        raise
                    
                    # Network error - retry with backoff
                    print(f"⚠️  Network error (attempt {attempt + 1}/{max_retries + 1}): {str(e)[:100]}")
                    print(f"🔄 Retrying in {delay}s...")
                    time.sleep(delay)
                    delay *= backoff_factor
            
            # Should never reach here, but just in case
            raise last_exception
        
        return wrapper
    return decorator

# Initialize Firebase Admin SDK
def init_firebase_admin():
    """Initialize Firebase Admin SDK"""
    if not firebase_admin._apps:
        cred_path = os.getenv('GOOGLE_APPLICATION_CREDENTIALS')
        if not cred_path or not os.path.exists(cred_path):
            raise Exception(f"Firebase credentials not found at: {cred_path}")
        
        cred = credentials.Certificate(cred_path)
        firebase_admin.initialize_app(cred)
        print(f"✅ Firebase Admin SDK initialized")

@retry_on_network_error(max_retries=3, initial_delay=2, backoff_factor=2)
def create_test_user(email: str, password: str, display_name: str) -> dict:
    """
    Create a test user in Firebase Auth AND Firestore
    
    Returns:
        dict with uid, email, and custom_token
    """
    init_firebase_admin()
    
    try:
        # Try to get existing user
        user = auth.get_user_by_email(email)
        print(f"✅ User exists in Auth: {email}")
    except auth.UserNotFoundError:
        # Create new user
        user = auth.create_user(
            email=email,
            password=password,
            display_name=display_name,
            email_verified=True
        )
        print(f"✅ Created user in Auth: {email}")
    
    # Also create user in Firestore (required by backend)
    from google.cloud import firestore
    db = firestore.Client(project=os.getenv("GOOGLE_CLOUD_PROJECT"))
    user_ref = db.collection('users').document(user.uid)
    
    # Check if user exists in Firestore
    user_doc = user_ref.get()
    if not user_doc.exists:
        # Create user document
        user_ref.set({
            'uid': user.uid,
            'email': user.email,
            'name': display_name,
            'created_at': firestore.SERVER_TIMESTAMP,
            'email_verified': True
        })
        print(f"✅ Created user in Firestore: {email}")
    else:
        print(f"✅ User exists in Firestore: {email}")
    
    # Generate custom token
    custom_token = auth.create_custom_token(user.uid)
    
    return {
        'uid': user.uid,
        'email': user.email,
        'display_name': user.display_name,
        'custom_token': custom_token.decode('utf-8') if isinstance(custom_token, bytes) else custom_token
    }

def delete_test_user(email: str):
    """Delete a test user"""
    init_firebase_admin()
    
    try:
        user = auth.get_user_by_email(email)
        auth.delete_user(user.uid)
        print(f"✅ Deleted user: {email}")
    except auth.UserNotFoundError:
        print(f"⚠️  User not found: {email}")

@retry_on_network_error(max_retries=3, initial_delay=1, backoff_factor=2)
def exchange_custom_token_for_id_token(custom_token: str, api_key: str) -> str:
    """
    Exchange custom token for ID token using Firebase REST API
    
    Args:
        custom_token: Custom token from Firebase Admin SDK
        api_key: Firebase Web API key
    
    Returns:
        ID token (JWT) for API authentication
    """
    import requests
    
    url = f"https://identitytoolkit.googleapis.com/v1/accounts:signInWithCustomToken?key={api_key}"
    
    response = requests.post(url, json={
        "token": custom_token,
        "returnSecureToken": True
    }, timeout=10)
    
    if response.status_code == 200:
        data = response.json()
        return data['idToken']
    else:
        raise Exception(f"Failed to exchange token: {response.text}")

def get_firebase_api_key() -> str:
    """Get Firebase Web API key from environment or config"""
    api_key = os.getenv('FIREBASE_API_KEY')
    if not api_key:
        # Try to import from test config
        try:
            from tests.test_config import FIREBASE_API_KEY
            api_key = FIREBASE_API_KEY
        except ImportError:
            print("⚠️  FIREBASE_API_KEY not set")
            return None
    return api_key

def create_test_user_with_token(email: str, password: str, display_name: str) -> dict:
    """
    Create test user and get ID token for API calls
    
    Returns:
        dict with uid, email, custom_token, and id_token
    """
    user_data = create_test_user(email, password, display_name)
    
    # Try to get ID token
    api_key = get_firebase_api_key()
    if api_key:
        try:
            id_token = exchange_custom_token_for_id_token(user_data['custom_token'], api_key)
            user_data['id_token'] = id_token
            print(f"✅ Got ID token for {email}")
        except Exception as e:
            print(f"⚠️  Could not get ID token: {e}")
            user_data['id_token'] = user_data['custom_token']  # Fallback
    else:
        # Use custom token directly
        user_data['id_token'] = user_data['custom_token']
    
    return user_data

def cleanup_test_users(prefix: str = "testuser"):
    """Delete all test users with given prefix"""
    init_firebase_admin()
    
    # List all users
    page = auth.list_users()
    deleted = 0
    
    while page:
        for user in page.users:
            if user.email and user.email.startswith(prefix):
                try:
                    auth.delete_user(user.uid)
                    deleted += 1
                    print(f"✅ Deleted: {user.email}")
                except Exception as e:
                    print(f"❌ Error deleting {user.email}: {e}")
        
        # Get next page
        page = page.get_next_page()
    
    print(f"\n✅ Deleted {deleted} test users")

if __name__ == "__main__":
    # Test the helper
    print("\n🧪 Testing Firebase Admin Helper\n")
    
    # Create a test user
    test_email = "test_simulation@aiproductivity.test"
    user_data = create_test_user_with_token(
        email=test_email,
        password="TestPass123!",
        display_name="Test Simulation User"
    )
    
    print(f"\n✅ Test user created:")
    print(f"  UID: {user_data['uid']}")
    print(f"  Email: {user_data['email']}")
    print(f"  Custom Token: {user_data['custom_token'][:50]}...")
    if 'id_token' in user_data:
        print(f"  ID Token: {user_data['id_token'][:50]}...")
    
    # Clean up
    # delete_test_user(test_email)

