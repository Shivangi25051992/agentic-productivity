#!/usr/bin/env python3
"""
Debug the 620 kcal bug - Test what backend actually returns
"""

import sys
sys.path.insert(0, '/Users/pchintanwar/Documents/Projects-AIProductivity/agentic-productivity')

from app.services.multi_food_parser import get_parser

def test_calorie_calculation():
    """Test the exact input from user"""
    parser = get_parser()
    
    # Test individual foods
    test_cases = [
        ("eggs", "2"),
        ("rice", "1 bowl"),
        ("curd", "1 bowl"),
    ]
    
    print("\n" + "="*70)
    print("  DEBUGGING 620 KCAL BUG")
    print("="*70)
    
    for food, quantity in test_cases:
        from app.services.multi_food_parser import MealEntry
        entry = MealEntry(food=food, quantity=quantity, meal_type="lunch", meal_time=None)
        macros = parser.calculate_macros(entry)
        
        print(f"\n{food} ({quantity}):")
        print(f"  Calories: {macros['calories']}")
        print(f"  Protein: {macros['protein']}g")
        print(f"  Carbs: {macros['carbs']}g")
        print(f"  Fat: {macros['fat']}g")
        print(f"  Estimated: {macros.get('estimated', False)}")
    
    print("\n" + "="*70)
    print("  TESTING FULL PARSE")
    print("="*70)
    
    # Test full parsing
    test_input = "2 eggs, 1 bowl rice, 1 bowl curd"
    meals = parser.parse(test_input)
    
    print(f"\nInput: {test_input}")
    print(f"Detected: {len(meals)} meals\n")
    
    for i, meal in enumerate(meals, 1):
        macros = parser.calculate_macros(meal)
        print(f"{i}. {meal.food} ({meal.quantity or 'default'})")
        print(f"   Calories: {macros['calories']}")
        print(f"   Protein: {macros['protein']}g")
        print(f"   Estimated: {macros.get('estimated', False)}")
        print()

if __name__ == "__main__":
    test_calorie_calculation()


