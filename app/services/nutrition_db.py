"""
Comprehensive Nutrition Database with Macros and Micronutrients
Data per 100g unless otherwise specified
"""
from typing import Optional, Dict, Any
import re


class NutritionData:
    """Nutrition information for a food item"""
    def __init__(
        self,
        name: str,
        calories: int,
        protein_g: float,
        carbs_g: float,
        fat_g: float,
        fiber_g: float = 0,
        sugar_g: float = 0,
        sodium_mg: int = 0,
        cholesterol_mg: int = 0,
        calcium_mg: int = 0,
        iron_mg: float = 0,
        vitamin_c_mg: float = 0,
        serving_size_g: int = 100,
    ):
        self.name = name
        self.calories = calories
        self.protein_g = protein_g
        self.carbs_g = carbs_g
        self.fat_g = fat_g
        self.fiber_g = fiber_g
        self.sugar_g = sugar_g
        self.sodium_mg = sodium_mg
        self.cholesterol_mg = cholesterol_mg
        self.calcium_mg = calcium_mg
        self.iron_mg = iron_mg
        self.vitamin_c_mg = vitamin_c_mg
        self.serving_size_g = serving_size_g

    def scale(self, grams: int) -> Dict[str, Any]:
        """Scale nutrition data to specified grams"""
        factor = grams / self.serving_size_g
        return {
            "food": self.name,
            "quantity_g": grams,
            "calories": round(self.calories * factor),
            "protein_g": round(self.protein_g * factor, 1),
            "carbs_g": round(self.carbs_g * factor, 1),
            "fat_g": round(self.fat_g * factor, 1),
            "fiber_g": round(self.fiber_g * factor, 1),
            "sugar_g": round(self.sugar_g * factor, 1),
            "sodium_mg": round(self.sodium_mg * factor),
            "cholesterol_mg": round(self.cholesterol_mg * factor),
            "calcium_mg": round(self.calcium_mg * factor),
            "iron_mg": round(self.iron_mg * factor, 1),
            "vitamin_c_mg": round(self.vitamin_c_mg * factor, 1),
        }


# Comprehensive nutrition database (per 100g)
NUTRITION_DB = {
    # Proteins
    "chicken breast": NutritionData("Chicken Breast", 165, 31, 0, 3.6, 0, 0, 74, 85, 15, 0.9, 0),
    "chicken": NutritionData("Chicken", 165, 31, 0, 3.6, 0, 0, 74, 85, 15, 0.9, 0),
    "salmon": NutritionData("Salmon", 208, 20, 0, 13, 0, 0, 59, 63, 12, 0.8, 0),
    "tuna": NutritionData("Tuna", 132, 28, 0, 1.3, 0, 0, 47, 50, 10, 1.3, 0),
    "egg": NutritionData("Egg", 155, 13, 1.1, 11, 0, 0.6, 124, 373, 56, 1.8, 0, 50),  # per egg ~50g
    "eggs": NutritionData("Eggs", 155, 13, 1.1, 11, 0, 0.6, 124, 373, 56, 1.8, 0, 50),
    "greek yogurt": NutritionData("Greek Yogurt", 97, 10, 3.6, 5, 0, 3.6, 36, 10, 110, 0.1, 1),
    "cottage cheese": NutritionData("Cottage Cheese", 98, 11, 3.4, 4.3, 0, 2.7, 364, 12, 83, 0.1, 0),
    "tofu": NutritionData("Tofu", 76, 8, 1.9, 4.8, 0.3, 0.7, 7, 0, 350, 5.4, 0.1),
    "beef": NutritionData("Beef", 250, 26, 0, 15, 0, 0, 72, 90, 18, 2.6, 0),
    "pork": NutritionData("Pork", 242, 27, 0, 14, 0, 0, 62, 80, 19, 0.9, 0),
    "turkey": NutritionData("Turkey", 135, 30, 0, 1.5, 0, 0, 70, 70, 21, 1.4, 0),
    "shrimp": NutritionData("Shrimp", 99, 24, 0.2, 0.3, 0, 0, 111, 189, 70, 0.5, 0),
    
    # Carbs
    "rice": NutritionData("Rice", 130, 2.7, 28, 0.3, 0.4, 0.1, 1, 0, 10, 0.2, 0),
    "brown rice": NutritionData("Brown Rice", 112, 2.6, 24, 0.9, 1.8, 0.2, 5, 0, 10, 0.4, 0),
    "quinoa": NutritionData("Quinoa", 120, 4.4, 21, 1.9, 2.8, 0.9, 7, 0, 17, 1.5, 0),
    "oats": NutritionData("Oats", 389, 17, 66, 6.9, 10.6, 0.9, 2, 0, 54, 4.7, 0),
    "bread": NutritionData("Bread", 265, 9, 49, 3.2, 2.7, 4.3, 491, 0, 151, 3.6, 0),
    "whole wheat bread": NutritionData("Whole Wheat Bread", 247, 13, 41, 3.4, 6.8, 3.5, 443, 0, 107, 2.5, 0),
    "pasta": NutritionData("Pasta", 131, 5, 25, 1.1, 0.9, 0.6, 1, 0, 7, 0.5, 0),
    "potato": NutritionData("Potato", 77, 2, 17, 0.1, 2.1, 0.8, 6, 0, 12, 0.8, 19.7),
    "sweet potato": NutritionData("Sweet Potato", 86, 1.6, 20, 0.1, 3, 4.2, 55, 0, 30, 0.6, 2.4),
    "banana": NutritionData("Banana", 89, 1.1, 23, 0.3, 2.6, 12, 1, 0, 5, 0.3, 8.7),
    "apple": NutritionData("Apple", 52, 0.3, 14, 0.2, 2.4, 10, 1, 0, 6, 0.1, 4.6),
    "orange": NutritionData("Orange", 47, 0.9, 12, 0.1, 2.4, 9, 0, 0, 40, 0.1, 53.2),
    
    # Vegetables
    "broccoli": NutritionData("Broccoli", 34, 2.8, 7, 0.4, 2.6, 1.7, 33, 0, 47, 0.7, 89.2),
    "spinach": NutritionData("Spinach", 23, 2.9, 3.6, 0.4, 2.2, 0.4, 79, 0, 99, 2.7, 28.1),
    "carrot": NutritionData("Carrot", 41, 0.9, 10, 0.2, 2.8, 4.7, 69, 0, 33, 0.3, 5.9),
    "tomato": NutritionData("Tomato", 18, 0.9, 3.9, 0.2, 1.2, 2.6, 5, 0, 10, 0.3, 13.7),
    "lettuce": NutritionData("Lettuce", 15, 1.4, 2.9, 0.2, 1.3, 0.8, 28, 0, 36, 0.9, 9.2),
    "cucumber": NutritionData("Cucumber", 15, 0.7, 3.6, 0.1, 0.5, 1.7, 2, 0, 16, 0.3, 2.8),
    "bell pepper": NutritionData("Bell Pepper", 31, 1, 6, 0.3, 2.1, 4.2, 4, 0, 7, 0.4, 127.7),
    "avocado": NutritionData("Avocado", 160, 2, 9, 15, 7, 0.7, 7, 0, 12, 0.6, 10),
    
    # Nuts & Seeds
    "almonds": NutritionData("Almonds", 579, 21, 22, 50, 12.5, 4.4, 1, 0, 269, 3.7, 0),
    "peanuts": NutritionData("Peanuts", 567, 26, 16, 49, 8.5, 4.7, 18, 0, 92, 4.6, 0),
    "walnuts": NutritionData("Walnuts", 654, 15, 14, 65, 6.7, 2.6, 2, 0, 98, 2.9, 1.3),
    "chia seeds": NutritionData("Chia Seeds", 486, 17, 42, 31, 34.4, 0, 16, 0, 631, 7.7, 1.6),
    "peanut butter": NutritionData("Peanut Butter", 588, 25, 20, 50, 6, 9, 476, 0, 49, 1.9, 0),
    
    # Dairy
    "milk": NutritionData("Milk", 61, 3.2, 4.8, 3.3, 0, 5.1, 44, 12, 113, 0, 0),
    "cheese": NutritionData("Cheese", 402, 25, 1.3, 33, 0, 0.5, 621, 105, 721, 0.7, 0),
    "yogurt": NutritionData("Yogurt", 59, 3.5, 4.7, 3.3, 0, 4.7, 46, 13, 121, 0.1, 0.5),
    
    # Beverages
    "protein shake": NutritionData("Protein Shake", 103, 20, 3, 1.5, 0, 2, 120, 5, 150, 0.5, 0),
    "smoothie": NutritionData("Smoothie", 85, 2, 18, 0.5, 2, 14, 25, 0, 80, 0.5, 30),
    
    # Fast Food / Common Meals
    "pizza": NutritionData("Pizza", 266, 11, 33, 10, 2.3, 3.6, 598, 17, 184, 2.5, 1.5),
    "burger": NutritionData("Burger", 295, 17, 24, 14, 1.5, 4, 497, 52, 92, 2.7, 1),
    "sandwich": NutritionData("Sandwich", 250, 12, 30, 9, 2, 3, 550, 30, 100, 2, 2),
    "salad": NutritionData("Salad", 20, 1.5, 3.5, 0.3, 1.8, 1.5, 25, 0, 40, 1, 15),
    "bowl": NutritionData("Bowl", 150, 8, 22, 4, 3, 2, 300, 20, 50, 1.5, 10),
}


def find_food(text: str) -> Optional[NutritionData]:
    """
    Find food in database by matching keywords in text.
    Returns the best match or None.
    """
    text_lower = text.lower()
    
    # Try exact matches first
    for key, data in NUTRITION_DB.items():
        if key in text_lower:
            return data
    
    # Try partial matches
    for key, data in NUTRITION_DB.items():
        words = key.split()
        if any(word in text_lower for word in words):
            return data
    
    return None


def parse_quantity(text: str) -> Optional[int]:
    """
    Extract quantity in grams from text.
    Supports: "200g", "2 eggs", "1 cup", "100ml", etc.
    """
    text_lower = text.lower()
    
    # Look for explicit grams
    match = re.search(r'(\d+)\s*(g|gm|grams?)', text_lower)
    if match:
        return int(match.group(1))
    
    # Look for ml (approximate as grams for liquids)
    match = re.search(r'(\d+)\s*(ml|mL)', text_lower)
    if match:
        return int(match.group(1))
    
    # Look for eggs (assume 50g per egg)
    match = re.search(r'(\d+)\s*eggs?', text_lower)
    if match:
        return int(match.group(1)) * 50
    
    # Look for cups (approximate 240g for most foods)
    match = re.search(r'(\d+)\s*cups?', text_lower)
    if match:
        return int(match.group(1)) * 240
    
    # Look for tablespoons (approximate 15g)
    match = re.search(r'(\d+)\s*(tbsp|tablespoons?)', text_lower)
    if match:
        return int(match.group(1)) * 15
    
    # Look for teaspoons (approximate 5g)
    match = re.search(r'(\d+)\s*(tsp|teaspoons?)', text_lower)
    if match:
        return int(match.group(1)) * 5
    
    # Look for slices (bread ~30g, cheese ~20g)
    match = re.search(r'(\d+)\s*slices?', text_lower)
    if match:
        return int(match.group(1)) * 30
    
    # Look for pieces/servings (approximate 100g)
    match = re.search(r'(\d+)\s*(piece|serving|portion)s?', text_lower)
    if match:
        return int(match.group(1)) * 100
    
    # Default: 100g if no quantity specified
    return 100


def get_nutrition_info(text: str) -> Optional[Dict[str, Any]]:
    """
    Get complete nutrition information for food mentioned in text.
    Returns scaled nutrition data or None if food not found.
    """
    food = find_food(text)
    if not food:
        return None
    
    quantity = parse_quantity(text)
    if not quantity:
        quantity = 100  # default
    
    return food.scale(quantity)


def estimate_meal_nutrition(items: list[str]) -> Dict[str, Any]:
    """
    Estimate total nutrition for a meal with multiple items.
    Returns aggregated macros.
    """
    total = {
        "calories": 0,
        "protein_g": 0,
        "carbs_g": 0,
        "fat_g": 0,
        "fiber_g": 0,
        "sugar_g": 0,
        "sodium_mg": 0,
        "cholesterol_mg": 0,
        "calcium_mg": 0,
        "iron_mg": 0,
        "vitamin_c_mg": 0,
        "items": []
    }
    
    for item in items:
        info = get_nutrition_info(item)
        if info:
            total["items"].append(info)
            for key in ["calories", "protein_g", "carbs_g", "fat_g", "fiber_g", 
                       "sugar_g", "sodium_mg", "cholesterol_mg", "calcium_mg", 
                       "iron_mg", "vitamin_c_mg"]:
                total[key] += info[key]
    
    # Round totals
    for key in total:
        if isinstance(total[key], (int, float)) and key != "items":
            if "_g" in key or "_mg" in key:
                total[key] = round(total[key], 1)
            else:
                total[key] = round(total[key])
    
    return total





