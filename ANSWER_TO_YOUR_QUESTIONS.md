# ✅ ANSWERS TO YOUR QUESTIONS

## 📋 Your Questions:

1. **Which DB are you storing meals, tasks, events, workouts?**
2. **What table names?**
3. **How are you displaying in timeline view?**
4. **What is the filter criteria?**

---

## 🗄️ COMPLETE ANSWERS

### 1️⃣ MEALS

**Database**: Firestore  
**Collection**: `users/{userId}/fitness_logs` (Subcollection)  
**Table Name**: `fitness_logs` (under each user)  
**Identifier**: `log_type: "meal"`

**Fields Stored**:
```json
{
  "log_id": "abc-123",
  "user_id": "user-xyz",
  "log_type": "meal",
  "content": "2 eggs, 1 slice toast",
  "calories": 220,
  "timestamp": "2025-11-03T10:30:00Z",
  "ai_parsed_data": {
    "meal_type": "breakfast",
    "items": ["2 eggs", "1 slice toast"],
    "protein_g": 18.5,
    "carbs_g": 15.2,
    "fat_g": 12.0
  }
}
```

**Timeline Display**: ✅ **YES** - Shows in timeline  
**Filter Criteria**: `type == 'meal'` AND sorted by `timestamp`

---

### 2️⃣ WORKOUTS

**Database**: Firestore  
**Collection**: `users/{userId}/fitness_logs` (Same as meals)  
**Table Name**: `fitness_logs`  
**Identifier**: `log_type: "workout"`

**Fields Stored**:
```json
{
  "log_id": "def-456",
  "user_id": "user-xyz",
  "log_type": "workout",
  "content": "30 min run",
  "calories": 300,
  "timestamp": "2025-11-03T18:00:00Z",
  "ai_parsed_data": {
    "activity_type": "running",
    "duration_minutes": 30,
    "intensity": "moderate"
  }
}
```

**Timeline Display**: ❌ **NO** - Not currently shown  
**Reason**: Timeline filter only shows `type == 'meal'`  
**Fix Needed**: Change filter to include workouts

---

### 3️⃣ TASKS

**Database**: Firestore  
**Collection**: `tasks` (Flat collection - NOT subcollection)  
**Table Name**: `tasks`  
**Identifier**: `task_id`

**Fields Stored**:
```json
{
  "task_id": "task-789",
  "user_id": "user-xyz",
  "title": "Remind me to workout at 7 pm",
  "description": "",
  "due_date": null,
  "priority": "medium",
  "status": "pending",
  "created_at": "2025-11-03T10:00:00Z"
}
```

**Timeline Display**: ❌ **NO** - Not in timeline at all  
**Reason**: Tasks stored separately, not fetched in timeline data  
**Fix Needed**: 
1. Fetch tasks in `DashboardProvider`
2. Merge into `activities` array
3. Update timeline filter

---

### 4️⃣ EVENTS

**Database**: N/A  
**Collection**: ❌ **NOT IMPLEMENTED**  
**Status**: No event tracking currently exists

---

## 🖼️ TIMELINE VIEW BREAKDOWN

### **File**: `flutter_app/lib/screens/meals/timeline_view_screen.dart`

### **How It Works**:

```dart
// Step 1: Fetch data from backend
DashboardProvider.fetchDailyStats(auth)
  ↓
// Step 2: Backend queries Firestore
GET /fitness/logs?start={date}&end={date}
  ↓
// Step 3: Firestore query
users/{userId}/fitness_logs
  WHERE timestamp >= start AND timestamp <= end
  ORDER BY timestamp DESC
  ↓
// Step 4: Returns meals + workouts (but workouts filtered out later)
  ↓
// Step 5: Frontend filters
final activities = dashboardProvider.stats.activities
    .where((a) => a.type == 'meal')  // ← ONLY MEALS!
    .toList()
  ..sort((a, b) => a.timestamp.compareTo(b.timestamp));
  ↓
// Step 6: Display each meal
_buildTimelineItem(activity)
```

### **Filter Criteria (Current)**:

```dart
// Line 53-56 in timeline_view_screen.dart
.where((a) => a.type == 'meal')  // ← ONLY shows meals
.sort((a, b) => a.timestamp.compareTo(b.timestamp))  // ← Chronological
```

**What's Shown**:
- ✅ Meals (breakfast, lunch, dinner, snack)
- ✅ Timestamp (e.g., "5:29 PM")
- ✅ Calories
- ✅ Macros (protein, carbs, fat)

**What's Hidden**:
- ❌ Workouts
- ❌ Tasks
- ❌ Water logs
- ❌ Supplement logs

---

## 🐛 ISSUES FOUND

### **Issue 1: `/insights` 500 Error**
**Status**: ✅ **FIXED** (backend restarted with fix)

**Root Cause**: 
```python
# app/main.py line 162
goals = profile.daily_goals  # ❌ profile is dict, not object
```

**Fix Applied**:
```python
goals = profile.get("daily_goals", {})  # ✅ Correct dict access
```

---

### **Issue 2: Tasks Not Showing in Chat Response**
**Screenshot shows**: "I'll remind you at 6 pm" but task not visible

**Root Cause**: 
1. Task IS being created in database ✅
2. But NOT displayed in dashboard/timeline ❌

**Why?**
- Dashboard filters tasks by `start_due` date
- Tasks without `due_date` are excluded
- Query: `GET /tasks/?start_due=2025-11-03` excludes tasks with `due_date=null`

**Fix Options**:
- **Option A**: Remove date filter for dashboard
- **Option B**: Parse due_date from "at 6 pm" → set `due_date: "2025-11-03T18:00:00Z"`
- **Option C**: Show ALL pending tasks regardless of due_date

---

### **Issue 3: Timeline Times Showing Incorrectly**
**Status**: ✅ **FIXED**

**Changed**: `DateFormat('HH:mm')` → `DateFormat('h:mm a')`  
**Result**: "17:29" → "5:29 PM"

---

### **Issue 4: No Activity Logs in Timeline**
**Symptoms**: Console shows "✅ Fetched 2 fitness logs" but timeline empty

**Possible Causes**:
1. Data format mismatch
2. `ai_parsed_data` not parsed correctly
3. Frontend expecting different field structure

**Need to Debug**: Check what's in `dashboardProvider.stats.activities`

---

### **Issue 5: setState() Errors**
**Status**: ✅ **FIXED**

**Applied**:
1. Added `mounted` checks in `mobile_first_home_screen.dart`
2. Wrapped `notifyListeners()` in `SchedulerBinding.addPostFrameCallback()` in `profile_provider.dart`

---

## 📊 SUMMARY TABLE

| Type | Collection Path | Stored? | Timeline? | Dashboard? | Issue |
|------|----------------|---------|-----------|------------|-------|
| **Meals** | `users/{userId}/fitness_logs` | ✅ YES | ✅ YES | ✅ YES | None |
| **Workouts** | `users/{userId}/fitness_logs` | ✅ YES | ❌ NO | ⚠️ Partial | Filter excludes |
| **Tasks** | `tasks/{taskId}` | ✅ YES | ❌ NO | ⚠️ Partial | Date filter excludes |
| **Events** | N/A | ❌ NO | ❌ NO | ❌ NO | Not implemented |
| **Water** | `users/{userId}/fitness_logs` | ✅ YES | ❌ NO | ❌ NO | Not displayed |
| **Supplements** | `users/{userId}/fitness_logs` | ✅ YES | ❌ NO | ❌ NO | Not displayed |

---

## 🎯 NEXT STEPS

### **To Show Tasks in Dashboard**:

**Option A**: Remove date filter (Quick fix)
```dart
// dashboard_provider.dart line 153
final taskModels = await apiService.getTasks();  // No date filter
```

**Option B**: Parse due_date from natural language (Better UX)
```python
# app/main.py - Parse "at 7 pm" → due_date
if "at" in text or "pm" in text or "am" in text:
    due_date = parse_time_from_text(text)  # Extract time
```

### **To Show Workouts in Timeline**:
```dart
// timeline_view_screen.dart line 53
.where((a) => a.type == 'meal' || a.type == 'workout')
```

### **To Show Tasks in Timeline**:
1. Fetch tasks in `DashboardProvider.fetchDailyStats()`
2. Add to `activities` array
3. Update timeline filter

---

## 📝 DETAILED DOCUMENTATION

See `DATA_FLOW_BREAKDOWN.md` for complete technical breakdown with:
- Full database schema
- Query patterns
- Code references
- Filter logic
- Recommended fixes

---

**Backend Status**: ✅ Running on http://localhost:8000  
**Frontend Status**: ✅ Running on http://localhost:9090  
**Fixes Applied**: ✅ `/insights` error, timeline format, setState() errors

