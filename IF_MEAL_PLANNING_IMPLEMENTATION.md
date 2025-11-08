# 🚀 IF & Meal Planning Implementation Plan

## Date: November 4, 2025

## Strategy: Two Independent Tabs

We'll build **Intermittent Fasting** and **Meal Planning** as separate, standalone features that can work independently. Integration comes later.

---

## 📱 NAVIGATION STRUCTURE

### New Bottom Navigation
```
┌─────────────────────────────────────────────────────┐
│  🏠 Home  |  💬 Chat  |  📊 Timeline  |  🍽️ Plan  │
└─────────────────────────────────────────────────────┘
```

### "Plan" Tab (New) - Has Two Sub-Tabs
```
┌─────────────────────────────────────────────────────┐
│  Plan                                     [Profile] │
├─────────────────────────────────────────────────────┤
│  [ ⏱️ Fasting ]  [ 🍱 Meals ]                       │
├─────────────────────────────────────────────────────┤
│                                                     │
│  (Content switches based on selected tab)          │
│                                                     │
└─────────────────────────────────────────────────────┘
```

---

## 🎯 PHASE 1: FOUNDATION (Days 1-3)

### Day 1: Setup & Structure

#### Backend Models
```python
# app/models/fasting.py
from pydantic import BaseModel
from datetime import datetime
from typing import Optional
from enum import Enum

class FastingProtocol(str, Enum):
    sixteen_eight = "16:8"
    eighteen_six = "18:6"
    twenty_four = "20:4"
    omad = "OMAD"
    custom = "custom"

class FastingSession(BaseModel):
    id: str
    user_id: str
    start_time: datetime
    end_time: Optional[datetime] = None
    target_duration_hours: int
    actual_duration_hours: Optional[float] = None
    protocol: FastingProtocol
    break_reason: Optional[str] = None  # "completed", "hunger", "social", "weakness"
    energy_level: Optional[int] = None  # 1-5
    hunger_level: Optional[int] = None  # 1-5
    notes: Optional[str] = None
    created_at: datetime
    updated_at: datetime

class FastingProfile(BaseModel):
    user_id: str
    default_protocol: FastingProtocol
    eating_window_start: str  # "12:00"
    eating_window_end: str  # "20:00"
    goals: str
    experience_level: str  # "beginner", "intermediate", "advanced"
```

```python
# app/models/meal_planning.py
from pydantic import BaseModel
from datetime import date, datetime
from typing import List, Optional

class Recipe(BaseModel):
    id: str
    name: str
    description: str
    category: str  # "breakfast", "lunch", "dinner", "snack"
    cuisine: str  # "italian", "mexican", "asian", etc.
    difficulty: str  # "easy", "medium", "hard"
    prep_time_minutes: int
    cook_time_minutes: int
    servings: int
    ingredients: List[dict]  # [{"name": "chicken", "amount": "500g"}]
    instructions: List[str]
    nutrition: dict  # {"calories": 450, "protein": 35, ...}
    tags: List[str]  # ["high-protein", "low-carb", "quick"]
    image_url: Optional[str] = None
    created_at: datetime

class PlannedMeal(BaseModel):
    day: str  # "monday", "tuesday", etc.
    meal_type: str  # "breakfast", "lunch", "dinner"
    recipe_id: str
    recipe_name: str
    servings: int
    notes: Optional[str] = None

class MealPlan(BaseModel):
    id: str
    user_id: str
    week_start_date: date
    week_end_date: date
    meals: List[PlannedMeal]
    dietary_preferences: List[str]
    daily_calorie_target: int
    created_by_ai: bool
    created_at: datetime
    updated_at: datetime

class GroceryList(BaseModel):
    id: str
    user_id: str
    meal_plan_id: str
    week_start_date: date
    items: List[dict]  # [{"name": "chicken", "quantity": "1kg", "category": "protein"}]
    total_estimated_cost: float
    checked_items: List[str]
    created_at: datetime
```

#### Frontend Structure
```
flutter_app/lib/
├── screens/
│   └── plan/
│       ├── plan_screen.dart              # Main container with tabs
│       ├── fasting/
│       │   ├── fasting_tab.dart          # IF main view
│       │   ├── fasting_timer_widget.dart # Timer UI
│       │   ├── fasting_history.dart      # Past fasts
│       │   └── fasting_settings.dart     # Protocol selection
│       └── meals/
│           ├── meals_tab.dart            # Meal planning main view
│           ├── meal_plan_week_view.dart  # Weekly calendar
│           ├── meal_detail_screen.dart   # Recipe details
│           └── grocery_list_screen.dart  # Shopping list
├── providers/
│   ├── fasting_provider.dart
│   └── meal_plan_provider.dart
└── models/
    ├── fasting_session.dart
    ├── meal_plan.dart
    └── recipe.dart
```

---

### Day 2: Backend API Endpoints

#### Fasting Endpoints
```python
# app/routers/fasting.py
from fastapi import APIRouter, Depends
from app.models.fasting import FastingSession, FastingProfile
from app.services.database import get_db

router = APIRouter(prefix="/fasting", tags=["fasting"])

@router.post("/start")
async def start_fast(
    protocol: str,
    target_hours: int,
    current_user: User = Depends(get_current_user)
):
    """Start a new fasting session"""
    pass

@router.post("/end/{session_id}")
async def end_fast(
    session_id: str,
    break_reason: str,
    energy_level: int,
    hunger_level: int,
    current_user: User = Depends(get_current_user)
):
    """End current fasting session"""
    pass

@router.get("/current")
async def get_current_fast(current_user: User = Depends(get_current_user)):
    """Get active fasting session"""
    pass

@router.get("/history")
async def get_fasting_history(
    limit: int = 30,
    current_user: User = Depends(get_current_user)
):
    """Get past fasting sessions"""
    pass

@router.get("/analytics")
async def get_fasting_analytics(
    days: int = 30,
    current_user: User = Depends(get_current_user)
):
    """Get fasting performance analytics"""
    pass

@router.get("/profile")
async def get_fasting_profile(current_user: User = Depends(get_current_user)):
    """Get user's fasting preferences"""
    pass

@router.put("/profile")
async def update_fasting_profile(
    profile: FastingProfile,
    current_user: User = Depends(get_current_user)
):
    """Update fasting preferences"""
    pass
```

#### Meal Planning Endpoints
```python
# app/routers/meal_planning.py
from fastapi import APIRouter, Depends
from app.models.meal_planning import MealPlan, Recipe, GroceryList

router = APIRouter(prefix="/meal-planning", tags=["meal_planning"])

@router.post("/generate")
async def generate_meal_plan(
    week_start: date,
    preferences: dict,
    current_user: User = Depends(get_current_user)
):
    """AI generates a weekly meal plan"""
    pass

@router.get("/plans")
async def get_meal_plans(
    limit: int = 10,
    current_user: User = Depends(get_current_user)
):
    """Get user's meal plans"""
    pass

@router.get("/plans/{plan_id}")
async def get_meal_plan(
    plan_id: str,
    current_user: User = Depends(get_current_user)
):
    """Get specific meal plan"""
    pass

@router.put("/plans/{plan_id}/meals/{day}/{meal_type}")
async def update_planned_meal(
    plan_id: str,
    day: str,
    meal_type: str,
    recipe_id: str,
    current_user: User = Depends(get_current_user)
):
    """Swap a meal in the plan"""
    pass

@router.get("/recipes")
async def search_recipes(
    query: str = "",
    category: str = "",
    tags: List[str] = [],
    limit: int = 20
):
    """Search recipe database"""
    pass

@router.get("/recipes/{recipe_id}")
async def get_recipe(recipe_id: str):
    """Get recipe details"""
    pass

@router.post("/grocery-list/{plan_id}")
async def generate_grocery_list(
    plan_id: str,
    current_user: User = Depends(get_current_user)
):
    """Generate shopping list from meal plan"""
    pass

@router.get("/grocery-list/{list_id}")
async def get_grocery_list(
    list_id: str,
    current_user: User = Depends(get_current_user)
):
    """Get grocery list"""
    pass

@router.put("/grocery-list/{list_id}/check/{item_name}")
async def check_grocery_item(
    list_id: str,
    item_name: str,
    checked: bool,
    current_user: User = Depends(get_current_user)
):
    """Check/uncheck grocery item"""
    pass
```

---

### Day 3: Basic Frontend UI

#### Plan Screen (Container)
```dart
// flutter_app/lib/screens/plan/plan_screen.dart
import 'package:flutter/material.dart';
import 'fasting/fasting_tab.dart';
import 'meals/meals_tab.dart';

class PlanScreen extends StatefulWidget {
  const PlanScreen({Key? key}) : super(key: key);

  @override
  State<PlanScreen> createState() => _PlanScreenState();
}

class _PlanScreenState extends State<PlanScreen> with SingleTickerProviderStateMixin {
  late TabController _tabController;

  @override
  void initState() {
    super.initState();
    _tabController = TabController(length: 2, vsync: this);
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: const Text('Plan'),
        bottom: TabBar(
          controller: _tabController,
          tabs: const [
            Tab(icon: Icon(Icons.timer), text: 'Fasting'),
            Tab(icon: Icon(Icons.restaurant_menu), text: 'Meals'),
          ],
        ),
      ),
      body: TabBarView(
        controller: _tabController,
        children: const [
          FastingTab(),
          MealsTab(),
        ],
      ),
    );
  }
}
```

#### Fasting Tab (Basic)
```dart
// flutter_app/lib/screens/plan/fasting/fasting_tab.dart
import 'package:flutter/material.dart';

class FastingTab extends StatelessWidget {
  const FastingTab({Key? key}) : super(key: key);

  @override
  Widget build(BuildContext context) {
    return SingleChildScrollView(
      padding: const EdgeInsets.all(16),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          // Fasting Timer Widget
          _buildFastingTimer(),
          const SizedBox(height: 24),
          
          // Quick Stats
          _buildQuickStats(),
          const SizedBox(height: 24),
          
          // Fasting History
          _buildFastingHistory(),
        ],
      ),
    );
  }

  Widget _buildFastingTimer() {
    return Card(
      child: Padding(
        padding: const EdgeInsets.all(24),
        child: Column(
          children: [
            // Timer will go here
            const Text('Fasting Timer', style: TextStyle(fontSize: 24)),
            const SizedBox(height: 16),
            ElevatedButton(
              onPressed: () {},
              child: const Text('Start Fasting'),
            ),
          ],
        ),
      ),
    );
  }

  Widget _buildQuickStats() {
    return Row(
      children: [
        Expanded(child: _statCard('Current Streak', '7 days')),
        const SizedBox(width: 12),
        Expanded(child: _statCard('Avg Duration', '16.2h')),
      ],
    );
  }

  Widget _statCard(String label, String value) {
    return Card(
      child: Padding(
        padding: const EdgeInsets.all(16),
        child: Column(
          children: [
            Text(label, style: const TextStyle(fontSize: 12)),
            const SizedBox(height: 8),
            Text(value, style: const TextStyle(fontSize: 20, fontWeight: FontWeight.bold)),
          ],
        ),
      ),
    );
  }

  Widget _buildFastingHistory() {
    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        const Text('Recent Fasts', style: TextStyle(fontSize: 18, fontWeight: FontWeight.bold)),
        const SizedBox(height: 12),
        // History list will go here
        const Text('History coming soon...'),
      ],
    );
  }
}
```

#### Meals Tab (Basic)
```dart
// flutter_app/lib/screens/plan/meals/meals_tab.dart
import 'package:flutter/material.dart';

class MealsTab extends StatelessWidget {
  const MealsTab({Key? key}) : super(key: key);

  @override
  Widget build(BuildContext context) {
    return SingleChildScrollView(
      padding: const EdgeInsets.all(16),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          // Week selector
          _buildWeekSelector(),
          const SizedBox(height: 24),
          
          // Meal plan
          _buildMealPlan(),
          const SizedBox(height: 24),
          
          // Actions
          _buildActions(),
        ],
      ),
    );
  }

  Widget _buildWeekSelector() {
    return Card(
      child: Padding(
        padding: const EdgeInsets.all(16),
        child: Row(
          mainAxisAlignment: MainAxisAlignment.spaceBetween,
          children: [
            IconButton(icon: const Icon(Icons.chevron_left), onPressed: () {}),
            const Text('Nov 4 - Nov 10', style: TextStyle(fontSize: 16, fontWeight: FontWeight.bold)),
            IconButton(icon: const Icon(Icons.chevron_right), onPressed: () {}),
          ],
        ),
      ),
    );
  }

  Widget _buildMealPlan() {
    return Column(
      children: [
        _dayMealCard('Monday', 'Nov 4'),
        _dayMealCard('Tuesday', 'Nov 5'),
        _dayMealCard('Wednesday', 'Nov 6'),
      ],
    );
  }

  Widget _dayMealCard(String day, String date) {
    return Card(
      margin: const EdgeInsets.only(bottom: 12),
      child: ExpansionTile(
        title: Text(day, style: const TextStyle(fontWeight: FontWeight.bold)),
        subtitle: Text(date),
        children: [
          ListTile(
            leading: const Icon(Icons.breakfast_dining),
            title: const Text('Breakfast'),
            subtitle: const Text('Not planned yet'),
            trailing: IconButton(icon: const Icon(Icons.add), onPressed: () {}),
          ),
          ListTile(
            leading: const Icon(Icons.lunch_dining),
            title: const Text('Lunch'),
            subtitle: const Text('Not planned yet'),
            trailing: IconButton(icon: const Icon(Icons.add), onPressed: () {}),
          ),
          ListTile(
            leading: const Icon(Icons.dinner_dining),
            title: const Text('Dinner'),
            subtitle: const Text('Not planned yet'),
            trailing: IconButton(icon: const Icon(Icons.add), onPressed: () {}),
          ),
        ],
      ),
    );
  }

  Widget _buildActions() {
    return Column(
      children: [
        SizedBox(
          width: double.infinity,
          child: ElevatedButton.icon(
            onPressed: () {},
            icon: const Icon(Icons.auto_awesome),
            label: const Text('Generate AI Meal Plan'),
          ),
        ),
        const SizedBox(height: 12),
        SizedBox(
          width: double.infinity,
          child: OutlinedButton.icon(
            onPressed: () {},
            icon: const Icon(Icons.shopping_cart),
            label: const Text('View Grocery List'),
          ),
        ),
      ],
    );
  }
}
```

---

## 🎯 PHASE 2: FASTING FEATURES (Days 4-8)

### Day 4: Fasting Timer Implementation
- Real-time countdown
- Progress ring animation
- Fasting stages display
- Start/stop/pause functionality

### Day 5: Protocol Selection & Settings
- Protocol picker UI
- Eating window customization
- Save to profile
- Quick start from saved protocol

### Day 6: Fasting History & Analytics
- Past fasts list with completion status
- Completion rate chart
- Average duration tracking
- Streak calculation

### Day 7-8: AI Fasting Coach (Basic)
- Chat integration for fasting commands
- Smart window recommendation
- Breaking fast meal suggestions
- Motivational messages

---

## 🎯 PHASE 3: MEAL PLANNING FEATURES (Days 9-13)

### Day 9: Recipe Database Setup
- Seed database with 50+ basic recipes
- Recipe search functionality
- Recipe detail view
- Nutrition display

### Day 10: Meal Plan Generation (AI)
- Conversational meal plan creation
- Weekly plan generation
- Save to database
- Display in calendar view

### Day 11: Meal Plan Editing
- Swap meals
- Add/remove meals
- Adjust servings
- Notes per meal

### Day 12: Grocery List
- Auto-generate from meal plan
- Categorize by store section
- Check/uncheck items
- Cost estimation

### Day 13: Daily Meal Suggestions
- AI suggests today's meals
- Adapt based on logged meals
- Macro balancing
- Quick meal swap

---

## 🎯 PHASE 4: POLISH & AI ENHANCEMENT (Days 14-16)

### Day 14: Advanced Fasting AI
- Context-aware coaching
- Pattern detection
- Predictive warnings
- Performance insights

### Day 15: Advanced Meal Planning AI
- Dynamic daily adaptation
- Smart grocery optimization
- Meal prep guide
- Nutritional education

### Day 16: Testing & Bug Fixes
- End-to-end testing
- UI/UX polish
- Performance optimization
- Documentation

---

## 📊 DATABASE SCHEMA

### Firestore Collections
```
users/{userId}/
├── fasting_profile/
│   └── profile (doc)
├── fasting_sessions/
│   └── {sessionId} (docs)
├── meal_plans/
│   └── {planId} (docs)
└── grocery_lists/
    └── {listId} (docs)

recipes/ (global collection)
└── {recipeId} (docs)
```

---

## 🚀 LET'S START!

I'll begin with **Day 1: Setup & Structure**. This includes:
1. Creating backend models
2. Setting up frontend folder structure
3. Adding navigation to Plan screen
4. Basic UI scaffolding

**Ready to start building?** Let me know and I'll begin! 🎯

