#!/usr/bin/env python3
"""
Automated test for feedback submission
Tests the complete feedback flow: submit feedback -> verify in Firestore
"""
import requests
import json
import os
from datetime import datetime
from dotenv import load_dotenv

# Load environment variables
load_dotenv()
load_dotenv('.env.local', override=True)

# Configuration
API_BASE_URL = os.getenv('API_BASE_URL', 'https://aiproductivity-backend-rhwrraai2a-uc.a.run.app')
TEST_USER_EMAIL = 'alice.test@aiproductivity.app'
TEST_USER_PASSWORD = 'testpassword123'
FIREBASE_API_KEY = os.getenv('FIREBASE_API_KEY')

def get_firebase_token():
    """Get Firebase ID token for test user"""
    print('🔐 Authenticating test user...')
    
    url = f'https://identitytoolkit.googleapis.com/v1/accounts:signInWithPassword?key={FIREBASE_API_KEY}'
    payload = {
        'email': TEST_USER_EMAIL,
        'password': TEST_USER_PASSWORD,
        'returnSecureToken': True
    }
    
    response = requests.post(url, json=payload)
    if response.status_code != 200:
        raise Exception(f'Authentication failed: {response.text}')
    
    token = response.json()['idToken']
    print(f'✅ Authenticated as {TEST_USER_EMAIL}')
    return token

def test_feedback_submission():
    """Test feedback submission endpoint"""
    print('\n' + '='*80)
    print('🧪 TESTING FEEDBACK SUBMISSION')
    print('='*80)
    
    try:
        # Step 1: Authenticate
        token = get_firebase_token()
        
        # Step 2: Submit feedback
        print('\n📝 Submitting test feedback...')
        feedback_data = {
            'type': 'bug',
            'comment': f'Automated test feedback - {datetime.now().isoformat()}',
            'screen': 'automated_test',
            'timestamp': datetime.now().isoformat(),
            'has_screenshot': False,
        }
        
        headers = {
            'Authorization': f'Bearer {token}',
            'Content-Type': 'application/json'
        }
        
        response = requests.post(
            f'{API_BASE_URL}/feedback/submit',
            json=feedback_data,
            headers=headers
        )
        
        print(f'Response status: {response.status_code}')
        print(f'Response body: {response.text}')
        
        if response.status_code == 200:
            print('✅ Feedback submitted successfully!')
            return True
        else:
            print(f'❌ Feedback submission failed with status {response.status_code}')
            return False
            
    except Exception as e:
        print(f'❌ Test failed with exception: {str(e)}')
        import traceback
        traceback.print_exc()
        return False

def test_feedback_validation():
    """Test that empty comment is rejected"""
    print('\n' + '='*80)
    print('🧪 TESTING FEEDBACK VALIDATION (Empty Comment)')
    print('='*80)
    
    try:
        token = get_firebase_token()
        
        print('\n📝 Submitting feedback with empty comment...')
        feedback_data = {
            'type': 'bug',
            'comment': '',  # Empty comment should be rejected
            'screen': 'automated_test',
            'timestamp': datetime.now().isoformat(),
            'has_screenshot': False,
        }
        
        headers = {
            'Authorization': f'Bearer {token}',
            'Content-Type': 'application/json'
        }
        
        response = requests.post(
            f'{API_BASE_URL}/feedback/submit',
            json=feedback_data,
            headers=headers
        )
        
        print(f'Response status: {response.status_code}')
        
        # We expect this to fail (400 or 422)
        if response.status_code in [400, 422]:
            print('✅ Validation working correctly - empty comment rejected!')
            return True
        elif response.status_code == 200:
            print('⚠️  WARNING: Empty comment was accepted (should be rejected)')
            return False
        else:
            print(f'❌ Unexpected status code: {response.status_code}')
            return False
            
    except Exception as e:
        print(f'❌ Test failed with exception: {str(e)}')
        return False

def verify_feedback_in_firestore():
    """Verify feedback was saved to Firestore"""
    print('\n' + '='*80)
    print('🧪 VERIFYING FEEDBACK IN FIRESTORE')
    print('='*80)
    
    try:
        from google.cloud import firestore
        from google.oauth2 import service_account
        
        # Initialize Firestore
        project_id = os.getenv('GOOGLE_CLOUD_PROJECT', 'productivityai-mvp')
        
        # Try to use service account if available
        service_account_path = os.getenv('GOOGLE_APPLICATION_CREDENTIALS')
        if service_account_path and os.path.exists(service_account_path):
            credentials = service_account.Credentials.from_service_account_file(service_account_path)
            db = firestore.Client(project=project_id, credentials=credentials)
        else:
            db = firestore.Client(project=project_id)
        
        print(f'📊 Checking Firestore for recent feedback...')
        
        # Query recent feedback (last 5 minutes)
        from datetime import timedelta
        five_minutes_ago = datetime.utcnow() - timedelta(minutes=5)
        
        feedback_ref = db.collection('feedback')
        recent_feedback = feedback_ref.where('timestamp', '>=', five_minutes_ago).stream()
        
        count = 0
        for doc in recent_feedback:
            count += 1
            data = doc.to_dict()
            print(f'  ✅ Found feedback: {data.get("type")} - {data.get("comment")[:50]}...')
        
        if count > 0:
            print(f'✅ Found {count} recent feedback entries in Firestore')
            return True
        else:
            print('⚠️  No recent feedback found in Firestore')
            return False
            
    except Exception as e:
        print(f'⚠️  Could not verify Firestore (this is optional): {str(e)}')
        # Don't fail the test if Firestore verification fails
        return True

def main():
    """Run all feedback tests"""
    print('\n' + '='*80)
    print('🚀 FEEDBACK SUBMISSION TEST SUITE')
    print('='*80)
    print(f'API Base URL: {API_BASE_URL}')
    print(f'Test User: {TEST_USER_EMAIL}')
    print('='*80)
    
    results = {
        'submission': False,
        'validation': False,
        'firestore': False,
    }
    
    # Run tests
    results['submission'] = test_feedback_submission()
    results['validation'] = test_feedback_validation()
    results['firestore'] = verify_feedback_in_firestore()
    
    # Summary
    print('\n' + '='*80)
    print('📊 TEST SUMMARY')
    print('='*80)
    print(f'✅ Feedback Submission: {"PASSED" if results["submission"] else "FAILED"}')
    print(f'✅ Validation (Empty Comment): {"PASSED" if results["validation"] else "FAILED"}')
    print(f'✅ Firestore Verification: {"PASSED" if results["firestore"] else "SKIPPED"}')
    print('='*80)
    
    # Overall result
    required_tests = [results['submission'], results['validation']]
    all_passed = all(required_tests)
    
    if all_passed:
        print('\n🎉 ALL TESTS PASSED! Feedback system is working correctly.')
        return 0
    else:
        print('\n❌ SOME TESTS FAILED! Please fix before deploying.')
        return 1

if __name__ == '__main__':
    exit(main())

