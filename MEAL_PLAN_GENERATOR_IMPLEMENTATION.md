# 🍽️ Production-Grade Meal Plan Generator - Implementation Plan

## Status: 🚀 READY FOR IMPLEMENTATION

**Date:** November 8, 2025  
**Priority:** HIGH - Flagship Feature for Production  
**Estimated Time:** 2-3 hours  
**Monetization Ready:** YES

---

## 🎯 Overview

Transform the current mock meal plan generator into a production-grade, LLM-powered, monetizable feature that generates personalized meal plans based on user profile, preferences, goals, and real-time context.

### Current State
- ✅ UI/UX complete and beautiful
- ✅ Data models defined (`MealPlan`, `PlannedMeal`, `Recipe`)
- ✅ API endpoints exist (`/meal-planning/plans/generate`)
- ❌ Returns mock/stub data
- ❌ No LLM integration
- ❌ No real personalization

### Target State
- ✅ LLM-powered meal generation (OpenAI GPT-4)
- ✅ Full personalization (profile, goals, preferences)
- ✅ Real-time context awareness (logged meals, streaks)
- ✅ Grocery list generation
- ✅ Meal swap/correction capability
- ✅ Monetization-ready API structure

---

## 📋 Implementation Steps

### Phase 1: LLM Integration (60 min)

#### Step 1.1: Create LLM Prompt Template
**File:** `app/services/meal_plan_llm_service.py` (NEW)

```python
"""
LLM-powered Meal Plan Generation Service
Uses OpenAI GPT-4 for intelligent, personalized meal planning
"""

from openai import AsyncOpenAI
import json
from typing import Dict, Any, List
from datetime import date, datetime

class MealPlanLLMService:
    def __init__(self):
        self.client = AsyncOpenAI(api_key=os.getenv("OPENAI_API_KEY"))
        
    async def generate_meal_plan(
        self,
        user_profile: Dict[str, Any],
        preferences: Dict[str, Any],
        context: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Generate personalized meal plan using LLM
        
        Args:
            user_profile: age, gender, weight, height, activity_level, goal
            preferences: diet, allergies, cuisine, budget, cooking_skill
            context: logged_meals_today, current_streak, last_workout
        
        Returns:
            Structured meal plan JSON
        """
        
        prompt = self._build_prompt(user_profile, preferences, context)
        
        response = await self.client.chat.completions.create(
            model="gpt-4o-mini",  # Fast and cost-effective
            messages=[
                {"role": "system", "content": self._get_system_instruction()},
                {"role": "user", "content": prompt}
            ],
            temperature=0.7,  # Creative but consistent
            response_format={"type": "json_object"}  # Enforce JSON output
        )
        
        meal_plan_json = json.loads(response.choices[0].message.content)
        return meal_plan_json
    
    def _get_system_instruction(self) -> str:
        return """You are an expert nutrition and meal planning AI powered by the latest scientific research, national health guidelines, and user-centric personalization.

Your job is to generate a precise meal plan with these goals:

- Always hit calorie and macronutrient targets based on user profile (age, gender, weight, height, activity).
- Respect ALL user dietary preferences, allergies, medical needs, budget, food dislikes, preferred cuisines, and ingredient restrictions.
- Integrate actual logged food, skipped meals, and real-world adherence into your suggestions.
- Optimize for user's active goal (e.g. weight loss/gain, muscle gain, heart health) and any current context (busy day, workout schedule, fasting/feast, etc).
- Generate a structured daily meal plan with time-slotted meals, portion sizes, food/recipe names, and simple prep notes.
- Each meal includes a brief "why we chose this" - make reasoning about macros or food type understandable for the user.
- Provide a grocery list that covers all ingredients for the chosen meals.
- Always output strict JSON in the specified format.

IMPORTANT:
- Use simple, real-world food names (not complex recipes)
- Portions should be practical (e.g., "2 dosas", "1 cup rice", "150g chicken")
- Prep notes should be 1-2 sentences max
- "Why" explanations should be user-friendly, not technical"""

    def _build_prompt(
        self,
        user_profile: Dict[str, Any],
        preferences: Dict[str, Any],
        context: Dict[str, Any]
    ) -> str:
        return f"""Generate a meal plan for today with the following details:

USER PROFILE:
- Age: {user_profile.get('age')} years
- Gender: {user_profile.get('gender')}
- Weight: {user_profile.get('weight_kg')} kg
- Height: {user_profile.get('height_cm')} cm
- Activity Level: {user_profile.get('activity_level')}
- Goal: {user_profile.get('fitness_goal')}

DAILY TARGETS:
- Calories: {user_profile.get('daily_calories', 2000)} kcal
- Protein: {user_profile.get('daily_protein', 150)}g
- Carbs: {user_profile.get('daily_carbs', 200)}g
- Fat: {user_profile.get('daily_fat', 65)}g

PREFERENCES:
- Diet: {preferences.get('diet_preference', 'none')}
- Allergies: {', '.join(preferences.get('allergies', []))}
- Disliked Foods: {', '.join(preferences.get('disliked_foods', []))}
- Preferred Cuisines: {', '.join(preferences.get('preferred_cuisines', ['Indian', 'International']))}
- Budget: {preferences.get('budget', 'medium')}
- Cooking Skill: {preferences.get('cooking_skill', 'easy')}

CURRENT CONTEXT:
- Today's Date: {context.get('date', date.today().isoformat())}
- Meals Logged Today: {context.get('meals_logged_today', 0)}
- Current Streak: {context.get('current_streak', 0)} days
- Last Workout: {context.get('last_workout', 'None')}

Generate a meal plan with 3-4 meals (breakfast, lunch, dinner, optional snack) that:
1. Hits the calorie and macro targets
2. Respects all dietary restrictions and preferences
3. Uses simple, practical recipes
4. Includes portion sizes and brief prep notes
5. Explains why each meal was chosen

Return JSON in this exact format:
{{
  "date": "YYYY-MM-DD",
  "goal": "{user_profile.get('fitness_goal')}",
  "calorie_target": {user_profile.get('daily_calories', 2000)},
  "protein_target": {user_profile.get('daily_protein', 150)},
  "carb_target": {user_profile.get('daily_carbs', 200)},
  "fat_target": {user_profile.get('daily_fat', 65)},
  "meals": [
    {{
      "name": "Oats Dosa",
      "time": "Breakfast",
      "ingredients": ["oats", "urad dal", "curd", "spices"],
      "portion": "2 dosas",
      "prep_notes": "Soak oats and dal overnight. Blend and ferment.",
      "macros": {{ "calories": 300, "protein": 16, "carbs": 45, "fat": 6 }},
      "why": "High-fiber, high-protein, fits your vegetarian preference, suitable for muscle recovery."
    }}
  ],
  "grocery_list": ["oats", "urad dal", "curd", "spices"],
  "daily_totals": {{ "calories": 0, "protein": 0, "carbs": 0, "fat": 0 }},
  "feedback_prompt": "What would you like to swap or change in your plan?"
}}"""
```

#### Step 1.2: Update Meal Planning Service
**File:** `app/services/meal_planning_service.py`

Replace the mock `generate_meal_plan_ai` method (lines 282-319) with:

```python
async def generate_meal_plan_ai(
    self,
    user_id: str,
    request: GenerateMealPlanRequest
) -> MealPlan:
    """
    Generate a meal plan using LLM
    """
    print(f"🟢 [MEAL PLANNING] Generating AI meal plan...")
    print(f"   User: {user_id}")
    
    # 1. Get user profile
    user_doc = self.db.collection('users').document(user_id).get()
    if not user_doc.exists:
        raise ValueError(f"User {user_id} not found")
    
    user_data = user_doc.to_dict()
    profile_data = user_data.get('profile', {})
    
    # 2. Build user profile for LLM
    user_profile = {
        'age': profile_data.get('age'),
        'gender': profile_data.get('gender'),
        'weight_kg': profile_data.get('weight_kg'),
        'height_cm': profile_data.get('height_cm'),
        'activity_level': profile_data.get('activity_level'),
        'fitness_goal': profile_data.get('fitness_goal'),
        'daily_calories': profile_data.get('daily_goals', {}).get('calories', 2000),
        'daily_protein': profile_data.get('daily_goals', {}).get('protein_g', 150),
        'daily_carbs': profile_data.get('daily_goals', {}).get('carbs_g', 200),
        'daily_fat': profile_data.get('daily_goals', {}).get('fat_g', 65),
    }
    
    # 3. Build preferences
    preferences = {
        'diet_preference': profile_data.get('diet_preference', 'none'),
        'allergies': profile_data.get('allergies', []),
        'disliked_foods': profile_data.get('disliked_foods', []),
        'preferred_cuisines': request.dietary_preferences or ['Indian', 'International'],
        'budget': 'medium',
        'cooking_skill': 'easy',
    }
    
    # 4. Build context (today's activity)
    from app.services.context_service import ContextService
    context_service = ContextService(self.db)
    user_context = context_service.get_user_context(user_id)
    
    context = {
        'date': request.week_start_date.isoformat(),
        'meals_logged_today': user_context.meals_logged_today,
        'current_streak': profile_data.get('current_streak', 0),
        'last_workout': 'Today' if user_context.workouts_today > 0 else 'None',
    }
    
    # 5. Generate meal plan using LLM
    from app.services.meal_plan_llm_service import MealPlanLLMService
    llm_service = MealPlanLLMService()
    meal_plan_data = await llm_service.generate_meal_plan(
        user_profile=user_profile,
        preferences=preferences,
        context=context
    )
    
    # 6. Convert LLM output to MealPlan model
    meal_plan = self._convert_llm_to_meal_plan(
        user_id=user_id,
        llm_data=meal_plan_data,
        request=request
    )
    
    # 7. Save to Firestore
    await self.create_meal_plan(user_id, meal_plan)
    
    print(f"✅ [MEAL PLANNING] AI meal plan generated! {len(meal_plan.meals)} meals")
    return meal_plan

def _convert_llm_to_meal_plan(
    self,
    user_id: str,
    llm_data: Dict[str, Any],
    request: GenerateMealPlanRequest
) -> MealPlan:
    """Convert LLM JSON output to MealPlan model"""
    
    # Create meal plan
    week_end = request.week_start_date + timedelta(days=6)
    
    meal_plan = MealPlan(
        user_id=user_id,
        week_start_date=request.week_start_date,
        week_end_date=week_end,
        dietary_preferences=request.dietary_preferences,
        daily_calorie_target=llm_data.get('calorie_target', 2000),
        daily_protein_target=llm_data.get('protein_target', 150),
        created_by_ai=True,
        ai_generation_prompt=f"LLM-generated for {llm_data.get('goal')}",
        meals=[]
    )
    
    # Convert LLM meals to PlannedMeal objects
    for llm_meal in llm_data.get('meals', []):
        # Create a simple recipe for this meal
        recipe_id = f"ai_recipe_{llm_meal['name'].lower().replace(' ', '_')}"
        
        # Map time to meal type
        time_str = llm_meal.get('time', 'Breakfast').lower()
        if 'breakfast' in time_str:
            meal_type = MealType.BREAKFAST
        elif 'lunch' in time_str:
            meal_type = MealType.LUNCH
        elif 'dinner' in time_str:
            meal_type = MealType.DINNER
        else:
            meal_type = MealType.SNACK
        
        # Create planned meal
        planned_meal = PlannedMeal(
            day=DayOfWeek.MONDAY,  # For daily plan, use first day
            meal_type=meal_type,
            recipe_id=recipe_id,
            recipe_name=llm_meal['name'],
            portion_size=llm_meal.get('portion', '1 serving'),
            notes=llm_meal.get('why', ''),
            is_logged=False
        )
        
        meal_plan.meals.append(planned_meal)
        
        # Store recipe details in meal plan metadata for display
        if not hasattr(meal_plan, 'ai_meal_details'):
            meal_plan.ai_meal_details = {}
        
        meal_plan.ai_meal_details[recipe_id] = {
            'ingredients': llm_meal.get('ingredients', []),
            'prep_notes': llm_meal.get('prep_notes', ''),
            'macros': llm_meal.get('macros', {}),
            'why': llm_meal.get('why', '')
        }
    
    # Store grocery list
    meal_plan.grocery_list_items = llm_data.get('grocery_list', [])
    
    return meal_plan
```

---

### Phase 2: API Enhancement (30 min)

#### Step 2.1: Add Environment Variable
**File:** `.env.local`

```
OPENAI_API_KEY=your-openai-api-key-here
```

#### Step 2.2: Update Requirements
**File:** `requirements.txt`

```
openai>=1.3.0
```

#### Step 2.3: Install Dependencies
```bash
pip install openai
```

---

### Phase 3: Frontend Enhancement (30 min)

#### Step 3.1: Update Meal Card Display
**File:** `flutter_app/lib/screens/plan/meal_planning_tab.dart`

Update `_buildMealCard` to show AI-generated details:

```dart
Widget _buildMealCard(Map<String, dynamic> meal) {
  final mealName = meal['name'] ?? meal['recipe_name'] ?? 'Meal';
  final calories = meal['calories'] ?? 0;
  final protein = meal['protein'] ?? 0;
  
  // AI-generated details
  final aiDetails = meal['ai_details'] as Map<String, dynamic>?;
  final why = aiDetails?['why'] as String?;
  final ingredients = aiDetails?['ingredients'] as List?;
  final prepNotes = aiDetails?['prep_notes'] as String?;
  
  return Container(
    margin: const EdgeInsets.only(bottom: 16),
    decoration: BoxDecoration(
      color: Colors.white,
      borderRadius: BorderRadius.circular(20),
      boxShadow: [
        BoxShadow(
          color: Colors.black.withOpacity(0.05),
          blurRadius: 20,
          offset: const Offset(0, 4),
        ),
      ],
    ),
    child: Material(
      color: Colors.transparent,
      child: InkWell(
        borderRadius: BorderRadius.circular(20),
        onTap: () => _showMealDetails(meal),
        child: Padding(
          padding: const EdgeInsets.all(20),
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              // Meal name and calories
              Row(
                mainAxisAlignment: MainAxisAlignment.spaceBetween,
                children: [
                  Expanded(
                    child: Text(
                      mealName,
                      style: const TextStyle(
                        fontSize: 18,
                        fontWeight: FontWeight.bold,
                        color: Color(0xFF1F2937),
                      ),
                    ),
                  ),
                  Container(
                    padding: const EdgeInsets.symmetric(horizontal: 12, vertical: 6),
                    decoration: BoxDecoration(
                      color: const Color(0xFF10B981).withOpacity(0.1),
                      borderRadius: BorderRadius.circular(12),
                    ),
                    child: Text(
                      '$calories kcal',
                      style: const TextStyle(
                        fontSize: 14,
                        fontWeight: FontWeight.w600,
                        color: Color(0xFF10B981),
                      ),
                    ),
                  ),
                ],
              ),
              
              // Protein
              if (protein > 0) ...[
                const SizedBox(height: 8),
                Text(
                  '${protein}g protein',
                  style: TextStyle(
                    fontSize: 14,
                    color: Colors.grey[600],
                  ),
                ),
              ],
              
              // AI "Why" explanation
              if (why != null && why.isNotEmpty) ...[
                const SizedBox(height: 12),
                Container(
                  padding: const EdgeInsets.all(12),
                  decoration: BoxDecoration(
                    color: const Color(0xFF3B82F6).withOpacity(0.05),
                    borderRadius: BorderRadius.circular(12),
                    border: Border.all(
                      color: const Color(0xFF3B82F6).withOpacity(0.2),
                    ),
                  ),
                  child: Row(
                    crossAxisAlignment: CrossAxisAlignment.start,
                    children: [
                      const Icon(
                        Icons.lightbulb_outline,
                        size: 16,
                        color: Color(0xFF3B82F6),
                      ),
                      const SizedBox(width: 8),
                      Expanded(
                        child: Text(
                          why,
                          style: const TextStyle(
                            fontSize: 13,
                            color: Color(0xFF1F2937),
                            height: 1.4,
                          ),
                        ),
                      ),
                    ],
                  ),
                ),
              ],
              
              // Tap to see more
              const SizedBox(height: 12),
              Text(
                'Tap for ingredients & prep notes',
                style: TextStyle(
                  fontSize: 12,
                  color: Colors.grey[500],
                  fontStyle: FontStyle.italic,
                ),
              ),
            ],
          ),
        ),
      ),
    ),
  );
}

void _showMealDetails(Map<String, dynamic> meal) {
  final aiDetails = meal['ai_details'] as Map<String, dynamic>?;
  if (aiDetails == null) return;
  
  showModalBottomSheet(
    context: context,
    isScrollControlled: true,
    backgroundColor: Colors.transparent,
    builder: (context) => DraggableScrollableSheet(
      initialChildSize: 0.7,
      minChildSize: 0.5,
      maxChildSize: 0.95,
      builder: (context, scrollController) => Container(
        decoration: const BoxDecoration(
          color: Colors.white,
          borderRadius: BorderRadius.vertical(top: Radius.circular(20)),
        ),
        child: ListView(
          controller: scrollController,
          padding: const EdgeInsets.all(24),
          children: [
            // Meal name
            Text(
              meal['name'] ?? 'Meal Details',
              style: const TextStyle(
                fontSize: 24,
                fontWeight: FontWeight.bold,
              ),
            ),
            
            const SizedBox(height: 16),
            
            // Ingredients
            if (aiDetails['ingredients'] != null) ...[
              const Text(
                'Ingredients',
                style: TextStyle(
                  fontSize: 18,
                  fontWeight: FontWeight.w600,
                ),
              ),
              const SizedBox(height: 8),
              ...(aiDetails['ingredients'] as List).map((ingredient) => 
                Padding(
                  padding: const EdgeInsets.symmetric(vertical: 4),
                  child: Row(
                    children: [
                      const Icon(Icons.check_circle, size: 16, color: Color(0xFF10B981)),
                      const SizedBox(width: 8),
                      Text(ingredient.toString()),
                    ],
                  ),
                ),
              ),
              const SizedBox(height: 16),
            ],
            
            // Prep notes
            if (aiDetails['prep_notes'] != null) ...[
              const Text(
                'Preparation',
                style: TextStyle(
                  fontSize: 18,
                  fontWeight: FontWeight.w600,
                ),
              ),
              const SizedBox(height: 8),
              Text(
                aiDetails['prep_notes'].toString(),
                style: const TextStyle(height: 1.5),
              ),
              const SizedBox(height: 16),
            ],
            
            // Macros
            if (aiDetails['macros'] != null) ...[
              const Text(
                'Nutrition',
                style: TextStyle(
                  fontSize: 18,
                  fontWeight: FontWeight.w600,
                ),
              ),
              const SizedBox(height: 8),
              _buildMacroGrid(aiDetails['macros']),
            ],
          ],
        ),
      ),
    ),
  );
}

Widget _buildMacroGrid(Map<String, dynamic> macros) {
  return GridView.count(
    crossAxisCount: 2,
    shrinkWrap: true,
    physics: const NeverScrollableScrollPhysics(),
    childAspectRatio: 2.5,
    mainAxisSpacing: 12,
    crossAxisSpacing: 12,
    children: [
      _buildMacroCard('Calories', '${macros['calories']} kcal', Icons.local_fire_department),
      _buildMacroCard('Protein', '${macros['protein']}g', Icons.fitness_center),
      _buildMacroCard('Carbs', '${macros['carbs']}g', Icons.grain),
      _buildMacroCard('Fat', '${macros['fat']}g', Icons.water_drop),
    ],
  );
}

Widget _buildMacroCard(String label, String value, IconData icon) {
  return Container(
    padding: const EdgeInsets.all(12),
    decoration: BoxDecoration(
      color: Colors.grey[50],
      borderRadius: BorderRadius.circular(12),
    ),
    child: Row(
      children: [
        Icon(icon, size: 20, color: const Color(0xFF3B82F6)),
        const SizedBox(width: 8),
        Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          mainAxisAlignment: MainAxisAlignment.center,
          children: [
            Text(
              label,
              style: TextStyle(
                fontSize: 11,
                color: Colors.grey[600],
              ),
            ),
            Text(
              value,
              style: const TextStyle(
                fontSize: 14,
                fontWeight: FontWeight.w600,
              ),
            ),
          ],
        ),
      ],
    ),
  );
}
```

---

### Phase 4: Testing & Validation (30 min)

#### Test Cases:
1. ✅ Generate meal plan for vegetarian user
2. ✅ Generate meal plan with allergies (peanuts, lactose)
3. ✅ Generate meal plan for weight loss goal
4. ✅ Generate meal plan for muscle gain goal
5. ✅ Verify calorie targets are met
6. ✅ Verify macro targets are respected
7. ✅ Verify grocery list is generated
8. ✅ Verify "why" explanations are present
9. ✅ Test meal details modal
10. ✅ Test with different cuisines

---

## 🎯 Success Criteria

- [ ] LLM generates personalized meal plans
- [ ] Calorie and macro targets are met (±10%)
- [ ] All dietary restrictions respected
- [ ] "Why" explanations are clear and helpful
- [ ] Grocery list is complete
- [ ] UI displays all AI-generated details
- [ ] Response time < 10 seconds
- [ ] Cost per generation < $0.10

---

## 💰 Monetization Readiness

### API Structure (Already in place)
- ✅ Clean REST API (`/meal-planning/plans/generate`)
- ✅ User authentication required
- ✅ Rate limiting ready (can add middleware)
- ✅ Usage tracking (log all generations)

### Future Enhancements
1. **Premium Tier:** Unlimited meal plans, advanced customization
2. **B2B API:** White-label for fitness apps, corporate wellness
3. **Meal Swap Feature:** Real-time corrections and swaps
4. **Weekly Plans:** Generate 7-day plans
5. **Recipe Library:** Save and share favorite AI recipes

---

## 📊 Estimated Costs

**Per Meal Plan Generation:**
- GPT-4o-mini: ~2000 tokens input + 1500 tokens output
- Cost: ~$0.005 per generation
- Monthly (1000 users, 2 plans/week): ~$40/month

**Monetization Potential:**
- Premium: $9.99/month (unlimited plans)
- Break-even: 5 premium users
- Target: 100 premium users = $999/month revenue

---

## 🚀 Deployment Checklist

- [ ] Add `OPENAI_API_KEY` to production `.env`
- [ ] Install `openai` package in production
- [ ] Test with 5 different user profiles
- [ ] Monitor LLM response times
- [ ] Set up error logging for LLM failures
- [ ] Add fallback to mock data if LLM fails
- [ ] Document API for future monetization

---

## 📝 Next Steps After Implementation

1. **User Feedback Loop:** Capture "helpful/not helpful" on each meal
2. **Meal Swap Feature:** Allow users to request alternatives
3. **Weekly Plans:** Extend to 7-day meal planning
4. **Recipe Photos:** Add AI-generated or stock photos
5. **Shopping Integration:** Link to grocery delivery APIs

---

**Ready to implement!** This will be a flagship feature for production. 🎉


