#!/usr/bin/env python3
"""
Verify Firestore Connection for Production Deployment
Tests that we can connect to Firestore with production credentials.
"""

import sys
import os
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

def verify_firestore_connection():
    """Verify we can connect to Firestore."""
    
    try:
        # Load environment variables
        from dotenv import load_dotenv
        load_dotenv('.env.production')
        
        # Import Firestore
        from google.cloud import firestore
        
        # Get project ID
        project_id = os.getenv('GOOGLE_CLOUD_PROJECT') or os.getenv('FIREBASE_PROJECT_ID')
        
        if not project_id:
            print("❌ GOOGLE_CLOUD_PROJECT or FIREBASE_PROJECT_ID not set")
            return False
        
        print(f"🔍 Testing connection to project: {project_id}")
        
        # Initialize Firestore client
        db = firestore.Client(project=project_id)
        
        # Try to list collections (read-only operation)
        collections = list(db.collections())
        
        print(f"✅ Firestore connection successful!")
        print(f"📊 Found {len(collections)} collections:")
        for collection in collections[:5]:  # Show first 5
            print(f"   - {collection.id}")
        if len(collections) > 5:
            print(f"   ... and {len(collections) - 5} more")
        
        return True
        
    except ImportError as e:
        print(f"❌ Missing dependency: {e}")
        print("💡 Run: pip install google-cloud-firestore python-dotenv")
        return False
        
    except Exception as e:
        print(f"❌ Firestore connection failed: {e}")
        print("\n💡 Troubleshooting:")
        print("   1. Check GOOGLE_CLOUD_PROJECT in .env.production")
        print("   2. Ensure you're authenticated: gcloud auth application-default login")
        print("   3. Verify project exists: gcloud projects list")
        print("   4. Check Firestore is enabled in the project")
        return False

if __name__ == "__main__":
    print("=" * 60)
    print("🔥 FIRESTORE CONNECTION VERIFICATION")
    print("=" * 60)
    print()
    
    success = verify_firestore_connection()
    
    print()
    print("=" * 60)
    if success:
        print("✅ FIRESTORE CONNECTION: OK")
        sys.exit(0)
    else:
        print("❌ FIRESTORE CONNECTION: FAILED")
        sys.exit(1)


