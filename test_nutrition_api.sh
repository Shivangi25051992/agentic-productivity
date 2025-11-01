#!/bin/bash

# Test script for enhanced nutrition API
# Run backend first: ./start-dev.sh

BASE_URL="http://localhost:8000"

echo "🧪 Testing Enhanced Nutrition API"
echo "=================================="
echo ""

# Test 1: Chat endpoint with "2 eggs"
echo "📝 Test 1: Chat with '2 eggs'"
echo "Expected: Detailed macro breakdown"
curl -s -X POST "$BASE_URL/chat" \
  -H "Content-Type: application/json" \
  -d '{"user_input":"2 eggs","type":"auto"}' | jq '.'
echo ""
echo "---"
echo ""

# Test 2: Chat with "Lunch: chicken breast 200g"
echo "📝 Test 2: Chat with 'Lunch: chicken breast 200g'"
echo "Expected: 330 cal, 62g protein"
curl -s -X POST "$BASE_URL/chat" \
  -H "Content-Type: application/json" \
  -d '{"user_input":"Lunch: chicken breast 200g","type":"auto"}' | jq '.'
echo ""
echo "---"
echo ""

# Test 3: Calculate goals for a user
echo "📝 Test 3: Calculate recommended goals"
echo "Expected: Personalized calorie and macro targets"
curl -s -X POST "$BASE_URL/profile/calculate-goals" \
  -H "Content-Type: application/json" \
  -d '{
    "gender": "male",
    "age": 25,
    "height_cm": 175,
    "weight_kg": 75,
    "activity_level": "moderately_active",
    "fitness_goal": "lose_weight"
  }' | jq '.'
echo ""
echo "---"
echo ""

# Test 4: Complex meal
echo "📝 Test 4: Chat with complex meal"
echo "Expected: Multiple items with aggregated macros"
curl -s -X POST "$BASE_URL/chat" \
  -H "Content-Type: application/json" \
  -d '{"user_input":"Breakfast: 3 eggs, oats, and banana","type":"auto"}' | jq '.'
echo ""
echo "---"
echo ""

echo "✅ Tests complete!"
echo ""
echo "🎯 Key Features Tested:"
echo "  - Comprehensive macro tracking (protein, carbs, fat, fiber, etc.)"
echo "  - Smart quantity parsing (eggs, grams, etc.)"
echo "  - Goal calculations (BMR, TDEE, macros)"
echo "  - Personalized recommendations"
echo ""
echo "📊 Sample Response for '2 eggs':"
echo "  {
    \"food\": \"Eggs\",
    \"quantity_g\": 100,
    \"calories\": 155,
    \"protein_g\": 13.0,
    \"carbs_g\": 1.1,
    \"fat_g\": 11.0,
    \"fiber_g\": 0.0,
    \"sugar_g\": 0.6,
    \"sodium_mg\": 124,
    \"cholesterol_mg\": 373,
    \"calcium_mg\": 56,
    \"iron_mg\": 1.8,
    \"vitamin_c_mg\": 0.0
  }"





