"""
Indian Food Database with Accurate Macros
Per 100g unless otherwise specified
"""

INDIAN_FOODS = {
    # GRAINS & BREADS
    "rice": {
        "name": "Rice, cooked",
        "per_100g": {"calories": 130, "protein": 2.7, "carbs": 28, "fat": 0.3, "fiber": 0.4},
        "portions": {"1 bowl": 200, "1 cup": 150, "1 plate": 250},
        "aliases": ["chawal", "rice cooked", "white rice"]
    },
    "brown_rice": {
        "name": "Brown Rice, cooked",
        "per_100g": {"calories": 112, "protein": 2.6, "carbs": 24, "fat": 0.9, "fiber": 1.8},
        "portions": {"1 bowl": 200, "1 cup": 150},
        "aliases": ["brown chawal"]
    },
    "roti": {
        "name": "Roti/Chapati",
        "per_piece": {"calories": 120, "protein": 3.5, "carbs": 22, "fat": 2.5, "fiber": 2.5},
        "portions": {"1 roti": 1, "1 chapati": 1, "1 phulka": 1},
        "aliases": ["chapati", "phulka", "fulka"]
    },
    "paratha": {
        "name": "Paratha",
        "per_piece": {"calories": 200, "protein": 4, "carbs": 28, "fat": 8, "fiber": 2},
        "portions": {"1 paratha": 1},
        "aliases": ["parantha"]
    },
    "naan": {
        "name": "Naan",
        "per_piece": {"calories": 260, "protein": 7, "carbs": 45, "fat": 5, "fiber": 2},
        "portions": {"1 naan": 1},
        "aliases": []
    },
    
    # LENTILS & LEGUMES
    "dal": {
        "name": "Dal (cooked)",
        "per_100g": {"calories": 105, "protein": 7, "carbs": 18, "fat": 0.4, "fiber": 5},
        "portions": {"1 bowl": 200, "1 cup": 200, "1 katori": 150},
        "aliases": ["daal", "lentils", "toor dal", "moong dal"]
    },
    "rajma": {
        "name": "Rajma (kidney beans)",
        "per_100g": {"calories": 127, "protein": 8.7, "carbs": 22.8, "fat": 0.5, "fiber": 6.4},
        "portions": {"1 bowl": 200, "1 cup": 200},
        "aliases": ["kidney beans", "red beans"]
    },
    "chole": {
        "name": "Chole (chickpeas)",
        "per_100g": {"calories": 164, "protein": 8.9, "carbs": 27.4, "fat": 2.6, "fiber": 7.6},
        "portions": {"1 bowl": 200, "1 cup": 200},
        "aliases": ["chana", "chickpeas", "garbanzo beans"]
    },
    
    # DAIRY
    "curd": {
        "name": "Curd/Dahi",
        "per_100g": {"calories": 60, "protein": 3.5, "carbs": 4.7, "fat": 3.3, "fiber": 0},
        "portions": {"1 bowl": 200, "1 cup": 240, "1 katori": 150},
        "aliases": ["dahi", "yogurt", "yoghurt"]
    },
    "paneer": {
        "name": "Paneer",
        "per_100g": {"calories": 265, "protein": 18, "carbs": 1.2, "fat": 20.8, "fiber": 0},
        "portions": {"1 piece": 50, "100g": 100},
        "aliases": ["cottage cheese"]
    },
    "milk": {
        "name": "Milk, whole",
        "per_100ml": {"calories": 61, "protein": 3.2, "carbs": 4.8, "fat": 3.3, "fiber": 0},
        "portions": {"1 glass": 250, "1 cup": 240},
        "aliases": ["doodh"]
    },
    
    # VEGETABLES
    "spinach": {
        "name": "Spinach, cooked",
        "per_100g": {"calories": 23, "protein": 2.9, "carbs": 3.6, "fat": 0.4, "fiber": 2.2},
        "portions": {"1 bowl": 150, "1 cup": 180},
        "aliases": ["palak", "saag"]
    },
    "potato": {
        "name": "Potato, cooked",
        "per_100g": {"calories": 87, "protein": 2, "carbs": 20, "fat": 0.1, "fiber": 1.8},
        "portions": {"1 medium": 150, "1 large": 200},
        "aliases": ["aloo", "alu"]
    },
    "tomato": {
        "name": "Tomato",
        "per_100g": {"calories": 18, "protein": 0.9, "carbs": 3.9, "fat": 0.2, "fiber": 1.2},
        "portions": {"1 medium": 120, "1 large": 180},
        "aliases": ["tamatar"]
    },
    "onion": {
        "name": "Onion",
        "per_100g": {"calories": 40, "protein": 1.1, "carbs": 9.3, "fat": 0.1, "fiber": 1.7},
        "portions": {"1 medium": 110, "1 large": 150},
        "aliases": ["pyaz", "pyaaz"]
    },
    
    # PROTEINS
    "egg": {
        "name": "Egg",
        "per_piece": {"calories": 70, "protein": 6, "carbs": 0.5, "fat": 5, "fiber": 0},
        "portions": {"1 egg": 1, "2 eggs": 2},
        "preparations": {"boiled": 1.0, "fried": 1.3, "scrambled": 1.2, "omelette": 1.2},
        "aliases": ["anda", "eggs", "boiled eggs", "boiled egg"]
    },
    "chicken_breast": {
        "name": "Chicken Breast, cooked",
        "per_100g": {"calories": 165, "protein": 31, "carbs": 0, "fat": 3.6, "fiber": 0},
        "portions": {"100g": 100, "200g": 200, "1 piece": 150},
        "preparations": {"grilled": 1.0, "fried": 1.4, "curry": 1.3},
        "aliases": ["chicken", "murgh"]
    },
    "fish": {
        "name": "Fish, cooked",
        "per_100g": {"calories": 206, "protein": 22, "carbs": 0, "fat": 12, "fiber": 0},
        "portions": {"100g": 100, "1 piece": 150},
        "preparations": {"grilled": 1.0, "fried": 1.3, "curry": 1.2},
        "aliases": ["machli", "macchi"]
    },
    
    # SNACKS & NUTS
    "almond": {
        "name": "Almonds",
        "per_piece": {"calories": 7, "protein": 0.26, "carbs": 0.24, "fat": 0.61, "fiber": 0.14},
        "portions": {"10 almonds": 10, "handful": 15},
        "aliases": ["badam"]
    },
    "pistachio": {
        "name": "Pistachios",
        "per_piece": {"calories": 3, "protein": 0.12, "carbs": 0.16, "fat": 0.26, "fiber": 0.06},
        "portions": {"10 pistachios": 10, "handful": 20},
        "aliases": ["pista", "pistachios"]
    },
    "cashew": {
        "name": "Cashews",
        "per_piece": {"calories": 9, "protein": 0.3, "carbs": 0.5, "fat": 0.7, "fiber": 0.05},
        "portions": {"10 cashews": 10, "handful": 15},
        "aliases": ["kaju"]
    },
    
    # FRUITS
    "banana": {
        "name": "Banana",
        "per_piece": {"calories": 105, "protein": 1.3, "carbs": 27, "fat": 0.4, "fiber": 3.1},
        "portions": {"1 banana": 1, "1 medium": 1},
        "aliases": ["kela"]
    },
    "apple": {
        "name": "Apple",
        "per_piece": {"calories": 95, "protein": 0.5, "carbs": 25, "fat": 0.3, "fiber": 4.4},
        "portions": {"1 apple": 1, "1 medium": 1},
        "aliases": ["seb"]
    },
    "mango": {
        "name": "Mango",
        "per_100g": {"calories": 60, "protein": 0.8, "carbs": 15, "fat": 0.4, "fiber": 1.6},
        "portions": {"1 mango": 200, "1 slice": 50},
        "aliases": ["aam"]
    },
    
    # POPULAR DISHES
    "biryani": {
        "name": "Biryani",
        "per_100g": {"calories": 150, "protein": 8, "carbs": 20, "fat": 4, "fiber": 1},
        "portions": {"1 plate": 300, "1 bowl": 250},
        "aliases": []
    },
    "khichdi": {
        "name": "Khichdi",
        "per_100g": {"calories": 120, "protein": 4, "carbs": 20, "fat": 2, "fiber": 2},
        "portions": {"1 bowl": 200, "1 plate": 250},
        "aliases": ["khichadi"]
    },
    "poha": {
        "name": "Poha",
        "per_100g": {"calories": 130, "protein": 2.5, "carbs": 25, "fat": 2, "fiber": 1.5},
        "portions": {"1 bowl": 150, "1 plate": 200},
        "aliases": ["pauwa", "chivda"]
    },
    "upma": {
        "name": "Upma",
        "per_100g": {"calories": 135, "protein": 3, "carbs": 22, "fat": 3.5, "fiber": 2},
        "portions": {"1 bowl": 150, "1 plate": 200},
        "aliases": []
    },
    "idli": {
        "name": "Idli",
        "per_piece": {"calories": 39, "protein": 2, "carbs": 8, "fat": 0.1, "fiber": 0.3},
        "portions": {"1 idli": 1, "2 idlis": 2, "3 idlis": 3},
        "aliases": []
    },
    "dosa": {
        "name": "Dosa",
        "per_piece": {"calories": 133, "protein": 4, "carbs": 25, "fat": 1.5, "fiber": 1},
        "portions": {"1 dosa": 1},
        "aliases": ["dosai"]
    },
    
    # BEVERAGES
    "chai": {
        "name": "Chai (tea with milk)",
        "per_cup": {"calories": 60, "protein": 1.5, "carbs": 10, "fat": 1.5, "fiber": 0},
        "portions": {"1 cup": 1, "1 glass": 1},
        "aliases": ["tea", "chay"]
    },
    "coffee": {
        "name": "Coffee with milk",
        "per_cup": {"calories": 50, "protein": 1.2, "carbs": 8, "fat": 1, "fiber": 0},
        "portions": {"1 cup": 1},
        "aliases": []
    }
}

def get_food_info(food_name: str):
    """Get food info by name or alias"""
    food_name_lower = food_name.lower().strip()
    
    # Direct match
    if food_name_lower in INDIAN_FOODS:
        return INDIAN_FOODS[food_name_lower]
    
    # Check aliases
    for key, food in INDIAN_FOODS.items():
        if food_name_lower in [alias.lower() for alias in food.get('aliases', [])]:
            return food
    
    return None

def search_foods(query: str):
    """Search foods by partial name"""
    query_lower = query.lower().strip()
    results = []
    
    for key, food in INDIAN_FOODS.items():
        if query_lower in key.lower() or query_lower in food['name'].lower():
            results.append((key, food))
        else:
            # Check aliases
            for alias in food.get('aliases', []):
                if query_lower in alias.lower():
                    results.append((key, food))
                    break
    
    return results

# Export for easy import
__all__ = ['INDIAN_FOODS', 'get_food_info', 'search_foods']

