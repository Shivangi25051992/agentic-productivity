# Meal Plan Prompt Upgrade - Geo-Aware AI Dietitian

## ✅ Current Status

### What's Working:
- ✅ Meal plans generate successfully (28 meals/week)
- ✅ Dietary preferences respected (vegetarian, keto, etc.)
- ✅ Nutrition data included (calories, protein, carbs, fat)
- ✅ Plans save to database and display correctly
- ⚠️ Recipe detail fix in progress (CuisineType enum fix)

---

## 🎯 Your Vision: Geo-Aware, Culturally-Intelligent Meal Planner

### Key Enhancements:
1. **Location-Aware**: City, country, timezone, lat/long
2. **Seasonal Intelligence**: Climate-based food selection
3. **Cultural Sensitivity**: Religious holidays, fasting periods, festivals
4. **Local Availability**: Regional ingredients, market accessibility
5. **Real-Time Swaps**: Instant ingredient substitution
6. **Explainability**: Why each meal fits user's context

---

## 📋 Implementation Plan

### Phase 1: Data Model Extensions (Backend)
**File**: `app/models/meal_planning.py`

```python
class UserLocation(BaseModel):
    city: str
    country: str
    timezone: str
    latitude: float
    longitude: float
    climate: Optional[str] = None  # "tropical", "temperate", etc.
    season: Optional[str] = None   # "summer", "monsoon", etc.

class CulturalContext(BaseModel):
    festivals: List[str] = []  # Next 7 days
    fasting_days: List[date] = []
    dietary_restrictions: List[str] = []  # Religious/cultural
    
class MealSwapOption(BaseModel):
    ingredient_to_remove: str
    swap_with: str
    reason: Optional[str] = None

class PlannedMeal(BaseModel):
    # ... existing fields ...
    seasonal_note: Optional[str] = None
    cultural_note: Optional[str] = None
    why: Optional[str] = None  # Explainability
    swap_options: List[MealSwapOption] = []
```

### Phase 2: User Profile Extension
**File**: `app/models/profile.py`

```python
class UserProfile(BaseModel):
    # ... existing fields ...
    location: Optional[UserLocation] = None
    cultural_context: Optional[CulturalContext] = None
    cooking_skill: Optional[str] = "intermediate"  # beginner, intermediate, advanced
    budget_per_week: Optional[float] = None
    market_access: Optional[str] = "urban"  # urban, suburban, rural
```

### Phase 3: Enhanced LLM Prompt
**File**: `app/services/meal_plan_llm_service.py`

**Current Location**: `_build_prompt()` method (line ~232)

**New System Instruction**:
```python
def _get_system_instruction(self) -> str:
    return """You are a cutting-edge AI dietitian and meal planner, trusted to deliver meal plans that are scientifically sound, deeply personalized, and geo-aware. Your mission is to be accurate, resonant, and health-driven.

**CONTEXT INPUT:**
- User profile (age, gender, height, weight, activity, goals, medical history, allergies, diet, dislikes/preferences, cooking skill, budget)
- User's current location: {city}, {country}, {timezone}, latitude, longitude
- Local climate/season (derived or specified)
- Local food markets (urban/rural), ingredient accessibility, cultural norms
- Local and religious/cultural holidays or festivals for the next 7 days

**Your plan MUST:**
- Hit calorie and macro targets, but select meals and ingredients easily available/affordable in user's location.
- Preferences for local cuisines, regional and seasonal produce, and user's cultural/religious food patterns.
- Exclude foods not available in that region or out of season.
- For days with local holidays or fast/feast periods, adjust meals accordingly—respect religious rules, fasting traditions, and offer themed/comfort options with full nutritional compliance.
- Ingredient list and prep times tailored for the local urban/rural context (suggest substitutions if something is rare).
- Explain every meal's health rationale and why it matches user location (e.g., "uses in-season mangoes in Mumbai summer", "root-based dishes for Polish winter").
- Include options for the user to instantly remove meals/ingredients and suggest practical alternatives drawn from local cuisine.

**STRICT JSON OUTPUT:**
{
  "date": "YYYY-MM-DD",
  "location": {
    "city": "Mumbai",
    "country": "India",
    "timezone": "IST",
    "latitude": 19.076,
    "longitude": 72.8777
  },
  "season": "Monsoon",
  "cultural_festival": "Ganesh Chaturthi",
  "goal": "weight maintenance",
  "calories": 1900,
  "protein_g": 120,
  "carbs_g": 200,
  "fat_g": 65,
  "meals": [
    {
      "day": "monday",
      "meal_type": "breakfast",
      "meal_name": "Kanda Poha",
      "ingredients": ["flattened rice (poha)", "onion", "mustard seeds", "turmeric", "curry leaves"],
      "portion": "1 large bowl",
      "prep_time": "10 min",
      "calories": 350,
      "protein_g": 8,
      "carbs_g": 65,
      "fat_g": 6,
      "fiber_g": 4,
      "seasonal_note": "Easily digestible, suitable for rainy mornings",
      "cultural_note": "Popular in Maharashtra",
      "why": "Light, energizing, using local ingredients in season, fits your urban food access.",
      "swap_options": [
        {
          "ingredient_to_remove": "onion",
          "swap_with": "peanuts",
          "reason": "For Jain diet or personal preference"
        }
      ]
    }
  ],
  "grocery_list": {
    "produce": ["onion", "curry leaves"],
    "pantry": ["flattened rice", "mustard seeds", "turmeric"]
  },
  "user_feedback_prompt": "What meal or ingredient do you want to remove, swap, or localize? Reply and I'll instantly update your plan.",
  "explainability": {
    "approach": "Personalized for Mumbai monsoon, using local and seasonal foods you can find in your neighborhood. All macros are within ±5% of your target.",
    "nutrition_balance": "Balanced to support your activity and recovery, sodium and oils minimized as per Indian RDA."
  }
}

Respond with ONLY the JSON, no additional text."""
```

### Phase 4: Location & Cultural Data Services
**New File**: `app/services/location_service.py`

```python
class LocationService:
    """Get location data, season, and cultural context"""
    
    async def get_location_from_ip(self, ip_address: str) -> UserLocation:
        """Use geolocation API to get user location"""
        pass
    
    async def get_season(self, latitude: float, date: date) -> str:
        """Determine season based on latitude and date"""
        pass
    
    async def get_cultural_events(
        self, 
        country: str, 
        start_date: date, 
        end_date: date
    ) -> List[str]:
        """Get festivals, holidays, fasting days for date range"""
        pass
```

**New File**: `app/services/food_availability_service.py`

```python
class FoodAvailabilityService:
    """Check ingredient availability by region/season"""
    
    async def is_ingredient_available(
        self,
        ingredient: str,
        country: str,
        season: str
    ) -> bool:
        """Check if ingredient is in season/available"""
        pass
    
    async def suggest_substitutes(
        self,
        ingredient: str,
        country: str,
        cuisine: str
    ) -> List[str]:
        """Suggest local alternatives"""
        pass
```

---

## 🚀 Implementation Priority

### Immediate (Before Sleep):
1. ✅ Fix recipe detail error (CuisineType enum) - **IN PROGRESS**
2. ⏳ Add Fat to daily summary bar

### Phase 1 (Next Session):
1. Extend UserProfile model with location fields
2. Add location capture in onboarding/profile
3. Update LLM prompt with geo-aware instructions
4. Test with Mumbai, India example

### Phase 2 (Future):
1. Build LocationService (geolocation API integration)
2. Build FoodAvailabilityService (seasonal ingredient DB)
3. Add cultural calendar (festivals, fasting days)
4. Implement meal swap API endpoint

### Phase 3 (Advanced):
1. Real-time ingredient substitution
2. Multi-language support
3. Local market price integration
4. Community meal sharing

---

## 💡 Technical Considerations

### APIs Needed:
- **Geolocation**: ipapi.co, ipstack.com (free tiers available)
- **Weather/Season**: OpenWeatherMap API
- **Cultural Calendar**: Calendarific API, Google Calendar API
- **Food Data**: USDA FoodData Central, local food databases

### Database Extensions:
- **Ingredients Table**: region, season, availability_score
- **Cultural Events Table**: country, date, event_type, dietary_impact
- **User Preferences**: location_override, auto_detect_location

### Frontend Changes:
- Location permission request
- Manual location override
- Ingredient swap UI
- Cultural context display

---

## 📊 Expected Impact

### User Experience:
- 🎯 **Relevance**: Meals feel "made for me"
- 🌍 **Practicality**: Ingredients actually available
- 🕉️ **Respect**: Cultural/religious sensitivity
- 💰 **Affordability**: Budget-aware, local pricing
- 🔄 **Flexibility**: Instant swaps and adjustments

### Business Value:
- 🚀 **Differentiation**: Unique geo-aware feature
- 💎 **Premium Tier**: Location-based meal planning
- 🌐 **Global Expansion**: Works anywhere in the world
- 📈 **Engagement**: Higher user satisfaction and retention

---

## ✅ Current Prompt Location

**File**: `/Users/pchintanwar/Documents/Projects-AIProductivity/agentic-productivity/app/services/meal_plan_llm_service.py`

**Method**: `_get_system_instruction()` (line ~135)
**Method**: `_build_prompt()` (line ~232)

**YES, the prompt is 100% configurable!** We can upgrade it anytime.

---

## 🎯 Next Steps

1. **Fix recipe detail** (completing now)
2. **Add Fat to summary bar**
3. **Test current system thoroughly**
4. **Then upgrade to geo-aware prompt** (your amazing vision!)

This is a **game-changing feature** that will make your app truly world-class! 🌍✨


