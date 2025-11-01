"""
Meal Management Endpoints
Handles meal CRUD operations, classification, and editing
"""

from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime

from app.models.user import User
from app.services.auth import get_current_user
from app.services.database import (
    get_fitness_log,
    update_fitness_log,
    delete_fitness_log,
    list_fitness_logs_by_user
)

router = APIRouter(prefix="/meals", tags=["meals"])


class MealUpdateRequest(BaseModel):
    """Request to update a meal"""
    meal_type: Optional[str] = Field(None, description="breakfast, lunch, snack, dinner")
    timestamp: Optional[datetime] = Field(None, description="When the meal was consumed")
    description: Optional[str] = Field(None, description="Meal description")


class MealMoveRequest(BaseModel):
    """Request to move a meal to a different type"""
    new_meal_type: str = Field(..., description="breakfast, lunch, snack, dinner")


class MealClassificationRequest(BaseModel):
    """Request to classify/confirm a meal"""
    food_items: List[str] = Field(..., description="List of food items")
    timestamp: Optional[datetime] = Field(None, description="When consumed")
    user_hint: Optional[str] = Field(None, description="User's hint (e.g., 'for breakfast')")


@router.get("/{meal_id}")
async def get_meal_detail(
    meal_id: str,
    current_user: User = Depends(get_current_user)
):
    """
    Get detailed information about a specific meal
    
    Returns:
    - Meal information
    - All food items
    - Total macros
    - Timestamps
    """
    # Get the fitness log (meal)
    meal = get_fitness_log(meal_id)
    
    if not meal or meal.user_id != current_user.user_id:
        raise HTTPException(status_code=404, detail="Meal not found")
    
    if meal.log_type.value != "meal":
        raise HTTPException(status_code=400, detail="Not a meal")
    
    # Extract data
    ai_data = meal.ai_parsed_data or {}
    
    return {
        "meal_id": meal_id,
        "description": ai_data.get("description", meal.content),
        "meal_type": ai_data.get("meal_type", "snack"),
        "timestamp": meal.timestamp.isoformat(),
        "calories": meal.calories,
        "macros": {
            "protein_g": ai_data.get("protein_g", 0),
            "carbs_g": ai_data.get("carbs_g", 0),
            "fat_g": ai_data.get("fat_g", 0),
            "fiber_g": ai_data.get("fiber_g", 0)
        },
        "estimated": ai_data.get("estimated", False),
        "confidence": ai_data.get("confidence", "medium")
    }


@router.put("/{meal_id}")
async def update_meal(
    meal_id: str,
    update: MealUpdateRequest,
    current_user: User = Depends(get_current_user)
):
    """
    Update a meal's details
    
    Can update:
    - meal_type (move to different meal)
    - timestamp (change when it was consumed)
    - description (edit food description)
    """
    # Get existing meal
    meal = get_fitness_log(meal_id)
    
    if not meal or meal.user_id != current_user.user_id:
        raise HTTPException(status_code=404, detail="Meal not found")
    
    if meal.log_type.value != "meal":
        raise HTTPException(status_code=400, detail="Not a meal")
    
    # Update fields
    ai_data = meal.ai_parsed_data or {}
    
    if update.meal_type:
        valid_types = ["breakfast", "lunch", "snack", "dinner"]
        if update.meal_type not in valid_types:
            raise HTTPException(
                status_code=400,
                detail=f"Invalid meal_type. Must be one of: {', '.join(valid_types)}"
            )
        ai_data["meal_type"] = update.meal_type
    
    if update.timestamp:
        meal.timestamp = update.timestamp
    
    if update.description:
        ai_data["description"] = update.description
        meal.content = update.description
    
    # Prepare updates
    updates = {
        "ai_parsed_data": ai_data
    }
    if update.timestamp:
        updates["timestamp"] = update.timestamp
    if update.description:
        updates["content"] = update.description
    
    # Save updates
    update_fitness_log(meal_id, updates)
    
    return {
        "success": True,
        "meal_id": meal_id,
        "updated_fields": {
            "meal_type": update.meal_type,
            "timestamp": update.timestamp.isoformat() if update.timestamp else None,
            "description": update.description
        }
    }


@router.post("/{meal_id}/move")
async def move_meal(
    meal_id: str,
    move_request: MealMoveRequest,
    current_user: User = Depends(get_current_user)
):
    """
    Move a meal to a different meal type
    
    Example: Move from "snack" to "lunch"
    """
    update = MealUpdateRequest(meal_type=move_request.new_meal_type)
    return await update_meal(meal_id, update, current_user)


@router.delete("/{meal_id}")
async def delete_meal(
    meal_id: str,
    current_user: User = Depends(get_current_user)
):
    """
    Delete a meal
    """
    # Get existing meal
    meal = get_fitness_log(meal_id)
    
    if not meal or meal.user_id != current_user.user_id:
        raise HTTPException(status_code=404, detail="Meal not found")
    
    if meal.log_type.value != "meal":
        raise HTTPException(status_code=400, detail="Not a meal")
    
    # Delete
    delete_fitness_log(meal_id)
    
    return {
        "success": True,
        "meal_id": meal_id,
        "message": "Meal deleted successfully"
    }


@router.post("/classify")
async def classify_meal(
    request: MealClassificationRequest
):
    """
    Classify a meal based on food items, time, and context
    
    Returns:
    - Suggested meal_type
    - Confidence score
    - Reasoning
    """
    from app.services.multi_food_parser import MultiFoodParser
    
    parser = MultiFoodParser()
    
    # Determine timestamp
    timestamp = request.timestamp or datetime.now()
    hour = timestamp.hour
    
    # Time-based classification
    if 5 <= hour < 11:
        suggested_type = "breakfast"
        confidence = 0.9
        reasoning = "Time of day (morning)"
    elif 11 <= hour < 15:
        suggested_type = "lunch"
        confidence = 0.9
        reasoning = "Time of day (midday)"
    elif 15 <= hour < 18:
        suggested_type = "snack"
        confidence = 0.8
        reasoning = "Time of day (afternoon)"
    elif 18 <= hour < 23:
        suggested_type = "dinner"
        confidence = 0.9
        reasoning = "Time of day (evening)"
    else:
        suggested_type = "snack"
        confidence = 0.5
        reasoning = "Time of day (late night)"
    
    # Check for user hints
    if request.user_hint:
        hint_lower = request.user_hint.lower()
        if "breakfast" in hint_lower:
            suggested_type = "breakfast"
            confidence = 1.0
            reasoning = "User specified 'breakfast'"
        elif "lunch" in hint_lower:
            suggested_type = "lunch"
            confidence = 1.0
            reasoning = "User specified 'lunch'"
        elif "dinner" in hint_lower:
            suggested_type = "dinner"
            confidence = 1.0
            reasoning = "User specified 'dinner'"
        elif "snack" in hint_lower:
            suggested_type = "snack"
            confidence = 1.0
            reasoning = "User specified 'snack'"
    
    # Food-based hints (optional enhancement)
    breakfast_foods = ["egg", "oatmeal", "cereal", "pancake", "waffle", "toast"]
    if any(food in " ".join(request.food_items).lower() for food in breakfast_foods):
        if suggested_type == "breakfast":
            confidence = min(confidence + 0.1, 1.0)
            reasoning += " + typical breakfast foods"
    
    return {
        "suggested_meal_type": suggested_type,
        "confidence": confidence,
        "confidence_level": "high" if confidence > 0.8 else "medium" if confidence > 0.5 else "low",
        "reasoning": reasoning,
        "timestamp": timestamp.isoformat(),
        "needs_confirmation": confidence < 0.8
    }


@router.get("/")
async def list_meals(
    date: Optional[str] = None,
    meal_type: Optional[str] = None,
    limit: int = 100,
    current_user: User = Depends(get_current_user)
):
    """
    List meals for a user
    
    Filters:
    - date: YYYY-MM-DD format
    - meal_type: breakfast, lunch, snack, dinner
    - limit: max results
    """
    from app.models.fitness_log import FitnessLogType
    
    # Parse date if provided
    start_ts = None
    end_ts = None
    if date:
        try:
            from datetime import timezone
            date_obj = datetime.fromisoformat(date)
            start_ts = date_obj.replace(hour=0, minute=0, second=0, tzinfo=timezone.utc)
            end_ts = date_obj.replace(hour=23, minute=59, second=59, tzinfo=timezone.utc)
        except ValueError:
            raise HTTPException(status_code=400, detail="Invalid date format. Use YYYY-MM-DD")
    
    # Get all meals
    logs = list_fitness_logs_by_user(
        user_id=current_user.user_id,
        log_type=FitnessLogType.meal,
        start_ts=start_ts,
        end_ts=end_ts,
        limit=limit
    )
    
    # Filter by meal_type if specified
    meals = []
    for log in logs:
        ai_data = log.ai_parsed_data or {}
        log_meal_type = ai_data.get("meal_type", "snack")
        
        if meal_type and log_meal_type != meal_type:
            continue
        
        meals.append({
            "meal_id": log.log_id,
            "description": ai_data.get("description", log.content),
            "meal_type": log_meal_type,
            "timestamp": log.timestamp.isoformat(),
            "calories": log.calories,
            "macros": {
                "protein_g": ai_data.get("protein_g", 0),
                "carbs_g": ai_data.get("carbs_g", 0),
                "fat_g": ai_data.get("fat_g", 0),
                "fiber_g": ai_data.get("fiber_g", 0)
            }
        })
    
    return {
        "meals": meals,
        "count": len(meals),
        "filters": {
            "date": date,
            "meal_type": meal_type
        }
    }

