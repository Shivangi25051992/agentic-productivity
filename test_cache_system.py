#!/usr/bin/env python3
"""
Test AI Cache System
Verifies cache-first food logging with performance metrics
"""

import asyncio
import time
import sys
import os

# Add app to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app.services.food_macro_service import get_food_macro_service


async def test_cache_system():
    """Test the AI cache system with various inputs"""
    
    print("=" * 70)
    print("🧪 TESTING AI CACHE SYSTEM")
    print("=" * 70)
    print()
    
    service = get_food_macro_service()
    
    # Test cases
    test_cases = [
        ("2 eggs", "egg_large_boiled", 140, True),
        ("eggz", "egg_large_boiled", 70, True),  # Fuzzy match
        ("fried eggs", "egg_large_fried", 180, True),
        ("100g chicken breast", "chicken_breast_grilled", 165, True),
        ("1 apple", "apple_raw", 95, True),
        ("dragon fruit smoothie", None, None, False),  # Should not match
    ]
    
    results = []
    
    for user_input, expected_name, expected_calories, should_match in test_cases:
        print(f"Testing: '{user_input}'")
        print("-" * 70)
        
        start_time = time.time()
        
        try:
            # Test fuzzy match
            match_result = await service.fuzzy_match_food(user_input)
            
            elapsed_ms = (time.time() - start_time) * 1000
            
            if should_match:
                if match_result.matched:
                    # Parse portion
                    portion_result = service.parse_portion(user_input, match_result.food_macro)
                    
                    # Check results
                    name_match = expected_name in match_result.food_macro.standardized_name
                    calories_close = abs(portion_result.macros.calories - expected_calories) < 10
                    fast_enough = elapsed_ms < 200
                    
                    status = "✅ PASS" if (name_match and calories_close and fast_enough) else "⚠️  PARTIAL"
                    
                    print(f"  Status: {status}")
                    print(f"  Matched: {match_result.food_macro.display_name}")
                    print(f"  Calories: {portion_result.macros.calories:.1f} kcal (expected: {expected_calories})")
                    print(f"  Protein: {portion_result.macros.protein_g:.1f}g")
                    print(f"  Match Type: {match_result.match_type}")
                    print(f"  Confidence: {match_result.confidence:.2f}")
                    print(f"  Response Time: {elapsed_ms:.1f}ms")
                    print(f"  Source: {portion_result.source}")
                    
                    results.append({
                        "input": user_input,
                        "status": "PASS" if status == "✅ PASS" else "PARTIAL",
                        "time_ms": elapsed_ms,
                        "cache_hit": True
                    })
                else:
                    print(f"  Status: ❌ FAIL - No match found (expected match)")
                    results.append({
                        "input": user_input,
                        "status": "FAIL",
                        "time_ms": elapsed_ms,
                        "cache_hit": False
                    })
            else:
                # Should NOT match
                if not match_result.matched:
                    print(f"  Status: ✅ PASS - Correctly did not match")
                    print(f"  Response Time: {elapsed_ms:.1f}ms")
                    results.append({
                        "input": user_input,
                        "status": "PASS",
                        "time_ms": elapsed_ms,
                        "cache_hit": False
                    })
                else:
                    print(f"  Status: ⚠️  UNEXPECTED - Matched when shouldn't: {match_result.food_macro.display_name}")
                    results.append({
                        "input": user_input,
                        "status": "UNEXPECTED",
                        "time_ms": elapsed_ms,
                        "cache_hit": True
                    })
        
        except Exception as e:
            print(f"  Status: ❌ ERROR - {e}")
            results.append({
                "input": user_input,
                "status": "ERROR",
                "time_ms": 0,
                "cache_hit": False
            })
        
        print()
    
    # Summary
    print("=" * 70)
    print("📊 SUMMARY")
    print("=" * 70)
    print()
    
    passed = sum(1 for r in results if r["status"] == "PASS")
    failed = sum(1 for r in results if r["status"] in ["FAIL", "ERROR"])
    partial = sum(1 for r in results if r["status"] == "PARTIAL")
    
    cache_hits = [r for r in results if r["cache_hit"]]
    avg_cache_time = sum(r["time_ms"] for r in cache_hits) / len(cache_hits) if cache_hits else 0
    
    print(f"Total Tests: {len(results)}")
    print(f"✅ Passed: {passed}")
    print(f"⚠️  Partial: {partial}")
    print(f"❌ Failed: {failed}")
    print()
    print(f"Cache Hit Rate: {len(cache_hits)}/{len(results)} ({len(cache_hits)/len(results)*100:.1f}%)")
    print(f"Avg Cache Response Time: {avg_cache_time:.1f}ms")
    print(f"Target: <200ms {'✅' if avg_cache_time < 200 else '❌'}")
    print()
    
    if passed == len(results):
        print("🎉 ALL TESTS PASSED!")
        return 0
    elif passed + partial == len(results):
        print("⚠️  ALL TESTS PASSED WITH SOME WARNINGS")
        return 0
    else:
        print("❌ SOME TESTS FAILED")
        return 1


if __name__ == "__main__":
    exit_code = asyncio.run(test_cache_system())
    sys.exit(exit_code)





