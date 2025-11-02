"""
Quick test to verify macro calculation fix
"""
import sys
sys.path.insert(0, '/Users/pchintanwar/Documents/Projects-AIProductivity/agentic-productivity')

from app.services.multi_food_parser import get_parser

def test_user_input():
    """Test the exact user input from manual testing"""
    parser = get_parser()
    
    # User's input: "2 egg Omlet+ 1 bowl of rice+ beans curry 100 gm + 1 egg dosa + 1.5 litres of water + 1 Multivitamin, 1 omega 3 capsule, 1 probiotics"
    test_input = "2 egg Omlet+ 1 bowl of rice+ beans curry 100 gm + 1 egg dosa + 1.5 litres of water + 1 Multivitamin, 1 omega 3 capsule, 1 probiotics"
    
    print("=" * 80)
    print("🧪 TESTING MACRO CALCULATION FIX")
    print("=" * 80)
    print(f"\nInput: {test_input}\n")
    
    # Parse
    meals = parser.parse(test_input)
    
    print(f"✅ Parsed {len(meals)} items:\n")
    
    total_calories = 0
    total_protein = 0
    total_carbs = 0
    total_fat = 0
    
    # Calculate macros for each
    for i, meal in enumerate(meals, 1):
        macros = parser.calculate_macros(meal)
        
        print(f"{i}. {meal.food}")
        print(f"   Quantity: {meal.quantity or 'default'}")
        print(f"   Meal Type: {meal.meal_type}")
        print(f"   Macros:")
        print(f"     • Calories: {macros['calories']} kcal")
        print(f"     • Protein: {macros['protein']}g")
        print(f"     • Carbs: {macros['carbs']}g")
        print(f"     • Fat: {macros['fat']}g")
        print(f"     • Fiber: {macros.get('fiber', 0)}g")
        
        if macros.get('estimated'):
            print(f"     ⚠️  ESTIMATED")
        if macros.get('needs_clarification'):
            print(f"     ❓ {macros.get('clarification_question')}")
        
        print()
        
        total_calories += macros['calories']
        total_protein += macros['protein']
        total_carbs += macros['carbs']
        total_fat += macros['fat']
    
    print("=" * 80)
    print("📊 TOTAL MACROS")
    print("=" * 80)
    print(f"Total Calories: {total_calories} kcal")
    print(f"Total Protein: {total_protein}g")
    print(f"Total Carbs: {total_carbs}g")
    print(f"Total Fat: {total_fat}g")
    print()
    
    # Expected values (approximate)
    expected = {
        "2 egg omelet": {"calories": 280, "protein": 20},
        "1 bowl rice": {"calories": 260, "protein": 5.4},
        "100g beans curry": {"calories": 50, "protein": 3},
        "1 egg dosa": {"calories": 200, "protein": 8},
        "1.5L water": {"calories": 0, "protein": 0},
        "1 multivitamin": {"calories": 0, "protein": 0},
        "1 omega 3": {"calories": 10, "protein": 0},
        "1 probiotic": {"calories": 5, "protein": 0.5}
    }
    
    expected_total_calories = sum(v["calories"] for v in expected.values())
    expected_total_protein = sum(v["protein"] for v in expected.values())
    
    print("=" * 80)
    print("✅ EXPECTED vs ACTUAL")
    print("=" * 80)
    print(f"Expected Total Calories: ~{expected_total_calories} kcal")
    print(f"Actual Total Calories: {total_calories} kcal")
    print(f"Difference: {abs(expected_total_calories - total_calories)} kcal")
    print()
    print(f"Expected Total Protein: ~{expected_total_protein}g")
    print(f"Actual Total Protein: {total_protein}g")
    print(f"Difference: {abs(expected_total_protein - total_protein)}g")
    print()
    
    # Check for flat values bug
    flat_values_found = False
    for meal in meals:
        macros = parser.calculate_macros(meal)
        if macros['calories'] == 200 and macros['protein'] == 10 and macros['carbs'] == 25:
            print(f"❌ FLAT VALUES BUG STILL EXISTS for: {meal.food}")
            flat_values_found = True
    
    if not flat_values_found:
        print("✅ NO FLAT VALUES FOUND - BUG IS FIXED!")
    
    print("\n" + "=" * 80)

if __name__ == "__main__":
    test_user_input()


