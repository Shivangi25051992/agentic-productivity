"""
Supplements, Vitamins, and Miscellaneous Foods Database
"""

SUPPLEMENTS_AND_MISC = {
    # Supplements & Vitamins
    "multivitamin": {
        "name": "Multivitamin",
        "per_piece": {"calories": 0, "protein": 0, "carbs": 0, "fat": 0, "fiber": 0},
        "portions": {"1 tablet": 1, "1 capsule": 1},
        "aliases": ["multi vitamin", "vitamin tablet", "multivitamins"]
    },
    "omega_3": {
        "name": "Omega 3 Capsule",
        "per_piece": {"calories": 10, "protein": 0, "carbs": 0, "fat": 1, "fiber": 0},
        "portions": {"1 capsule": 1, "1 softgel": 1},
        "aliases": ["omega 3", "omega3", "fish oil", "omega 3 capsule"]
    },
    "probiotic": {
        "name": "Probiotic",
        "per_piece": {"calories": 5, "protein": 0.5, "carbs": 0.5, "fat": 0, "fiber": 0},
        "portions": {"1 capsule": 1, "1 tablet": 1},
        "aliases": ["probiotics", "probiotic capsule"]
    },
    "vitamin_d": {
        "name": "Vitamin D",
        "per_piece": {"calories": 0, "protein": 0, "carbs": 0, "fat": 0, "fiber": 0},
        "portions": {"1 capsule": 1},
        "aliases": ["vit d", "vitamin d3"]
    },
    "calcium": {
        "name": "Calcium Supplement",
        "per_piece": {"calories": 5, "protein": 0, "carbs": 1, "fat": 0, "fiber": 0},
        "portions": {"1 tablet": 1},
        "aliases": ["calcium tablet", "cal supplement"]
    },
    
    # Beverages
    "water": {
        "name": "Water",
        "per_100ml": {"calories": 0, "protein": 0, "carbs": 0, "fat": 0, "fiber": 0},
        "portions": {"1 glass": 250, "1 bottle": 500, "1 litre": 1000, "1 liter": 1000},
        "aliases": ["drinking water", "mineral water", "pani"]
    },
    "green_tea": {
        "name": "Green Tea",
        "per_100ml": {"calories": 1, "protein": 0, "carbs": 0, "fat": 0, "fiber": 0},
        "portions": {"1 cup": 240},
        "aliases": ["green tea"]
    },
    "black_coffee": {
        "name": "Black Coffee",
        "per_100ml": {"calories": 2, "protein": 0.3, "carbs": 0, "fat": 0, "fiber": 0},
        "portions": {"1 cup": 240},
        "aliases": ["coffee", "black coffee"]
    },
    
    # Indian Preparations
    "egg_omlet": {
        "name": "Egg Omelet",
        "per_piece": {"calories": 140, "protein": 10, "carbs": 1, "fat": 10, "fiber": 0},
        "portions": {"1 omelet": 1, "2 egg omelet": 2},
        "aliases": ["egg omelette", "omelet", "omelette", "egg omlet", "omlet"]
    },
    "egg_dosa": {
        "name": "Egg Dosa",
        "per_piece": {"calories": 200, "protein": 8, "carbs": 25, "fat": 7, "fiber": 2},
        "portions": {"1 dosa": 1},
        "aliases": ["egg dosa", "egg dose"]
    },
    "beans_curry": {
        "name": "Beans Curry",
        "per_100g": {"calories": 50, "protein": 3, "carbs": 8, "fat": 1, "fiber": 3},
        "portions": {"1 bowl": 200, "100g": 100},
        "aliases": ["bean curry", "beans", "green beans curry"]
    },
    "rice_beans": {
        "name": "Rice with Beans",
        "per_100g": {"calories": 130, "protein": 4, "carbs": 25, "fat": 1, "fiber": 2},
        "portions": {"1 bowl": 250},
        "aliases": ["rice and beans", "rice with beans", "rice beans"]
    },
}

