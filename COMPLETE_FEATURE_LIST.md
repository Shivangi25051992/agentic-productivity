# 📋 Complete Feature List - Yuvi AI Productivity App

**Every Feature, Function, Object, Sync/Async Details**

---

## 🎯 **FEATURE CATEGORIES**

1. **Authentication & User Management**
2. **Chat & AI Conversation**
3. **Food & Nutrition Tracking**
4. **Fitness & Workout Logging**
5. **Water & Hydration Tracking**
6. **Supplement Tracking**
7. **Task Management**
8. **Timeline & Activity Feed**
9. **Dashboard & Analytics**
10. **Profile & Settings**
11. **Meal Planning**
12. **Fasting Tracking**

---

## 1️⃣ **AUTHENTICATION & USER MANAGEMENT**

### **Feature 1.1: User Registration**
- **What**: Create new user account with email/password
- **Frontend**: `lib/screens/auth/signup_screen.dart`
- **Backend**: Firebase Auth (managed by Firebase SDK)
- **Function**: `signUpWithEmailPassword(email, password)`
- **Type**: **ASYNC**
- **Flow**:
  1. User enters email, password, name
  2. Frontend validates input
  3. Calls Firebase Auth `createUserWithEmailAndPassword()`
  4. Creates user document in Firestore: `users/{user_id}`
  5. Navigates to onboarding

**Objects**:
```dart
// Frontend
class SignupScreen extends StatefulWidget
TextEditingController _emailController
TextEditingController _passwordController
AuthProvider (Provider)

// Backend (Firestore)
User {
  user_id: string
  email: string
  display_name: string
  created_at: timestamp
}
```

---

### **Feature 1.2: User Login**
- **What**: Authenticate existing user
- **Frontend**: `lib/screens/auth/login_screen.dart`
- **Backend**: Firebase Auth
- **Function**: `signInWithEmailPassword(email, password)`
- **Type**: **ASYNC**
- **Flow**:
  1. User enters credentials
  2. Calls Firebase Auth `signInWithEmailAndPassword()`
  3. Gets JWT token
  4. Stores token in secure storage
  5. Navigates to home

**Objects**:
```dart
// Frontend
class LoginScreen extends StatefulWidget
AuthProvider (Provider)
SecureStorage (for token)

// Backend
JWT Token {
  user_id: string
  email: string
  exp: timestamp
}
```

---

### **Feature 1.3: Auto-Login (Session Persistence)**
- **What**: Keep user logged in across app restarts
- **Frontend**: `lib/main.dart` → `AppRoot`
- **Function**: `checkAuthStatus()`
- **Type**: **ASYNC**
- **Flow**:
  1. App starts
  2. Check if JWT token exists in secure storage
  3. If valid, auto-login
  4. If expired, show login screen

---

### **Feature 1.4: Logout**
- **What**: Sign out user and clear session
- **Frontend**: `lib/screens/profile/profile_screen.dart`
- **Function**: `signOut()`
- **Type**: **ASYNC**
- **Flow**:
  1. User taps "Logout"
  2. Clear JWT token from storage
  3. Call Firebase Auth `signOut()`
  4. Navigate to login screen

---

## 2️⃣ **CHAT & AI CONVERSATION**

### **Feature 2.1: Chat Interface**
- **What**: Conversational AI interface for logging and queries
- **Frontend**: `lib/screens/chat/chat_screen.dart`
- **Backend**: `app/main.py` → `POST /chat`
- **Function**: `chat_endpoint(req: ChatRequest)`
- **Type**: **ASYNC**
- **Flow**:
  1. User types message
  2. Frontend adds message to UI (optimistic)
  3. Calls `POST /chat` with text
  4. Backend routes to fast-path or LLM
  5. Returns response
  6. Frontend renders AI response

**Objects**:
```dart
// Frontend
class ChatScreen extends StatefulWidget
List<_ChatItem> _items  // Chat messages
ScrollController _scroll
TextEditingController _messageController

class _ChatItem {
  String type  // 'message' | 'task' | 'fitness'
  String? role  // 'user' | 'assistant'
  String? text
  DateTime createdAt
  String? summary
  String? suggestion
  Map<String, dynamic>? details
  bool expandable
  String? messageId
}

// Backend
class ChatRequest(BaseModel):
    text: str
    type: str = "auto"  // auto | food | workout | task

class ChatResponse(BaseModel):
    items: List[dict]
    message: str
    summary: Optional[str]
    suggestion: Optional[str]
    details: Optional[dict]
    expandable: bool
    message_id: Optional[str]
```

---

### **Feature 2.2: Smart Routing (Fast-Path vs LLM)**
- **What**: Route simple logs to fast-path, complex queries to LLM
- **Backend**: `app/main.py` → `_is_simple_food_log()`, `_is_water_log()`
- **Function**: Pattern matching with regex
- **Type**: **SYNC**
- **Flow**:
  1. Receive chat message
  2. Check if matches fast-path patterns
  3. If yes → Fast-path (0ms, no LLM)
  4. If no → LLM path (10-15s)

**Patterns**:
```python
# Food patterns
r'i\s+(ate|had|consumed)\s+(\d+\.?\d*)\s+(\w+)'  # "I ate 2 eggs"
r'(\d+\.?\d*)\s+(\w+)'  # "2 eggs"

# Water patterns
r'(\d+\.?\d*)\s*(glass|cup|ml|liter|l|oz)'  # "2 glasses"
```

**Fast-Path Foods** (In-Memory Cache):
```python
COMMON_FOODS_CACHE = {
    "egg": {kcal_per_unit: 70, protein_g: 6, ...},
    "banana": {kcal_per_unit: 105, protein_g: 1.3, ...},
    "chicken breast": {kcal_per_unit: 165, protein_g: 31, ...},
    # ... 100 common foods
}
```

---

### **Feature 2.3: Chat History**
- **What**: Load and display past conversations
- **Frontend**: `lib/screens/chat/chat_screen.dart` → `_loadChatHistory()`
- **Backend**: `app/main.py` → `GET /chat/history`
- **Function**: `get_chat_history()`
- **Type**: **ASYNC**
- **Flow**:
  1. Chat screen opens
  2. Calls `GET /chat/history?limit=20`
  3. Backend queries Firestore: `users/{user_id}/chat_sessions/{session_id}/messages`
  4. Returns last 20 messages (sorted by timestamp DESC)
  5. Frontend renders messages

**Performance**:
- **Query time**: 1-3 seconds
- **Limit**: 20 messages (last 24 hours)
- **Optimization**: Silent reload (no loading spinner)

---

### **Feature 2.4: Expandable Message Bubbles**
- **What**: Collapsible AI responses with summary/details
- **Frontend**: `lib/widgets/chat/expandable_message_bubble.dart`
- **Widget**: `ExpandableMessageBubble`
- **Type**: **SYNC** (UI only)
- **Flow**:
  1. AI response has `expandable: true`
  2. Shows summary (collapsed)
  3. Shows suggestion in blue box
  4. "More details" button
  5. Tap to expand → Shows nutrition breakdown

**UI Structure**:
```
┌────────────────────────────────────┐
│ 🥚 2 eggs eaten logged! 140 kcal   │  ← Summary
│                                    │
│ 💡 Great choice! Keep it balanced. │  ← Suggestion
│                                    │
│ More details ▼                     │  ← Expand button
│                                    │
│ [EXPANDED]                         │
│ 📊 Nutrition Breakdown             │
│ Calories: 140 kcal                 │
│ Protein: 12g                       │
│ Carbs: 1g                          │
│ Fat: 10g                           │
│                                    │
│ 👍 👎                              │  ← Feedback buttons
└────────────────────────────────────┘
```

---

### **Feature 2.5: Feedback System (Like/Dislike)**
- **What**: User can rate AI responses
- **Frontend**: `lib/widgets/chat/feedback_buttons.dart`
- **Backend**: `app/main.py` → `POST /chat/feedback`
- **Function**: `submit_feedback()`
- **Type**: **ASYNC**
- **Flow**:
  1. User taps 👍 or 👎
  2. Calls `POST /chat/feedback` with `message_id` and `rating`
  3. Backend saves to `admin/feedback/messages/{feedback_id}`
  4. Shows "Thanks for the feedback!" message

**Objects**:
```python
# Backend
class ChatFeedbackRequest(BaseModel):
    message_id: str
    rating: str  # 'helpful' | 'not_helpful'
    corrections: List[str] = []
    comment: Optional[str] = None

# Firestore
admin/feedback/messages/{feedback_id} {
    user_id: string
    message_id: string
    rating: string
    corrections: array
    comment: string
    timestamp: timestamp
}
```

---

### **Feature 2.6: Alternative Picker (Corrections)**
- **What**: User can select alternative interpretations
- **Frontend**: `lib/widgets/chat/alternative_picker.dart`
- **Backend**: `app/main.py` → `POST /chat/select-alternative`
- **Function**: `select_alternative()`
- **Type**: **ASYNC**
- **Flow**:
  1. LLM returns multiple interpretations with confidence scores
  2. Frontend shows alternatives as chips
  3. User taps preferred alternative
  4. Backend updates message with selected alternative
  5. Saves feedback

**Example**:
```
User: "I had 10 pistachio"

AI Response:
┌────────────────────────────────────┐
│ 🥜 10 pistachios logged! 56 kcal   │
│ ✓ 89% confident                    │
│                                    │
│ Did you mean:                      │
│ [10 pistachios] ← Selected         │
│ [10g pistachios]                   │
│ [1 cup pistachios]                 │
└────────────────────────────────────┘
```

---

### **Feature 2.7: Confidence Scoring**
- **What**: Show AI confidence in interpretations
- **Frontend**: `lib/widgets/chat/confidence_badge.dart`
- **Backend**: LLM returns confidence score
- **Type**: **SYNC** (UI only)
- **Display**:
  - 90-100%: Green badge "High"
  - 70-89%: Yellow badge "Medium"
  - <70%: Red badge "Low"

---

### **Feature 2.8: "Why?" Explanations**
- **What**: Explain AI reasoning
- **Frontend**: `lib/widgets/chat/explanation_sheet.dart`
- **Backend**: LLM returns explanation
- **Type**: **SYNC** (UI only)
- **Flow**:
  1. User taps "Why?" button
  2. Shows bottom sheet with explanation
  3. Explains how AI interpreted the message

---

## 3️⃣ **FOOD & NUTRITION TRACKING**

### **Feature 3.1: Fast-Path Food Logging**
- **What**: Instant food logging for common foods (no LLM)
- **Backend**: `app/main.py` → `_handle_simple_food_log()`
- **Function**: Pattern matching + in-memory cache lookup
- **Type**: **ASYNC**
- **Performance**: **~500ms** (10x faster than LLM)
- **Flow**:
  1. User types "I ate 2 eggs"
  2. Pattern matches: `r'i\s+ate\s+(\d+)\s+(\w+)'`
  3. Extracts: quantity=2, food="eggs"
  4. Lookup in `COMMON_FOODS_CACHE["egg"]`
  5. Calculate macros: 2 × 70 kcal = 140 kcal
  6. Infer meal type from time (breakfast/lunch/dinner/snack)
  7. Create `FitnessLog` object
  8. **Save to Firestore** (synchronous await)
  9. Return response

**Supported Foods** (100 common foods):
- Eggs, banana, apple, chicken, rice, bread, milk, yogurt, oats, almonds, etc.

**Limitations**:
- Only works for exact matches in cache
- No complex recipes or mixed dishes
- Falls back to LLM if not in cache

---

### **Feature 3.2: LLM-Based Food Logging**
- **What**: AI-powered food logging for complex foods
- **Backend**: `app/main.py` → LLM path
- **Function**: OpenAI GPT-4 API call
- **Type**: **ASYNC**
- **Performance**: **~12-15 seconds**
- **Flow**:
  1. User types "I had a chicken caesar salad with extra parmesan"
  2. Not in fast-path cache → Route to LLM
  3. Call OpenAI API with prompt
  4. LLM returns structured JSON:
     ```json
     {
       "food_name": "chicken caesar salad",
       "quantity": 1,
       "unit": "serving",
       "calories": 450,
       "protein_g": 35,
       "carbs_g": 20,
       "fat_g": 25,
       "meal_type": "lunch",
       "confidence_score": 0.85,
       "alternatives": [...]
     }
     ```
  5. Parse response
  6. Save to Firestore
  7. Return response with confidence score

**Advantages**:
- Handles complex foods
- Understands context
- Provides alternatives

**Disadvantages**:
- Slow (10-15s)
- Costs money ($0.01 per request)
- Requires internet

---

### **Feature 3.3: Meal Type Inference**
- **What**: Automatically detect meal type from time
- **Backend**: `app/main.py` → `_handle_simple_food_log()`
- **Function**: Time-based heuristic
- **Type**: **SYNC**
- **Logic**:
  ```python
  current_hour = datetime.now().hour
  if 5 <= current_hour < 11:
      meal_type = "breakfast"
  elif 11 <= current_hour < 16:
      meal_type = "lunch"
  elif 16 <= current_hour < 20:
      meal_type = "dinner"
  else:
      meal_type = "snack"
  ```

---

### **Feature 3.4: Nutrition Breakdown**
- **What**: Show detailed macros (calories, protein, carbs, fat)
- **Frontend**: `lib/widgets/chat/expandable_message_bubble.dart` → `_buildNutritionCard()`
- **Type**: **SYNC** (UI only)
- **Display**:
  ```
  📊 Nutrition Breakdown
  Calories: 140 kcal
  Protein: 12g
  Carbs: 1g
  Fat: 10g
  ```

---

### **Feature 3.5: Food Macro Database**
- **What**: Reference database of food nutritional info
- **Backend**: Firestore collection `food_macros/`
- **Type**: **READ-ONLY** (pre-populated)
- **Usage**: LLM can query this for accurate macro data
- **Structure**:
  ```python
  food_macros/{food_id} {
      food_id: string
      standardized_name: string
      calories_per_100g: number
      protein_g: number
      carbs_g: number
      fat_g: number
      verification_flag: boolean
      confidence_score: number
  }
  ```

---

## 4️⃣ **FITNESS & WORKOUT LOGGING**

### **Feature 4.1: Workout Logging**
- **What**: Log workouts with duration, calories burned
- **Backend**: `app/main.py` → LLM path (no fast-path yet)
- **Function**: `chat_endpoint()` → LLM
- **Type**: **ASYNC**
- **Flow**:
  1. User types "I ran 5km in 30 minutes"
  2. LLM parses: activity="run", distance=5, unit="km", duration=30
  3. Estimates calories burned: ~350 kcal
  4. Saves to `fitness_logs` with `log_type="workout"`

**Data Structure**:
```python
FitnessLog {
    log_id: string
    user_id: string
    log_type: "workout"
    content: "ran 5km in 30 minutes"
    timestamp: timestamp
    calories: 350
    ai_parsed_data: {
        activity_type: "run"
        distance: 5
        unit: "km"
        duration_minutes: 30
        intensity: "moderate"
    }
}
```

---

## 5️⃣ **WATER & HYDRATION TRACKING**

### **Feature 5.1: Water Logging**
- **What**: Track water intake
- **Backend**: `app/main.py` → Fast-path for water
- **Function**: `_is_water_log()` → `_handle_water_log()`
- **Type**: **ASYNC**
- **Performance**: **~500ms**
- **Flow**:
  1. User types "2 glasses of water" or "500ml water"
  2. Pattern matches: `r'(\d+\.?\d*)\s*(glass|cup|ml|liter)'`
  3. Convert to ml: 2 glasses = 500ml
  4. Save to `fitness_logs` with `log_type="water"`

**Conversions**:
- 1 glass = 250ml
- 1 cup = 250ml
- 1 liter = 1000ml
- 1 oz = 30ml

---

## 6️⃣ **SUPPLEMENT TRACKING**

### **Feature 6.1: Supplement Logging**
- **What**: Track vitamins, supplements
- **Backend**: `app/main.py` → LLM path
- **Function**: `chat_endpoint()` → LLM
- **Type**: **ASYNC**
- **Flow**:
  1. User types "I took 1 Vitamin D supplement"
  2. LLM parses: supplement="Vitamin D", quantity=1, unit="tablet"
  3. Saves to `fitness_logs` with `log_type="supplement"`

---

## 7️⃣ **TASK MANAGEMENT**

### **Feature 7.1: Task Creation**
- **What**: Create tasks with due dates and priorities
- **Backend**: `app/main.py` → `POST /tasks/`
- **Function**: `create_task()`
- **Type**: **ASYNC**
- **Flow**:
  1. User types "Remind me to call doctor tomorrow at 3pm"
  2. LLM parses: title="Call doctor", due_date=tomorrow 3pm, priority="medium"
  3. Saves to `users/{user_id}/tasks/{task_id}`

**Data Structure**:
```python
Task {
    task_id: string
    user_id: string
    title: string
    description: string
    status: enum [pending, in_progress, completed, cancelled]
    priority: enum [low, medium, high]
    due_date: timestamp
    created_at: timestamp
    updated_at: timestamp
}
```

---

### **Feature 7.2: Task List**
- **What**: View all tasks
- **Frontend**: `lib/screens/tasks/tasks_screen.dart`
- **Backend**: `app/main.py` → `GET /tasks/`
- **Function**: `list_tasks()`
- **Type**: **ASYNC**
- **Flow**:
  1. User opens Tasks screen
  2. Calls `GET /tasks/`
  3. Backend queries: `users/{user_id}/tasks`
  4. Returns tasks sorted by due_date

---

### **Feature 7.3: Task Completion**
- **What**: Mark task as done
- **Backend**: `app/main.py` → `PUT /tasks/{task_id}`
- **Function**: `update_task()`
- **Type**: **ASYNC**
- **Flow**:
  1. User taps checkbox
  2. Calls `PUT /tasks/{task_id}` with `status="completed"`
  3. Backend updates task
  4. Frontend shows strikethrough

---

## 8️⃣ **TIMELINE & ACTIVITY FEED**

### **Feature 8.1: Unified Timeline**
- **What**: Chronological feed of all activities (meals, workouts, tasks, water, supplements)
- **Frontend**: `lib/screens/timeline/timeline_screen.dart`
- **Backend**: `app/routers/timeline.py` → `GET /timeline`
- **Function**: `get_timeline()`
- **Type**: **ASYNC**
- **Performance**: **~1-3 seconds**
- **Flow**:
  1. User opens Timeline tab
  2. Calls `GET /timeline?types=meal,workout,task,water,supplement&limit=50`
  3. Backend queries:
     - `fitness_logs` (meals, workouts, water, supplements)
     - `tasks` (tasks)
  4. Merges results
  5. Sorts by timestamp DESC
  6. Returns paginated response

**Query Logic**:
```python
# Step 1: Fetch fitness logs
fitness_logs = db.collection('users').document(user_id) \
    .collection('fitness_logs') \
    .where('timestamp', '>=', start_ts) \
    .where('timestamp', '<=', end_ts) \
    .order_by('timestamp', direction='DESCENDING') \
    .limit(500) \
    .stream()

# Step 2: Fetch tasks
tasks = db.collection('users').document(user_id) \
    .collection('tasks') \
    .limit(500) \
    .stream()

# Step 3: Merge and sort
all_activities = fitness_logs + tasks
all_activities.sort(key=lambda x: x.timestamp, reverse=True)

# Step 4: Paginate
return all_activities[offset:offset+limit]
```

---

### **Feature 8.2: Timeline Filters**
- **What**: Filter by activity type
- **Frontend**: `lib/screens/timeline/timeline_screen.dart` → Filter chips
- **Function**: `toggleFilter(type)`
- **Type**: **SYNC** (UI) + **ASYNC** (API call)
- **Flow**:
  1. User taps "Meals" filter chip
  2. Updates `selected_types` set
  3. Calls `GET /timeline?types=meal`
  4. Backend returns only meals

**Available Filters**:
- Meals 🍽️
- Workouts 💪
- Tasks ✅
- Water 💧
- Supplements 💊

---

### **Feature 8.3: Timeline Auto-Refresh**
- **What**: Automatically refresh timeline after logging
- **Frontend**: `lib/screens/home/ios_home_screen_v6_enhanced.dart` → `_handleChatSubmit()`
- **Function**: `timeline.fetchTimeline()`
- **Type**: **ASYNC**
- **Flow**:
  1. User logs food from home page
  2. Navigates to chat screen
  3. Message sent and response received
  4. User navigates back to home
  5. **Auto-refresh trigger**: `timeline.fetchTimeline()`
  6. Timeline updates with new log

**Implementation**:
```dart
void _handleChatSubmit() async {
  // ... send message ...
  
  await Navigator.push(ChatScreen(...));
  
  // After returning from chat
  if (mounted) {
    context.read<TimelineProvider>().fetchTimeline();
  }
}
```

---

### **Feature 8.4: Timeline Pull-to-Refresh**
- **What**: Manual refresh by pulling down
- **Frontend**: `lib/screens/timeline/timeline_screen.dart` → `RefreshIndicator`
- **Type**: **ASYNC**
- **Flow**:
  1. User pulls down timeline
  2. Shows loading spinner
  3. Calls `timeline.fetchTimeline()`
  4. Updates UI with latest data

---

## 9️⃣ **DASHBOARD & ANALYTICS**

### **Feature 9.1: Daily Stats**
- **What**: Today's nutrition summary (calories, protein, carbs, fat, water)
- **Frontend**: `lib/providers/dashboard_provider.dart` → `fetchDailyStats()`
- **Backend**: `app/main.py` → `GET /fitness/logs`
- **Function**: `get_fitness_logs()`
- **Type**: **ASYNC**
- **Performance**: **~1-2 seconds**
- **Flow**:
  1. Home screen opens
  2. Calls `GET /fitness/logs?start=today_00:00&end=today_23:59`
  3. Backend queries `fitness_logs` for today
  4. Aggregates:
     - Total calories
     - Total protein
     - Total carbs
     - Total fat
     - Total water (ml)
  5. Returns `DailyStats` object

**Data Structure**:
```dart
class DailyStats {
  int caloriesConsumed;
  int caloriesGoal;
  double proteinG;
  double proteinGoal;
  double carbsG;
  double carbsGoal;
  double fatG;
  double fatGoal;
  double waterMl;
  double waterGoal;
  int stepsCompleted;
  int stepsGoal;
}
```

---

### **Feature 9.2: Activity Rings**
- **What**: Visual progress indicators (Apple Watch style)
- **Frontend**: `lib/screens/home/ios_home_screen_v6_enhanced.dart` → `_AppleActivityRingsPainter`
- **Type**: **SYNC** (UI only)
- **Rings**:
  1. **Calories** (Red): `caloriesConsumed / caloriesGoal`
  2. **Protein** (Green): `proteinG / proteinGoal`
  3. **Fat** (Orange): `fatG / fatGoal`
  4. **Water** (Cyan): `waterMl / waterGoal`

**Rendering**:
```dart
CustomPaint(
  painter: _AppleActivityRingsPainter(
    caloriesProgress: 0.58,  // 58%
    proteinProgress: 0.59,   // 59%
    fatProgress: 1.15,       // 115% (over goal!)
    waterProgress: 0.0,      // 0%
  ),
)
```

---

### **Feature 9.3: AI Nudges**
- **What**: Personalized suggestions based on progress
- **Frontend**: `lib/screens/home/ios_home_screen_v6_enhanced.dart` → `_generateNudges()`
- **Type**: **SYNC** (local logic)
- **Logic**:
  ```dart
  if (stats.proteinG < stats.proteinGoal * 0.5) {
    return "🥩 Protein is low! Consider adding eggs or chicken.";
  }
  if (stats.waterMl < 1000) {
    return "💧 Hydration check! Drink some water.";
  }
  if (stats.caloriesConsumed > stats.caloriesGoal) {
    return "⚠️ Over calorie goal. Consider lighter dinner.";
  }
  ```

---

### **Feature 9.4: Wins & Streaks**
- **What**: Celebrate achievements (streaks, goals hit)
- **Frontend**: `lib/screens/home/ios_home_screen_v6_enhanced.dart` → Wins card
- **Type**: **SYNC** (UI only)
- **Display**:
  ```
  🏆 Your Wins This Week
  🔥 3-day logging streak
  🎯 Hit protein goal 5/7 days
  💪 Level 12 - Keep crushing it!
  ```

---

## 🔟 **PROFILE & SETTINGS**

### **Feature 10.1: User Profile**
- **What**: View/edit user info (name, email, goals)
- **Frontend**: `lib/screens/profile/profile_screen.dart`
- **Backend**: `app/main.py` → `GET /profile`, `PUT /profile`
- **Type**: **ASYNC**

---

### **Feature 10.2: Goals Settings**
- **What**: Set daily goals (calories, protein, water)
- **Frontend**: `lib/screens/profile/edit_profile_screen.dart`
- **Backend**: Stored in user profile
- **Type**: **ASYNC**

---

### **Feature 10.3: Home Screen Variant Selector**
- **What**: Choose home screen style (V1-V6)
- **Frontend**: `lib/screens/settings/home_screen_style_selector.dart`
- **Function**: `setVariant(variant)`
- **Type**: **SYNC** (local storage)
- **Flow**:
  1. User taps variant card
  2. Saves to `SharedPreferences`
  3. Updates `HomeVariantProvider`
  4. Home screen rebuilds instantly

---

## 1️⃣1️⃣ **MEAL PLANNING**

### **Feature 11.1: AI Meal Plan Generator**
- **What**: Generate personalized meal plans
- **Frontend**: `lib/screens/plan/meal_plan_generator_screen.dart`
- **Backend**: `app/main.py` → `POST /meal-planning/generate`
- **Function**: `generate_meal_plan()`
- **Type**: **ASYNC**
- **Performance**: **~30-60 seconds** (multiple LLM calls)
- **Flow**:
  1. User sets preferences (calories, protein, diet type, allergies)
  2. Calls `POST /meal-planning/generate`
  3. Backend calls LLM to generate 7-day plan
  4. Returns structured meal plan
  5. Frontend displays day-by-day meals

---

## 1️⃣2️⃣ **FASTING TRACKING**

### **Feature 12.1: Intermittent Fasting Timer**
- **What**: Track fasting windows (16:8, 18:6, etc.)
- **Frontend**: `lib/screens/fasting/fasting_screen.dart`
- **Backend**: `app/main.py` → `POST /fasting/start`, `POST /fasting/end`
- **Type**: **ASYNC**
- **Flow**:
  1. User starts fast
  2. Saves start time to Firestore
  3. Shows countdown timer
  4. User ends fast
  5. Calculates duration
  6. Shows stats (fasting hours, eating window)

---

## 📊 **PERFORMANCE SUMMARY**

| Feature | Type | Performance | Optimization |
|---------|------|-------------|--------------|
| **Fast-Path Food Log** | ASYNC | ~500ms | ✅ Optimized |
| **LLM Food Log** | ASYNC | ~12-15s | ⚠️ Slow (LLM) |
| **Water Log** | ASYNC | ~500ms | ✅ Optimized |
| **Timeline Query** | ASYNC | ~1-3s | ⚠️ Needs caching |
| **Daily Stats** | ASYNC | ~1-2s | ⚠️ Needs caching |
| **Chat History** | ASYNC | ~1-3s | ⚠️ Needs caching |
| **Activity Rings** | SYNC | <10ms | ✅ Optimized |
| **Auto-Refresh** | ASYNC | ~1-3s | ✅ Working |

---

## 🚀 **ASYNC vs SYNC BREAKDOWN**

### **ASYNC Operations** (Non-Blocking)
- All API calls (HTTP requests)
- All Firestore queries/writes
- LLM API calls
- File I/O
- Navigation (with await)

### **SYNC Operations** (Blocking)
- UI rendering
- State updates
- Pattern matching (regex)
- Math calculations
- In-memory cache lookups
- Local storage reads/writes

---

## 🎯 **CRITICAL PATH ANALYSIS**

**Most Used Features** (by frequency):
1. **Food Logging** (fast-path) - 50% of requests
2. **Timeline View** - 30% of requests
3. **Chat History** - 10% of requests
4. **Daily Stats** - 5% of requests
5. **Task Management** - 5% of requests

**Optimization Priority**:
1. ✅ **Food Logging** - Already optimized (fast-path)
2. ⚠️ **Timeline** - Needs caching (1-3s → 100ms)
3. ⚠️ **Daily Stats** - Needs caching (1-2s → 50ms)
4. ⚠️ **Chat History** - Needs pagination (1-3s → 500ms)

---

This completes the comprehensive feature list! Let me know if you want me to dive deeper into any specific feature or create visual diagrams.

