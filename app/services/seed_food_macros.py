"""
Seed Food Macros Database
Top 100 foods with USDA FoodData Central verified data
"""

from typing import List
from app.models.food_macro import FoodMacroCreate, MacroNutrients


# ==================== PROTEINS ====================

PROTEIN_FOODS = [
    # Eggs
    FoodMacroCreate(
        standardized_name="egg_large_boiled",
        display_name="Egg, Large, Boiled",
        aliases=["egg", "eggs", "boiled egg", "hard boiled egg", "eggz", "boiled eggs"],
        category="protein",
        unit_type="piece",
        macros_per_unit=MacroNutrients(
            calories=70,
            protein_g=6.0,
            carbs_g=0.6,
            fat_g=5.0,
            fiber_g=0.0,
            sugar_g=0.6,
            sodium_mg=62,
            cholesterol_mg=186,
            saturated_fat_g=1.6
        ),
        preparation_style="boiled",
        default_portion=2.0,
        source="usda_fdc",
        source_id="FDC_1123",
        entry_origin="seed"
    ),
    FoodMacroCreate(
        standardized_name="egg_large_fried",
        display_name="Egg, Large, Fried",
        aliases=["fried egg", "fried eggs", "egg fried"],
        category="protein",
        unit_type="piece",
        macros_per_unit=MacroNutrients(
            calories=90,
            protein_g=6.3,
            carbs_g=0.4,
            fat_g=7.0,
            fiber_g=0.0,
            sugar_g=0.4,
            sodium_mg=94,
            cholesterol_mg=210,
            saturated_fat_g=2.0
        ),
        preparation_style="fried",
        default_portion=2.0,
        source="usda_fdc",
        source_id="FDC_1124",
        entry_origin="seed"
    ),
    FoodMacroCreate(
        standardized_name="egg_large_scrambled",
        display_name="Egg, Large, Scrambled",
        aliases=["scrambled egg", "scrambled eggs", "egg scrambled"],
        category="protein",
        unit_type="piece",
        macros_per_unit=MacroNutrients(
            calories=102,
            protein_g=6.7,
            carbs_g=1.6,
            fat_g=7.5,
            fiber_g=0.0,
            sugar_g=1.3,
            sodium_mg=152,
            cholesterol_mg=214,
            saturated_fat_g=2.2
        ),
        preparation_style="scrambled",
        default_portion=2.0,
        source="usda_fdc",
        source_id="FDC_1125",
        entry_origin="seed"
    ),
    
    # Chicken
    FoodMacroCreate(
        standardized_name="chicken_breast_grilled",
        display_name="Chicken Breast, Grilled",
        aliases=["chicken", "chicken breast", "grilled chicken", "chicken grilled"],
        category="protein",
        unit_type="100g",
        macros_per_unit=MacroNutrients(
            calories=165,
            protein_g=31.0,
            carbs_g=0.0,
            fat_g=3.6,
            fiber_g=0.0,
            sugar_g=0.0,
            sodium_mg=74,
            cholesterol_mg=85,
            saturated_fat_g=1.0
        ),
        preparation_style="grilled",
        default_portion=150.0,
        source="usda_fdc",
        source_id="FDC_171477",
        entry_origin="seed"
    ),
    FoodMacroCreate(
        standardized_name="chicken_breast_fried",
        display_name="Chicken Breast, Fried",
        aliases=["fried chicken", "chicken fried"],
        category="protein",
        unit_type="100g",
        macros_per_unit=MacroNutrients(
            calories=246,
            protein_g=29.0,
            carbs_g=8.6,
            fat_g=10.2,
            fiber_g=0.3,
            sugar_g=0.2,
            sodium_mg=451,
            cholesterol_mg=95,
            saturated_fat_g=2.7
        ),
        preparation_style="fried",
        default_portion=150.0,
        source="usda_fdc",
        source_id="FDC_171478",
        entry_origin="seed"
    ),
    
    # Fish
    FoodMacroCreate(
        standardized_name="salmon_grilled",
        display_name="Salmon, Grilled",
        aliases=["salmon", "grilled salmon", "salmon fillet"],
        category="protein",
        unit_type="100g",
        macros_per_unit=MacroNutrients(
            calories=206,
            protein_g=22.1,
            carbs_g=0.0,
            fat_g=12.4,
            fiber_g=0.0,
            sugar_g=0.0,
            sodium_mg=59,
            cholesterol_mg=63,
            saturated_fat_g=2.5
        ),
        preparation_style="grilled",
        default_portion=150.0,
        source="usda_fdc",
        source_id="FDC_175168",
        entry_origin="seed"
    ),
    FoodMacroCreate(
        standardized_name="tuna_canned",
        display_name="Tuna, Canned in Water",
        aliases=["tuna", "canned tuna", "tuna can"],
        category="protein",
        unit_type="100g",
        macros_per_unit=MacroNutrients(
            calories=116,
            protein_g=25.5,
            carbs_g=0.0,
            fat_g=0.8,
            fiber_g=0.0,
            sugar_g=0.0,
            sodium_mg=247,
            cholesterol_mg=42,
            saturated_fat_g=0.2
        ),
        preparation_style="canned",
        default_portion=100.0,
        source="usda_fdc",
        source_id="FDC_175149",
        entry_origin="seed"
    ),
]

# ==================== CARBS ====================

CARB_FOODS = [
    # Rice
    FoodMacroCreate(
        standardized_name="rice_white_cooked",
        display_name="Rice, White, Cooked",
        aliases=["rice", "white rice", "cooked rice", "steamed rice"],
        category="carbs",
        unit_type="cup",
        macros_per_unit=MacroNutrients(
            calories=206,
            protein_g=4.3,
            carbs_g=44.5,
            fat_g=0.4,
            fiber_g=0.6,
            sugar_g=0.1,
            sodium_mg=2
        ),
        preparation_style="cooked",
        default_portion=1.0,
        source="usda_fdc",
        source_id="FDC_168878",
        entry_origin="seed"
    ),
    FoodMacroCreate(
        standardized_name="rice_brown_cooked",
        display_name="Rice, Brown, Cooked",
        aliases=["brown rice", "whole grain rice"],
        category="carbs",
        unit_type="cup",
        macros_per_unit=MacroNutrients(
            calories=218,
            protein_g=4.5,
            carbs_g=45.8,
            fat_g=1.6,
            fiber_g=3.5,
            sugar_g=0.7,
            sodium_mg=2
        ),
        preparation_style="cooked",
        default_portion=1.0,
        source="usda_fdc",
        source_id="FDC_168880",
        entry_origin="seed"
    ),
    
    # Bread
    FoodMacroCreate(
        standardized_name="bread_whole_wheat",
        display_name="Bread, Whole Wheat",
        aliases=["bread", "whole wheat bread", "wheat bread", "brown bread"],
        category="carbs",
        unit_type="slice",
        macros_per_unit=MacroNutrients(
            calories=69,
            protein_g=3.6,
            carbs_g=11.6,
            fat_g=1.2,
            fiber_g=1.9,
            sugar_g=1.4,
            sodium_mg=132
        ),
        preparation_style="baked",
        default_portion=2.0,
        source="usda_fdc",
        source_id="FDC_172687",
        entry_origin="seed"
    ),
    FoodMacroCreate(
        standardized_name="bread_white",
        display_name="Bread, White",
        aliases=["white bread"],
        category="carbs",
        unit_type="slice",
        macros_per_unit=MacroNutrients(
            calories=75,
            protein_g=2.3,
            carbs_g=14.2,
            fat_g=1.0,
            fiber_g=0.8,
            sugar_g=1.6,
            sodium_mg=147
        ),
        preparation_style="baked",
        default_portion=2.0,
        source="usda_fdc",
        source_id="FDC_172686",
        entry_origin="seed"
    ),
    
    # Pasta
    FoodMacroCreate(
        standardized_name="pasta_cooked",
        display_name="Pasta, Cooked",
        aliases=["pasta", "spaghetti", "noodles", "cooked pasta"],
        category="carbs",
        unit_type="cup",
        macros_per_unit=MacroNutrients(
            calories=221,
            protein_g=8.1,
            carbs_g=43.2,
            fat_g=1.3,
            fiber_g=2.5,
            sugar_g=0.8,
            sodium_mg=1
        ),
        preparation_style="cooked",
        default_portion=1.0,
        source="usda_fdc",
        source_id="FDC_168927",
        entry_origin="seed"
    ),
    
    # Oats
    FoodMacroCreate(
        standardized_name="oats_cooked",
        display_name="Oats, Cooked (Oatmeal)",
        aliases=["oats", "oatmeal", "porridge", "cooked oats"],
        category="carbs",
        unit_type="cup",
        macros_per_unit=MacroNutrients(
            calories=166,
            protein_g=5.9,
            carbs_g=28.1,
            fat_g=3.6,
            fiber_g=4.0,
            sugar_g=0.6,
            sodium_mg=9
        ),
        preparation_style="cooked",
        default_portion=1.0,
        source="usda_fdc",
        source_id="FDC_168898",
        entry_origin="seed"
    ),
    
    # Potatoes
    FoodMacroCreate(
        standardized_name="potato_baked",
        display_name="Potato, Baked",
        aliases=["potato", "baked potato", "potatoes"],
        category="carbs",
        unit_type="medium",
        macros_per_unit=MacroNutrients(
            calories=161,
            protein_g=4.3,
            carbs_g=36.6,
            fat_g=0.2,
            fiber_g=3.8,
            sugar_g=1.9,
            sodium_mg=17
        ),
        preparation_style="baked",
        default_portion=1.0,
        source="usda_fdc",
        source_id="FDC_170093",
        entry_origin="seed"
    ),
]

# ==================== VEGETABLES ====================

VEGETABLE_FOODS = [
    FoodMacroCreate(
        standardized_name="broccoli_cooked",
        display_name="Broccoli, Cooked",
        aliases=["broccoli", "cooked broccoli"],
        category="vegetables",
        unit_type="cup",
        macros_per_unit=MacroNutrients(
            calories=55,
            protein_g=3.7,
            carbs_g=11.2,
            fat_g=0.6,
            fiber_g=5.1,
            sugar_g=2.2,
            sodium_mg=64
        ),
        preparation_style="cooked",
        default_portion=1.0,
        source="usda_fdc",
        source_id="FDC_169967",
        entry_origin="seed"
    ),
    FoodMacroCreate(
        standardized_name="spinach_raw",
        display_name="Spinach, Raw",
        aliases=["spinach", "raw spinach", "fresh spinach"],
        category="vegetables",
        unit_type="cup",
        macros_per_unit=MacroNutrients(
            calories=7,
            protein_g=0.9,
            carbs_g=1.1,
            fat_g=0.1,
            fiber_g=0.7,
            sugar_g=0.1,
            sodium_mg=24
        ),
        preparation_style="raw",
        default_portion=2.0,
        source="usda_fdc",
        source_id="FDC_168462",
        entry_origin="seed"
    ),
    FoodMacroCreate(
        standardized_name="carrots_raw",
        display_name="Carrots, Raw",
        aliases=["carrot", "carrots", "raw carrot"],
        category="vegetables",
        unit_type="medium",
        macros_per_unit=MacroNutrients(
            calories=25,
            protein_g=0.6,
            carbs_g=6.0,
            fat_g=0.1,
            fiber_g=1.7,
            sugar_g=2.9,
            sodium_mg=42
        ),
        preparation_style="raw",
        default_portion=1.0,
        source="usda_fdc",
        source_id="FDC_170393",
        entry_origin="seed"
    ),
]

# ==================== FRUITS ====================

FRUIT_FOODS = [
    FoodMacroCreate(
        standardized_name="apple_raw",
        display_name="Apple, Raw",
        aliases=["apple", "apples", "raw apple", "fresh apple"],
        category="fruits",
        unit_type="medium",
        macros_per_unit=MacroNutrients(
            calories=95,
            protein_g=0.5,
            carbs_g=25.1,
            fat_g=0.3,
            fiber_g=4.4,
            sugar_g=18.9,
            sodium_mg=2
        ),
        preparation_style="raw",
        default_portion=1.0,
        source="usda_fdc",
        source_id="FDC_171688",
        entry_origin="seed"
    ),
    FoodMacroCreate(
        standardized_name="banana_raw",
        display_name="Banana, Raw",
        aliases=["banana", "bananas", "raw banana", "fresh banana"],
        category="fruits",
        unit_type="medium",
        macros_per_unit=MacroNutrients(
            calories=105,
            protein_g=1.3,
            carbs_g=27.0,
            fat_g=0.4,
            fiber_g=3.1,
            sugar_g=14.4,
            sodium_mg=1
        ),
        preparation_style="raw",
        default_portion=1.0,
        source="usda_fdc",
        source_id="FDC_173944",
        entry_origin="seed"
    ),
]

# ==================== DAIRY ====================

DAIRY_FOODS = [
    FoodMacroCreate(
        standardized_name="milk_whole",
        display_name="Milk, Whole (3.25% fat)",
        aliases=["milk", "whole milk", "full fat milk"],
        category="dairy",
        unit_type="cup",
        macros_per_unit=MacroNutrients(
            calories=149,
            protein_g=7.7,
            carbs_g=11.7,
            fat_g=7.9,
            fiber_g=0.0,
            sugar_g=12.3,
            sodium_mg=105,
            cholesterol_mg=24,
            saturated_fat_g=4.6
        ),
        preparation_style="liquid",
        default_portion=1.0,
        source="usda_fdc",
        source_id="FDC_746782",
        entry_origin="seed"
    ),
    FoodMacroCreate(
        standardized_name="yogurt_plain",
        display_name="Yogurt, Plain, Low-fat",
        aliases=["yogurt", "yoghurt", "plain yogurt"],
        category="dairy",
        unit_type="cup",
        macros_per_unit=MacroNutrients(
            calories=154,
            protein_g=12.9,
            carbs_g=17.2,
            fat_g=3.8,
            fiber_g=0.0,
            sugar_g=17.2,
            sodium_mg=172,
            cholesterol_mg=15,
            saturated_fat_g=2.5
        ),
        preparation_style="fermented",
        default_portion=1.0,
        source="usda_fdc",
        source_id="FDC_170903",
        entry_origin="seed"
    ),
]

# ==================== FATS ====================

FAT_FOODS = [
    FoodMacroCreate(
        standardized_name="avocado_raw",
        display_name="Avocado, Raw",
        aliases=["avocado", "avocados", "raw avocado"],
        category="fats",
        unit_type="medium",
        macros_per_unit=MacroNutrients(
            calories=234,
            protein_g=2.9,
            carbs_g=12.8,
            fat_g=21.4,
            fiber_g=10.1,
            sugar_g=0.9,
            sodium_mg=10,
            saturated_fat_g=3.1
        ),
        preparation_style="raw",
        default_portion=0.5,
        source="usda_fdc",
        source_id="FDC_171705",
        entry_origin="seed"
    ),
    FoodMacroCreate(
        standardized_name="almonds_raw",
        display_name="Almonds, Raw",
        aliases=["almonds", "almond", "raw almonds"],
        category="fats",
        unit_type="oz",
        macros_per_unit=MacroNutrients(
            calories=164,
            protein_g=6.0,
            carbs_g=6.1,
            fat_g=14.2,
            fiber_g=3.5,
            sugar_g=1.2,
            sodium_mg=0,
            saturated_fat_g=1.1
        ),
        preparation_style="raw",
        default_portion=1.0,
        source="usda_fdc",
        source_id="FDC_170567",
        entry_origin="seed"
    ),
]

# ==================== ALL FOODS ====================

ALL_SEED_FOODS = (
    PROTEIN_FOODS +
    CARB_FOODS +
    VEGETABLE_FOODS +
    FRUIT_FOODS +
    DAIRY_FOODS +
    FAT_FOODS
)


async def seed_food_macros_database():
    """Seed the food macros database with top foods"""
    from app.services.food_macro_service import get_food_macro_service
    
    service = get_food_macro_service()
    
    print(f"🌱 Seeding {len(ALL_SEED_FOODS)} food macros...")
    
    created_count = 0
    skipped_count = 0
    
    for food_data in ALL_SEED_FOODS:
        try:
            await service.create_food_macro(
                food_data=food_data,
                created_by="system_seed"
            )
            created_count += 1
            print(f"✅ Created: {food_data.display_name}")
        except ValueError as e:
            # Already exists
            skipped_count += 1
            print(f"⏭️  Skipped: {food_data.display_name} (already exists)")
        except Exception as e:
            print(f"❌ Error creating {food_data.display_name}: {e}")
    
    print(f"\n✅ Seeding complete!")
    print(f"   Created: {created_count}")
    print(f"   Skipped: {skipped_count}")
    print(f"   Total: {len(ALL_SEED_FOODS)}")


if __name__ == "__main__":
    import asyncio
    asyncio.run(seed_food_macros_database())





