"""
Initialize LLM Provider Configuration in Firestore
===================================================
Run this script once to set up default LLM provider configuration

Usage:
    python scripts/init_llm_config.py
"""

import os
import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from google.cloud import firestore
from dotenv import load_dotenv

load_dotenv()
load_dotenv('.env.local', override=True)


def init_llm_config():
    """Initialize LLM provider configuration in Firestore"""
    
    print("🚀 [INIT] Initializing LLM provider configuration...")
    
    project = os.getenv("GOOGLE_CLOUD_PROJECT")
    if not project:
        print("❌ [INIT] GOOGLE_CLOUD_PROJECT not found in environment")
        return False
    
    try:
        db = firestore.Client(project=project)
        
        # Default LLM provider configuration
        llm_config = {
            "openai_gpt4o_mini": {
                "enabled": True,
                "priority": 1,
                "quota_per_day": 10000,
                "notes": "Primary provider - fast and cost-effective"
            },
            "openai_gpt4o": {
                "enabled": True,
                "priority": 2,
                "quota_per_day": 5000,
                "notes": "Fallback - higher quality"
            },
            "claude_35_sonnet": {
                "enabled": False,
                "priority": 3,
                "quota_per_day": 5000,
                "notes": "Disabled - pending API key"
            },
            "gemini_pro": {
                "enabled": False,
                "priority": 4,
                "quota_per_day": 5000,
                "notes": "Disabled - pending API key"
            }
        }
        
        # Save to Firestore
        config_ref = db.collection('system_config').document('llm_providers')
        config_ref.set(llm_config)
        
        print("✅ [INIT] LLM provider configuration initialized successfully")
        print(f"   Primary: openai_gpt4o_mini (enabled)")
        print(f"   Fallback: openai_gpt4o (enabled)")
        print(f"   Claude: claude_35_sonnet (disabled)")
        print(f"   Gemini: gemini_pro (disabled)")
        
        return True
        
    except Exception as e:
        print(f"❌ [INIT] Error initializing configuration: {e}")
        return False


def verify_config():
    """Verify configuration was saved correctly"""
    
    print("\n🔍 [VERIFY] Verifying configuration...")
    
    project = os.getenv("GOOGLE_CLOUD_PROJECT")
    db = firestore.Client(project=project)
    
    try:
        config_doc = db.collection('system_config').document('llm_providers').get()
        
        if config_doc.exists:
            config = config_doc.to_dict()
            print("✅ [VERIFY] Configuration found in Firestore")
            print(f"   Providers configured: {len(config)}")
            
            for provider, settings in config.items():
                status = "✅ enabled" if settings.get('enabled') else "⏸️ disabled"
                print(f"   - {provider}: {status} (priority: {settings.get('priority')})")
            
            return True
        else:
            print("❌ [VERIFY] Configuration not found in Firestore")
            return False
            
    except Exception as e:
        print(f"❌ [VERIFY] Error verifying configuration: {e}")
        return False


if __name__ == "__main__":
    print("=" * 70)
    print("LLM Provider Configuration Initializer")
    print("=" * 70)
    print()
    
    # Initialize
    success = init_llm_config()
    
    if success:
        # Verify
        verify_config()
        print()
        print("=" * 70)
        print("✅ Initialization complete!")
        print("=" * 70)
        print()
        print("Next steps:")
        print("1. Restart backend server to load new configuration")
        print("2. Test meal plan generation: POST /meal-planning/plans/generate")
        print("3. View analytics: GET /admin/llm-analytics")
        print()
    else:
        print()
        print("=" * 70)
        print("❌ Initialization failed")
        print("=" * 70)
        print()
        sys.exit(1)


