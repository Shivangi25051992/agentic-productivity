#!/usr/bin/env python3
"""
Test script to verify Timeline API response structure
Compares fast-path vs LLM-path logs
"""

import requests
import json
from datetime import datetime, timedelta
from google.cloud import firestore
import os
import sys

# Add app to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'app'))

def get_firestore_logs(user_id: str, limit: int = 20):
    """Fetch logs directly from Firestore"""
    print("━" * 80)
    print("📊 STEP 1: Fetching logs directly from Firestore")
    print("━" * 80)
    
    db = firestore.Client()
    
    # Get today's date range
    now = datetime.now()
    start_of_day = datetime(now.year, now.month, now.day)
    end_of_day = start_of_day + timedelta(days=1)
    
    # Query fitness_logs
    logs_ref = db.collection('users').document(user_id).collection('fitness_logs')
    query = logs_ref.where('timestamp', '>=', start_of_day).where('timestamp', '<', end_of_day).order_by('timestamp', direction=firestore.Query.DESCENDING).limit(limit)
    
    logs = []
    for doc in query.stream():
        log_data = doc.to_dict()
        log_data['log_id'] = doc.id
        logs.append(log_data)
    
    print(f"\n✅ Found {len(logs)} logs in Firestore\n")
    
    # Separate by source
    fast_path_logs = [log for log in logs if log.get('ai_parsed_data', {}).get('source') == 'fast_path']
    llm_path_logs = [log for log in logs if log.get('ai_parsed_data', {}).get('source') != 'fast_path']
    
    print(f"📊 Fast-path logs: {len(fast_path_logs)}")
    print(f"📊 LLM-path logs: {len(llm_path_logs)}")
    print()
    
    # Show sample of each
    if fast_path_logs:
        print("━" * 80)
        print("🚀 FAST-PATH LOG SAMPLE (from Firestore)")
        print("━" * 80)
        sample = fast_path_logs[0]
        print(f"Content: {sample.get('content')}")
        print(f"Calories: {sample.get('calories')}")
        print(f"Timestamp: {sample.get('timestamp')}")
        print(f"\nai_parsed_data structure:")
        print(json.dumps(sample.get('ai_parsed_data', {}), indent=2))
        print()
    
    if llm_path_logs:
        print("━" * 80)
        print("🤖 LLM-PATH LOG SAMPLE (from Firestore)")
        print("━" * 80)
        sample = llm_path_logs[0]
        print(f"Content: {sample.get('content')}")
        print(f"Calories: {sample.get('calories')}")
        print(f"Timestamp: {sample.get('timestamp')}")
        print(f"\nai_parsed_data structure:")
        print(json.dumps(sample.get('ai_parsed_data', {}), indent=2))
        print()
    
    return logs, fast_path_logs, llm_path_logs


def compare_structures(fast_path_logs, llm_path_logs):
    """Compare the structure of fast-path vs LLM-path logs"""
    print("━" * 80)
    print("🔍 STEP 2: Comparing Data Structures")
    print("━" * 80)
    print()
    
    if not fast_path_logs:
        print("❌ No fast-path logs found!")
        return
    
    if not llm_path_logs:
        print("❌ No LLM-path logs found!")
        return
    
    fast_keys = set(fast_path_logs[0].get('ai_parsed_data', {}).keys())
    llm_keys = set(llm_path_logs[0].get('ai_parsed_data', {}).keys())
    
    print("📊 Fast-path ai_parsed_data keys:")
    print(f"   {sorted(fast_keys)}")
    print()
    
    print("📊 LLM-path ai_parsed_data keys:")
    print(f"   {sorted(llm_keys)}")
    print()
    
    # Find differences
    only_in_fast = fast_keys - llm_keys
    only_in_llm = llm_keys - fast_keys
    
    if only_in_fast:
        print(f"✅ Keys ONLY in fast-path: {sorted(only_in_fast)}")
    
    if only_in_llm:
        print(f"⚠️  Keys ONLY in LLM-path: {sorted(only_in_llm)}")
        print()
        print("🎯 THIS IS LIKELY THE ROOT CAUSE!")
        print(f"   Frontend might expect these keys: {sorted(only_in_llm)}")
    
    print()


def test_timeline_api(user_id: str):
    """Test the Timeline API endpoint"""
    print("━" * 80)
    print("🌐 STEP 3: Testing Timeline API Endpoint")
    print("━" * 80)
    print()
    
    # Note: This requires the backend to be running
    # We'll use a mock auth token for testing
    
    url = "http://localhost:8000/timeline"
    params = {
        "types": "meal",
        "limit": 50,
        "offset": 0,
    }
    
    print(f"📡 Calling: GET {url}")
    print(f"   Params: {params}")
    print()
    
    try:
        # This will fail without auth, but we can check the structure from Firestore
        print("⚠️  Skipping API call (requires auth token)")
        print("   Using Firestore data instead (same structure)")
        print()
    except Exception as e:
        print(f"❌ API call failed: {e}")
        print()


def analyze_timeline_transformation():
    """Analyze how Firestore logs are transformed to TimelineActivity"""
    print("━" * 80)
    print("🔄 STEP 4: Analyzing Timeline Transformation Logic")
    print("━" * 80)
    print()
    
    print("Backend transforms FitnessLog → TimelineActivity:")
    print()
    print("TimelineActivity fields:")
    print("  - id: log.log_id")
    print("  - type: log.log_type")
    print("  - title: log.content")
    print("  - timestamp: log.timestamp")
    print("  - icon: emoji based on type")
    print("  - color: color based on type")
    print("  - status: calories/duration")
    print("  - details: log.ai_parsed_data  ← THIS IS THE KEY!")
    print()
    print("🎯 Frontend receives 'details' = ai_parsed_data")
    print("   If fast-path and LLM-path have different structures,")
    print("   frontend might not render fast-path logs correctly!")
    print()


def main():
    print()
    print("=" * 80)
    print("🔬 TIMELINE API RESPONSE VERIFICATION")
    print("=" * 80)
    print()
    
    # Get user ID
    try:
        with open('/tmp/test_user_id.txt', 'r') as f:
            user_id = f.read().strip()
    except:
        print("❌ Could not read user ID from /tmp/test_user_id.txt")
        print("   Please run the previous command to extract user ID")
        return
    
    print(f"👤 User ID: {user_id}")
    print()
    
    # Step 1: Get logs from Firestore
    logs, fast_path_logs, llm_path_logs = get_firestore_logs(user_id)
    
    # Step 2: Compare structures
    compare_structures(fast_path_logs, llm_path_logs)
    
    # Step 3: Test API (skipped, using Firestore data)
    test_timeline_api(user_id)
    
    # Step 4: Analyze transformation
    analyze_timeline_transformation()
    
    # Summary
    print("━" * 80)
    print("📋 SUMMARY")
    print("━" * 80)
    print()
    print(f"✅ Total logs found: {len(logs)}")
    print(f"🚀 Fast-path logs: {len(fast_path_logs)}")
    print(f"🤖 LLM-path logs: {len(llm_path_logs)}")
    print()
    
    if fast_path_logs and llm_path_logs:
        fast_keys = set(fast_path_logs[0].get('ai_parsed_data', {}).keys())
        llm_keys = set(llm_path_logs[0].get('ai_parsed_data', {}).keys())
        missing_keys = llm_keys - fast_keys
        
        if missing_keys:
            print("🎯 ROOT CAUSE IDENTIFIED:")
            print(f"   Fast-path logs are missing these keys: {sorted(missing_keys)}")
            print()
            print("💡 RECOMMENDED FIX:")
            print(f"   Add these keys to fast-path ai_parsed_data in app/main.py")
            print()
        else:
            print("✅ Both paths have identical key structure")
            print("   Root cause must be elsewhere (frontend rendering, cache, etc.)")
            print()
    
    print("=" * 80)
    print()


if __name__ == "__main__":
    main()

