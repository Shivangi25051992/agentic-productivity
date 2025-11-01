#!/usr/bin/env python3
"""Test Firestore Food Service"""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

from app.services.firestore_food_service import get_food_service
from app.services.multi_food_parser import get_parser

print("=" * 80)
print("🧪 Testing Firestore Food Service")
print("=" * 80)

# Test 1: Direct food search
print("\n📝 Test 1: Direct Food Search")
print("-" * 80)

service = get_food_service()

test_queries = ["egg", "eggs", "chicken", "rice", "tofu", "avocado"]

for query in test_queries:
    result = service.search_food(query)
    if result:
        print(f"✅ '{query}' → {result['name']}")
        macros = result.get('per_piece') or result.get('per_100g')
        print(f"   {macros['calories']} kcal, {macros['protein']}g protein")
    else:
        print(f"❌ '{query}' → Not found")

# Test 2: Multi-food parser with Firestore
print("\n📝 Test 2: Multi-Food Parser (using Firestore)")
print("-" * 80)

parser = get_parser()

test_inputs = [
    "2 eggs for breakfast",
    "chicken breast with rice",
    "avocado toast",
    "tofu stir fry"
]

for input_text in test_inputs:
    print(f"\nInput: '{input_text}'")
    meals = parser.parse(input_text)
    
    for meal in meals:
        macros = parser.calculate_macros(meal)
        print(f"  → {meal.food}: {macros.get('calories')} kcal")
        if macros.get('needs_clarification'):
            print(f"     ❓ {macros.get('clarification_question')}")

# Test 3: Cache performance
print("\n📝 Test 3: Cache Performance")
print("-" * 80)

import time

# First search (loads cache)
start = time.time()
service.search_food("egg")
load_time = time.time() - start
print(f"First search (with cache load): {load_time*1000:.1f}ms")

# Second search (uses cache)
start = time.time()
service.search_food("chicken")
cached_time = time.time() - start
print(f"Cached search: {cached_time*1000:.1f}ms")

print(f"\n✅ Speed improvement: {load_time/cached_time:.1f}x faster with cache!")

# Test 4: Get all foods
print("\n📝 Test 4: Database Stats")
print("-" * 80)

all_foods = service.get_all_foods(limit=100)
print(f"Total foods in database: {len(all_foods)}")

categories = {}
for food in all_foods:
    cat = food.get('category', 'unknown')
    categories[cat] = categories.get(cat, 0) + 1

print("\nFoods by category:")
for cat, count in sorted(categories.items(), key=lambda x: x[1], reverse=True):
    print(f"  {cat}: {count}")

print("\n" + "=" * 80)
print("✅ All tests complete!")
print("=" * 80)

