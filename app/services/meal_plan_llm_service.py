"""
Meal Plan LLM Service - Production-Grade AI Meal Planning
==========================================================
Uses LLM Router for multi-provider support with intelligent failover

Architecture Principles:
- Agentic AI: Context-aware, personalized meal planning
- Zero regression: Isolated service, clean interfaces
- Production-ready: Comprehensive error handling, fallback strategies
- Monetization-first: Cost tracking, usage analytics
"""

from typing import Dict, Any, Optional, List
from datetime import date, datetime, timedelta
import asyncio
import time
from app.services.llm_router import LLMRouter, LLMProvider
from app.models.meal_planning import (
    MealPlan, PlannedMeal, MealType, DayOfWeek,
    NutritionInfo, GenerateMealPlanRequest
)
import uuid


class MealPlanLLMService:
    """
    Production-grade meal plan generation using LLM Router
    
    Features:
    - Multi-provider LLM support (OpenAI, Claude, Gemini)
    - Intelligent prompt engineering for personalization
    - Automatic failover and error handling
    - Cost tracking and analytics
    - Fallback to curated mock data if all LLMs fail
    """
    
    def __init__(self):
        self.router = LLMRouter()
        print("✅ [MEAL PLAN LLM] Service initialized")
    
    async def generate_meal_plan(
        self,
        user_profile: Dict[str, Any],
        request: GenerateMealPlanRequest,
        user_id: str,
        preferred_provider: Optional[LLMProvider] = None
    ) -> Dict[str, Any]:
        """
        Generate personalized meal plan using LLM Router
        
        Args:
            user_profile: User's profile data (age, gender, goals, etc.)
            request: Meal plan generation request
            user_id: For analytics and cost tracking
            preferred_provider: Optional provider preference
        
        Returns:
            {
                'meal_plan_data': MealPlan object,
                'metadata': {
                    'provider_used': 'openai_gpt4o_mini',
                    'cost': 0.005,
                    'latency_ms': 2500,
                    'ai_generated': True,
                    ...
                }
            }
        """
        
        print(f"🍽️ [MEAL PLAN LLM] Generating meal plan for user: {user_id}")
        print(f"   Goal: {user_profile.get('fitness_goal', 'unknown')}")
        print(f"   Diet: {user_profile.get('diet_preference', 'none')}")
        print(f"   Calories: {request.daily_calorie_target}")
        
        try:
            # Build personalized prompt
            prompt = self._build_prompt(user_profile, request)
            system_instruction = self._get_system_instruction()
            
            # Generate using router (handles provider selection, failover, analytics)
            result = await self.router.generate_meal_plan(
                prompt=prompt,
                system_instruction=system_instruction,
                user_id=user_id,
                preferred_provider=preferred_provider
            )
            
            # Parse LLM response into MealPlan object
            meal_plan = self._parse_llm_response(
                llm_data=result['meal_plan'],
                user_id=user_id,
                request=request
            )
            
            print(f"✅ [MEAL PLAN LLM] Generated {len(meal_plan.meals)} meals")
            
            return {
                'meal_plan_data': meal_plan,
                'metadata': {
                    'provider_used': result['provider_used'],
                    'model_name': result['model_name'],
                    'cost': result['cost'],
                    'tokens_input': result['tokens_input'],
                    'tokens_output': result['tokens_output'],
                    'latency_ms': result['latency_ms'],
                    'timestamp': result['timestamp'],
                    'providers_tried': result['providers_tried'],
                    'ai_generated': True,
                    'fallback_used': False
                }
            }
            
        except Exception as e:
            print(f"❌ [MEAL PLAN LLM] Generation failed: {e}")
            print(f"🔄 [MEAL PLAN LLM] Falling back to curated mock data")
            
            # Fallback to mock data (ensures zero downtime)
            mock_plan = self._generate_fallback_plan(user_profile, request, user_id)
            
            return {
                'meal_plan_data': mock_plan,
                'metadata': {
                    'provider_used': 'fallback',
                    'model_name': 'curated_mock',
                    'cost': 0.0,
                    'tokens_input': 0,
                    'tokens_output': 0,
                    'latency_ms': 0,
                    'timestamp': datetime.now().isoformat(),
                    'providers_tried': ['all_failed'],
                    'ai_generated': False,
                    'fallback_used': True,
                    'error': str(e)
                }
            }
    
    async def generate_meal_plan_parallel(
        self,
        user_profile: Dict[str, Any],
        request: GenerateMealPlanRequest,
        user_id: str,
        preferred_provider: Optional[LLMProvider] = None
    ) -> Dict[str, Any]:
        """
        Generate meal plan using PARALLEL generation (7 days simultaneously)
        
        Performance: Reduces generation time from 78s to 15-20s (4-5x faster!)
        
        How it works:
        1. Split week into 7 days
        2. Generate each day in parallel (4 meals per day)
        3. Combine results into single meal plan
        4. Track cost and performance metrics
        
        Returns same format as generate_meal_plan()
        """
        
        start_time = time.time()
        print(f"⚡ [PARALLEL GENERATION] Starting parallel meal plan generation for user: {user_id}")
        print(f"   Generating 7 days in parallel (4 meals each = 28 total)")
        
        try:
            # Create tasks for all 7 days
            days = ['monday', 'tuesday', 'wednesday', 'thursday', 'friday', 'saturday', 'sunday']
            tasks = []
            
            for day_index, day_name in enumerate(days):
                task = self._generate_single_day(
                    user_profile=user_profile,
                    request=request,
                    user_id=user_id,
                    day_name=day_name,
                    day_index=day_index,
                    preferred_provider=preferred_provider
                )
                tasks.append(task)
            
            # Execute all 7 days in parallel
            parallel_start = time.time()
            day_results = await asyncio.gather(*tasks, return_exceptions=True)
            parallel_time = time.time() - parallel_start
            
            print(f"⏱️ [PERFORMANCE] Parallel LLM calls: {parallel_time:.2f}s (7 days simultaneously)")
            
            # Combine results
            all_meals = []
            total_cost = 0.0
            total_tokens_input = 0
            total_tokens_output = 0
            failed_days = []
            
            for day_index, result in enumerate(day_results):
                if isinstance(result, Exception):
                    print(f"❌ [PARALLEL GENERATION] Day {days[day_index]} failed: {result}")
                    failed_days.append(days[day_index])
                    continue
                
                all_meals.extend(result['meals'])
                total_cost += result['cost']
                total_tokens_input += result['tokens_input']
                total_tokens_output += result['tokens_output']
            
            if len(failed_days) >= 4:  # More than half failed
                raise Exception(f"Too many days failed: {failed_days}")
            
            # Create MealPlan object
            meal_plan = MealPlan(
                id=str(uuid.uuid4()),
                user_id=user_id,
                week_start_date=request.week_start_date,
                week_end_date=request.week_start_date + timedelta(days=6),
                meals=all_meals,
                dietary_preferences=request.dietary_preferences or [],
                daily_calorie_target=request.daily_calorie_target,
                daily_protein_target=request.daily_protein_target,
                is_active=True,
                created_at=datetime.now(),
                updated_at=datetime.now(),
                created_by_ai=True
            )
            
            total_time = time.time() - start_time
            print(f"✅ [PARALLEL GENERATION] Generated {len(all_meals)} meals in {total_time:.2f}s")
            print(f"   Speed improvement: {78 / total_time:.1f}x faster than sequential")
            print(f"   Total cost: ${total_cost:.4f}")
            
            return {
                'meal_plan_data': meal_plan,
                'metadata': {
                    'provider_used': 'openai_gpt4o_mini',
                    'model_name': 'gpt-4o-mini',
                    'cost': total_cost,
                    'tokens_input': total_tokens_input,
                    'tokens_output': total_tokens_output,
                    'latency_ms': int(total_time * 1000),
                    'timestamp': datetime.now().isoformat(),
                    'providers_tried': ['openai'],
                    'ai_generated': True,
                    'fallback_used': False,
                    'parallel_generation': True,
                    'days_generated': len(days) - len(failed_days),
                    'days_failed': failed_days
                }
            }
            
        except Exception as e:
            print(f"❌ [PARALLEL GENERATION] Failed: {e}")
            print(f"🔄 [PARALLEL GENERATION] Falling back to sequential generation")
            
            # Fallback to regular sequential generation
            return await self.generate_meal_plan(user_profile, request, user_id, preferred_provider)
    
    async def _generate_single_day(
        self,
        user_profile: Dict[str, Any],
        request: GenerateMealPlanRequest,
        user_id: str,
        day_name: str,
        day_index: int,
        preferred_provider: Optional[LLMProvider] = None
    ) -> Dict[str, Any]:
        """Generate meals for a single day (4 meals)"""
        
        # Build single-day prompt
        prompt = self._build_single_day_prompt(user_profile, request, day_name, day_index)
        system_instruction = self._get_single_day_system_instruction()
        
        # Generate using router
        result = await self.router.generate_meal_plan(
            prompt=prompt,
            system_instruction=system_instruction,
            user_id=user_id,
            preferred_provider=preferred_provider
        )
        
        # Parse response
        meals_data = result['meal_plan'].get('meals', [])
        
        # Convert to PlannedMeal objects
        planned_meals = []
        current_date = request.week_start_date + timedelta(days=day_index)
        
        # Map day_name to DayOfWeek enum
        day_enum = DayOfWeek(day_name.lower())
        
        for meal_data in meals_data:
            planned_meal = PlannedMeal(
                id=str(uuid.uuid4()),
                day=day_enum,  # CRITICAL: Add day field
                recipe_id=str(uuid.uuid4()),  # Temporary ID for LLM-generated meals
                recipe_name=meal_data.get('meal_name', 'Unnamed Meal'),
                meal_type=MealType(meal_data.get('meal_type', 'breakfast')),
                date=current_date,
                servings=1,
                notes=meal_data.get('why', ''),
                calories=meal_data.get('calories', 0),
                protein_g=meal_data.get('protein_g', 0),
                carbs_g=meal_data.get('carbs_g', 0),
                fat_g=meal_data.get('fat_g', 0),
                fiber_g=meal_data.get('fiber_g', 0)
            )
            planned_meals.append(planned_meal)
        
        return {
            'meals': planned_meals,
            'cost': result['cost'],
            'tokens_input': result['tokens_input'],
            'tokens_output': result['tokens_output']
        }
    
    def _get_system_instruction(self) -> str:
        """Get system-level instructions for LLM"""
        
        return """You are Yuvi, a friendly and knowledgeable AI nutrition companion. You help users achieve their health and fitness goals through personalized meal planning.

Your personality:
- Warm, encouraging, and supportive (like a helpful friend)
- Expert in nutrition science and meal planning
- Culturally aware and respectful of diverse food preferences
- Always positive and motivating

Your job is to generate a precise FULL WEEK meal plan with these goals:
- Always hit calorie and macronutrient targets based on user profile FOR EACH DAY
- Respect ALL user dietary preferences, allergies, and food dislikes
- Optimize for user's active goal (weight loss/gain, muscle gain, health)
- Generate practical, easy-to-follow meals with real-world portions
- Include brief reasoning for each meal choice
- Provide variety across the week

CRITICAL: You MUST respond with valid JSON only, in this exact format:

{
  "daily_summary": {
    "total_calories": 1800,
    "total_protein_g": 130,
    "total_carbs_g": 180,
    "total_fat_g": 65
  },
  "meals": [
    {
      "day": "monday",
      "meal_type": "breakfast",
      "meal_name": "Oats Dosa with Chutney",
      "ingredients": ["oats", "urad dal", "curd", "spices"],
      "portion": "2 dosas",
      "calories": 350,
      "protein_g": 16,
      "carbs_g": 45,
      "fat_g": 8,
      "fiber_g": 6,
      "why": "High-fiber, high-protein breakfast. Fits vegetarian preference and provides sustained energy."
    },
    {
      "day": "monday",
      "meal_type": "lunch",
      "meal_name": "Quinoa Power Bowl",
      "ingredients": ["quinoa", "chickpeas", "vegetables", "tahini"],
      "portion": "1 large bowl",
      "calories": 480,
      "protein_g": 22,
      "carbs_g": 65,
      "fat_g": 15,
      "fiber_g": 12,
      "why": "Complete protein source. Rich in fiber and micronutrients for sustained energy."
    },
    {
      "day": "monday",
      "meal_type": "dinner",
      "meal_name": "Grilled Tofu with Vegetables",
      "ingredients": ["tofu", "broccoli", "bell peppers", "olive oil"],
      "portion": "200g tofu + 2 cups vegetables",
      "calories": 420,
      "protein_g": 35,
      "carbs_g": 30,
      "fat_g": 18,
      "fiber_g": 8,
      "why": "High-protein dinner. Low-carb for evening meal. Rich in vitamins."
    },
    {
      "day": "tuesday",
      "meal_type": "breakfast",
      "meal_name": "Protein Pancakes",
      "ingredients": ["oats", "eggs", "banana", "protein powder"],
      "portion": "3 pancakes",
      "calories": 380,
      "protein_g": 28,
      "carbs_g": 42,
      "fat_g": 10,
      "fiber_g": 5,
      "why": "High-protein breakfast for muscle maintenance. Natural sweetness from banana."
    }
    ... (continue for all 7 days, 3-4 meals per day = 21-28 total meals)
  ],
  "grocery_list": ["oats", "urad dal", "curd", "spices", "quinoa", "chickpeas", "vegetables", "tahini", "tofu", "broccoli", "bell peppers", "olive oil", "eggs", "banana", "protein powder"],
  "weekly_tips": "Meal prep on Sunday for the week. Drink 8-10 glasses of water daily. Vary protein sources throughout the week."
}

IMPORTANT RULES:
1. day must be one of: "monday", "tuesday", "wednesday", "thursday", "friday", "saturday", "sunday"
2. meal_type must be one of: "breakfast", "lunch", "dinner", "snack"
3. All numeric values must be numbers, not strings
4. Generate EXACTLY 4 meals for EACH of the 7 days (total 28 meals) - include breakfast, lunch, dinner, AND snack for every day
5. CRITICAL: Each day MUST hit calorie target ±50 calories (calculate total before finalizing)
6. CRITICAL: Each day MUST meet or exceed protein target (add protein-rich snacks if needed)
7. Use GENEROUS portions to hit targets - don't be conservative with serving sizes
8. Include "why" for each meal to build user trust and explain nutritional value
9. STRICTLY respect dietary restrictions (vegetarian = NO meat/fish/poultry, vegan = NO animal products)
10. Use simple, accessible ingredients available in local markets
11. Provide variety across the week - don't repeat the same meals every day
12. Provide practical grocery list for the entire week
13. ACCURACY MATTERS: Double-check your nutrition calculations before responding

Respond with ONLY the JSON, no additional text."""
    
    def _build_prompt(
        self,
        user_profile: Dict[str, Any],
        request: GenerateMealPlanRequest
    ) -> str:
        """Build personalized prompt for meal plan generation"""
        
        # Extract user data
        age = user_profile.get('age', 30)
        gender = user_profile.get('gender', 'unknown')
        weight_kg = user_profile.get('weight_kg', 70)
        height_cm = user_profile.get('height_cm', 170)
        activity_level = user_profile.get('activity_level', 'moderate')
        fitness_goal = user_profile.get('fitness_goal', 'maintain')
        diet_preference = user_profile.get('diet_preference', 'none')
        allergies = user_profile.get('allergies', [])
        disliked_foods = user_profile.get('disliked_foods', [])
        
        # Build dietary preferences string
        dietary_prefs = []
        if request.dietary_preferences:
            # Convert enum values to strings
            dietary_prefs.extend([str(pref.value) if hasattr(pref, 'value') else str(pref) for pref in request.dietary_preferences])
        if diet_preference and diet_preference != 'none':
            dietary_prefs.append(diet_preference)
        
        dietary_str = ", ".join(dietary_prefs) if dietary_prefs else "No specific restrictions"
        
        print(f"🔍 [MEAL PLAN LLM] Dietary preferences: {dietary_str}")
        print(f"   Request prefs: {request.dietary_preferences}")
        print(f"   Profile diet: {diet_preference}")
        allergies_str = ", ".join(allergies) if allergies else "None"
        dislikes_str = ", ".join(disliked_foods) if disliked_foods else "None"
        
        # Map fitness goal to meal plan strategy
        goal_strategy = {
            'lose_weight': 'weight loss with moderate calorie deficit',
            'gain_weight': 'muscle gain with calorie surplus',
            'build_muscle': 'muscle building with high protein',
            'maintain': 'weight maintenance and health',
            'improve_health': 'overall health and wellness'
        }.get(fitness_goal, 'health and wellness')
        
        # Calculate week dates
        week_end = request.week_start_date + timedelta(days=6)
        
        prompt = f"""Generate a personalized FULL WEEK meal plan for:

USER PROFILE:
- Age: {age} years
- Gender: {gender}
- Weight: {weight_kg} kg
- Height: {height_cm} cm
- Activity Level: {activity_level}
- Fitness Goal: {goal_strategy}

DIETARY REQUIREMENTS (STRICTLY FOLLOW THESE):
- Dietary Preferences: {dietary_str}
- Allergies (MUST AVOID): {allergies_str}
- Disliked Foods (MUST AVOID): {dislikes_str}

CRITICAL: If dietary preferences include "vegetarian" or "vegan", DO NOT include any meat, fish, poultry, or seafood.
CRITICAL: If dietary preferences include "keto", focus on high-fat, very low-carb meals (<20g carbs per day).
CRITICAL: Respect ALL dietary restrictions strictly

DAILY TARGETS (MUST HIT ACCURATELY):
- Calories: {request.daily_calorie_target} kcal (±50 kcal tolerance, aim for exact target)
- Protein: {request.daily_protein_target}g (MINIMUM required, can exceed by 10-20%)
- Carbs: Balanced for goal (adjust based on dietary preference)
- Fat: 25-35% of total calories from healthy fats

CRITICAL NUTRITION RULES:
1. EACH DAY must hit the calorie target (not just weekly average)
2. EACH DAY must meet or exceed the protein target
3. If a day is under target after 3 meals, ADD a protein-rich snack to reach goals
4. Protein priority: Include high-protein foods in every meal (eggs, paneer, chicken, lentils, Greek yogurt, protein powder)
5. Calculate nutrition accurately - don't underestimate portions

MEAL PLAN REQUIREMENTS:
- Generate meals for ENTIRE WEEK: {request.week_start_date.strftime('%A, %B %d')} to {week_end.strftime('%A, %B %d, %Y')}
- For EACH of the 7 days, include: Breakfast, Lunch, Dinner, and MANDATORY Snack (to hit targets)
- Total meals: 28 meals (4 meals × 7 days) - all days must have 4 meals
- Use simple, accessible ingredients
- Provide realistic, GENEROUS portions to hit targets (e.g., "3 eggs", "200g paneer", "2 cups dal")
- Respect all dietary restrictions strictly
- Include brief "why" for each meal to explain nutritional benefits
- Vary meals across the week for diversity

CUISINE PREFERENCES:
- Prefer Indian and International cuisines
- Simple preparation methods
- Ingredients easily available in local markets

Generate the meal plan now in the specified JSON format."""
        
        return prompt
    
    def _build_single_day_prompt(
        self,
        user_profile: Dict[str, Any],
        request: GenerateMealPlanRequest,
        day_name: str,
        day_index: int
    ) -> str:
        """Build prompt for generating a single day (4 meals)"""
        
        # Extract user data
        age = user_profile.get('age', 30)
        gender = user_profile.get('gender', 'prefer_not_to_say')
        weight_kg = user_profile.get('weight_kg', 70)
        height_cm = user_profile.get('height_cm', 170)
        activity_level = user_profile.get('activity_level', 'moderate')
        fitness_goal = user_profile.get('fitness_goal', 'maintain')
        diet_preference = user_profile.get('diet_preference', 'none')
        allergies = user_profile.get('allergies', [])
        disliked_foods = user_profile.get('disliked_foods', [])
        
        # Convert dietary preferences to strings
        dietary_prefs = request.dietary_preferences or []
        dietary_str = ", ".join([pref.value if hasattr(pref, 'value') else str(pref) for pref in dietary_prefs]) if dietary_prefs else "None"
        
        allergies_str = ", ".join(allergies) if allergies else "None"
        dislikes_str = ", ".join(disliked_foods) if disliked_foods else "None"
        
        # Map fitness goal
        goal_strategy = {
            'lose_weight': 'weight loss with moderate calorie deficit',
            'gain_weight': 'muscle gain with calorie surplus',
            'build_muscle': 'muscle building with high protein',
            'maintain': 'weight maintenance and health',
            'improve_health': 'overall health and wellness'
        }.get(fitness_goal, 'health and wellness')
        
        prompt = f"""Generate meals for {day_name.upper()} for:

USER PROFILE:
- Age: {age} years
- Gender: {gender}
- Weight: {weight_kg} kg
- Height: {height_cm} cm
- Activity Level: {activity_level}
- Fitness Goal: {goal_strategy}

DIETARY REQUIREMENTS (STRICTLY FOLLOW):
- Dietary Preferences: {dietary_str}
- Allergies (MUST AVOID): {allergies_str}
- Disliked Foods (MUST AVOID): {dislikes_str}

CRITICAL: Respect ALL dietary restrictions strictly!

DAILY TARGETS (MUST HIT ACCURATELY):
- Calories: {request.daily_calorie_target} kcal (±50 kcal tolerance)
- Protein: {request.daily_protein_target}g (MINIMUM required, can exceed by 10-20%)
- Fat: 25-35% of total calories

MEAL REQUIREMENTS FOR {day_name.upper()}:
- Generate EXACTLY 4 meals: Breakfast, Lunch, Dinner, Snack
- Each meal must hit portion of daily target
- Use simple, accessible ingredients
- Provide realistic, GENEROUS portions
- Include brief "why" for each meal

Generate the 4 meals now in JSON format."""
        
        return prompt
    
    def _get_single_day_system_instruction(self) -> str:
        """System instruction for single-day generation"""
        
        return """You are an expert nutrition AI. Generate EXACTLY 4 meals for ONE day.

Respond with ONLY valid JSON in this format:

{
  "meals": [
    {
      "meal_type": "breakfast",
      "meal_name": "Protein Pancakes",
      "ingredients": ["oats", "eggs", "banana"],
      "portion": "3 pancakes",
      "calories": 450,
      "protein_g": 30,
      "carbs_g": 50,
      "fat_g": 12,
      "fiber_g": 6,
      "why": "High-protein breakfast for muscle maintenance"
    },
    {
      "meal_type": "lunch",
      "meal_name": "Quinoa Bowl",
      "ingredients": ["quinoa", "chickpeas", "vegetables"],
      "portion": "1 large bowl",
      "calories": 550,
      "protein_g": 25,
      "carbs_g": 70,
      "fat_g": 15,
      "fiber_g": 12,
      "why": "Balanced lunch with complete protein"
    },
    {
      "meal_type": "dinner",
      "meal_name": "Grilled Tofu Stir-Fry",
      "ingredients": ["tofu", "vegetables", "brown rice"],
      "portion": "1 plate",
      "calories": 500,
      "protein_g": 35,
      "carbs_g": 55,
      "fat_g": 18,
      "fiber_g": 10,
      "why": "High-protein dinner, low-carb for evening"
    },
    {
      "meal_type": "snack",
      "meal_name": "Greek Yogurt with Berries",
      "ingredients": ["greek yogurt", "berries", "nuts"],
      "portion": "1 bowl",
      "calories": 300,
      "protein_g": 20,
      "carbs_g": 30,
      "fat_g": 10,
      "fiber_g": 5,
      "why": "Protein-rich snack to hit daily targets"
    }
  ]
}

RULES:
1. meal_type must be: "breakfast", "lunch", "dinner", or "snack"
2. Generate EXACTLY 4 meals
3. All numeric values must be numbers, not strings
4. Day total should hit calorie and protein targets
5. Respect dietary restrictions strictly
6. Use generous portions to hit targets

Respond with ONLY the JSON, no additional text."""
    
    def _parse_llm_response(
        self,
        llm_data: Dict[str, Any],
        user_id: str,
        request: GenerateMealPlanRequest
    ) -> MealPlan:
        """Parse LLM JSON response into MealPlan object"""
        
        # Extract meals from LLM response
        meals_data = llm_data.get('meals', [])
        
        print(f"🔍 [MEAL PLAN LLM] Parsing {len(meals_data)} meals from LLM response")
        
        # Create PlannedMeal objects (using existing model structure)
        planned_meals = []
        for meal_data in meals_data:
            try:
                # Map day string to enum
                day_str = meal_data.get('day', 'monday').lower()
                try:
                    day = DayOfWeek(day_str)
                except ValueError:
                    print(f"⚠️ [MEAL PLAN LLM] Invalid day '{day_str}', defaulting to MONDAY")
                    day = DayOfWeek.MONDAY
                
                # Map meal_type string to enum
                meal_type_str = meal_data.get('meal_type', 'snack').lower()
                meal_type = MealType(meal_type_str)
                
                # Extract nutrition data from LLM response
                calories = meal_data.get('calories', 0)
                protein_g = meal_data.get('protein_g', 0)
                carbs_g = meal_data.get('carbs_g', 0)
                fat_g = meal_data.get('fat_g', 0)
                fiber_g = meal_data.get('fiber_g', 0)
                
                # Create planned meal using existing model structure
                planned_meal = PlannedMeal(
                    day=day,
                    meal_type=meal_type,
                    recipe_id=str(uuid.uuid4()),  # Generate temp ID
                    recipe_name=meal_data.get('meal_name', 'Unnamed Meal'),
                    servings=1,
                    notes=meal_data.get('why', ''),
                    calories=calories,
                    protein_g=protein_g,
                    carbs_g=carbs_g,
                    fat_g=fat_g,
                    fiber_g=fiber_g
                )
                
                planned_meals.append(planned_meal)
                
            except Exception as e:
                print(f"⚠️ [MEAL PLAN LLM] Error parsing meal: {e}")
                import traceback
                traceback.print_exc()
                continue
        
        print(f"✅ [MEAL PLAN LLM] Successfully parsed {len(planned_meals)} meals")
        
        # Count meals per day and calculate nutrition totals for verification
        meals_per_day = {}
        nutrition_per_day = {}
        
        for meal in planned_meals:
            day_name = meal.day.value
            meals_per_day[day_name] = meals_per_day.get(day_name, 0) + 1
            
            if day_name not in nutrition_per_day:
                nutrition_per_day[day_name] = {'calories': 0, 'protein_g': 0}
            
            nutrition_per_day[day_name]['calories'] += meal.calories or 0
            nutrition_per_day[day_name]['protein_g'] += meal.protein_g or 0
        
        print(f"📊 [MEAL PLAN LLM] Meals per day: {meals_per_day}")
        print(f"🍽️ [MEAL PLAN LLM] Daily nutrition totals:")
        for day, nutrition in nutrition_per_day.items():
            print(f"   {day}: {nutrition['calories']} kcal, {nutrition['protein_g']:.1f}g protein")
        
        # Calculate average daily nutrition
        if nutrition_per_day:
            avg_calories = sum(n['calories'] for n in nutrition_per_day.values()) / len(nutrition_per_day)
            avg_protein = sum(n['protein_g'] for n in nutrition_per_day.values()) / len(nutrition_per_day)
            print(f"📈 [MEAL PLAN LLM] Average per day: {avg_calories:.0f} kcal, {avg_protein:.1f}g protein")
            print(f"🎯 [MEAL PLAN LLM] Target: {request.daily_calorie_target} kcal, {request.daily_protein_target}g protein")
        
        # Create meal plan
        week_end = request.week_start_date + timedelta(days=6)
        
        meal_plan = MealPlan(
            id=str(uuid.uuid4()),
            user_id=user_id,
            week_start_date=request.week_start_date,
            week_end_date=week_end,
            dietary_preferences=request.dietary_preferences,
            daily_calorie_target=request.daily_calorie_target,
            daily_protein_target=request.daily_protein_target,
            created_by_ai=True,
            ai_generation_prompt=f"Personalized meal plan for week {request.week_start_date}",
            meals=planned_meals
        )
        
        return meal_plan
    
    def _generate_fallback_plan(
        self,
        user_profile: Dict[str, Any],
        request: GenerateMealPlanRequest,
        user_id: str
    ) -> MealPlan:
        """
        Generate fallback meal plan if all LLMs fail
        Uses curated, healthy meals that work for most users
        """
        
        print("🔄 [MEAL PLAN LLM] Generating curated fallback plan")
        
        # Get dietary preference
        diet_pref = user_profile.get('diet_preference', 'none')
        is_vegetarian = diet_pref in ['vegetarian', 'vegan']
        
        # Curated meals (healthy, balanced, accessible)
        if is_vegetarian:
            meals_data = [
                {
                    'meal_type': 'breakfast',
                    'meal_name': 'Oats Dosa with Chutney',
                    'ingredients': ['oats', 'urad dal', 'curd', 'spices'],
                    'portion': '2 dosas',
                    'calories': 350,
                    'protein_g': 16,
                    'carbs_g': 45,
                    'fat_g': 8,
                    'fiber_g': 6,
                    'why': 'High-fiber, high-protein breakfast. Provides sustained energy.'
                },
                {
                    'meal_type': 'lunch',
                    'meal_name': 'Quinoa Power Bowl',
                    'ingredients': ['quinoa', 'chickpeas', 'vegetables', 'tahini'],
                    'portion': '1 large bowl',
                    'calories': 480,
                    'protein_g': 22,
                    'carbs_g': 65,
                    'fat_g': 15,
                    'fiber_g': 12,
                    'why': 'Complete protein source. Rich in fiber and micronutrients.'
                },
                {
                    'meal_type': 'snack',
                    'meal_name': 'Greek Yogurt with Berries',
                    'ingredients': ['greek yogurt', 'mixed berries', 'honey'],
                    'portion': '1 cup',
                    'calories': 180,
                    'protein_g': 15,
                    'carbs_g': 25,
                    'fat_g': 3,
                    'fiber_g': 3,
                    'why': 'High-protein snack. Probiotics support gut health.'
                },
                {
                    'meal_type': 'dinner',
                    'meal_name': 'Paneer Tikka with Vegetables',
                    'ingredients': ['paneer', 'bell peppers', 'onions', 'spices'],
                    'portion': '200g paneer + vegetables',
                    'calories': 420,
                    'protein_g': 30,
                    'carbs_g': 25,
                    'fat_g': 22,
                    'fiber_g': 6,
                    'why': 'High-protein dinner. Low-carb for evening meal.'
                }
            ]
        else:
            meals_data = [
                {
                    'meal_type': 'breakfast',
                    'meal_name': 'Veggie Omelette with Toast',
                    'ingredients': ['eggs', 'vegetables', 'whole wheat bread'],
                    'portion': '3-egg omelette + 2 slices toast',
                    'calories': 380,
                    'protein_g': 28,
                    'carbs_g': 35,
                    'fat_g': 12,
                    'fiber_g': 5,
                    'why': 'High-protein breakfast. Provides sustained energy and essential nutrients.'
                },
                {
                    'meal_type': 'lunch',
                    'meal_name': 'Grilled Chicken Salad',
                    'ingredients': ['chicken breast', 'mixed greens', 'quinoa', 'olive oil'],
                    'portion': '150g chicken + large salad',
                    'calories': 450,
                    'protein_g': 40,
                    'carbs_g': 35,
                    'fat_g': 15,
                    'fiber_g': 8,
                    'why': 'Lean protein with complex carbs. Rich in vitamins and minerals.'
                },
                {
                    'meal_type': 'snack',
                    'meal_name': 'Protein Smoothie',
                    'ingredients': ['protein powder', 'banana', 'almond milk', 'peanut butter'],
                    'portion': '1 large glass',
                    'calories': 280,
                    'protein_g': 25,
                    'carbs_g': 30,
                    'fat_g': 8,
                    'fiber_g': 4,
                    'why': 'Quick protein boost. Convenient and nutritious.'
                },
                {
                    'meal_type': 'dinner',
                    'meal_name': 'Baked Salmon with Vegetables',
                    'ingredients': ['salmon', 'broccoli', 'sweet potato', 'olive oil'],
                    'portion': '150g salmon + vegetables',
                    'calories': 480,
                    'protein_g': 38,
                    'carbs_g': 40,
                    'fat_g': 18,
                    'fiber_g': 7,
                    'why': 'Omega-3 rich protein. Balanced macros for recovery.'
                }
            ]
        
        # Parse into MealPlan object
        return self._parse_llm_response(
            llm_data={'meals': meals_data},
            user_id=user_id,
            request=request
        )

