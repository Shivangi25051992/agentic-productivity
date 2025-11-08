# 📊 DATA FLOW BREAKDOWN - COMPLETE ANALYSIS

## 🗄️ DATABASE STRUCTURE

### **Firestore Collections Overview**

```
Firestore Root
├── users/                          (Flat collection)
│   └── {userId}/
│       ├── fitness_logs/           (Subcollection - NEW STRUCTURE)
│       │   └── {logId}/
│       │       ├── log_id
│       │       ├── user_id
│       │       ├── log_type: "meal" | "workout" | "water" | "supplement"
│       │       ├── content
│       │       ├── calories
│       │       ├── timestamp
│       │       ├── ai_parsed_data {...}
│       │       ├── created_at
│       │       └── updated_at
│       │
│       └── chat_sessions/          (Subcollection - planned)
│           └── {sessionId}/
│               └── messages/
│
├── tasks/                          (Flat collection)
│   └── {taskId}/
│       ├── task_id
│       ├── user_id
│       ├── title
│       ├── description
│       ├── due_date (OPTIONAL)
│       ├── priority
│       ├── status
│       ├── created_at
│       └── updated_at
│
├── user_profiles/                  (Flat collection)
│   └── {userId}/
│       ├── name
│       ├── email
│       ├── timezone
│       ├── daily_goals {...}
│       └── ...
│
└── fitness_logs/                   (Flat collection - OLD STRUCTURE)
    └── {logId}/                    (Deprecated, fallback only)
        └── ...
```

---

## 1️⃣ MEALS

### **Storage Location**
- **Collection**: `users/{userId}/fitness_logs` (Subcollection - NEW)
- **Fallback**: `fitness_logs` (Flat collection - OLD)
- **Feature Flag**: `USE_NEW_STRUCTURE = True` (in `app/services/database.py:191`)

### **Database Fields**
```python
{
  "log_id": "UUID",
  "user_id": "string",
  "log_type": "meal",  # ← Identifies as meal
  "content": "2 eggs, 1 slice toast",  # User's original input
  "calories": 220,
  "timestamp": "2025-11-03T10:30:00Z",
  "ai_parsed_data": {
    "meal_type": "breakfast",  # breakfast|lunch|dinner|snack|unknown
    "items": ["2 eggs", "1 slice toast"],
    "protein_g": 18.5,
    "carbs_g": 15.2,
    "fat_g": 12.0,
    "fiber_g": 2.0,
    "confidence": 0.95
  },
  "created_at": "2025-11-03T10:30:00Z",
  "updated_at": "2025-11-03T10:30:00Z"
}
```

### **How Meals are Saved**
**File**: `app/main.py` (chat_endpoint)
**Lines**: ~800-850

```python
# When AI classifies input as "meal"
if item.category == "meal":
    log = FitnessLog(
        user_id=current_user.user_id,
        log_type=FitnessLogType.meal,
        content=text,
        calories=item.data.get("calories", 0),
        timestamp=datetime.now(timezone.utc),
        ai_parsed_data=item.data,
    )
    dbsvc.create_fitness_log(log)  # Saves to users/{userId}/fitness_logs
```

### **How Meals are Queried**
**File**: `app/services/database.py`
**Function**: `list_fitness_logs_by_user()` (lines 276-343)

```python
# Query NEW structure (subcollection)
query = db.collection('users').document(user_id)\
          .collection('fitness_logs')

# Filters applied:
if start_ts:
    query = query.where("timestamp", ">=", start_ts)
if end_ts:
    query = query.where("timestamp", "<=", end_ts)

# Order by timestamp
query = query.order_by("timestamp", direction=firestore.Query.DESCENDING)

# Filter by log_type IN MEMORY (to avoid composite index)
if log_type:
    # Filter after fetching to avoid: user_id + log_type + timestamp index
    logs = [log for log in logs if log.log_type == log_type]
```

### **Timeline Display**
**File**: `flutter_app/lib/screens/meals/timeline_view_screen.dart`
**Lines**: 53-56

```dart
// 1. Fetch from DashboardProvider
final activities = dashboardProvider.stats.activities
    .where((a) => a.type == 'meal')  // ← Filter only meals
    .toList()
  ..sort((a, b) => a.timestamp.compareTo(b.timestamp));  // ← Sort by time

// 2. Display each activity
_buildTimelineItem(activity)
  // Shows: timestamp, meal_type, description, calories, macros
```

**Filter Criteria**:
- ✅ `type == 'meal'` (excludes workouts, tasks, etc.)
- ✅ Sorted by `timestamp` (chronological order)
- ✅ Date filter: Currently shows today's meals only

---

## 2️⃣ WORKOUTS

### **Storage Location**
- **Collection**: `users/{userId}/fitness_logs` (Same as meals)
- **Identified by**: `log_type: "workout"`

### **Database Fields**
```python
{
  "log_id": "UUID",
  "user_id": "string",
  "log_type": "workout",  # ← Identifies as workout
  "content": "30 min run",
  "calories": 300,  # Calories BURNED
  "timestamp": "2025-11-03T18:00:00Z",
  "ai_parsed_data": {
    "activity_type": "running",  # running|cycling|gym|yoga|etc
    "duration_minutes": 30,
    "intensity": "moderate",  # low|moderate|high
    "distance_km": 5.0,  # Optional
    "confidence": 0.90
  },
  "created_at": "2025-11-03T18:00:00Z",
  "updated_at": "2025-11-03T18:00:00Z"
}
```

### **How Workouts are Saved**
**File**: `app/main.py` (chat_endpoint)

```python
if item.category == "workout":
    log = FitnessLog(
        user_id=current_user.user_id,
        log_type=FitnessLogType.workout,
        content=text,
        calories=item.data.get("calories", 0),  # Calories burned
        timestamp=datetime.now(timezone.utc),
        ai_parsed_data=item.data,
    )
    dbsvc.create_fitness_log(log)
```

### **How Workouts are Queried**
- **Same as meals**: `list_fitness_logs_by_user()`
- **Filter**: `log_type == FitnessLogType.workout`

### **Timeline Display**
**Current Status**: ❌ **NOT DISPLAYED IN TIMELINE**

**Why?**
```dart
// timeline_view_screen.dart:53-54
final activities = dashboardProvider.stats.activities
    .where((a) => a.type == 'meal')  // ← ONLY shows meals!
```

**To Fix**: Change filter to include workouts:
```dart
.where((a) => a.type == 'meal' || a.type == 'workout')
```

---

## 3️⃣ TASKS

### **Storage Location**
- **Collection**: `tasks` (Flat collection - NOT subcollection)
- **Path**: `tasks/{taskId}`

### **Database Fields**
```python
{
  "task_id": "UUID",
  "user_id": "string",
  "title": "Remind me to workout at 7 pm",
  "description": "",
  "due_date": None,  # ⚠️ OPTIONAL - often null!
  "priority": "medium",  # low|medium|high
  "status": "pending",  # pending|in_progress|completed|cancelled
  "created_at": "2025-11-03T10:00:00Z",
  "updated_at": "2025-11-03T10:00:00Z"
}
```

### **How Tasks are Saved**
**File**: `app/main.py` (chat_endpoint)
**Lines**: 889-904

```python
if item.category in ("task", "reminder"):
    try:
        t = Task(
            user_id=current_user.user_id,
            title=item.data.get("title") or item.summary or text,
            description=item.data.get("notes", ""),
            due_date=None,  # TODO: Parse due_date from natural language
            priority=TaskPriority.medium,
            status=TaskStatus.pending,
        )
        dbsvc.create_task(t)  # Saves to tasks/{taskId}
        print(f"✅ Task created: {t.task_id} - {t.title}")
    except Exception as e:
        print(f"❌ Failed to create task: {e}")
```

### **How Tasks are Queried**
**File**: `app/services/database.py`
**Function**: `list_tasks_by_user()` (lines 135-184)

```python
query = db.collection(TASKS_COLLECTION).where("user_id", "==", user_id)

# Optional filters:
if status:
    query = query.where("status", "==", status.value)
if priority:
    query = query.where("priority", "==", priority.value)

# Date range filter (if provided)
if date_range:
    start, end = date_range
    if start:
        query = query.where("due_date", ">=", start)  # ⚠️ Excludes tasks with due_date=None!
    if end:
        query = query.where("due_date", "<=", end)

# Order by created_at (or due_date if filtering by date)
query = query.order_by(order_field, direction=firestore.Query.DESCENDING)
```

### **Timeline Display**
**Current Status**: ❌ **NOT DISPLAYED IN TIMELINE**

**Why?**
1. Timeline only shows `type == 'meal'`
2. Tasks are NOT included in `dashboardProvider.stats.activities`
3. Tasks are fetched separately but not merged into timeline

**To Fix**:
1. Fetch tasks in `DashboardProvider.fetchDailyStats()`
2. Add tasks to `activities` list with `type: 'task'`
3. Update timeline filter to include tasks

---

## 4️⃣ EVENTS

### **Storage Location**
**Current Status**: ❌ **NOT IMPLEMENTED**

**Planned Structure**:
- Could use `tasks` collection with `task_type: "event"`
- OR create separate `events` collection
- OR use `fitness_logs` with `log_type: "event"`

### **Not Currently Tracked**

---

## 🔍 TIMELINE VIEW - COMPLETE BREAKDOWN

### **File**: `flutter_app/lib/screens/meals/timeline_view_screen.dart`

### **Data Flow**:

```dart
1. initState() → _loadData()
   ↓
2. DashboardProvider.fetchDailyStats(auth)
   ↓
3. Backend: GET /fitness/logs?start={date}&end={date}
   ↓
4. Backend: list_fitness_logs_by_user(user_id, start_ts, end_ts)
   ↓
5. Firestore: users/{userId}/fitness_logs
   WHERE timestamp >= start AND timestamp <= end
   ORDER BY timestamp DESC
   ↓
6. Returns: List<FitnessLog> (meals + workouts)
   ↓
7. Frontend: dashboardProvider.stats.activities
   ↓
8. Timeline: Filter .where((a) => a.type == 'meal')
   ↓
9. Display: _buildTimelineItem() for each meal
```

### **Filter Criteria (Current)**:

```dart
// Line 53-56
final activities = dashboardProvider.stats.activities
    .where((a) => a.type == 'meal')  // ← ONLY MEALS
    .toList()
  ..sort((a, b) => a.timestamp.compareTo(b.timestamp));  // ← CHRONOLOGICAL
```

**What's Filtered OUT**:
- ❌ Workouts (`type == 'workout'`)
- ❌ Tasks (`type == 'task'`)
- ❌ Water logs (`type == 'water'`)
- ❌ Supplement logs (`type == 'supplement'`)

### **What's Displayed**:
- ✅ Meal timestamp (e.g., "5:29 PM")
- ✅ Meal type badge (breakfast/lunch/dinner/snack)
- ✅ Description (e.g., "2 eggs, 1 slice toast")
- ✅ Calories
- ✅ Macros (protein, carbs, fat)

---

## 🐛 CURRENT ISSUES IDENTIFIED

### **Issue 1: Tasks Not in Timeline**
**Root Cause**: 
- Tasks stored in separate `tasks` collection
- Not fetched in `DashboardProvider.fetchDailyStats()`
- Not included in `activities` array

**Fix Required**:
1. Fetch tasks in `fetchDailyStats()`
2. Merge tasks into `activities` with proper format
3. Update timeline filter to include `type == 'task'`

### **Issue 2: Tasks Not in Dashboard**
**Root Cause**:
- Frontend filters tasks by `start_due` date
- Tasks without `due_date` are excluded from query
- Query: `GET /tasks/?start_due=2025-11-03T00:00:00.000`

**Fix Required**:
- Remove date filter for dashboard task list
- OR make `due_date` parsing work from natural language
- OR show ALL pending tasks regardless of due_date

### **Issue 3: Workouts Not in Timeline**
**Root Cause**: Timeline filter only shows `type == 'meal'`

**Fix Required**:
```dart
.where((a) => a.type == 'meal' || a.type == 'workout')
```

### **Issue 4: No Activity Logs Visible**
**Symptoms**: 
- Console shows "✅ Fetched 2 fitness logs"
- Timeline shows times but no details

**Possible Causes**:
- Data format mismatch between backend and frontend
- `ai_parsed_data` not being parsed correctly
- Display logic expecting different field names

---

## 📋 SUMMARY TABLE

| Type | Collection | Path | log_type/Identifier | Timeline? | Dashboard? |
|------|-----------|------|---------------------|-----------|------------|
| **Meals** | `users/{userId}/fitness_logs` | Subcollection | `log_type: "meal"` | ✅ YES | ✅ YES |
| **Workouts** | `users/{userId}/fitness_logs` | Subcollection | `log_type: "workout"` | ❌ NO | ⚠️ Partial |
| **Tasks** | `tasks` | Flat | `task_id` | ❌ NO | ⚠️ Partial |
| **Events** | N/A | N/A | N/A | ❌ NO | ❌ NO |
| **Water** | `users/{userId}/fitness_logs` | Subcollection | `log_type: "water"` | ❌ NO | ❌ NO |
| **Supplements** | `users/{userId}/fitness_logs` | Subcollection | `log_type: "supplement"` | ❌ NO | ❌ NO |

---

## 🎯 RECOMMENDED FIXES

### **Priority 1: Fix Task Display**
1. Remove date filter from dashboard task query
2. Parse `due_date` from natural language ("at 7 pm")
3. Show all pending tasks in dashboard

### **Priority 2: Complete Timeline View**
1. Include workouts: `.where((a) => ['meal', 'workout'].contains(a.type))`
2. Include tasks: Add tasks to `activities` array
3. Add water/supplement logs as timeline items

### **Priority 3: Unify Data Structure**
1. Consider moving tasks to subcollection: `users/{userId}/tasks`
2. Consistent querying pattern across all log types
3. Single timeline source with all activity types

---

**End of Analysis**

