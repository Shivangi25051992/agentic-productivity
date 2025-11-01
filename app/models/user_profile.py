"""
User Profile Model with Goals, Preferences, and Activity Tracking
"""
from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime
from enum import Enum


class Gender(str, Enum):
    male = "male"
    female = "female"
    other = "other"


class ActivityLevel(str, Enum):
    sedentary = "sedentary"  # Little to no exercise
    lightly_active = "lightly_active"  # 1-3 days/week
    moderately_active = "moderately_active"  # 3-5 days/week
    very_active = "very_active"  # 6-7 days/week
    extremely_active = "extremely_active"  # Athlete level


class FitnessGoal(str, Enum):
    lose_weight = "lose_weight"
    maintain = "maintain"
    gain_muscle = "gain_muscle"
    improve_fitness = "improve_fitness"


class DietPreference(str, Enum):
    none = "none"
    vegetarian = "vegetarian"
    vegan = "vegan"
    pescatarian = "pescatarian"
    keto = "keto"
    paleo = "paleo"
    low_carb = "low_carb"
    high_protein = "high_protein"


class DailyGoals(BaseModel):
    """Daily nutrition and fitness goals"""
    calories: int = Field(..., description="Daily calorie target")
    protein_g: int = Field(..., description="Daily protein target (grams)")
    carbs_g: int = Field(..., description="Daily carbs target (grams)")
    fat_g: int = Field(..., description="Daily fat target (grams)")
    fiber_g: int = Field(default=25, description="Daily fiber target (grams)")
    water_ml: int = Field(default=2000, description="Daily water target (ml)")
    steps: int = Field(default=10000, description="Daily steps target")
    workouts_per_week: int = Field(default=3, description="Target workouts per week")


class UserProfile(BaseModel):
    """Complete user profile with goals and preferences"""
    user_id: str
    
    # Basic Info
    name: str
    gender: Gender
    age: int = Field(..., ge=13, le=120)
    height_cm: int = Field(..., ge=100, le=250)
    weight_kg: float = Field(..., ge=30, le=300)
    
    # Activity & Goals
    activity_level: ActivityLevel
    fitness_goal: FitnessGoal
    target_weight_kg: Optional[float] = None
    
    # Daily Goals
    daily_goals: DailyGoals
    
    # Preferences
    diet_preference: DietPreference = DietPreference.none
    allergies: List[str] = Field(default_factory=list)
    disliked_foods: List[str] = Field(default_factory=list)
    
    # Tracking
    onboarding_completed: bool = False
    current_streak: int = 0
    total_days_logged: int = 0
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    
    # Metadata
    timezone: str = "UTC"
    units: str = "metric"  # metric or imperial


def calculate_bmr(gender: Gender, weight_kg: float, height_cm: int, age: int) -> int:
    """
    Calculate Basal Metabolic Rate using Mifflin-St Jeor Equation
    BMR = calories burned at rest
    """
    if gender == Gender.male:
        bmr = (10 * weight_kg) + (6.25 * height_cm) - (5 * age) + 5
    else:  # female or other
        bmr = (10 * weight_kg) + (6.25 * height_cm) - (5 * age) - 161
    
    return int(bmr)


def calculate_tdee(bmr: int, activity_level: ActivityLevel) -> int:
    """
    Calculate Total Daily Energy Expenditure
    TDEE = BMR × Activity Multiplier
    """
    multipliers = {
        ActivityLevel.sedentary: 1.2,
        ActivityLevel.lightly_active: 1.375,
        ActivityLevel.moderately_active: 1.55,
        ActivityLevel.very_active: 1.725,
        ActivityLevel.extremely_active: 1.9,
    }
    
    return int(bmr * multipliers[activity_level])


def calculate_calorie_goal(tdee: int, fitness_goal: FitnessGoal) -> int:
    """
    Calculate daily calorie goal based on fitness objective
    """
    if fitness_goal == FitnessGoal.lose_weight:
        # 500 cal deficit for ~0.5kg/week loss
        return max(1200, tdee - 500)
    elif fitness_goal == FitnessGoal.gain_muscle:
        # 300 cal surplus for muscle gain
        return tdee + 300
    else:  # maintain or improve_fitness
        return tdee


def calculate_macro_goals(calorie_goal: int, fitness_goal: FitnessGoal, weight_kg: float) -> dict:
    """
    Calculate macro distribution based on goal
    Returns protein, carbs, fat in grams
    """
    if fitness_goal == FitnessGoal.lose_weight:
        # High protein (35%), moderate carbs (35%), moderate fat (30%)
        protein_g = int((calorie_goal * 0.35) / 4)  # 4 cal/g
        carbs_g = int((calorie_goal * 0.35) / 4)
        fat_g = int((calorie_goal * 0.30) / 9)  # 9 cal/g
    elif fitness_goal == FitnessGoal.gain_muscle:
        # Very high protein (40%), high carbs (40%), moderate fat (20%)
        protein_g = int((calorie_goal * 0.40) / 4)
        carbs_g = int((calorie_goal * 0.40) / 4)
        fat_g = int((calorie_goal * 0.20) / 9)
    else:  # maintain or improve_fitness
        # Balanced (30% protein, 40% carbs, 30% fat)
        protein_g = int((calorie_goal * 0.30) / 4)
        carbs_g = int((calorie_goal * 0.40) / 4)
        fat_g = int((calorie_goal * 0.30) / 9)
    
    # Ensure minimum protein (1.6g per kg bodyweight for active individuals)
    min_protein = int(weight_kg * 1.6)
    protein_g = max(protein_g, min_protein)
    
    return {
        "protein_g": protein_g,
        "carbs_g": carbs_g,
        "fat_g": fat_g,
        "fiber_g": 25,  # Standard recommendation
    }


def recommend_goals(
    gender: Gender,
    age: int,
    height_cm: int,
    weight_kg: float,
    activity_level: ActivityLevel,
    fitness_goal: FitnessGoal,
    target_weight_kg: Optional[float] = None
) -> DailyGoals:
    """
    Generate recommended daily goals based on user profile
    """
    bmr = calculate_bmr(gender, weight_kg, height_cm, age)
    tdee = calculate_tdee(bmr, activity_level)
    calorie_goal = calculate_calorie_goal(tdee, fitness_goal)
    macros = calculate_macro_goals(calorie_goal, fitness_goal, weight_kg)
    
    # Calculate water goal (30ml per kg bodyweight)
    water_ml = int(weight_kg * 30)
    
    # Workout recommendations
    workout_map = {
        FitnessGoal.lose_weight: 4,
        FitnessGoal.maintain: 3,
        FitnessGoal.gain_muscle: 5,
        FitnessGoal.improve_fitness: 4,
    }
    
    return DailyGoals(
        calories=calorie_goal,
        protein_g=macros["protein_g"],
        carbs_g=macros["carbs_g"],
        fat_g=macros["fat_g"],
        fiber_g=macros["fiber_g"],
        water_ml=water_ml,
        steps=10000,
        workouts_per_week=workout_map[fitness_goal],
    )


class ProfileUpdate(BaseModel):
    """Model for updating user profile"""
    name: Optional[str] = None
    gender: Optional[Gender] = None
    age: Optional[int] = Field(None, ge=13, le=120)
    height_cm: Optional[int] = Field(None, ge=100, le=250)
    weight_kg: Optional[float] = Field(None, ge=30, le=300)
    activity_level: Optional[ActivityLevel] = None
    fitness_goal: Optional[FitnessGoal] = None
    target_weight_kg: Optional[float] = None
    diet_preference: Optional[DietPreference] = None
    allergies: Optional[List[str]] = None
    disliked_foods: Optional[List[str]] = None
    daily_goals: Optional[DailyGoals] = None
    timezone: Optional[str] = None





