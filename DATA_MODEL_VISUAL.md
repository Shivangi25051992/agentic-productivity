# 🎨 Visual Data Model - Yuvi AI Productivity App

**Interactive ASCII Diagrams**

---

## 📊 **FIRESTORE COLLECTIONS - TREE VIEW**

```
firestore (root database)
│
├─── 👥 users/ (collection)
│    │
│    └─── {user_id}/ (document)
│         │
│         ├─── 📧 email: "user@example.com"
│         ├─── 👤 display_name: "John Doe"
│         ├─── 📅 created_at: 2025-01-01T00:00:00Z
│         ├─── 🎯 goals: {
│         │        calories: 2000,
│         │        protein: 150,
│         │        water: 2000
│         │    }
│         │
│         ├─── 🍽️ fitness_logs/ (subcollection) ⭐ MAIN DATA
│         │    │
│         │    ├─── {log_id_1}/ (meal)
│         │    │    ├─── log_type: "meal"
│         │    │    ├─── content: "2 eggs"
│         │    │    ├─── timestamp: 2025-11-10T08:30:00Z
│         │    │    ├─── calories: 140
│         │    │    └─── ai_parsed_data: {
│         │    │         meal_type: "breakfast",
│         │    │         food_name: "egg",
│         │    │         quantity: 2,
│         │    │         protein_g: 12,
│         │    │         carbs_g: 1,
│         │    │         fat_g: 10
│         │    │    }
│         │    │
│         │    ├─── {log_id_2}/ (workout)
│         │    │    ├─── log_type: "workout"
│         │    │    ├─── content: "ran 5km"
│         │    │    ├─── timestamp: 2025-11-10T18:00:00Z
│         │    │    ├─── calories: 350
│         │    │    └─── ai_parsed_data: {
│         │    │         activity_type: "run",
│         │    │         distance: 5,
│         │    │         unit: "km",
│         │    │         duration_minutes: 30
│         │    │    }
│         │    │
│         │    ├─── {log_id_3}/ (water)
│         │    │    ├─── log_type: "water"
│         │    │    ├─── content: "2 glasses"
│         │    │    ├─── timestamp: 2025-11-10T14:00:00Z
│         │    │    ├─── calories: 0
│         │    │    └─── ai_parsed_data: {
│         │    │         quantity_ml: 500
│         │    │    }
│         │    │
│         │    └─── {log_id_4}/ (supplement)
│         │         ├─── log_type: "supplement"
│         │         ├─── content: "Vitamin D"
│         │         ├─── timestamp: 2025-11-10T09:00:00Z
│         │         ├─── calories: 0
│         │         └─── ai_parsed_data: {
│         │              supplement_name: "Vitamin D",
│         │              dosage: "1000 IU"
│         │         }
│         │
│         ├─── 💬 chat_sessions/ (subcollection)
│         │    │
│         │    └─── {session_id}/ (document)
│         │         │
│         │         ├─── created_at: 2025-11-10T00:00:00Z
│         │         ├─── lastMessageAt: 2025-11-10T18:30:00Z
│         │         ├─── messageCount: 42
│         │         │
│         │         └─── messages/ (subcollection)
│         │              │
│         │              ├─── {message_id_1}/ (user message)
│         │              │    ├─── messageId: "1762778830212"
│         │              │    ├─── role: "user"
│         │              │    ├─── content: "I ate 2 eggs"
│         │              │    ├─── timestamp: 2025-11-10T08:30:00Z
│         │              │    └─── metadata: {}
│         │              │
│         │              └─── {message_id_2}/ (AI response)
│         │                   ├─── messageId: "1762778830312"
│         │                   ├─── role: "assistant"
│         │                   ├─── content: "🥚 2 eggs logged!"
│         │                   ├─── timestamp: 2025-11-10T08:30:01Z
│         │                   ├─── summary: "🥚 2 eggs eaten logged! 140 kcal"
│         │                   ├─── suggestion: "Great choice!"
│         │                   ├─── details: {
│         │                   │    nutrition: {
│         │                   │        calories: 140,
│         │                   │        protein_g: 12,
│         │                   │        carbs_g: 1,
│         │                   │        fat_g: 10
│         │                   │    }
│         │                   │}
│         │                   ├─── expandable: true
│         │                   ├─── confidence_score: 0.95
│         │                   └─── metadata: {
│         │                        category: "food_log",
│         │                        fast_path: true
│         │                   }
│         │
│         └─── ✅ tasks/ (subcollection)
│              │
│              ├─── {task_id_1}/
│              │    ├─── title: "Call doctor"
│              │    ├─── description: "Schedule checkup"
│              │    ├─── status: "pending"
│              │    ├─── priority: "high"
│              │    ├─── due_date: 2025-11-11T15:00:00Z
│              │    ├─── created_at: 2025-11-10T10:00:00Z
│              │    └─── updated_at: 2025-11-10T10:00:00Z
│              │
│              └─── {task_id_2}/
│                   ├─── title: "Buy groceries"
│                   ├─── status: "completed"
│                   ├─── priority: "medium"
│                   └─── ...
│
├─── 🥗 food_macros/ (collection) - Reference Data
│    │
│    ├─── {food_id_1}/
│    │    ├─── food_id: "egg_001"
│    │    ├─── standardized_name: "egg"
│    │    ├─── calories_per_100g: 143
│    │    ├─── protein_g: 12.6
│    │    ├─── carbs_g: 0.7
│    │    ├─── fat_g: 9.5
│    │    ├─── verification_flag: true
│    │    └─── confidence_score: 0.98
│    │
│    ├─── {food_id_2}/
│    │    ├─── standardized_name: "banana"
│    │    ├─── calories_per_100g: 89
│    │    └─── ...
│    │
│    └─── ... (100+ foods)
│
└─── 🔧 admin/ (collection) - System Data
     │
     ├─── llm_usage_logs/ (document)
     │    └─── logs/ (subcollection)
     │         ├─── {log_id_1}/
     │         │    ├─── provider: "openai"
     │         │    ├─── model_name: "gpt-4"
     │         │    ├─── tokens_used: 1500
     │         │    ├─── cost_usd: 0.015
     │         │    └─── timestamp: 2025-11-10T18:30:00Z
     │         └─── ...
     │
     └─── feedback/ (document)
          └─── messages/ (subcollection)
               ├─── {feedback_id_1}/
               │    ├─── user_id: "mLNCSrl01vhubtZXJYj7R4kEQ8g2"
               │    ├─── message_id: "1762778830312"
               │    ├─── rating: "helpful"
               │    ├─── corrections: []
               │    └─── timestamp: 2025-11-10T18:31:00Z
               └─── ...
```

---

## 🔗 **DATA RELATIONSHIPS - ENTITY DIAGRAM**

```
┌──────────────────────────────────────────────────────────────────┐
│                         ENTITY RELATIONSHIPS                      │
└──────────────────────────────────────────────────────────────────┘

        ┌─────────────┐
        │    USER     │
        │             │
        │ • user_id   │
        │ • email     │
        │ • name      │
        │ • goals     │
        └──────┬──────┘
               │
               │ owns (1:N)
               │
       ┌───────┼───────┬───────────────┬──────────────┐
       │       │       │               │              │
       ▼       ▼       ▼               ▼              ▼
┌──────────┐ ┌────┐ ┌────────┐ ┌─────────────┐ ┌─────────┐
│ FITNESS  │ │CHAT│ │ TASKS  │ │   FEEDBACK  │ │  PLANS  │
│   LOGS   │ │SESS│ │        │ │             │ │         │
│          │ │ION │ │        │ │             │ │         │
│ • log_id │ │    │ │• task  │ │• message_id │ │• plan   │
│ • type   │ │    │ │  _id   │ │• rating     │ │  _id    │
│ • content│ │    │ │• title │ │• comment    │ │• type   │
│ • kcal   │ │    │ │• status│ │             │ │• meals  │
│ • macros │ │    │ │• due   │ │             │ │         │
└──────────┘ └─┬──┘ └────────┘ └─────────────┘ └─────────┘
               │
               │ contains (1:N)
               │
               ▼
        ┌──────────┐
        │ MESSAGES │
        │          │
        │• msg_id  │
        │• role    │
        │• content │
        │• summary │
        │• details │
        └──────────┘
```

---

## 📊 **TIMELINE QUERY - DATA FLOW**

```
┌──────────────────────────────────────────────────────────────────┐
│                      TIMELINE QUERY FLOW                          │
└──────────────────────────────────────────────────────────────────┘

USER OPENS TIMELINE TAB
        │
        ▼
┌───────────────────────────────────────────────────────────────┐
│ FRONTEND: timeline_provider.dart                              │
│ ───────────────────────────────────────────────────────────── │
│ fetchTimeline()                                               │
│   ├─ types = "meal,workout,task,water,supplement"            │
│   ├─ startDate = today - 30 days                             │
│   ├─ endDate = today                                          │
│   └─ limit = 50                                               │
└───────────────────────────────────────────────────────────────┘
        │
        │ GET /timeline?types=...&limit=50
        ▼
┌───────────────────────────────────────────────────────────────┐
│ BACKEND: app/routers/timeline.py                              │
│ ───────────────────────────────────────────────────────────── │
│ get_timeline()                                                │
│                                                               │
│ STEP 1: Query fitness_logs                                    │
│ ┌─────────────────────────────────────────────────────────┐  │
│ │ db.collection('users/{user_id}/fitness_logs')           │  │
│ │   .where('timestamp', '>=', start_ts)                   │  │
│ │   .where('timestamp', '<=', end_ts)                     │  │
│ │   .order_by('timestamp', direction='DESC')              │  │
│ │   .limit(500)                                           │  │
│ │                                                         │  │
│ │ RETURNS: [                                              │  │
│ │   {log_id: "1", type: "meal", content: "2 eggs", ...}, │  │
│ │   {log_id: "2", type: "water", content: "2 glasses"}, │  │
│ │   {log_id: "3", type: "workout", content: "ran 5km"}, │  │
│ │   ...                                                   │  │
│ │ ]                                                       │  │
│ └─────────────────────────────────────────────────────────┘  │
│                                                               │
│ STEP 2: Query tasks                                           │
│ ┌─────────────────────────────────────────────────────────┐  │
│ │ db.collection('users/{user_id}/tasks')                  │  │
│ │   .limit(500)                                           │  │
│ │                                                         │  │
│ │ RETURNS: [                                              │  │
│ │   {task_id: "1", title: "Call doctor", status: "..."}, │  │
│ │   {task_id: "2", title: "Buy groceries", ...},        │  │
│ │   ...                                                   │  │
│ │ ]                                                       │  │
│ └─────────────────────────────────────────────────────────┘  │
│                                                               │
│ STEP 3: Convert to TimelineActivity objects                   │
│ ┌─────────────────────────────────────────────────────────┐  │
│ │ for log in fitness_logs:                                │  │
│ │     activity = TimelineActivity(                        │  │
│ │         id = log.log_id,                                │  │
│ │         type = log.log_type,  # "meal"                  │  │
│ │         title = "Breakfast - 2 eggs",                   │  │
│ │         timestamp = log.timestamp,                      │  │
│ │         icon = "restaurant",                            │  │
│ │         color = "green",                                │  │
│ │         details = log.ai_parsed_data                    │  │
│ │     )                                                   │  │
│ │     all_activities.append(activity)                     │  │
│ └─────────────────────────────────────────────────────────┘  │
│                                                               │
│ STEP 4: Merge & Sort                                          │
│ ┌─────────────────────────────────────────────────────────┐  │
│ │ all_activities = fitness_logs + tasks                   │  │
│ │ all_activities.sort(                                    │  │
│ │     key=lambda x: x.timestamp,                          │  │
│ │     reverse=True  # Most recent first                   │  │
│ │ )                                                       │  │
│ └─────────────────────────────────────────────────────────┘  │
│                                                               │
│ STEP 5: Paginate                                              │
│ ┌─────────────────────────────────────────────────────────┐  │
│ │ paginated = all_activities[offset:offset+limit]         │  │
│ │ # offset=0, limit=50 → First 50 activities              │  │
│ └─────────────────────────────────────────────────────────┘  │
│                                                               │
│ STEP 6: Return response                                       │
│ ┌─────────────────────────────────────────────────────────┐  │
│ │ return TimelineResponse(                                │  │
│ │     activities = paginated,  # 50 items                 │  │
│ │     total_count = len(all_activities),  # 123           │  │
│ │     has_more = (offset + limit) < total_count,          │  │
│ │     next_offset = offset + limit                        │  │
│ │ )                                                       │  │
│ └─────────────────────────────────────────────────────────┘  │
└───────────────────────────────────────────────────────────────┘
        │
        │ HTTP 200 OK
        ▼
┌───────────────────────────────────────────────────────────────┐
│ FRONTEND: timeline_screen.dart                                │
│ ───────────────────────────────────────────────────────────── │
│ ListView.builder(                                             │
│   itemCount: activities.length,                               │
│   itemBuilder: (context, index) {                             │
│     final activity = activities[index];                       │
│     return TimelineCard(                                      │
│       icon: activity.icon,  // 🍽️                            │
│       title: activity.title,  // "Breakfast - 2 eggs"        │
│       timestamp: activity.timestamp,  // "8:30 AM"           │
│       calories: activity.details.calories,  // 140           │
│       onTap: () => showDetails(activity)                     │
│     );                                                        │
│   }                                                           │
│ )                                                             │
│                                                               │
│ RENDERS:                                                      │
│ ┌─────────────────────────────────────────────────────────┐  │
│ │ 🍽️ Breakfast - 2 eggs           8:30 AM ▼              │  │
│ │ 140 cal                                                 │  │
│ ├─────────────────────────────────────────────────────────┤  │
│ │ 💧 Water - 2 glasses            2:00 PM ▼              │  │
│ │ 0 cal                                                   │  │
│ ├─────────────────────────────────────────────────────────┤  │
│ │ 💪 Workout - Ran 5km            6:00 PM ▼              │  │
│ │ 350 cal burned                                          │  │
│ ├─────────────────────────────────────────────────────────┤  │
│ │ ✅ Task - Call doctor           Tomorrow 3 PM ▼        │  │
│ │ High priority                                           │  │
│ └─────────────────────────────────────────────────────────┘  │
└───────────────────────────────────────────────────────────────┘
```

---

## 🔄 **FAST-PATH vs LLM PATH - COMPARISON**

```
┌──────────────────────────────────────────────────────────────────┐
│                    FAST-PATH (2 eggs)                             │
└──────────────────────────────────────────────────────────────────┘

USER: "I ate 2 eggs"
  │
  ▼
┌─────────────────────────────────────────────────────────────┐
│ Pattern Match: r'i\s+ate\s+(\d+)\s+(\w+)'                  │
│ ✅ MATCH: quantity=2, food="eggs"                          │
└─────────────────────────────────────────────────────────────┘
  │
  ▼
┌─────────────────────────────────────────────────────────────┐
│ Cache Lookup: COMMON_FOODS_CACHE["egg"]                    │
│ ✅ FOUND: {kcal: 70, protein: 6, carbs: 0.5, fat: 5}      │
└─────────────────────────────────────────────────────────────┘
  │
  ▼
┌─────────────────────────────────────────────────────────────┐
│ Calculate: 2 × 70 = 140 kcal                                │
│ Infer meal: "breakfast" (8:30 AM)                          │
└─────────────────────────────────────────────────────────────┘
  │
  ▼
┌─────────────────────────────────────────────────────────────┐
│ Save to Firestore: users/{uid}/fitness_logs/{id}           │
│ ⏱️ 200-500ms                                                │
└─────────────────────────────────────────────────────────────┘
  │
  ▼
┌─────────────────────────────────────────────────────────────┐
│ Return: "🥚 2 eggs logged! 140 kcal"                       │
│ ⏱️ TOTAL: ~500ms                                            │
└─────────────────────────────────────────────────────────────┘


┌──────────────────────────────────────────────────────────────────┐
│              LLM PATH (chicken caesar salad)                      │
└──────────────────────────────────────────────────────────────────┘

USER: "I had a chicken caesar salad with extra parmesan"
  │
  ▼
┌─────────────────────────────────────────────────────────────┐
│ Pattern Match: No match in fast-path                       │
│ ❌ NOT FOUND in cache                                       │
└─────────────────────────────────────────────────────────────┘
  │
  ▼
┌─────────────────────────────────────────────────────────────┐
│ Call OpenAI GPT-4 API                                       │
│ Prompt: "Parse this food log: ..."                         │
│ ⏱️ 10-15 seconds                                            │
└─────────────────────────────────────────────────────────────┘
  │
  ▼
┌─────────────────────────────────────────────────────────────┐
│ LLM Response:                                               │
│ {                                                           │
│   "food_name": "chicken caesar salad",                     │
│   "quantity": 1,                                           │
│   "unit": "serving",                                       │
│   "calories": 450,                                         │
│   "protein_g": 35,                                         │
│   "carbs_g": 20,                                           │
│   "fat_g": 25,                                             │
│   "meal_type": "lunch",                                    │
│   "confidence_score": 0.85,                                │
│   "alternatives": [...]                                    │
│ }                                                           │
└─────────────────────────────────────────────────────────────┘
  │
  ▼
┌─────────────────────────────────────────────────────────────┐
│ Parse & Save to Firestore                                   │
│ ⏱️ 200-500ms                                                │
└─────────────────────────────────────────────────────────────┘
  │
  ▼
┌─────────────────────────────────────────────────────────────┐
│ Return: "🥗 Chicken caesar salad logged! 450 kcal"         │
│ ⏱️ TOTAL: ~12-15 seconds                                    │
└─────────────────────────────────────────────────────────────┘


┌──────────────────────────────────────────────────────────────────┐
│                         COMPARISON                                │
├──────────────────────────────────────────────────────────────────┤
│                    Fast-Path    │    LLM Path                    │
├──────────────────────────────────────────────────────────────────┤
│ Speed              ~500ms       │    ~12-15s                     │
│ Accuracy           High (95%)   │    Very High (98%)             │
│ Cost               $0           │    $0.01 per request           │
│ Coverage           100 foods    │    All foods                   │
│ Complexity         Simple        │    Complex recipes             │
│ Alternatives       No           │    Yes (multiple options)      │
│ Confidence         N/A          │    Scored (0-1)                │
└──────────────────────────────────────────────────────────────────┘
```

---

## 🎯 **OPTIMIZATION OPPORTUNITIES**

```
┌──────────────────────────────────────────────────────────────────┐
│                    CURRENT BOTTLENECKS                            │
└──────────────────────────────────────────────────────────────────┘

1. TIMELINE QUERY (1-3 seconds)
   ┌────────────────────────────────────────────────────────┐
   │ Problem: Fetches 500 logs, only shows 50              │
   │ Solution: Cursor-based pagination                      │
   │ Expected: 1-3s → 200-500ms (5x faster)                │
   └────────────────────────────────────────────────────────┘

2. DAILY STATS (1-2 seconds)
   ┌────────────────────────────────────────────────────────┐
   │ Problem: Queries all logs for today on every request  │
   │ Solution: In-memory cache (1 hour TTL)                │
   │ Expected: 1-2s → 50ms (20x faster)                    │
   └────────────────────────────────────────────────────────┘

3. CHAT HISTORY (1-3 seconds)
   ┌────────────────────────────────────────────────────────┐
   │ Problem: Loads 50 messages on every open              │
   │ Solution: Pagination + local cache                     │
   │ Expected: 1-3s → 500ms (3x faster)                    │
   └────────────────────────────────────────────────────────┘

4. LLM CALLS (10-15 seconds)
   ┌────────────────────────────────────────────────────────┐
   │ Problem: Slow API response time                        │
   │ Solution: Expand fast-path cache (100 → 500 foods)    │
   │ Expected: 80% of logs use fast-path (10x faster)      │
   └────────────────────────────────────────────────────────┘
```

---

**End of Visual Data Model**

