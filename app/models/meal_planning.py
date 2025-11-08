"""
Meal Planning Domain Models - Enterprise Architecture
Follows Domain-Driven Design (DDD) with rich domain models
"""

from pydantic import BaseModel, Field, validator
from datetime import date, datetime
from typing import List, Optional, Dict, Any
from enum import Enum
import uuid


class MealType(str, Enum):
    """Types of meals"""
    BREAKFAST = "breakfast"
    LUNCH = "lunch"
    DINNER = "dinner"
    SNACK = "snack"


class DayOfWeek(str, Enum):
    """Days of the week"""
    MONDAY = "monday"
    TUESDAY = "tuesday"
    WEDNESDAY = "wednesday"
    THURSDAY = "thursday"
    FRIDAY = "friday"
    SATURDAY = "saturday"
    SUNDAY = "sunday"


class RecipeCategory(str, Enum):
    """Recipe categories"""
    BREAKFAST = "breakfast"
    MAIN_COURSE = "main_course"
    SIDE_DISH = "side_dish"
    SALAD = "salad"
    SOUP = "soup"
    DESSERT = "dessert"
    SNACK = "snack"
    BEVERAGE = "beverage"


class CuisineType(str, Enum):
    """Cuisine types"""
    AMERICAN = "american"
    ITALIAN = "italian"
    MEXICAN = "mexican"
    ASIAN = "asian"
    INDIAN = "indian"
    MEDITERRANEAN = "mediterranean"
    MIDDLE_EASTERN = "middle_eastern"
    FUSION = "fusion"
    OTHER = "other"


class DifficultyLevel(str, Enum):
    """Recipe difficulty"""
    EASY = "easy"
    MEDIUM = "medium"
    HARD = "hard"


class DietaryTag(str, Enum):
    """Dietary tags for recipes"""
    VEGETARIAN = "vegetarian"
    VEGAN = "vegan"
    GLUTEN_FREE = "gluten_free"
    DAIRY_FREE = "dairy_free"
    KETO = "keto"
    LOW_CARB = "low_carb"
    HIGH_PROTEIN = "high_protein"
    PALEO = "paleo"
    WHOLE30 = "whole30"
    PESCATARIAN = "pescatarian"


# ============================================================================
# VALUE OBJECTS
# ============================================================================

class Ingredient(BaseModel):
    """Represents a recipe ingredient"""
    name: str
    amount: str  # "2 cups", "500g", "1 tbsp"
    category: str = "other"  # "protein", "produce", "pantry", etc.
    optional: bool = False
    notes: Optional[str] = None


class NutritionInfo(BaseModel):
    """Nutritional information per serving"""
    calories: int = Field(ge=0)
    protein_g: float = Field(ge=0)
    carbs_g: float = Field(ge=0)
    fat_g: float = Field(ge=0)
    fiber_g: float = Field(default=0, ge=0)
    sugar_g: float = Field(default=0, ge=0)
    sodium_mg: float = Field(default=0, ge=0)


class CostEstimate(BaseModel):
    """Cost estimation for recipe"""
    total_cost: float = Field(ge=0)
    cost_per_serving: float = Field(ge=0)
    currency: str = "USD"


# ============================================================================
# DOMAIN ENTITIES
# ============================================================================

class Recipe(BaseModel):
    """
    Recipe Entity - Aggregate Root
    Represents a complete recipe with all details
    """
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    name: str
    description: str
    category: RecipeCategory
    cuisine: CuisineType = CuisineType.OTHER
    difficulty: DifficultyLevel = DifficultyLevel.MEDIUM
    prep_time_minutes: int = Field(ge=0)
    cook_time_minutes: int = Field(ge=0)
    servings: int = Field(ge=1)
    ingredients: List[Ingredient]
    instructions: List[str]
    nutrition: NutritionInfo
    tags: List[DietaryTag] = []
    image_url: Optional[str] = None
    video_url: Optional[str] = None
    cost_estimate: Optional[CostEstimate] = None
    meal_prep_friendly: bool = False
    freezer_friendly: bool = False
    source: Optional[str] = None  # "user_created", "ai_generated", "imported"
    created_by: Optional[str] = None  # user_id
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    
    @property
    def total_time_minutes(self) -> int:
        """Total time to prepare recipe"""
        return self.prep_time_minutes + self.cook_time_minutes
    
    @property
    def is_quick(self) -> bool:
        """Is this a quick recipe? (<30 min)"""
        return self.total_time_minutes <= 30
    
    @property
    def is_high_protein(self) -> bool:
        """Does this recipe have high protein? (>30g)"""
        return self.nutrition.protein_g >= 30
    
    @property
    def macros_ratio(self) -> Dict[str, float]:
        """Calculate macro ratio (P:C:F)"""
        total_cals = self.nutrition.calories
        if total_cals == 0:
            return {"protein": 0, "carbs": 0, "fat": 0}
        
        protein_cals = self.nutrition.protein_g * 4
        carbs_cals = self.nutrition.carbs_g * 4
        fat_cals = self.nutrition.fat_g * 9
        
        return {
            "protein": round((protein_cals / total_cals) * 100, 1),
            "carbs": round((carbs_cals / total_cals) * 100, 1),
            "fat": round((fat_cals / total_cals) * 100, 1),
        }
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for Firestore"""
        return {
            "id": self.id,
            "name": self.name,
            "description": self.description,
            "category": self.category.value,
            "cuisine": self.cuisine.value,
            "difficulty": self.difficulty.value,
            "prep_time_minutes": self.prep_time_minutes,
            "cook_time_minutes": self.cook_time_minutes,
            "servings": self.servings,
            "ingredients": [ing.dict() for ing in self.ingredients],
            "instructions": self.instructions,
            "nutrition": self.nutrition.dict(),
            "tags": [tag.value for tag in self.tags],
            "image_url": self.image_url,
            "video_url": self.video_url,
            "cost_estimate": self.cost_estimate.dict() if self.cost_estimate else None,
            "meal_prep_friendly": self.meal_prep_friendly,
            "freezer_friendly": self.freezer_friendly,
            "source": self.source,
            "created_by": self.created_by,
            "created_at": self.created_at,
            "updated_at": self.updated_at,
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "Recipe":
        """Create from Firestore dictionary"""
        return cls(
            id=data.get("id"),
            name=data["name"],
            description=data["description"],
            category=RecipeCategory(data["category"]),
            cuisine=CuisineType(data.get("cuisine", "other")),
            difficulty=DifficultyLevel(data.get("difficulty", "medium")),
            prep_time_minutes=data["prep_time_minutes"],
            cook_time_minutes=data["cook_time_minutes"],
            servings=data["servings"],
            ingredients=[Ingredient(**ing) for ing in data["ingredients"]],
            instructions=data["instructions"],
            nutrition=NutritionInfo(**data["nutrition"]),
            tags=[DietaryTag(tag) for tag in data.get("tags", [])],
            image_url=data.get("image_url"),
            video_url=data.get("video_url"),
            cost_estimate=CostEstimate(**data["cost_estimate"]) if data.get("cost_estimate") else None,
            meal_prep_friendly=data.get("meal_prep_friendly", False),
            freezer_friendly=data.get("freezer_friendly", False),
            source=data.get("source"),
            created_by=data.get("created_by"),
            created_at=data.get("created_at", datetime.utcnow()),
            updated_at=data.get("updated_at", datetime.utcnow()),
        )


class PlannedMeal(BaseModel):
    """
    Represents a meal planned for a specific day/time
    Value Object in DDD
    """
    day: DayOfWeek
    meal_type: MealType
    recipe_id: str
    recipe_name: str
    servings: int = Field(ge=1)
    notes: Optional[str] = None
    is_prepared: bool = False
    is_logged: bool = False
    
    # Nutrition information (from LLM or recipe)
    calories: Optional[int] = None
    protein_g: Optional[float] = None
    carbs_g: Optional[float] = None
    fat_g: Optional[float] = None
    fiber_g: Optional[float] = None


class MealPlan(BaseModel):
    """
    Weekly Meal Plan - Aggregate Root
    Manages a week's worth of planned meals
    """
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    user_id: str
    week_start_date: date
    week_end_date: date
    meals: List[PlannedMeal] = []
    dietary_preferences: List[DietaryTag] = []
    daily_calorie_target: int = Field(ge=1000, le=5000)
    daily_protein_target: int = Field(ge=50, le=300)
    created_by_ai: bool = False
    ai_generation_prompt: Optional[str] = None
    is_active: bool = True
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    
    @validator('week_end_date')
    def validate_week_dates(cls, v, values):
        """Ensure week_end_date is after week_start_date"""
        if 'week_start_date' in values and v < values['week_start_date']:
            raise ValueError('week_end_date must be after week_start_date')
        return v
    
    @property
    def total_meals_planned(self) -> int:
        """Count total planned meals"""
        return len(self.meals)
    
    @property
    def meals_by_day(self) -> Dict[str, List[PlannedMeal]]:
        """Group meals by day"""
        result = {}
        for meal in self.meals:
            if meal.day.value not in result:
                result[meal.day.value] = []
            result[meal.day.value].append(meal)
        return result
    
    @property
    def completion_percentage(self) -> float:
        """Calculate how many meals are logged"""
        if not self.meals:
            return 0.0
        logged = sum(1 for m in self.meals if m.is_logged)
        return (logged / len(self.meals)) * 100
    
    def add_meal(self, meal: PlannedMeal):
        """Add a meal to the plan"""
        # Check if meal already exists for this day/type
        existing = next((m for m in self.meals if m.day == meal.day and m.meal_type == meal.meal_type), None)
        if existing:
            self.meals.remove(existing)
        self.meals.append(meal)
        self.updated_at = datetime.utcnow()
    
    def remove_meal(self, day: DayOfWeek, meal_type: MealType):
        """Remove a meal from the plan"""
        self.meals = [m for m in self.meals if not (m.day == day and m.meal_type == meal_type)]
        self.updated_at = datetime.utcnow()
    
    def mark_meal_prepared(self, day: DayOfWeek, meal_type: MealType):
        """Mark a meal as prepared"""
        meal = next((m for m in self.meals if m.day == day and m.meal_type == meal_type), None)
        if meal:
            meal.is_prepared = True
            self.updated_at = datetime.utcnow()
    
    def mark_meal_logged(self, day: DayOfWeek, meal_type: MealType):
        """Mark a meal as logged"""
        meal = next((m for m in self.meals if m.day == day and m.meal_type == meal_type), None)
        if meal:
            meal.is_logged = True
            self.updated_at = datetime.utcnow()
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for Firestore"""
        return {
            "id": self.id,
            "user_id": self.user_id,
            "week_start_date": self.week_start_date.isoformat(),
            "week_end_date": self.week_end_date.isoformat(),
            "meals": [m.dict() for m in self.meals],
            "dietary_preferences": [pref.value for pref in self.dietary_preferences],
            "daily_calorie_target": self.daily_calorie_target,
            "daily_protein_target": self.daily_protein_target,
            "created_by_ai": self.created_by_ai,
            "ai_generation_prompt": self.ai_generation_prompt,
            "is_active": self.is_active,
            "created_at": self.created_at,
            "updated_at": self.updated_at,
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "MealPlan":
        """Create from Firestore dictionary"""
        # Handle dietary_preferences - could be None, list of strings, or list of enums
        dietary_prefs = data.get("dietary_preferences", [])
        if dietary_prefs is None:
            dietary_prefs = []
        elif isinstance(dietary_prefs, list) and len(dietary_prefs) > 0:
            # Convert strings to DietaryTag enum
            dietary_prefs = [DietaryTag(pref) if isinstance(pref, str) else pref for pref in dietary_prefs]
        
        return cls(
            id=data.get("id"),
            user_id=data["user_id"],
            week_start_date=date.fromisoformat(data["week_start_date"]) if isinstance(data["week_start_date"], str) else data["week_start_date"],
            week_end_date=date.fromisoformat(data["week_end_date"]) if isinstance(data["week_end_date"], str) else data["week_end_date"],
            meals=[PlannedMeal(**m) for m in data.get("meals", [])],
            dietary_preferences=dietary_prefs,
            daily_calorie_target=data.get("daily_calorie_target", 2000),
            daily_protein_target=data.get("daily_protein_target", 150),
            created_by_ai=data.get("created_by_ai", False),
            ai_generation_prompt=data.get("ai_generation_prompt"),
            is_active=data.get("is_active", True),
            created_at=data.get("created_at", datetime.utcnow()),
            updated_at=data.get("updated_at", datetime.utcnow()),
        )


class GroceryItem(BaseModel):
    """Individual grocery item"""
    name: str
    quantity: str
    unit: str
    category: str  # "protein", "produce", "dairy", "pantry", etc.
    estimated_cost: float = Field(default=0.0, ge=0)
    is_checked: bool = False
    recipe_ids: List[str] = []  # Which recipes need this item
    alternatives: List[str] = []  # Alternative ingredients


class GroceryList(BaseModel):
    """
    Grocery List - Aggregate Root
    Generated from meal plan
    """
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    user_id: str
    meal_plan_id: str
    week_start_date: date
    items: List[GroceryItem] = []
    total_estimated_cost: float = Field(default=0.0, ge=0)
    store_suggestions: List[str] = []
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    
    @property
    def items_by_category(self) -> Dict[str, List[GroceryItem]]:
        """Group items by category"""
        result = {}
        for item in self.items:
            if item.category not in result:
                result[item.category] = []
            result[item.category].append(item)
        return result
    
    @property
    def checked_items_count(self) -> int:
        """Count checked items"""
        return sum(1 for item in self.items if item.is_checked)
    
    @property
    def completion_percentage(self) -> float:
        """Calculate shopping completion"""
        if not self.items:
            return 0.0
        return (self.checked_items_count / len(self.items)) * 100
    
    def check_item(self, item_name: str):
        """Check an item"""
        item = next((i for i in self.items if i.name == item_name), None)
        if item:
            item.is_checked = True
            self.updated_at = datetime.utcnow()
    
    def uncheck_item(self, item_name: str):
        """Uncheck an item"""
        item = next((i for i in self.items if i.name == item_name), None)
        if item:
            item.is_checked = False
            self.updated_at = datetime.utcnow()
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for Firestore"""
        return {
            "id": self.id,
            "user_id": self.user_id,
            "meal_plan_id": self.meal_plan_id,
            "week_start_date": self.week_start_date.isoformat(),
            "items": [item.dict() for item in self.items],
            "total_estimated_cost": self.total_estimated_cost,
            "store_suggestions": self.store_suggestions,
            "created_at": self.created_at,
            "updated_at": self.updated_at,
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "GroceryList":
        """Create from Firestore dictionary"""
        return cls(
            id=data.get("id"),
            user_id=data["user_id"],
            meal_plan_id=data["meal_plan_id"],
            week_start_date=date.fromisoformat(data["week_start_date"]) if isinstance(data["week_start_date"], str) else data["week_start_date"],
            items=[GroceryItem(**item) for item in data.get("items", [])],
            total_estimated_cost=data.get("total_estimated_cost", 0.0),
            store_suggestions=data.get("store_suggestions", []),
            created_at=data.get("created_at", datetime.utcnow()),
            updated_at=data.get("updated_at", datetime.utcnow()),
        )


# ============================================================================
# DTOs (Data Transfer Objects)
# ============================================================================

class GenerateMealPlanRequest(BaseModel):
    """Request to generate a meal plan"""
    week_start_date: date
    dietary_preferences: List[DietaryTag] = []
    daily_calorie_target: int = Field(ge=1000, le=5000)
    daily_protein_target: int = Field(ge=50, le=300)
    prep_time_preference: str = "medium"  # "quick", "medium", "elaborate"
    budget_per_week: Optional[float] = None
    num_people: int = Field(default=1, ge=1, le=10)
    meal_types: List[MealType] = [MealType.BREAKFAST, MealType.LUNCH, MealType.DINNER]
    favorite_cuisines: List[CuisineType] = []
    disliked_ingredients: List[str] = []


class RecipeSearchQuery(BaseModel):
    """Query for searching recipes"""
    query: str = ""
    category: Optional[RecipeCategory] = None
    cuisine: Optional[CuisineType] = None
    difficulty: Optional[DifficultyLevel] = None
    max_prep_time: Optional[int] = None
    tags: List[DietaryTag] = []
    max_calories: Optional[int] = None
    min_protein: Optional[int] = None
    limit: int = Field(default=20, ge=1, le=100)

