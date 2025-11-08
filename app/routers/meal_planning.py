"""
Meal Planning API Router - REST Endpoints
Clean API design with proper validation and error handling
"""

from fastapi import APIRouter, Depends, HTTPException, Query
from typing import List, Optional
from datetime import date, timedelta

from app.models.meal_planning import (
    Recipe,
    MealPlan,
    PlannedMeal,
    GroceryList,
    GenerateMealPlanRequest,
    RecipeSearchQuery,
    MealType,
    DayOfWeek,
)
from app.services.meal_planning_service import get_meal_planning_service, MealPlanningService
from app.models.user import User
from app.services.auth import get_current_user

router = APIRouter(prefix="/meal-planning", tags=["meal_planning"])


# ============================================================================
# RECIPE ENDPOINTS
# ============================================================================

@router.post("/recipes", response_model=Recipe)
async def create_recipe(
    recipe: Recipe,
    current_user: User = Depends(get_current_user),
    service: MealPlanningService = Depends(get_meal_planning_service)
):
    """
    Create a new recipe
    
    Can be user-created or AI-generated
    """
    recipe.created_by = current_user.user_id
    recipe.source = "user_created"
    return await service.create_recipe(recipe)


@router.get("/recipes/{recipe_id}", response_model=Recipe)
async def get_recipe(
    recipe_id: str,
    current_user: User = Depends(get_current_user),
    service: MealPlanningService = Depends(get_meal_planning_service)
):
    """Get a specific recipe by ID"""
    recipe = await service.get_recipe_by_id(recipe_id)
    if not recipe:
        # Check if this is an LLM-generated meal (temp UUID)
        # Search in user's active meal plans for this recipe_id
        plans = await service.get_user_meal_plans(current_user.user_id, limit=5, active_only=True)
        
        for plan in plans:
            for meal in plan.meals:
                if meal.recipe_id == recipe_id:
                    # Found the LLM meal! Create a lightweight recipe from it
                    print(f"✅ [RECIPE API] Found LLM meal: {meal.recipe_name}")
                    
                    # Create a simple recipe object from the meal data
                    from app.models.meal_planning import Recipe, NutritionInfo, RecipeCategory, DifficultyLevel, CuisineType, Ingredient
                    import uuid
                    from datetime import datetime
                    
                    recipe = Recipe(
                        id=recipe_id,
                        name=meal.recipe_name,
                        description=meal.notes or "AI-generated meal from your personalized meal plan.",
                        category=RecipeCategory.MAIN_COURSE,
                        cuisine=CuisineType.OTHER,  # Use valid enum value
                        difficulty=DifficultyLevel.EASY,
                        prep_time_minutes=15,
                        cook_time_minutes=20,
                        servings=meal.servings,
                        ingredients=[
                            Ingredient(
                                name="Ingredients coming soon",
                                amount="",
                                unit="",
                                notes="Full recipe details will be added soon"
                            )
                        ],
                        instructions=["This is an AI-generated meal suggestion.", "Full cooking instructions coming soon!"],
                        nutrition=NutritionInfo(
                            calories=meal.calories or 0,
                            protein_g=meal.protein_g or 0,
                            carbs_g=meal.carbs_g or 0,
                            fat_g=meal.fat_g or 0,
                            fiber_g=meal.fiber_g or 0
                        ),
                        tags=[],
                        image_url=None,
                        source="AI Generated",
                        created_at=datetime.utcnow(),
                        updated_at=datetime.utcnow()
                    )
                    return recipe
        
        # Not found in meal plans either
        raise HTTPException(status_code=404, detail="Recipe not found")
    return recipe


@router.post("/recipes/search", response_model=List[Recipe])
async def search_recipes(
    query: RecipeSearchQuery,
    service: MealPlanningService = Depends(get_meal_planning_service)
):
    """
    Search recipes with filters
    
    Supports:
    - Text search
    - Category, cuisine, difficulty filters
    - Dietary tags
    - Prep time limits
    - Nutrition filters
    """
    recipes = await service.search_recipes(query)
    return recipes


# ============================================================================
# MEAL PLAN ENDPOINTS
# ============================================================================

@router.post("/plans/generate", response_model=MealPlan)
async def generate_meal_plan(
    request: GenerateMealPlanRequest,
    current_user: User = Depends(get_current_user),
    service: MealPlanningService = Depends(get_meal_planning_service)
):
    """
    Generate a meal plan using AI
    
    Takes user preferences and generates a complete weekly meal plan
    """
    print(f"🟢 [MEAL PLANNING API] generate_meal_plan called for user: {current_user.user_id}")
    print(f"   Request: {request.dict()}")
    
    # ✅ CRITICAL: Check free tier limits BEFORE any expensive operations
    from datetime import datetime
    try:
        # Get user profile to check subscription tier
        profile_doc = service.db.collection('user_profiles').document(current_user.user_id).get()
        
        if profile_doc.exists:
            profile_data = profile_doc.to_dict()
            subscription_tier = profile_data.get('subscription_tier', 'free')
            plans_generated_this_week = profile_data.get('meal_plans_generated_this_week', 0)
            week_start = profile_data.get('week_start_for_limit')
            
            # Reset counter if new week
            now = datetime.now()
            if week_start:
                week_start_dt = datetime.fromisoformat(week_start) if isinstance(week_start, str) else week_start
                if (now - week_start_dt).days >= 7:
                    print(f"🔄 [FREE TIER] New week detected, resetting counter")
                    plans_generated_this_week = 0
                    week_start = now
                    # Update in DB
                    service.db.collection('user_profiles').document(current_user.user_id).update({
                        'meal_plans_generated_this_week': 0,
                        'week_start_for_limit': now.isoformat()
                    })
            else:
                week_start = now
            
            # ⛔ ENFORCE FREE TIER LIMIT - Block BEFORE LLM call
            if subscription_tier == 'free' and plans_generated_this_week >= 3:
                print(f"⛔ [FREE TIER] User {current_user.user_id} has reached limit ({plans_generated_this_week}/3)")
                raise HTTPException(
                    status_code=403,
                    detail={
                        "error": "free_tier_limit_reached",
                        "message": "You've reached your limit of 3 meal plans per week. Upgrade to Premium for unlimited meal plans!",
                        "plans_generated": plans_generated_this_week,
                        "limit": 3,
                        "upgrade_url": "/premium"
                    }
                )
            
            print(f"✅ [FREE TIER] User has generated {plans_generated_this_week}/3 plans this week")
        else:
            print(f"⚠️ [FREE TIER] No profile found for user, allowing generation")
    except HTTPException:
        raise  # Re-raise the 403 error
    except Exception as e:
        print(f"⚠️ [FREE TIER] Error checking limits: {e}, allowing generation")
    
    try:
        meal_plan = await service.generate_meal_plan_ai(current_user.user_id, request)
        print(f"✅ [MEAL PLANNING API] Meal plan generated successfully! ID: {meal_plan.id}")
        
        # ✅ Increment usage counter for free tier tracking (AFTER successful generation)
        try:
            profile_doc = service.db.collection('user_profiles').document(current_user.user_id).get()
            if profile_doc.exists:
                profile_data = profile_doc.to_dict()
                subscription_tier = profile_data.get('subscription_tier', 'free')
                
                if subscription_tier == 'free':
                    plans_generated = profile_data.get('meal_plans_generated_this_week', 0)
                    new_count = plans_generated + 1
                    
                    service.db.collection('user_profiles').document(current_user.user_id).update({
                        'meal_plans_generated_this_week': new_count,
                        'week_start_for_limit': profile_data.get('week_start_for_limit', datetime.now().isoformat())
                    })
                    print(f"📊 [FREE TIER] Updated counter: {new_count}/3 plans this week")
        except Exception as counter_error:
            print(f"⚠️ [FREE TIER] Failed to update counter: {counter_error}")
            # Don't fail the request if counter update fails
        
        return meal_plan
    except Exception as e:
        print(f"❌ [MEAL PLANNING API] Error generating meal plan: {e}")
        import traceback
        traceback.print_exc()
        raise


@router.get("/plans", response_model=List[MealPlan])
async def get_meal_plans(
    limit: int = Query(10, ge=1, le=50),
    active_only: bool = Query(True),
    current_user: User = Depends(get_current_user),
    service: MealPlanningService = Depends(get_meal_planning_service)
):
    """
    Get user's meal plans
    
    Returns plans in reverse chronological order
    """
    plans = await service.get_user_meal_plans(
        current_user.user_id,
        limit=limit,
        active_only=active_only
    )
    return plans


@router.get("/plans/current")
async def get_current_week_plan(
    current_user: User = Depends(get_current_user),
    service: MealPlanningService = Depends(get_meal_planning_service)
):
    """Get meal plan for current week"""
    print(f"🟢 [MEAL PLANNING API] get_current_week_plan called for user: {current_user.user_id}")
    
    try:
        plan = await service.get_current_week_meal_plan(current_user.user_id)
        if plan:
            print(f"✅ [MEAL PLANNING API] Found current week plan: {plan.id}")
            print(f"   📋 Plan details:")
            print(f"      Week: {plan.week_start_date} to {plan.week_end_date}")
            print(f"      Meals type: {type(plan.meals)}")
            print(f"      Meals length: {len(plan.meals) if isinstance(plan.meals, list) else 'N/A'}")
            
            # Convert to dict and add actual dates to meals
            plan_dict = plan.dict()
            
            # Map day names to day offsets (week starts on Monday)
            day_map = {
                'monday': 0, 'tuesday': 1, 'wednesday': 2, 'thursday': 3,
                'friday': 4, 'saturday': 5, 'sunday': 6  # Sunday is last day of week
            }
            
            # Add date field and nutrition to each meal
            for meal in plan_dict['meals']:
                day_name = meal['day'].lower()
                day_offset = day_map.get(day_name, 0)
                meal_date = plan.week_start_date + timedelta(days=day_offset)
                meal['date'] = meal_date.isoformat()
                
                # Use nutrition data from PlannedMeal (already stored from LLM)
                # Only fetch from recipe collection if nutrition is missing
                if meal.get('calories') is None or meal.get('calories') == 0:
                    try:
                        recipe_doc = service.db.collection('recipes').document(meal['recipe_id']).get()
                        if recipe_doc.exists:
                            recipe_data = recipe_doc.to_dict()
                            nutrition = recipe_data.get('nutrition', {})
                            meal['calories'] = nutrition.get('calories', 0)
                            meal['protein'] = int(nutrition.get('protein_g', 0))
                            print(f"      ✅ Fetched nutrition from recipe: {meal['recipe_name']} - {meal['calories']} cal, {meal['protein']}g protein")
                        else:
                            # Recipe not found, keep existing values or default to 0
                            meal['calories'] = meal.get('calories', 0)
                            meal['protein'] = meal.get('protein_g', 0)
                            print(f"      ℹ️ Using stored nutrition for: {meal['recipe_name']} - {meal['calories']} cal, {meal['protein']}g protein")
                    except Exception as e:
                        print(f"      ⚠️ Error fetching recipe, using stored values: {e}")
                        meal['calories'] = meal.get('calories', 0)
                        meal['protein'] = meal.get('protein_g', 0)
                else:
                    # Nutrition already exists in PlannedMeal
                    meal['protein'] = meal.get('protein_g', 0)
                    print(f"      ✅ Using LLM nutrition: {meal['recipe_name']} - {meal['calories']} cal, {meal['protein']}g protein")
            
            print(f"   ✅ Enriched {len(plan_dict['meals'])} meals with dates and nutrition")
            return plan_dict
        else:
            print(f"ℹ️ [MEAL PLANNING API] No current week plan found")
            return None
    except Exception as e:
        print(f"❌ [MEAL PLANNING API] Error getting current week plan: {e}")
        import traceback
        traceback.print_exc()
        raise


@router.get("/plans/{plan_id}", response_model=MealPlan)
async def get_meal_plan(
    plan_id: str,
    current_user: User = Depends(get_current_user),
    service: MealPlanningService = Depends(get_meal_planning_service)
):
    """Get a specific meal plan"""
    plan = await service.get_meal_plan_by_id(current_user.user_id, plan_id)
    if not plan:
        raise HTTPException(status_code=404, detail="Meal plan not found")
    return plan


@router.post("/plans/{plan_id}/meals", response_model=MealPlan)
async def add_meal_to_plan(
    plan_id: str,
    meal: PlannedMeal,
    current_user: User = Depends(get_current_user),
    service: MealPlanningService = Depends(get_meal_planning_service)
):
    """
    Add or update a meal in the plan
    
    If meal already exists for that day/type, it will be replaced
    """
    try:
        plan = await service.add_meal_to_plan(current_user.user_id, plan_id, meal)
        return plan
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))


@router.delete("/plans/{plan_id}/meals/{day}/{meal_type}", response_model=MealPlan)
async def remove_meal_from_plan(
    plan_id: str,
    day: DayOfWeek,
    meal_type: MealType,
    current_user: User = Depends(get_current_user),
    service: MealPlanningService = Depends(get_meal_planning_service)
):
    """Remove a meal from the plan"""
    try:
        plan = await service.remove_meal_from_plan(
            current_user.user_id,
            plan_id,
            day,
            meal_type
        )
        return plan
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))


@router.get("/plans/{plan_id}/analytics")
async def get_plan_analytics(
    plan_id: str,
    current_user: User = Depends(get_current_user),
    service: MealPlanningService = Depends(get_meal_planning_service)
):
    """
    Get analytics for a meal plan
    
    Returns:
    - Daily calorie/macro totals
    - Completion percentage
    - Cost estimates
    """
    analytics = await service.get_meal_plan_analytics(current_user.user_id, plan_id)
    if not analytics:
        raise HTTPException(status_code=404, detail="Meal plan not found")
    return analytics


# ============================================================================
# DAILY SUGGESTIONS
# ============================================================================

@router.get("/suggestions/daily", response_model=List[Recipe])
async def get_daily_suggestions(
    target_date: date = Query(default_factory=date.today),
    remaining_calories: int = Query(1500, ge=0),
    remaining_protein: int = Query(100, ge=0),
    current_user: User = Depends(get_current_user),
    service: MealPlanningService = Depends(get_meal_planning_service)
):
    """
    Get AI-powered daily meal suggestions
    
    Suggests meals based on remaining macros and user preferences
    """
    suggestions = await service.suggest_daily_meals(
        current_user.user_id,
        target_date,
        remaining_calories,
        remaining_protein
    )
    return suggestions


# ============================================================================
# GROCERY LIST ENDPOINTS
# ============================================================================

@router.post("/grocery-lists/generate/{plan_id}", response_model=GroceryList)
async def generate_grocery_list(
    plan_id: str,
    current_user: User = Depends(get_current_user),
    service: MealPlanningService = Depends(get_meal_planning_service)
):
    """
    Generate grocery list from meal plan
    
    Aggregates all ingredients and organizes by category
    """
    try:
        grocery_list = await service.generate_grocery_list(current_user.user_id, plan_id)
        return grocery_list
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))


@router.get("/grocery-lists/{list_id}", response_model=GroceryList)
async def get_grocery_list(
    list_id: str,
    current_user: User = Depends(get_current_user),
    service: MealPlanningService = Depends(get_meal_planning_service)
):
    """Get a grocery list"""
    grocery_list = await service.get_grocery_list_by_id(current_user.user_id, list_id)
    if not grocery_list:
        raise HTTPException(status_code=404, detail="Grocery list not found")
    return grocery_list


@router.put("/grocery-lists/{list_id}/items/{item_name}/check", response_model=GroceryList)
async def check_grocery_item(
    list_id: str,
    item_name: str,
    checked: bool = Query(True),
    current_user: User = Depends(get_current_user),
    service: MealPlanningService = Depends(get_meal_planning_service)
):
    """Check or uncheck a grocery item"""
    try:
        grocery_list = await service.check_grocery_item(
            current_user.user_id,
            list_id,
            item_name,
            checked
        )
        return grocery_list
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))

