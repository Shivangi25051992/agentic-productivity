"""
Meal Planning Service - Business Logic Layer
Orchestrates meal planning, recipe management, and grocery list generation
Enterprise-grade with clean separation of concerns
"""

from datetime import date, datetime, timedelta
from typing import List, Optional, Dict, Any
from google.cloud import firestore
import os
from dotenv import load_dotenv

from app.models.meal_planning import (
    Recipe,
    NutritionInfo,
    MealPlan,
    PlannedMeal,
    GroceryList,
    GroceryItem,
    MealType,
    DayOfWeek,
    GenerateMealPlanRequest,
    RecipeSearchQuery,
    RecipeCategory,
    DietaryTag,
)

load_dotenv()
load_dotenv('.env.local', override=True)


class MealPlanningService:
    """
    Service for managing meal plans, recipes, and grocery lists
    
    Responsibilities:
    - Recipe CRUD operations
    - Meal plan generation and management
    - Grocery list generation
    - AI-powered meal suggestions
    """
    
    def __init__(self):
        self.db = firestore.Client(project=os.getenv("GOOGLE_CLOUD_PROJECT"))
        self.recipes_collection = "recipes"
        self.meal_plans_collection = "meal_plans"
        self.grocery_lists_collection = "grocery_lists"
    
    # ========================================================================
    # RECIPE OPERATIONS
    # ========================================================================
    
    async def create_recipe(self, recipe: Recipe) -> Recipe:
        """Create a new recipe"""
        recipe.created_at = datetime.utcnow()
        recipe.updated_at = datetime.utcnow()
        
        doc_ref = self.db.collection(self.recipes_collection).document(recipe.id)
        doc_ref.set(recipe.to_dict())
        
        print(f"✅ Created recipe: {recipe.name} ({recipe.id})")
        return recipe
    
    async def get_recipe_by_id(self, recipe_id: str) -> Optional[Recipe]:
        """Get a recipe by ID"""
        doc = self.db.collection(self.recipes_collection).document(recipe_id).get()
        
        if doc.exists:
            return Recipe.from_dict(doc.to_dict())
        return None
    
    async def search_recipes(self, query: RecipeSearchQuery) -> List[Recipe]:
        """
        Search recipes with filters
        
        Supports:
        - Text search (name, description)
        - Category filter
        - Cuisine filter
        - Dietary tags
        - Prep time limit
        - Nutrition filters
        """
        # Start with base query
        db_query = self.db.collection(self.recipes_collection)
        
        # Apply filters
        if query.category:
            db_query = db_query.where('category', '==', query.category.value)
        
        if query.cuisine:
            db_query = db_query.where('cuisine', '==', query.cuisine.value)
        
        if query.difficulty:
            db_query = db_query.where('difficulty', '==', query.difficulty.value)
        
        # Limit results
        db_query = db_query.limit(query.limit)
        
        # Execute query
        recipes = []
        for doc in db_query.stream():
            recipe = Recipe.from_dict(doc.to_dict())
            
            # Apply additional filters (not supported by Firestore directly)
            if query.max_prep_time and recipe.total_time_minutes > query.max_prep_time:
                continue
            
            if query.max_calories and recipe.nutrition.calories > query.max_calories:
                continue
            
            if query.min_protein and recipe.nutrition.protein_g < query.min_protein:
                continue
            
            if query.tags:
                # Check if recipe has all required tags
                if not all(tag in recipe.tags for tag in query.tags):
                    continue
            
            # Text search (simple contains)
            if query.query:
                search_text = query.query.lower()
                if search_text not in recipe.name.lower() and search_text not in recipe.description.lower():
                    continue
            
            recipes.append(recipe)
        
        return recipes
    
    async def get_recipes_by_ids(self, recipe_ids: List[str]) -> List[Recipe]:
        """Get multiple recipes by their IDs"""
        recipes = []
        for recipe_id in recipe_ids:
            recipe = await self.get_recipe_by_id(recipe_id)
            if recipe:
                recipes.append(recipe)
        return recipes
    
    # ========================================================================
    # MEAL PLAN OPERATIONS
    # ========================================================================
    
    async def create_meal_plan(self, meal_plan: MealPlan) -> MealPlan:
        """Create a new meal plan"""
        meal_plan.created_at = datetime.utcnow()
        meal_plan.updated_at = datetime.utcnow()
        
        doc_ref = self.db.collection('users').document(meal_plan.user_id)\
                         .collection(self.meal_plans_collection).document(meal_plan.id)
        doc_ref.set(meal_plan.to_dict())
        
        print(f"✅ Created meal plan: {meal_plan.id} for user {meal_plan.user_id}")
        return meal_plan
    
    async def get_meal_plan_by_id(self, user_id: str, plan_id: str) -> Optional[MealPlan]:
        """Get a specific meal plan"""
        doc = self.db.collection('users').document(user_id)\
                     .collection(self.meal_plans_collection).document(plan_id).get()
        
        if doc.exists:
            return MealPlan.from_dict(doc.to_dict())
        return None
    
    async def get_user_meal_plans(
        self,
        user_id: str,
        limit: int = 10,
        active_only: bool = True
    ) -> List[MealPlan]:
        """Get user's meal plans"""
        print(f"🟢 [MEAL PLANNING SERVICE] get_user_meal_plans called for user: {user_id}")
        
        # Get plans sorted by creation date (newest first) to always show most recent
        # Filter by is_active in memory to avoid composite index requirement
        query = self.db.collection('users').document(user_id)\
                       .collection(self.meal_plans_collection)\
                       .order_by('created_at', direction=firestore.Query.DESCENDING)\
                       .limit(limit * 2)  # Get more to account for filtering
        
        plans = []
        doc_count = 0
        for doc in query.stream():
            doc_count += 1
            try:
                print(f"🔵 [MEAL PLANNING SERVICE] Processing document {doc_count}: {doc.id}")
                doc_data = doc.to_dict()
                
                # Log plan details
                week_start = doc_data.get('week_start_date')
                is_active_val = doc_data.get('is_active', True)
                print(f"   Week: {week_start}, Active: {is_active_val}")
                
                # Filter by is_active in memory
                if active_only and not is_active_val:
                    print(f"⏭️ [MEAL PLANNING SERVICE] Skipping inactive plan: {doc.id}")
                    continue
                
                print(f"🔵 [MEAL PLANNING SERVICE] Document data keys: {doc_data.keys()}")
                print(f"🔵 [MEAL PLANNING SERVICE] dietary_preferences type: {type(doc_data.get('dietary_preferences'))}")
                print(f"🔵 [MEAL PLANNING SERVICE] dietary_preferences value: {doc_data.get('dietary_preferences')}")
                
                meal_plan = MealPlan.from_dict(doc_data)
                plans.append(meal_plan)
                print(f"✅ [MEAL PLANNING SERVICE] Successfully parsed meal plan: {meal_plan.id}")
                
                # Stop if we have enough plans
                if len(plans) >= limit:
                    break
            except Exception as e:
                print(f"❌ [MEAL PLANNING SERVICE] Error parsing meal plan {doc.id}: {e}")
                import traceback
                traceback.print_exc()
                # Skip this plan and continue
                continue
        
        print(f"✅ [MEAL PLANNING SERVICE] Returning {len(plans)} meal plans")
        return plans
    
    async def get_current_week_meal_plan(self, user_id: str) -> Optional[MealPlan]:
        """Get meal plan for current week"""
        today = date.today()
        
        # Find plan that includes today (increased limit + debug logs)
        plans = await self.get_user_meal_plans(user_id, limit=20, active_only=True)
        
        print(f"🔍 [MEAL PLANNING] Found {len(plans)} active plans for user")
        for plan in plans:
            print(f"   📅 Plan {plan.id}: {plan.week_start_date} to {plan.week_end_date} (active: {plan.is_active})")
        
        for plan in plans:
            if plan.week_start_date <= today <= plan.week_end_date:
                print(f"✅ [MEAL PLANNING] Found current week plan: {plan.id}")
                return plan
        
        print(f"⚠️ [MEAL PLANNING] No plan found covering {today}")
        return None
    
    async def update_meal_plan(self, user_id: str, meal_plan: MealPlan) -> MealPlan:
        """Update an existing meal plan"""
        meal_plan.updated_at = datetime.utcnow()
        
        doc_ref = self.db.collection('users').document(user_id)\
                         .collection(self.meal_plans_collection).document(meal_plan.id)
        doc_ref.update(meal_plan.to_dict())
        
        print(f"✅ Updated meal plan: {meal_plan.id}")
        return meal_plan
    
    async def add_meal_to_plan(
        self,
        user_id: str,
        plan_id: str,
        meal: PlannedMeal
    ) -> MealPlan:
        """Add or update a meal in the plan"""
        plan = await self.get_meal_plan_by_id(user_id, plan_id)
        if not plan:
            raise ValueError(f"Meal plan {plan_id} not found")
        
        plan.add_meal(meal)
        return await self.update_meal_plan(user_id, plan)
    
    async def remove_meal_from_plan(
        self,
        user_id: str,
        plan_id: str,
        day: DayOfWeek,
        meal_type: MealType
    ) -> MealPlan:
        """Remove a meal from the plan"""
        plan = await self.get_meal_plan_by_id(user_id, plan_id)
        if not plan:
            raise ValueError(f"Meal plan {plan_id} not found")
        
        plan.remove_meal(day, meal_type)
        return await self.update_meal_plan(user_id, plan)
    
    # ========================================================================
    # AI MEAL PLAN GENERATION
    # ========================================================================
    
    async def generate_meal_plan_ai(
        self,
        user_id: str,
        request: GenerateMealPlanRequest
    ) -> MealPlan:
        """
        Generate a meal plan using production-grade LLM service
        Falls back to curated mock data if LLM fails (zero downtime)
        """
        print(f"🟢 [MEAL PLANNING] Generating AI-powered meal plan...")
        print(f"   User: {user_id}")
        print(f"   Preferences: {request.dietary_preferences}")
        
        try:
            # Import LLM service (lazy import to avoid circular dependencies)
            from app.services.meal_plan_llm_service import MealPlanLLMService
            from datetime import datetime, timedelta
            
            # Get user profile for personalization
            user_profile = await self._get_user_profile(user_id)
            
            # NOTE: Free tier limit check is now done at API endpoint level (before this service call)
            # This ensures we block BEFORE any expensive LLM operations
            
            # Generate using LLM service with PARALLEL generation (15-20s instead of 78s!)
            llm_service = MealPlanLLMService()
            result = await llm_service.generate_meal_plan_parallel(
                user_profile=user_profile,
                request=request,
                user_id=user_id
            )
            
            meal_plan = result['meal_plan_data']
            metadata = result['metadata']
            
            # Log generation metadata
            print(f"✅ [MEAL PLANNING] AI generation successful!")
            print(f"   Provider: {metadata.get('provider_used', 'unknown')}")
            print(f"   Cost: ${metadata.get('cost', 0):.4f}")
            print(f"   Latency: {metadata.get('latency_ms', 0):.0f}ms")
            print(f"   Meals: {len(meal_plan.meals)}")
            
            # Save to Firestore
            await self._save_meal_plan(meal_plan, metadata)
            
            # NOTE: Usage counter is now incremented at API endpoint level (after successful generation)
            
            return meal_plan
            
        except Exception as e:
            print(f"❌ [MEAL PLANNING] AI generation failed: {e}")
            print(f"🔄 [MEAL PLANNING] This should not happen (LLM service has fallback)")
            
            # Ultimate fallback (should never reach here)
            return await self._generate_mock_meal_plan(user_id, request)
    
    async def _get_user_profile(self, user_id: str) -> Dict[str, Any]:
        """Get user profile for meal plan personalization"""
        try:
            profile_doc = self.db.collection('profiles').document(user_id).get()
            if profile_doc.exists:
                return profile_doc.to_dict()
            else:
                print(f"⚠️ [MEAL PLANNING] No profile found for user {user_id}, using defaults")
                return {
                    'age': 30,
                    'gender': 'unknown',
                    'weight_kg': 70,
                    'height_cm': 170,
                    'activity_level': 'moderate',
                    'fitness_goal': 'maintain',
                    'diet_preference': 'none',
                    'allergies': [],
                    'disliked_foods': []
                }
        except Exception as e:
            print(f"⚠️ [MEAL PLANNING] Error fetching profile: {e}, using defaults")
            return {}
    
    async def _save_meal_plan(self, meal_plan: MealPlan, metadata: Dict[str, Any]):
        """Save meal plan to Firestore with metadata"""
        try:
            # ✨ NEW: Keep all plans active for plan selection feature
            # Users can now switch between multiple plans for the same week
            print(f"✅ [MEAL PLANNING] Keeping existing plans active for plan selection (user can switch between them)")
            
            # Convert to dict
            meal_plan_dict = meal_plan.dict()
            
            # Convert date objects to strings for Firestore
            if 'week_start_date' in meal_plan_dict:
                meal_plan_dict['week_start_date'] = meal_plan_dict['week_start_date'].isoformat()
            if 'week_end_date' in meal_plan_dict:
                meal_plan_dict['week_end_date'] = meal_plan_dict['week_end_date'].isoformat()
            
            # Convert dietary preferences enums to strings
            if 'dietary_preferences' in meal_plan_dict:
                meal_plan_dict['dietary_preferences'] = [
                    pref.value if hasattr(pref, 'value') else str(pref) 
                    for pref in meal_plan_dict['dietary_preferences']
                ]
            
            # Add generation metadata
            meal_plan_dict['generation_metadata'] = metadata
            
            # Ensure is_active is True for new plan
            meal_plan_dict['is_active'] = True
            
            # Save to Firestore in USER SUBCOLLECTION (matching where we read from)
            self.db.collection('users').document(meal_plan.user_id)\
                .collection(self.meal_plans_collection).document(meal_plan.id).set(meal_plan_dict)
            
            print(f"✅ [MEAL PLANNING] Saved NEW active plan to USER SUBCOLLECTION: {meal_plan.id}")
            print(f"   User: {meal_plan.user_id}")
            print(f"   Dietary preferences: {meal_plan_dict.get('dietary_preferences', [])}")
            
        except Exception as e:
            print(f"⚠️ [MEAL PLANNING] Error saving to Firestore: {e}")
            import traceback
            traceback.print_exc()
    
    async def _generate_mock_meal_plan(
        self,
        user_id: str,
        request: GenerateMealPlanRequest
    ) -> MealPlan:
        """
        Ultimate fallback - Generate mock meal plan
        This should NEVER be reached (LLM service has its own fallback)
        """
        print(f"🔄 [MEAL PLANNING] Generating ultimate fallback mock plan...")
        print(f"   User: {user_id}")
        print(f"   Preferences: {request.dietary_preferences}")
        
        # Create meal plan
        week_end = request.week_start_date + timedelta(days=6)
        
        meal_plan = MealPlan(
            user_id=user_id,
            week_start_date=request.week_start_date,
            week_end_date=week_end,
            dietary_preferences=request.dietary_preferences,
            daily_calorie_target=request.daily_calorie_target,
            daily_protein_target=request.daily_protein_target,
            created_by_ai=True,
            ai_generation_prompt=f"Mock data for testing",
            meals=[]
        )
        
        # Create mock meals for all 7 days
        days = [
            DayOfWeek.SUNDAY, DayOfWeek.MONDAY, DayOfWeek.TUESDAY,
            DayOfWeek.WEDNESDAY, DayOfWeek.THURSDAY, DayOfWeek.FRIDAY, DayOfWeek.SATURDAY
        ]
        
        meal_types = [MealType.BREAKFAST, MealType.LUNCH, MealType.DINNER]
        
        meal_templates = {
            MealType.BREAKFAST: [
                {"name": "Veggie Omelette", "cal": 350, "protein": 25},
                {"name": "Greek Yogurt Bowl", "cal": 320, "protein": 22},
                {"name": "Protein Pancakes", "cal": 380, "protein": 28},
            ],
            MealType.LUNCH: [
                {"name": "Quinoa Power Bowl", "cal": 450, "protein": 30},
                {"name": "Grilled Chicken Salad", "cal": 420, "protein": 35},
                {"name": "Lentil Soup", "cal": 380, "protein": 28},
            ],
            MealType.DINNER: [
                {"name": "Salmon with Veggies", "cal": 520, "protein": 40},
                {"name": "Turkey Stir Fry", "cal": 480, "protein": 38},
                {"name": "Tofu Curry", "cal": 440, "protein": 32},
            ]
        }
        
        for day_idx, day in enumerate(days):
            for meal_type in meal_types:
                template = meal_templates[meal_type][day_idx % 3]
                
                # Create recipe
                recipe = Recipe(
                    name=template["name"],
                    description=f"A delicious {template['name']} recipe",
                    category=RecipeCategory.BREAKFAST if meal_type == MealType.BREAKFAST else RecipeCategory.MAIN_COURSE,
                    ingredients=[],
                    instructions=["Mock instructions"],
                    prep_time_minutes=15,
                    cook_time_minutes=25,
                    servings=1,
                    nutrition=NutritionInfo(
                        calories=template["cal"],
                        protein_g=template["protein"],
                        carbs_g=45,
                        fat_g=18
                    ),
                    dietary_tags=request.dietary_preferences,
                    created_by_ai=True,
                    source="Mock Data"
                )
                
                # Save recipe
                recipe_doc_ref = self.db.collection('recipes').document(recipe.id)
                recipe_doc_ref.set(recipe.to_dict())
                
                # Create planned meal
                planned_meal = PlannedMeal(
                    day=day,
                    meal_type=meal_type,
                    recipe_id=recipe.id,
                    recipe_name=recipe.name,  # ← ADDED: Required field
                    servings=1
                )
                
                meal_plan.meals.append(planned_meal)
        
        print(f"✅ [MEAL PLANNING] Created {len(meal_plan.meals)} mock meals")
        print(f"📅 [MEAL PLANNING] Week: {meal_plan.week_start_date} to {meal_plan.week_end_date}")
        print(f"🔵 [MEAL PLANNING] Plan will be active: {meal_plan.is_active}")

        # FIRST: Deactivate any existing plans for the same week BEFORE saving new one
        # Get ALL plans and filter in memory to avoid index requirements
        print(f"🔍 [MEAL PLANNING] Checking for existing plans to deactivate...")
        print(f"   Looking for plans with week_start_date: {meal_plan.week_start_date}")
        try:
            # Get ALL plans for the user (no where clause to avoid index issues)
            existing_plans_query = self.db.collection('users').document(user_id)\
                                          .collection(self.meal_plans_collection)\
                                          .stream()
            
            deactivated_count = 0
            checked_count = 0
            for doc in existing_plans_query:
                checked_count += 1
                doc_data = doc.to_dict()
                doc_week_start = doc_data.get('week_start_date')
                doc_is_active = doc_data.get('is_active', True)
                
                # Convert doc_week_start to date for comparison
                if isinstance(doc_week_start, str):
                    # Parse ISO format string date (YYYY-MM-DD) to date object
                    doc_week_start = datetime.strptime(doc_week_start, '%Y-%m-%d').date()
                elif isinstance(doc_week_start, datetime):
                    doc_week_start = doc_week_start.date()
                
                print(f"   📋 Plan {doc.id}: week={doc_week_start} (type: {type(doc_week_start)}), active={doc_is_active}")
                print(f"   🔍 Comparing to: {meal_plan.week_start_date} (type: {type(meal_plan.week_start_date)})")
                
                # ✨ NEW: Keep all plans active for plan selection feature
                # Don't deactivate old plans - let users switch between them
                if doc_week_start == meal_plan.week_start_date:
                    print(f"   ✅ Found existing plan for same week: {doc.id} (keeping active for plan selection)")
                else:
                    print(f"   ⏭️ Different week, skipping")
            
            print(f"✅ [MEAL PLANNING] Checked {checked_count} plans, deactivated {deactivated_count} old plans")
        except Exception as deactivate_error:
            print(f"⚠️ [MEAL PLANNING] Error deactivating old plans (continuing anyway): {deactivate_error}")
            import traceback
            traceback.print_exc()
            # Continue even if deactivation fails
        
        # NOW: Save new meal plan
        saved_plan = await self.create_meal_plan(meal_plan)
        print(f"✅ [MEAL PLANNING] Saved NEW plan: {saved_plan.id}")
        print(f"   📋 Active: {saved_plan.is_active}")
        print(f"   📅 Week start: {saved_plan.week_start_date}")
        print(f"   🍽️  Meals: {len(saved_plan.meals)}")
        
        return saved_plan
    
    async def suggest_daily_meals(
        self,
        user_id: str,
        target_date: date,
        remaining_calories: int,
        remaining_protein: int
    ) -> List[Recipe]:
        """
        AI-powered daily meal suggestions
        
        Suggests meals based on:
        - Remaining macros for the day
        - User preferences
        - Previous meals
        - Time of day
        """
        # Get user's current meal plan
        current_plan = await self.get_current_week_meal_plan(user_id)
        
        # Determine which meal types are needed
        # For now, return general suggestions
        # Will be enhanced with AI
        
        query = RecipeSearchQuery(
            max_calories=remaining_calories,
            min_protein=remaining_protein // 3,  # Divide across meals
            limit=10
        )
        
        return await self.search_recipes(query)
    
    # ========================================================================
    # GROCERY LIST OPERATIONS
    # ========================================================================
    
    async def generate_grocery_list(
        self,
        user_id: str,
        meal_plan_id: str
    ) -> GroceryList:
        """
        Generate grocery list from meal plan
        
        Business Logic:
        - Aggregate ingredients from all recipes
        - Combine similar items
        - Categorize by store section
        - Estimate costs
        """
        # Get meal plan
        meal_plan = await self.get_meal_plan_by_id(user_id, meal_plan_id)
        if not meal_plan:
            raise ValueError(f"Meal plan {meal_plan_id} not found")
        
        # Get all recipes
        recipe_ids = [meal.recipe_id for meal in meal_plan.meals]
        recipes = await self.get_recipes_by_ids(recipe_ids)
        
        # Aggregate ingredients
        ingredient_map: Dict[str, GroceryItem] = {}
        
        for recipe in recipes:
            for ingredient in recipe.ingredients:
                key = ingredient.name.lower()
                
                if key in ingredient_map:
                    # Combine quantities (simplified - would need unit conversion)
                    existing = ingredient_map[key]
                    existing.recipe_ids.append(recipe.id)
                else:
                    # Create new grocery item
                    ingredient_map[key] = GroceryItem(
                        name=ingredient.name,
                        quantity=ingredient.amount,
                        unit="",  # Extract from amount string
                        category=ingredient.category,
                        estimated_cost=0.0,  # Would calculate based on price data
                        recipe_ids=[recipe.id],
                    )
        
        # Create grocery list
        grocery_list = GroceryList(
            user_id=user_id,
            meal_plan_id=meal_plan_id,
            week_start_date=meal_plan.week_start_date,
            items=list(ingredient_map.values()),
            total_estimated_cost=sum(item.estimated_cost for item in ingredient_map.values()),
        )
        
        # Save to database
        doc_ref = self.db.collection('users').document(user_id)\
                         .collection(self.grocery_lists_collection).document(grocery_list.id)
        doc_ref.set(grocery_list.to_dict())
        
        print(f"✅ Generated grocery list: {grocery_list.id} with {len(grocery_list.items)} items")
        return grocery_list
    
    async def get_grocery_list_by_id(self, user_id: str, list_id: str) -> Optional[GroceryList]:
        """Get a grocery list"""
        doc = self.db.collection('users').document(user_id)\
                     .collection(self.grocery_lists_collection).document(list_id).get()
        
        if doc.exists:
            return GroceryList.from_dict(doc.to_dict())
        return None
    
    async def check_grocery_item(
        self,
        user_id: str,
        list_id: str,
        item_name: str,
        checked: bool
    ) -> GroceryList:
        """Check/uncheck a grocery item"""
        grocery_list = await self.get_grocery_list_by_id(user_id, list_id)
        if not grocery_list:
            raise ValueError(f"Grocery list {list_id} not found")
        
        if checked:
            grocery_list.check_item(item_name)
        else:
            grocery_list.uncheck_item(item_name)
        
        # Update in database
        doc_ref = self.db.collection('users').document(user_id)\
                         .collection(self.grocery_lists_collection).document(list_id)
        doc_ref.update(grocery_list.to_dict())
        
        return grocery_list
    
    # ========================================================================
    # ANALYTICS & INSIGHTS
    # ========================================================================
    
    async def get_meal_plan_analytics(self, user_id: str, plan_id: str) -> Dict[str, Any]:
        """
        Get analytics for a meal plan
        
        Returns:
        - Total calories per day
        - Macro distribution
        - Completion percentage
        - Cost estimates
        """
        plan = await self.get_meal_plan_by_id(user_id, plan_id)
        if not plan:
            return {}
        
        # Get all recipes
        recipe_ids = [meal.recipe_id for meal in plan.meals]
        recipes = await self.get_recipes_by_ids(recipe_ids)
        
        # Calculate daily totals
        daily_totals = {}
        for meal in plan.meals:
            day = meal.day.value
            if day not in daily_totals:
                daily_totals[day] = {
                    "calories": 0,
                    "protein": 0,
                    "carbs": 0,
                    "fat": 0,
                    "meals_count": 0,
                }
            
            # Find recipe
            recipe = next((r for r in recipes if r.id == meal.recipe_id), None)
            if recipe:
                daily_totals[day]["calories"] += recipe.nutrition.calories * meal.servings
                daily_totals[day]["protein"] += recipe.nutrition.protein_g * meal.servings
                daily_totals[day]["carbs"] += recipe.nutrition.carbs_g * meal.servings
                daily_totals[day]["fat"] += recipe.nutrition.fat_g * meal.servings
                daily_totals[day]["meals_count"] += 1
        
        return {
            "plan_id": plan_id,
            "week_start": plan.week_start_date.isoformat(),
            "total_meals_planned": plan.total_meals_planned,
            "completion_percentage": plan.completion_percentage,
            "daily_totals": daily_totals,
            "target_calories": plan.daily_calorie_target,
            "target_protein": plan.daily_protein_target,
        }


# Singleton instance
_meal_planning_service = None

def get_meal_planning_service() -> MealPlanningService:
    """Get singleton instance of MealPlanningService"""
    global _meal_planning_service
    if _meal_planning_service is None:
        _meal_planning_service = MealPlanningService()
    return _meal_planning_service

