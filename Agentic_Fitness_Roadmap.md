# Agentic Fitness: AI-Powered Meal Planning Roadmap

**Version:** 1.0  
**Created:** November 5, 2025  
**Status:** Planning Phase  
**Objective:** Transform basic meal planning into an intelligent, agentic, personalized nutrition system

---

## Executive Summary

This roadmap transforms the current mock meal planning system into a production-grade, AI-powered, agentic nutrition platform that leverages user profiles, fitness data, and multi-LLM routing to deliver personalized, explainable, and adaptive meal plans.

**Key Differentiators:**
- 🤖 **Agentic AI** - Autonomous meal planning agents with reasoning
- 🎯 **Hyper-Personalization** - Profile + fitness logs + preferences
- 🔄 **Continuous Learning** - Feedback loops and adaptation
- 🛡️ **Multi-LLM Resilience** - Admin-configurable provider routing
- 💡 **Explainable Recommendations** - Every meal has transparent reasoning
- 🛒 **Integrated Grocery Lists** - Auto-generated, optimized shopping

---

## Current State Analysis

### ✅ What Exists (Foundation)
1. **User Profile System** (`app/models/user_profile.py`)
   - Dietary preferences (vegetarian, vegan, high-protein, etc.)
   - Allergies and disliked foods
   - Fitness goals (lose weight, gain muscle, improve fitness)
   - Activity level, BMR calculations
   - Daily macro targets (calories, protein, carbs, fat)

2. **Meal Planning Infrastructure** (`app/services/meal_planning_service.py`)
   - MealPlan, Recipe, PlannedMeal models
   - Firestore storage under `users/{userId}/meal_plans/`
   - Basic CRUD operations
   - Grocery list generation stub

3. **LLM Integration** (`app/main.py`)
   - OpenAI client integration
   - JSON-structured prompts
   - Chat classification system

4. **Frontend UI** (`flutter_app/lib/screens/plan/meal_planning_tab.dart`)
   - Weekly meal calendar view
   - Meal card display with nutrition
   - Generate plan dialog
   - Day navigation

### ❌ What's Missing (Gaps)
1. **No AI Integration in Meal Planning**
   - Currently returns hardcoded mock meals
   - No LLM calls for personalization
   - No user profile integration

2. **No Multi-LLM Router**
   - Only direct OpenAI calls
   - No admin-configurable provider switching
   - No fallback/quota management

3. **No Explainability**
   - Meals have no reasoning/justification
   - No "why this meal?" context

4. **No Feedback Loop**
   - No user rating system
   - No preference learning
   - No meal substitution

5. **No Grocery Integration**
   - Grocery list generation incomplete
   - No quantity calculation
   - No category organization

---

## Architecture Design

### System Components

```
┌─────────────────────────────────────────────────────────────┐
│                     FRONTEND (Flutter)                       │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐      │
│  │ Meal Calendar│  │Generate Plan │  │ Feedback UI  │      │
│  │   View       │  │   Dialog     │  │              │      │
│  └──────────────┘  └──────────────┘  └──────────────┘      │
└─────────────────────────────────────────────────────────────┘
                            │
                            ▼
┌─────────────────────────────────────────────────────────────┐
│                   BACKEND API (FastAPI)                      │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐      │
│  │Meal Planning │  │  LLM Router  │  │   Feedback   │      │
│  │   Router     │  │              │  │   Service    │      │
│  └──────────────┘  └──────────────┘  └──────────────┘      │
└─────────────────────────────────────────────────────────────┘
                            │
                            ▼
┌─────────────────────────────────────────────────────────────┐
│                    AGENT LAYER                               │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐      │
│  │Meal Planning │  │ Personalize  │  │  Learning    │      │
│  │    Agent     │  │    Agent     │  │   Agent      │      │
│  └──────────────┘  └──────────────┘  └──────────────┘      │
└─────────────────────────────────────────────────────────────┘
                            │
                            ▼
┌─────────────────────────────────────────────────────────────┐
│                  DATA LAYER (Firestore)                      │
│  users/{userId}/                                             │
│    ├── profile/         (dietary prefs, allergies, goals)   │
│    ├── meal_plans/      (AI-generated plans + reasoning)    │
│    ├── fitness_logs/    (workout history for context)       │
│    ├── feedback/        (meal ratings, preferences)         │
│    └── grocery_lists/   (auto-generated shopping)           │
└─────────────────────────────────────────────────────────────┘
                            │
                            ▼
┌─────────────────────────────────────────────────────────────┐
│                  ADMIN CONFIGURATION                         │
│  admin/llm_config/                                           │
│    ├── providers/       (Gemini, OpenAI, Mixtral configs)   │
│    ├── quotas/          (usage limits, costs)               │
│    └── prompts/         (system prompt templates)           │
└─────────────────────────────────────────────────────────────┘
```

---

## Implementation Phases

### 🔵 Phase 1: Foundation & Multi-LLM Router (Week 1)
**Goal:** Build robust LLM infrastructure without breaking existing features

#### 1.1 Multi-LLM Router Service
**Files:**
- `app/services/llm_router.py` (NEW)
- `app/models/llm_config.py` (NEW)
- `app/services/config_service.py` (EXTEND)

**Tasks:**
- [ ] Create `LLMConfig` model (provider, api_key, model_name, priority, quota)
- [ ] Create `LLMRouter` class with provider selection logic
- [ ] Implement fallback mechanism (primary → backup)
- [ ] Add quota tracking and enforcement
- [ ] Create admin Firestore collection: `admin/llm_config/providers/{provider_id}`
- [ ] Write unit tests for router logic

**Success Criteria:**
- ✅ Router can select LLM based on priority
- ✅ Falls back to secondary provider on failure
- ✅ Tracks quota usage in Firestore
- ✅ **NO REGRESSION:** Existing chat classification still works

#### 1.2 Prompt Template System
**Files:**
- `app/prompts/meal_planning_prompts.py` (NEW)
- `app/models/prompt_template.py` (NEW)

**Tasks:**
- [ ] Create structured prompt templates for meal planning
- [ ] Define JSON schema for meal plan response
- [ ] Add prompt versioning system
- [ ] Store prompts in Firestore: `admin/prompts/meal_planning_v1`
- [ ] Create prompt testing framework

**Success Criteria:**
- ✅ Prompts are reusable and configurable
- ✅ JSON schema validation works
- ✅ Can update prompts without code deployment

---

### 🟢 Phase 2: Agentic Meal Planning Core (Week 2)
**Goal:** Integrate AI into meal generation with user profile

#### 2.1 Meal Planning Agent
**Files:**
- `app/agents/meal_planning_agent.py` (NEW)
- `app/services/meal_planning_service.py` (EXTEND)

**Tasks:**
- [ ] Create `MealPlanningAgent` class
- [ ] Implement profile integration (pull user preferences, allergies, goals)
- [ ] Add fitness log context (recent workouts, calorie burn)
- [ ] Build prompt construction with personalization
- [ ] Implement LLM call via router
- [ ] Parse and validate LLM JSON response
- [ ] Store generated plan in Firestore

**Prompt Structure:**
```python
System: You are a nutrition AI agent. Generate personalized meal plans.
User Context:
  - Profile: {age, gender, weight, height, activity_level}
  - Goals: {fitness_goal, target_weight, daily_macros}
  - Dietary: {diet_preference, allergies, disliked_foods}
  - Recent Activity: {last_7_days_workouts, avg_calories_burned}
Task: Generate 7-day meal plan (3 meals/day) meeting macros, respecting restrictions.
Output: Strict JSON with meals array, each meal having:
  {name, time_slot, ingredients, macros, reasoning}
```

**Success Criteria:**
- ✅ Agent generates personalized 21-meal plan
- ✅ Respects all dietary restrictions
- ✅ Meets daily macro targets (±10% tolerance)
- ✅ **NO REGRESSION:** Old mock generation still accessible for testing

#### 2.2 Recipe Enhancement
**Files:**
- `app/models/meal_planning.py` (EXTEND)
- `app/services/recipe_service.py` (NEW)

**Tasks:**
- [ ] Add `reasoning` field to `PlannedMeal` model
- [ ] Add `explainability` field to `MealPlan` model
- [ ] Create recipe enrichment service
- [ ] Add recipe image URL generation (via Unsplash API or similar)
- [ ] Implement recipe caching to reduce API calls

**Success Criteria:**
- ✅ Every meal has reasoning text
- ✅ Recipes have images
- ✅ **NO BREAKING:** Existing meal display works with new fields

---

### 🟡 Phase 3: Explainability & Trust (Week 3)
**Goal:** Add transparency and reasoning to build user trust

#### 3.1 Explainability System
**Files:**
- `app/services/explainability_service.py` (NEW)
- `app/models/meal_planning.py` (EXTEND)

**Tasks:**
- [ ] Add `reasoning_summary` to meal plan response
- [ ] Generate "Why this meal?" explanations
- [ ] Create reasoning categories (macro alignment, preference match, variety)
- [ ] Build confidence scoring system
- [ ] Add alternative suggestions

**Example Reasoning:**
```json
{
  "meal_name": "Paneer Tikka",
  "reasoning": "Selected for high protein (28g) to support muscle recovery after your morning workout. Vegetarian as per your preference. Indian cuisine matches your taste profile. No nuts/lactose per restrictions.",
  "confidence": 0.92,
  "alternatives": ["Tofu Stir-Fry", "Chickpea Curry"]
}
```

**Success Criteria:**
- ✅ All meals have clear reasoning
- ✅ Frontend displays "Why?" button
- ✅ Users can request alternatives

#### 3.2 Frontend Explainability UI
**Files:**
- `flutter_app/lib/screens/plan/meal_planning_tab.dart` (EXTEND)
- `flutter_app/lib/widgets/meal_reasoning_dialog.dart` (NEW)

**Tasks:**
- [ ] Add "Why this meal?" icon to meal cards
- [ ] Create reasoning dialog popup
- [ ] Display confidence scores
- [ ] Add "Request Alternative" button
- [ ] Show macro breakdown chart

**Success Criteria:**
- ✅ Users can see reasoning for any meal
- ✅ UI is intuitive and informative
- ✅ **NO REGRESSION:** Meal display performance maintained

---

### 🟠 Phase 4: Feedback & Learning Loop (Week 4)
**Goal:** Enable user feedback and adaptive learning

#### 4.1 Feedback Collection System
**Files:**
- `app/models/feedback.py` (NEW)
- `app/services/feedback_service.py` (NEW)
- `app/routers/feedback.py` (NEW)

**Tasks:**
- [ ] Create `MealFeedback` model (rating, comment, action)
- [ ] Build feedback API endpoints
- [ ] Store feedback in Firestore: `users/{userId}/meal_feedback/{feedback_id}`
- [ ] Implement feedback aggregation
- [ ] Create feedback analytics dashboard

**Feedback Schema:**
```python
class MealFeedback(BaseModel):
    meal_plan_id: str
    meal_id: str
    rating: int  # 1-5
    action: FeedbackAction  # liked, disliked, substituted, skipped
    reason: Optional[str]  # "too spicy", "not enough protein"
    timestamp: datetime
```

**Success Criteria:**
- ✅ Users can rate meals (thumbs up/down)
- ✅ Feedback stored and tracked
- ✅ Analytics show preference patterns

#### 4.2 Learning Agent
**Files:**
- `app/agents/learning_agent.py` (NEW)
- `app/services/preference_learning.py` (NEW)

**Tasks:**
- [ ] Create `LearningAgent` class
- [ ] Analyze feedback patterns (frequently disliked ingredients)
- [ ] Update user preference profile automatically
- [ ] Adjust future meal generation based on feedback
- [ ] Implement collaborative filtering (similar users' preferences)

**Learning Logic:**
```python
# If user dislikes 3+ meals with ingredient X
if feedback.count(ingredient="spinach", rating<3) >= 3:
    user.disliked_foods.append("spinach")
    
# If user consistently rates high-protein meals 5/5
if feedback.avg_rating(protein_g > 30) >= 4.5:
    user.preferences["prefers_high_protein"] = True
```

**Success Criteria:**
- ✅ Agent learns from feedback automatically
- ✅ Future plans avoid disliked ingredients
- ✅ Recommendations improve over time

---

### 🔴 Phase 5: Grocery List & Shopping Integration (Week 5)
**Goal:** Complete end-to-end meal planning experience

#### 5.1 Smart Grocery List Generator
**Files:**
- `app/services/grocery_service.py` (EXTEND)
- `app/models/meal_planning.py` (EXTEND)

**Tasks:**
- [ ] Implement ingredient aggregation from meal plan
- [ ] Calculate quantities needed (servings × ingredients)
- [ ] Group by category (produce, protein, pantry, dairy)
- [ ] Detect pantry staples (user likely has salt, oil, etc.)
- [ ] Check for duplicates across meals
- [ ] Optimize for minimal waste

**Algorithm:**
```python
def generate_grocery_list(meal_plan):
    ingredients = {}
    for meal in meal_plan.meals:
        for ing in meal.ingredients:
            key = ing.name.lower()
            if key in ingredients:
                ingredients[key].quantity += ing.quantity
            else:
                ingredients[key] = ing
    
    # Remove pantry staples
    ingredients = {k:v for k,v in ingredients.items() 
                   if k not in ['salt', 'pepper', 'oil']}
    
    # Categorize
    categorized = categorize_ingredients(ingredients)
    return GroceryList(items=categorized)
```

**Success Criteria:**
- ✅ Accurate quantity calculations
- ✅ Well-organized categories
- ✅ No duplicate items

#### 5.2 Frontend Grocery UI
**Files:**
- `flutter_app/lib/screens/plan/grocery_list_screen.dart` (EXTEND)

**Tasks:**
- [ ] Display categorized grocery list
- [ ] Add checkboxes for items
- [ ] Implement "Add to Cart" API integration (optional)
- [ ] Enable list sharing (email, text)
- [ ] Add pantry management

**Success Criteria:**
- ✅ Beautiful, organized grocery UI
- ✅ Users can check off items
- ✅ Export/share functionality works

---

### ⚪ Phase 6: Admin Dashboard & Monitoring (Week 6)
**Goal:** Enable real-time management and monitoring

#### 6.1 Admin LLM Management UI
**Files:**
- `flutter_app/lib/screens/admin/llm_config_screen.dart` (NEW)
- `app/routers/admin.py` (NEW)

**Tasks:**
- [ ] Create admin auth middleware
- [ ] Build LLM provider CRUD UI
- [ ] Add quota monitoring dashboard
- [ ] Implement hot-swap LLM selection
- [ ] Create cost analytics charts
- [ ] Add error/fallback logs viewer

**Success Criteria:**
- ✅ Admin can manage LLM providers
- ✅ Real-time quota/cost tracking
- ✅ Error logs accessible

#### 6.2 Analytics & Monitoring
**Files:**
- `app/services/analytics_service.py` (NEW)
- `app/models/analytics.py` (NEW)

**Tasks:**
- [ ] Track meal plan generation metrics (success rate, latency)
- [ ] Monitor LLM API costs per user
- [ ] Analyze user engagement (plan adoption rate)
- [ ] Create feedback analytics dashboard
- [ ] Set up automated alerts for quota limits

**Metrics to Track:**
- Plan generation success rate
- Average LLM response time
- Cost per meal plan
- User feedback scores
- Ingredient preference trends

**Success Criteria:**
- ✅ Real-time metrics dashboard
- ✅ Cost tracking and alerts
- ✅ Performance monitoring

---

## Data Model Extensions

### New Firestore Collections

#### 1. `admin/llm_config/providers/{provider_id}`
```json
{
  "provider": "openai",
  "model_name": "gpt-4o-mini",
  "api_key": "sk-...",
  "enabled": true,
  "priority": 1,
  "quota_limit": 1000000,
  "quota_used": 43200,
  "cost_per_1k_tokens": 0.002,
  "fallback_provider": "gemini",
  "last_used": "2025-11-05T10:30:00Z"
}
```

#### 2. `users/{userId}/meal_feedback/{feedback_id}`
```json
{
  "meal_plan_id": "plan-123",
  "meal_id": "meal-456",
  "rating": 5,
  "action": "liked",
  "reason": "Perfect protein amount",
  "timestamp": "2025-11-05T12:00:00Z"
}
```

#### 3. `users/{userId}/preference_learning`
```json
{
  "learned_preferences": {
    "prefers_high_protein": true,
    "dislikes_spinach": true,
    "favorite_cuisines": ["indian", "mediterranean"]
  },
  "confidence_scores": {
    "high_protein": 0.95,
    "spinach": 0.87
  },
  "last_updated": "2025-11-05T10:00:00Z"
}
```

### Extended Models

#### `MealPlan` (Extended)
```python
class MealPlan(BaseModel):
    # ... existing fields ...
    explainability: str  # Overall plan reasoning
    generated_by_llm: str  # "openai-gpt4o-mini"
    generation_confidence: float  # 0.0-1.0
    alternative_plans: List[str] = []  # IDs of alternative plans
```

#### `PlannedMeal` (Extended)
```python
class PlannedMeal(BaseModel):
    # ... existing fields ...
    reasoning: str  # Why this meal was chosen
    confidence: float  # 0.0-1.0
    alternatives: List[Dict] = []  # Alternative meal suggestions
    user_rating: Optional[int] = None  # 1-5 stars
```

---

## Testing Strategy

### Phase-by-Phase Testing

#### Phase 1: LLM Router Testing
```python
def test_llm_router_fallback():
    """Test that router falls back to secondary provider on failure"""
    # Mock primary provider failure
    # Assert secondary provider is called
    # Verify quota tracking
```

#### Phase 2: Meal Generation Testing
```python
def test_meal_plan_personalization():
    """Test that generated plan respects user profile"""
    user = create_test_user(diet="vegetarian", allergies=["nuts"])
    plan = agent.generate_meal_plan(user)
    
    # Assert all meals are vegetarian
    # Assert no meals contain nuts
    # Assert macros within targets
```

#### Phase 3: Explainability Testing
```python
def test_reasoning_quality():
    """Test that reasoning is meaningful and accurate"""
    meal = get_test_meal()
    reasoning = explainability_service.generate_reasoning(meal, user_profile)
    
    # Assert reasoning mentions dietary preference
    # Assert reasoning explains macro alignment
    # Assert confidence score is calculated
```

### Regression Testing
- **Existing Features Protected:**
  - Chat-based meal logging
  - Manual meal plan creation
  - Workout tracking
  - Task management
  - Profile editing

- **Test Suite:**
  ```bash
  # Run before each deployment
  pytest tests/regression/
  pytest tests/integration/
  pytest tests/e2e/
  ```

---

## Migration Strategy

### No-Downtime Deployment

#### Step 1: Feature Flag System
```python
# Add to user profile
class UserProfile:
    feature_flags: Dict[str, bool] = {
        "ai_meal_planning": False,  # Default off
        "feedback_system": False,
        "explainability": False
    }
```

#### Step 2: Gradual Rollout
1. **Week 1-2:** Internal testing (10 test users)
2. **Week 3:** Beta users (100 users, feature flag enabled)
3. **Week 4:** 25% of users
4. **Week 5:** 50% of users
5. **Week 6:** 100% rollout

#### Step 3: Backward Compatibility
- **Mock meal generation remains available** as fallback
- **API versioning:** `/v1/meal-planning/` vs `/v2/meal-planning/`
- **Database migrations:** Additive only (no breaking schema changes)

---

## Success Metrics

### Technical Metrics
- **Meal Plan Generation Success Rate:** >95%
- **LLM API Latency:** <3 seconds (p95)
- **Cost per Meal Plan:** <$0.10
- **Fallback Trigger Rate:** <5%

### User Metrics
- **Plan Adoption Rate:** >60% of generated plans used
- **Feedback Participation:** >40% of users rate meals
- **User Satisfaction:** >4.2/5.0 average rating
- **Retention Improvement:** +15% after AI rollout

### Business Metrics
- **Engagement:** +30% daily active users
- **Feature Usage:** 70% of users generate at least 1 plan/week
- **Churn Reduction:** -20% after personalization

---

## Risk Mitigation

### Technical Risks

| Risk | Impact | Mitigation |
|------|--------|------------|
| LLM API downtime | High | Multi-provider fallback, local cache |
| High API costs | Medium | Quota limits, caching, efficient prompts |
| Poor AI quality | High | Prompt engineering, validation layer, feedback loop |
| Performance degradation | Medium | Async processing, rate limiting |
| Data privacy breach | Critical | Encryption, strict auth, audit logs |

### Rollback Plan
```bash
# If critical issues occur:
1. Disable feature flag for all users
2. Revert to mock meal generation
3. Restore previous API version
4. Rollback database migrations if needed
5. Investigate and fix issue
6. Gradual re-enable
```

---

## Dependencies

### External Services
- **OpenAI API** (gpt-4o-mini)
- **Google Gemini API** (backup)
- **Firestore** (data storage)
- **Cloud Functions** (optional background jobs)

### Internal Dependencies
- User profile system (✅ exists)
- Fitness logging (✅ exists)
- Authentication (✅ exists)
- Chat history (✅ exists)

---

## Next Steps

### Immediate Actions (This Week)
1. ✅ **Create this roadmap** - DONE
2. [ ] **Review & approve roadmap** - Waiting for user
3. [ ] **Set up development branch** - `feature/agentic-meal-planning`
4. [ ] **Create Phase 1 tickets** - LLM router implementation
5. [ ] **Begin Phase 1 development** - After approval

### CursorAI Developer Instructions

**To Begin Phase 1:**
```bash
# 1. Create feature branch
git checkout -b feature/agentic-meal-planning

# 2. Create new directories
mkdir -p app/agents
mkdir -p app/prompts
mkdir -p app/services/llm

# 3. Start with LLM router
# Create: app/services/llm/llm_router.py
# Create: app/models/llm_config.py
# Create: app/services/llm/provider_manager.py

# 4. Write tests first
# Create: tests/unit/test_llm_router.py

# 5. Run tests
pytest tests/unit/test_llm_router.py

# 6. Commit frequently
git commit -m "feat: add LLM router foundation"
```

---

## Appendix

### A. Prompt Templates

#### Meal Planning Prompt (v1.0)
```
SYSTEM:
You are an expert nutrition AI agent specializing in personalized meal planning.

INPUT CONTEXT:
- User Profile: {profile_json}
- Fitness Goals: {goals_json}
- Recent Activity: {activity_summary}
- Dietary Restrictions: {restrictions_json}

TASK:
Generate a 7-day meal plan (3 meals/day) that:
1. Meets daily macro targets (±10% tolerance)
2. Respects all dietary restrictions and allergies
3. Provides variety (no repeated meals within 3 days)
4. Aligns with fitness goals and activity level
5. Includes reasoning for each meal choice

OUTPUT FORMAT (strict JSON):
{
  "meals": [
    {
      "day": "monday",
      "meal_type": "breakfast",
      "name": "Veggie Omelette",
      "ingredients": [...],
      "macros": {...},
      "reasoning": "High protein for morning workout recovery, vegetarian as per preference"
    }
  ],
  "explainability": "Overall plan designed for muscle gain with 40% protein split...",
  "confidence": 0.92
}
```

### B. API Endpoint Summary

#### New Endpoints (Phase 2-6)
```
POST   /v2/meal-planning/plans/generate   # AI-powered generation
GET    /v2/meal-planning/plans/{id}/reasoning  # Get explainability
POST   /v2/meal-planning/feedback         # Submit feedback
GET    /v2/meal-planning/alternatives/{meal_id}  # Get alternatives
POST   /v2/meal-planning/grocery-list/generate  # Generate list
GET    /admin/llm/providers               # Admin: List LLM configs
POST   /admin/llm/providers               # Admin: Add provider
PUT    /admin/llm/providers/{id}          # Admin: Update provider
GET    /admin/analytics/meal-planning     # Admin: View metrics
```

### C. File Structure
```
agentic-productivity/
├── app/
│   ├── agents/
│   │   ├── __init__.py
│   │   ├── meal_planning_agent.py       # NEW - Phase 2
│   │   └── learning_agent.py            # NEW - Phase 4
│   ├── prompts/
│   │   ├── __init__.py
│   │   ├── meal_planning_prompts.py     # NEW - Phase 1
│   │   └── prompt_templates.py          # NEW - Phase 1
│   ├── services/
│   │   ├── llm/
│   │   │   ├── __init__.py
│   │   │   ├── llm_router.py            # NEW - Phase 1
│   │   │   └── provider_manager.py      # NEW - Phase 1
│   │   ├── explainability_service.py    # NEW - Phase 3
│   │   ├── feedback_service.py          # NEW - Phase 4
│   │   └── grocery_service.py           # EXTEND - Phase 5
│   └── models/
│       ├── llm_config.py                # NEW - Phase 1
│       ├── feedback.py                  # NEW - Phase 4
│       └── analytics.py                 # NEW - Phase 6
└── tests/
    ├── unit/
    │   ├── test_llm_router.py           # NEW - Phase 1
    │   └── test_meal_agent.py           # NEW - Phase 2
    └── integration/
        └── test_meal_planning_e2e.py    # NEW - Phase 2
```

---

## Version History

| Version | Date | Changes |
|---------|------|---------|
| 1.0 | Nov 5, 2025 | Initial roadmap created |

---

**END OF ROADMAP**

**Status:** 🔵 **READY FOR REVIEW & APPROVAL**

**Next Action:** User approval to begin Phase 1 implementation

