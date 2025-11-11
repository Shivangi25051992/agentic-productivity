#!/usr/bin/env python3
"""
Redis Cache Test Script
Tests Redis connection and cache operations
"""

import sys
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()
load_dotenv('.env.local', override=True)

# Add app to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'app'))

def test_redis_connection():
    """Test 1: Redis Connection"""
    print("\n" + "="*60)
    print("TEST 1: Redis Connection")
    print("="*60)
    
    from app.services.redis_client import redis_client
    
    if redis_client.is_enabled:
        print("✅ Redis is ENABLED and CONNECTED")
        stats = redis_client.get_stats()
        print(f"   - Memory used: {stats.get('used_memory', 'N/A')}")
        print(f"   - Connected clients: {stats.get('connected_clients', 0)}")
        print(f"   - Uptime: {stats.get('uptime_in_seconds', 0)}s")
    else:
        print("⚠️  Redis is DISABLED or NOT CONNECTED")
        print("   - Check REDIS_ENABLED in .env")
        print("   - Check Redis is running: docker ps | grep redis")
        return False
    
    return True


def test_basic_operations():
    """Test 2: Basic Cache Operations"""
    print("\n" + "="*60)
    print("TEST 2: Basic Cache Operations (GET/SET/DELETE)")
    print("="*60)
    
    from app.services.redis_client import redis_client
    
    if not redis_client.is_enabled:
        print("⚠️  Skipping (Redis not enabled)")
        return False
    
    # Test SET
    test_key = "test:basic:key"
    test_value = {"message": "Hello Redis!", "count": 42}
    
    print(f"\n1. SET '{test_key}'")
    success = redis_client.set(test_key, test_value, ttl=60)
    if success:
        print("   ✅ SET successful")
    else:
        print("   ❌ SET failed")
        return False
    
    # Test GET
    print(f"\n2. GET '{test_key}'")
    cached = redis_client.get(test_key)
    if cached and cached == test_value:
        print(f"   ✅ GET successful: {cached}")
    else:
        print(f"   ❌ GET failed (expected {test_value}, got {cached})")
        return False
    
    # Test EXISTS
    print(f"\n3. EXISTS '{test_key}'")
    exists = redis_client.exists(test_key)
    if exists:
        print("   ✅ EXISTS successful")
    else:
        print("   ❌ EXISTS failed")
        return False
    
    # Test DELETE
    print(f"\n4. DELETE '{test_key}'")
    success = redis_client.delete(test_key)
    if success:
        print("   ✅ DELETE successful")
    else:
        print("   ❌ DELETE failed")
        return False
    
    # Verify deletion
    print(f"\n5. Verify deletion")
    cached = redis_client.get(test_key)
    if cached is None:
        print("   ✅ Key deleted successfully")
    else:
        print(f"   ❌ Key still exists: {cached}")
        return False
    
    return True


def test_cache_service():
    """Test 3: Cache Service (Timeline/Dashboard)"""
    print("\n" + "="*60)
    print("TEST 3: Cache Service (Timeline/Dashboard)")
    print("="*60)
    
    from app.services.cache_service import cache_service
    from app.services.redis_client import redis_client
    
    if not redis_client.is_enabled:
        print("⚠️  Skipping (Redis not enabled)")
        return False
    
    test_user_id = "test_user_123"
    
    # Test Timeline Cache
    print(f"\n1. Timeline Cache")
    
    # Cache MISS (first time)
    cached = cache_service.get_timeline(test_user_id)
    if cached is None:
        print("   ✅ Cache MISS (expected)")
    else:
        print(f"   ⚠️  Unexpected cache HIT: {cached}")
    
    # Set timeline data
    timeline_data = {
        "activities": [
            {"id": "1", "type": "meal", "title": "Breakfast", "calories": 500},
            {"id": "2", "type": "workout", "title": "Running", "calories": 300},
        ],
        "cached_at": "2025-11-11T10:00:00Z"
    }
    
    success = cache_service.set_timeline(test_user_id, timeline_data)
    if success:
        print("   ✅ Timeline cached successfully")
    else:
        print("   ❌ Timeline caching failed")
        return False
    
    # Cache HIT (second time)
    cached = cache_service.get_timeline(test_user_id)
    if cached and cached == timeline_data:
        print("   ✅ Cache HIT (expected)")
    else:
        print(f"   ❌ Cache HIT failed (expected {timeline_data}, got {cached})")
        return False
    
    # Test Dashboard Cache
    print(f"\n2. Dashboard Cache")
    
    dashboard_data = {
        "calories": 2000,
        "protein": 150,
        "carbs": 200,
        "fat": 65,
        "cached_at": "2025-11-11T10:00:00Z"
    }
    
    success = cache_service.set_dashboard(test_user_id, dashboard_data, date="2025-11-11")
    if success:
        print("   ✅ Dashboard cached successfully")
    else:
        print("   ❌ Dashboard caching failed")
        return False
    
    cached = cache_service.get_dashboard(test_user_id, date="2025-11-11")
    if cached and cached == dashboard_data:
        print("   ✅ Dashboard cache HIT")
    else:
        print(f"   ❌ Dashboard cache HIT failed")
        return False
    
    # Test Cache Invalidation
    print(f"\n3. Cache Invalidation")
    
    deleted = cache_service.invalidate_all_user_caches(test_user_id)
    if deleted > 0:
        print(f"   ✅ Invalidated {deleted} cache entries")
    else:
        print("   ⚠️  No cache entries deleted (might be already cleared)")
    
    # Verify invalidation
    cached_timeline = cache_service.get_timeline(test_user_id)
    cached_dashboard = cache_service.get_dashboard(test_user_id, date="2025-11-11")
    
    if cached_timeline is None and cached_dashboard is None:
        print("   ✅ Cache invalidation successful")
    else:
        print(f"   ❌ Cache invalidation failed (timeline={cached_timeline}, dashboard={cached_dashboard})")
        return False
    
    return True


def test_pattern_deletion():
    """Test 4: Pattern-Based Deletion"""
    print("\n" + "="*60)
    print("TEST 4: Pattern-Based Deletion")
    print("="*60)
    
    from app.services.redis_client import redis_client
    
    if not redis_client.is_enabled:
        print("⚠️  Skipping (Redis not enabled)")
        return False
    
    # Create multiple keys with pattern
    test_user = "test_user_456"
    keys = [
        f"timeline:{test_user}:meal,workout",
        f"timeline:{test_user}:meal",
        f"timeline:{test_user}:workout",
        f"dashboard:{test_user}:2025-11-11",
        f"dashboard:{test_user}:2025-11-12",
    ]
    
    print(f"\n1. Creating {len(keys)} test keys")
    for key in keys:
        redis_client.set(key, {"test": "data"}, ttl=60)
    print(f"   ✅ Created {len(keys)} keys")
    
    # Delete timeline keys only
    print(f"\n2. Deleting timeline:* keys")
    deleted = redis_client.delete_pattern(f"timeline:{test_user}:*")
    print(f"   ✅ Deleted {deleted} timeline keys")
    
    # Verify dashboard keys still exist
    dashboard_key = f"dashboard:{test_user}:2025-11-11"
    exists = redis_client.exists(dashboard_key)
    if exists:
        print(f"   ✅ Dashboard keys still exist (as expected)")
    else:
        print(f"   ❌ Dashboard keys were deleted (unexpected)")
        return False
    
    # Clean up
    redis_client.delete_pattern(f"dashboard:{test_user}:*")
    
    return True


def main():
    """Run all tests"""
    print("\n" + "="*60)
    print("🚀 REDIS CACHE TEST SUITE")
    print("="*60)
    
    results = {
        "Connection": test_redis_connection(),
        "Basic Operations": test_basic_operations(),
        "Cache Service": test_cache_service(),
        "Pattern Deletion": test_pattern_deletion(),
    }
    
    print("\n" + "="*60)
    print("📊 TEST RESULTS")
    print("="*60)
    
    for test_name, passed in results.items():
        status = "✅ PASSED" if passed else "❌ FAILED"
        print(f"{test_name:20s}: {status}")
    
    total = len(results)
    passed = sum(results.values())
    
    print(f"\n{passed}/{total} tests passed")
    
    if passed == total:
        print("\n🎉 All tests passed! Redis cache is working correctly.")
        return 0
    else:
        print("\n⚠️  Some tests failed. Check the output above for details.")
        return 1


if __name__ == "__main__":
    exit(main())

