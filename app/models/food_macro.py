"""
Food Macro Reference Model
Stores nutrition data for fast, accurate food logging
"""

from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime


class MacroNutrients(BaseModel):
    """Macro and micro nutrients per unit"""
    calories: float = Field(..., description="Calories per unit")
    protein_g: float = Field(..., description="Protein in grams per unit")
    carbs_g: float = Field(..., description="Carbohydrates in grams per unit")
    fat_g: float = Field(..., description="Fat in grams per unit")
    fiber_g: float = Field(0.0, description="Fiber in grams per unit")
    sugar_g: float = Field(0.0, description="Sugar in grams per unit")
    sodium_mg: float = Field(0.0, description="Sodium in milligrams per unit")
    
    # Optional micronutrients
    cholesterol_mg: Optional[float] = Field(None, description="Cholesterol in mg")
    saturated_fat_g: Optional[float] = Field(None, description="Saturated fat in g")
    trans_fat_g: Optional[float] = Field(None, description="Trans fat in g")


class FoodMacro(BaseModel):
    """
    Food Macro Reference Entry
    Stores standardized nutrition data for cache-first logging
    """
    
    # Firestore document ID
    food_id: Optional[str] = Field(None, description="Firestore document ID")
    
    # Identification
    standardized_name: str = Field(
        ..., 
        description="Standardized food name (e.g., 'egg_large_boiled')"
    )
    display_name: str = Field(
        ...,
        description="Human-readable name (e.g., 'Egg, Large, Boiled')"
    )
    aliases: List[str] = Field(
        default_factory=list,
        description="All synonyms, plurals, variants (e.g., ['egg', 'eggs', 'boiled egg'])"
    )
    category: str = Field(
        ...,
        description="Food category (protein, carbs, vegetables, fruits, dairy, fats, snacks)"
    )
    
    # Nutrition Data (per universal unit)
    unit_type: str = Field(
        ...,
        description="Universal unit type (piece, 100g, cup, oz, serving)"
    )
    macros_per_unit: MacroNutrients = Field(
        ...,
        description="Macro and micro nutrients per unit"
    )
    
    # Preparation & Context
    preparation_style: Optional[str] = Field(
        None,
        description="Preparation method (boiled, fried, grilled, raw, baked)"
    )
    default_portion: float = Field(
        1.0,
        description="Default serving size in units"
    )
    
    # Metadata
    source: str = Field(
        ...,
        description="Data source (usda_fdc, nutritionix, ai_generated, user_custom)"
    )
    source_id: Optional[str] = Field(
        None,
        description="External reference ID (e.g., FDC_1123)"
    )
    entry_origin: str = Field(
        ...,
        description="How entry was created (seed, ai, user, admin)"
    )
    verification_flag: bool = Field(
        False,
        description="Admin verified for accuracy"
    )
    confidence_score: float = Field(
        1.0,
        description="Confidence score 0.0-1.0 (1.0 = verified)"
    )
    
    # Tracking
    access_count: int = Field(
        0,
        description="Number of times this entry was used"
    )
    last_accessed: Optional[datetime] = Field(
        None,
        description="Last time this entry was accessed"
    )
    created_at: datetime = Field(
        default_factory=datetime.now,
        description="Creation timestamp"
    )
    updated_at: datetime = Field(
        default_factory=datetime.now,
        description="Last update timestamp"
    )
    created_by: Optional[str] = Field(
        None,
        description="User ID or system that created this entry"
    )
    
    class Config:
        json_schema_extra = {
            "example": {
                "standardized_name": "egg_large_boiled",
                "display_name": "Egg, Large, Boiled",
                "aliases": ["egg", "eggs", "boiled egg", "hard boiled egg", "eggz"],
                "category": "protein",
                "unit_type": "piece",
                "macros_per_unit": {
                    "calories": 70,
                    "protein_g": 6.0,
                    "carbs_g": 0.6,
                    "fat_g": 5.0,
                    "fiber_g": 0.0,
                    "sugar_g": 0.6,
                    "sodium_mg": 62.0,
                    "cholesterol_mg": 186.0,
                    "saturated_fat_g": 1.6
                },
                "preparation_style": "boiled",
                "default_portion": 2.0,
                "source": "usda_fdc",
                "source_id": "FDC_1123",
                "entry_origin": "seed",
                "verification_flag": True,
                "confidence_score": 1.0,
                "access_count": 1523
            }
        }


class FoodMacroCreate(BaseModel):
    """Schema for creating new food macro entries"""
    standardized_name: str
    display_name: str
    aliases: List[str] = []
    category: str
    unit_type: str
    macros_per_unit: MacroNutrients
    preparation_style: Optional[str] = None
    default_portion: float = 1.0
    source: str = "user_custom"
    source_id: Optional[str] = None
    entry_origin: str = "user"


class FoodMacroUpdate(BaseModel):
    """Schema for updating food macro entries"""
    display_name: Optional[str] = None
    aliases: Optional[List[str]] = None
    category: Optional[str] = None
    macros_per_unit: Optional[MacroNutrients] = None
    preparation_style: Optional[str] = None
    default_portion: Optional[float] = None
    verification_flag: Optional[bool] = None
    confidence_score: Optional[float] = None


class FoodMacroHistory(BaseModel):
    """Audit trail for food macro changes"""
    history_id: Optional[str] = None
    food_macro_id: str
    action: str  # created, updated, verified, deleted
    old_values: Optional[dict] = None
    new_values: Optional[dict] = None
    changed_by: str
    changed_at: datetime = Field(default_factory=datetime.now)
    reason: Optional[str] = None


class FoodMatchResult(BaseModel):
    """Result of fuzzy matching food input"""
    matched: bool
    food_macro: Optional[FoodMacro] = None
    confidence: float = 0.0
    match_type: str  # exact, fuzzy, partial, none
    suggestions: List[FoodMacro] = []


class PortionParseResult(BaseModel):
    """Result of parsing portion from user input"""
    quantity: float
    unit: str
    macros: MacroNutrients
    source: str
    source_id: Optional[str] = None
    cache_hit: bool = True




