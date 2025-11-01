#!/usr/bin/env python3
"""
Generate 1 week of realistic test data for regression testing
"""

import json
from datetime import datetime, timedelta
from typing import List, Dict

class TestDataGenerator:
    """Generate realistic meal and activity data for testing"""
    
    def __init__(self):
        self.indian_meals = {
            "breakfast": [
                "2 boiled eggs and 2 toast",
                "1 bowl poha with peanuts",
                "2 parathas with curd",
                "1 bowl upma",
                "2 idlis with sambar",
                "1 bowl oats with milk and banana",
                "2 dosas with chutney"
            ],
            "lunch": [
                "2 rotis, dal, rice, and sabzi",
                "1 bowl rice, rajma, and salad",
                "chicken curry with 3 rotis",
                "fish curry with rice",
                "paneer tikka with rotis",
                "chole bhature",
                "biryani with raita"
            ],
            "snack": [
                "5 almonds and 1 apple",
                "1 banana",
                "10 pistachios",
                "1 cup chai with 2 biscuits",
                "1 bowl sprouts",
                "1 fruit salad",
                "2 boiled eggs"
            ],
            "dinner": [
                "2 rotis with dal and sabzi",
                "grilled chicken with salad",
                "200g paneer tikka with vegetables",
                "fish with steamed vegetables",
                "egg curry with 2 rotis",
                "vegetable pulao with raita",
                "dal khichdi with curd"
            ]
        }
        
        self.workouts = [
            "30 min running",
            "45 min gym workout",
            "1 hour yoga",
            "20 min HIIT",
            "1 hour cycling",
            "30 min swimming",
            "45 min strength training"
        ]
        
        self.complex_inputs = [
            "i ate 2 eggs in the morning, 1 bowl of rice and 1 bowl of curd during day time, 5 pistachios during afternoon, 200gm of spinach, 1 bowl of rice in the evening",
            "breakfast: 2 parathas with curd, lunch: chicken curry with rice, snack: banana, dinner: dal and rotis",
            "morning had oats, lunch was biryani, evening snack was almonds, dinner was light salad",
            "2 eggs and toast for breakfast, rice dal sabzi for lunch, evening chai with biscuits, dinner was grilled chicken",
            "ate poha in morning, had chole bhature for lunch, evening had fruit, dinner was light khichdi"
        ]
    
    def generate_week_data(self) -> List[Dict]:
        """Generate 1 week of realistic meal data"""
        test_data = []
        start_date = datetime.now() - timedelta(days=7)
        
        for day in range(7):
            current_date = start_date + timedelta(days=day)
            day_name = current_date.strftime("%A")
            
            # Generate meals for this day
            day_data = {
                "date": current_date.strftime("%Y-%m-%d"),
                "day": day_name,
                "meals": []
            }
            
            # Breakfast (8am)
            breakfast_time = current_date.replace(hour=8, minute=0)
            day_data["meals"].append({
                "time": breakfast_time.isoformat(),
                "meal_type": "breakfast",
                "input": self.indian_meals["breakfast"][day % 7],
                "expected_category": "meal"
            })
            
            # Lunch (1pm)
            lunch_time = current_date.replace(hour=13, minute=0)
            day_data["meals"].append({
                "time": lunch_time.isoformat(),
                "meal_type": "lunch",
                "input": self.indian_meals["lunch"][day % 7],
                "expected_category": "meal"
            })
            
            # Snack (4pm)
            snack_time = current_date.replace(hour=16, minute=0)
            day_data["meals"].append({
                "time": snack_time.isoformat(),
                "meal_type": "snack",
                "input": self.indian_meals["snack"][day % 7],
                "expected_category": "meal"
            })
            
            # Dinner (8pm)
            dinner_time = current_date.replace(hour=20, minute=0)
            day_data["meals"].append({
                "time": dinner_time.isoformat(),
                "meal_type": "dinner",
                "input": self.indian_meals["dinner"][day % 7],
                "expected_category": "meal"
            })
            
            # Workout (if not Sunday)
            if day % 7 != 6:  # Skip Sunday
                workout_time = current_date.replace(hour=18, minute=0)
                day_data["meals"].append({
                    "time": workout_time.isoformat(),
                    "meal_type": "workout",
                    "input": self.workouts[day % len(self.workouts)],
                    "expected_category": "workout"
                })
            
            test_data.append(day_data)
        
        return test_data
    
    def generate_complex_test_cases(self) -> List[Dict]:
        """Generate complex multi-food test cases"""
        test_cases = []
        
        for i, input_text in enumerate(self.complex_inputs):
            test_cases.append({
                "test_id": f"complex_{i+1}",
                "input": input_text,
                "expected_meal_count": 4,  # Should parse into 4 separate meals
                "expected_meal_types": ["breakfast", "lunch", "snack", "dinner"],
                "description": "Multi-food input with time markers"
            })
        
        return test_cases
    
    def generate_edge_cases(self) -> List[Dict]:
        """Generate edge case test data"""
        return [
            {
                "test_id": "edge_1",
                "input": "eggs",
                "expected_clarification": True,
                "description": "Ambiguous input - should ask for quantity"
            },
            {
                "test_id": "edge_2",
                "input": "I ate something",
                "expected_clarification": True,
                "description": "Very vague input"
            },
            {
                "test_id": "edge_3",
                "input": "200g chicken breast, grilled",
                "expected_meal_count": 1,
                "expected_calories_range": (300, 350),
                "description": "Specific portion with preparation"
            },
            {
                "test_id": "edge_4",
                "input": "1 bowl rice",
                "expected_meal_count": 1,
                "expected_calories_range": (250, 280),
                "description": "Common Indian portion"
            },
            {
                "test_id": "edge_5",
                "input": "2 rotis with dal",
                "expected_meal_count": 1,
                "expected_food_items": ["roti", "dal"],
                "description": "Common Indian meal combo"
            }
        ]
    
    def save_to_file(self, filename: str = "test_data.json"):
        """Save all test data to JSON file"""
        data = {
            "generated_at": datetime.now().isoformat(),
            "week_data": self.generate_week_data(),
            "complex_cases": self.generate_complex_test_cases(),
            "edge_cases": self.generate_edge_cases()
        }
        
        with open(filename, 'w') as f:
            json.dump(data, f, indent=2)
        
        print(f"✅ Test data saved to {filename}")
        print(f"   - Week data: {len(data['week_data'])} days")
        print(f"   - Complex cases: {len(data['complex_cases'])}")
        print(f"   - Edge cases: {len(data['edge_cases'])}")
        
        return data

if __name__ == "__main__":
    generator = TestDataGenerator()
    data = generator.save_to_file()
    
    # Print summary
    print("\n📊 Test Data Summary:")
    print(f"Total days: {len(data['week_data'])}")
    total_meals = sum(len(day['meals']) for day in data['week_data'])
    print(f"Total meal entries: {total_meals}")
    print(f"Complex test cases: {len(data['complex_cases'])}")
    print(f"Edge cases: {len(data['edge_cases'])}")

