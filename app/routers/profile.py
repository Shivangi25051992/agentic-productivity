"""
User Profile Management Endpoints
Handles onboarding, profile CRUD, and goal calculations
"""
from fastapi import APIRouter, HTTPException, Depends, Header
from typing import Optional
from datetime import datetime

from app.models.user_profile import (
    UserProfile,
    ProfileUpdate,
    Gender,
    ActivityLevel,
    FitnessGoal,
    DietPreference,
    DailyGoals,
    recommend_goals,
    calculate_bmr,
    calculate_tdee,
)
from app.services.auth import get_current_user, verify_firebase_id_token, _extract_bearer_token
from app.services.database import create_user, get_user
from app.models.user import User
from pydantic import BaseModel

router = APIRouter(prefix="/profile", tags=["profile"])


# Request models
class GoalCalculationRequest(BaseModel):
    gender: Gender
    age: int
    height_cm: int
    weight_kg: float
    activity_level: ActivityLevel
    fitness_goal: FitnessGoal
    target_weight_kg: Optional[float] = None


class OnboardRequest(BaseModel):
    name: str
    gender: Gender
    age: int
    height_cm: int
    weight_kg: float
    activity_level: ActivityLevel
    fitness_goal: FitnessGoal
    target_weight_kg: Optional[float] = None
    diet_preference: DietPreference = DietPreference.none
    allergies: list[str] = []
    disliked_foods: list[str] = []


# Firestore collection for profiles
from google.cloud import firestore
import os

def _get_firestore_db():
    """Get Firestore client"""
    project = os.getenv("GOOGLE_CLOUD_PROJECT", "productivityai-mvp")
    return firestore.Client(project=project)

PROFILES_COLLECTION = "user_profiles"


@router.post("/onboard")
def onboard_user(
    request: OnboardRequest,
    authorization: Optional[str] = Header(default=None),
):
    """
    Complete user onboarding with personalized goal recommendations.
    
    This endpoint:
    1. Verifies Firebase auth token and creates user if needed
    2. Calculates BMR and TDEE
    3. Recommends daily calorie and macro goals
    4. Creates user profile
    5. Returns personalized recommendations
    """
    # Verify Firebase token and get/create user
    token = _extract_bearer_token(authorization)
    claims = verify_firebase_id_token(token)
    uid = claims.get("uid")
    email = claims.get("email")
    
    if not uid or not email:
        raise HTTPException(status_code=401, detail="Invalid token: missing claims")
    
    # Check if user exists, if not create them
    existing_user = get_user(uid)
    if not existing_user:
        # Create new user in database (first time onboarding)
        new_user = User(
            user_id=uid,
            email=email,
            name=request.name,
            created_at=datetime.utcnow()
        )
        create_user(new_user)
    
    user_id = uid
    
    # Calculate recommended goals
    recommended = recommend_goals(
        gender=request.gender,
        age=request.age,
        height_cm=request.height_cm,
        weight_kg=request.weight_kg,
        activity_level=request.activity_level,
        fitness_goal=request.fitness_goal,
        target_weight_kg=request.target_weight_kg,
    )
    
    # Create profile
    profile = UserProfile(
        user_id=user_id,
        name=request.name,
        gender=request.gender,
        age=request.age,
        height_cm=request.height_cm,
        weight_kg=request.weight_kg,
        activity_level=request.activity_level,
        fitness_goal=request.fitness_goal,
        target_weight_kg=request.target_weight_kg,
        daily_goals=recommended,
        diet_preference=request.diet_preference,
        allergies=request.allergies,
        disliked_foods=request.disliked_foods,
        onboarding_completed=True,
        created_at=datetime.utcnow(),
        updated_at=datetime.utcnow(),
    )
    
    # Save to Firestore
    db = _get_firestore_db()
    db.collection(PROFILES_COLLECTION).document(user_id).set(profile.model_dump())
    
    # Calculate BMR and TDEE for display
    bmr = calculate_bmr(request.gender, request.weight_kg, request.height_cm, request.age)
    tdee = calculate_tdee(bmr, request.activity_level)
    
    return {
        "status": "success",
        "message": "Profile created! Your personalized plan is ready 🎯",
        "profile": profile.model_dump(),
        "recommended_goals": recommended.model_dump(),
        "metabolic_info": {
            "bmr": bmr,
            "tdee": tdee,
            "explanation": f"Your body burns {bmr} calories at rest and {tdee} calories per day with your activity level."
        }
    }


@router.get("/me")
def get_my_profile(current_user: User = Depends(get_current_user)):
    """Get current user's profile"""
    db = _get_firestore_db()
    doc = db.collection(PROFILES_COLLECTION).document(current_user.user_id).get()
    
    if not doc.exists:
        raise HTTPException(status_code=404, detail="Profile not found. Please complete onboarding.")
    
    profile_data = doc.to_dict()
    
    # Convert datetime objects to ISO strings for JSON serialization
    if "created_at" in profile_data and profile_data["created_at"]:
        profile_data["created_at"] = profile_data["created_at"].isoformat() if hasattr(profile_data["created_at"], "isoformat") else str(profile_data["created_at"])
    if "updated_at" in profile_data and profile_data["updated_at"]:
        profile_data["updated_at"] = profile_data["updated_at"].isoformat() if hasattr(profile_data["updated_at"], "isoformat") else str(profile_data["updated_at"])
    
    return {
        "status": "success",
        "profile": profile_data
    }


@router.put("/me")
def update_my_profile(
    update: ProfileUpdate,
    user_id: str = Depends(get_current_user)
):
    """Update current user's profile"""
    db = _get_firestore_db()
    doc = db.collection(PROFILES_COLLECTION).document(user_id).get()
    
    if not doc.exists:
        raise HTTPException(status_code=404, detail="Profile not found. Please complete onboarding.")
    
    profile_data = doc.to_dict()
    profile = UserProfile(**profile_data)
    
    # Update fields
    update_data = update.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        if hasattr(profile, key) and value is not None:
            setattr(profile, key, value)
    
    profile.updated_at = datetime.utcnow()
    
    # Recalculate goals if relevant fields changed
    if any(k in update_data for k in ["weight_kg", "activity_level", "fitness_goal", "target_weight_kg"]):
        new_goals = recommend_goals(
            gender=profile.gender,
            age=profile.age,
            height_cm=profile.height_cm,
            weight_kg=profile.weight_kg,
            activity_level=profile.activity_level,
            fitness_goal=profile.fitness_goal,
            target_weight_kg=profile.target_weight_kg,
        )
        profile.daily_goals = new_goals
    
    # Save to Firestore
    db.collection(PROFILES_COLLECTION).document(user_id).set(profile.model_dump())
    
    return {
        "status": "success",
        "message": "Profile updated successfully! 🎉",
        "profile": profile.model_dump()
    }


@router.post("/calculate-goals")
def calculate_goals_endpoint(request: GoalCalculationRequest):
    """
    Calculate recommended goals without saving.
    Useful for showing recommendations during onboarding.
    """
    gender = request.gender
    age = request.age
    height_cm = request.height_cm
    weight_kg = request.weight_kg
    activity_level = request.activity_level
    fitness_goal = request.fitness_goal
    target_weight_kg = request.target_weight_kg
    recommended = recommend_goals(
        gender=gender,
        age=age,
        height_cm=height_cm,
        weight_kg=weight_kg,
        activity_level=activity_level,
        fitness_goal=fitness_goal,
        target_weight_kg=target_weight_kg,
    )
    
    bmr = calculate_bmr(gender, weight_kg, height_cm, age)
    tdee = calculate_tdee(bmr, activity_level)
    
    return {
        "status": "success",
        "recommended_goals": recommended.model_dump(),
        "metabolic_info": {
            "bmr": bmr,
            "tdee": tdee,
            "explanation": f"Your body burns {bmr} cal at rest, {tdee} cal/day total."
        },
        "tips": _get_goal_tips(fitness_goal)
    }


@router.get("/recommendations")
def get_recommendations(user_id: str = Depends(get_current_user)):
    """
    Get personalized meal and workout recommendations based on profile.
    """
    db = _get_firestore_db()
    doc = db.collection(PROFILES_COLLECTION).document(user_id).get()
    
    if not doc.exists:
        raise HTTPException(status_code=404, detail="Profile not found.")
    
    profile_data = doc.to_dict()
    profile = UserProfile(**profile_data)
    
    goals = profile.daily_goals
    
    # Generate meal recommendations
    meal_recs = []
    if profile.fitness_goal == FitnessGoal.lose_weight:
        meal_recs = [
            {
                "meal": "High-Protein Breakfast",
                "suggestion": "2 eggs + Greek yogurt + berries",
                "calories": 350,
                "protein_g": 30,
                "why": "Keeps you full and preserves muscle during weight loss"
            },
            {
                "meal": "Lean Lunch",
                "suggestion": "Grilled chicken breast (150g) + quinoa + broccoli",
                "calories": 450,
                "protein_g": 45,
                "why": "Balanced macros with high protein"
            },
            {
                "meal": "Light Dinner",
                "suggestion": "Salmon (120g) + sweet potato + salad",
                "calories": 500,
                "protein_g": 35,
                "why": "Omega-3s for recovery, complex carbs for energy"
            }
        ]
    elif profile.fitness_goal == FitnessGoal.gain_muscle:
        meal_recs = [
            {
                "meal": "Power Breakfast",
                "suggestion": "3 eggs + oats + banana + peanut butter",
                "calories": 600,
                "protein_g": 35,
                "why": "High calories and protein for muscle growth"
            },
            {
                "meal": "Muscle-Building Lunch",
                "suggestion": "Beef (200g) + brown rice + avocado",
                "calories": 750,
                "protein_g": 55,
                "why": "Rich in protein and healthy fats"
            },
            {
                "meal": "Recovery Dinner",
                "suggestion": "Chicken (180g) + pasta + vegetables",
                "calories": 700,
                "protein_g": 50,
                "why": "Carbs for glycogen, protein for muscle repair"
            }
        ]
    else:  # maintain or improve_fitness
        meal_recs = [
            {
                "meal": "Balanced Breakfast",
                "suggestion": "Greek yogurt + granola + fruit",
                "calories": 400,
                "protein_g": 25,
                "why": "Balanced macros to start your day"
            },
            {
                "meal": "Energizing Lunch",
                "suggestion": "Turkey sandwich + salad + apple",
                "calories": 500,
                "protein_g": 30,
                "why": "Sustained energy throughout the day"
            },
            {
                "meal": "Wholesome Dinner",
                "suggestion": "Salmon + quinoa + roasted vegetables",
                "calories": 550,
                "protein_g": 35,
                "why": "Nutrient-dense and satisfying"
            }
        ]
    
    # Generate workout recommendations
    workout_recs = []
    if profile.fitness_goal == FitnessGoal.lose_weight:
        workout_recs = [
            {"type": "Cardio", "suggestion": "30 min run or cycling", "frequency": "4x/week"},
            {"type": "Strength", "suggestion": "Full body circuit", "frequency": "2x/week"},
            {"type": "Active Recovery", "suggestion": "Yoga or walking", "frequency": "1x/week"}
        ]
    elif profile.fitness_goal == FitnessGoal.gain_muscle:
        workout_recs = [
            {"type": "Upper Body", "suggestion": "Push/Pull split", "frequency": "2x/week"},
            {"type": "Lower Body", "suggestion": "Squats, deadlifts, lunges", "frequency": "2x/week"},
            {"type": "Core", "suggestion": "Planks, crunches", "frequency": "2x/week"}
        ]
    else:
        workout_recs = [
            {"type": "Mixed Cardio", "suggestion": "Running, cycling, swimming", "frequency": "3x/week"},
            {"type": "Strength", "suggestion": "Full body workout", "frequency": "2x/week"}
        ]
    
    return {
        "status": "success",
        "meal_recommendations": meal_recs,
        "workout_recommendations": workout_recs,
        "daily_goals": goals.model_dump(),
        "tips": _get_goal_tips(profile.fitness_goal)
    }


def _get_goal_tips(goal: FitnessGoal) -> list[str]:
    """Get tips based on fitness goal"""
    tips_map = {
        FitnessGoal.lose_weight: [
            "Aim for 500 cal deficit per day for ~0.5kg/week loss",
            "Prioritize protein to preserve muscle mass",
            "Stay hydrated - drink water before meals",
            "Get 7-9 hours of sleep for optimal fat loss"
        ],
        FitnessGoal.gain_muscle: [
            "Eat in a slight surplus (~300 cal above TDEE)",
            "Consume 1.6-2.2g protein per kg bodyweight",
            "Progressive overload in your workouts",
            "Recovery is key - don't skip rest days"
        ],
        FitnessGoal.maintain: [
            "Balance calories in vs calories out",
            "Focus on nutrient-dense whole foods",
            "Stay consistent with exercise routine",
            "Listen to your body's hunger cues"
        ],
        FitnessGoal.improve_fitness: [
            "Mix cardio and strength training",
            "Challenge yourself progressively",
            "Fuel your workouts with proper nutrition",
            "Track progress beyond the scale"
        ]
    }
    return tips_map.get(goal, [])


