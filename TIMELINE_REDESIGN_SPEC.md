# 🎯 ROBUST TIMELINE - SALESFORCE-STYLE REDESIGN

## 📋 REQUIREMENTS FROM SCREENSHOTS

### **Key Features Observed**:

1. **Unified Activity Feed**
   - ✅ Tasks (green icon)
   - ✅ Events (purple calendar icon)
   - ✅ All activities in single timeline

2. **Smart Grouping**
   - "Upcoming & Overdue" section
   - Date-based sections: "October 2025", "Last Month"
   - Chronological within each section

3. **Filter Options**
   - Filter by time: "All time"
   - Filter by activity type: "All activities"
   - Filter by type: "All types"
   - Settings icon for advanced filters

4. **Expandable Details**
   - Collapsed view: Title + basic info
   - Expanded view: Full details (Start, End, Description)
   - Chevron to expand/collapse

5. **Pagination**
   - "View More" button to load additional items
   - Prevents overwhelming UI with too many items

6. **Visual Hierarchy**
   - Icons for activity types (color-coded)
   - Vertical timeline connector
   - Date/time on right side
   - Dropdown menu for actions

---

## 🏗️ ARCHITECTURE DESIGN

### **Backend: Unified Timeline API**

**New Endpoint**: `GET /timeline`

**Query Parameters**:
- `start_date` (optional): Filter from date
- `end_date` (optional): Filter to date
- `types` (optional): Comma-separated list (meal,workout,task,event)
- `limit` (default: 50): Pagination limit
- `offset` (default: 0): Pagination offset

**Response Format**:
```json
{
  "activities": [
    {
      "id": "uuid",
      "type": "meal",
      "title": "Breakfast - 2 eggs, toast",
      "timestamp": "2025-11-03T08:30:00Z",
      "icon": "meal",
      "color": "green",
      "status": "completed",
      "details": {
        "meal_type": "breakfast",
        "calories": 220,
        "protein_g": 18.5,
        "carbs_g": 15.2,
        "fat_g": 12.0,
        "items": ["2 eggs", "1 slice toast"]
      }
    },
    {
      "id": "uuid",
      "type": "workout",
      "title": "30 min run",
      "timestamp": "2025-11-03T18:00:00Z",
      "icon": "workout",
      "color": "blue",
      "status": "completed",
      "details": {
        "activity_type": "running",
        "duration_minutes": 30,
        "calories_burned": 300,
        "intensity": "moderate"
      }
    },
    {
      "id": "uuid",
      "type": "task",
      "title": "Remind me to workout",
      "timestamp": "2025-11-03T18:00:00Z",
      "icon": "task",
      "color": "orange",
      "status": "pending",
      "due_date": "2025-11-03T18:00:00Z",
      "priority": "medium",
      "details": {
        "description": "",
        "assignee": "You"
      }
    },
    {
      "id": "uuid",
      "type": "event",
      "title": "Team Meeting",
      "timestamp": "2025-11-03T14:00:00Z",
      "icon": "event",
      "color": "purple",
      "status": "upcoming",
      "details": {
        "start_time": "2025-11-03T14:00:00Z",
        "end_time": "2025-11-03T15:00:00Z",
        "location": "Conference Room A",
        "attendees": ["John", "Jane"]
      }
    }
  ],
  "total_count": 150,
  "has_more": true,
  "next_offset": 50
}
```

---

### **Frontend: Timeline Architecture**

#### **1. TimelineProvider** (State Management)

**File**: `flutter_app/lib/providers/timeline_provider.dart`

**Responsibilities**:
- Fetch unified timeline data
- Manage filter state
- Handle pagination
- Group activities by date
- Expand/collapse state

**State**:
```dart
class TimelineProvider extends ChangeNotifier {
  List<TimelineActivity> _activities = [];
  Set<String> _selectedTypes = {'meal', 'workout', 'task', 'event'};
  DateTime? _startDate;
  DateTime? _endDate;
  bool _isLoading = false;
  bool _hasMore = true;
  int _offset = 0;
  Map<String, bool> _expandedStates = {};
  
  // Getters
  List<TimelineActivity> get activities => _activities;
  Map<String, List<TimelineActivity>> get groupedActivities => _groupByDate();
  
  // Methods
  Future<void> fetchTimeline({bool loadMore = false});
  void toggleFilter(String type);
  void setDateRange(DateTime? start, DateTime? end);
  void toggleExpanded(String activityId);
  void refresh();
}
```

#### **2. Timeline Screen** (UI)

**File**: `flutter_app/lib/screens/timeline/timeline_screen.dart`

**Layout**:
```
┌─────────────────────────────────────┐
│  Timeline                      ⚙️   │  ← AppBar
├─────────────────────────────────────┤
│  🍽️ Meals  🏃 Workouts  ✅ Tasks   │  ← Filter Chips
│  📅 Events  🔄 Refresh              │
├─────────────────────────────────────┤
│  📍 Upcoming & Overdue              │  ← Section Header
│  ┌───────────────────────────────┐ │
│  │ ✅ Remind me to workout   6PM │ │  ← Task Item
│  └───────────────────────────────┘ │
├─────────────────────────────────────┤
│  📅 Today - November 3, 2025        │  ← Date Section
│  ┌───────────────────────────────┐ │
│  │ 🍽️ Breakfast          8:30 AM │ │  ← Meal Item
│  │ 📋 2 eggs, toast               │ │
│  │ 220 cal • 18g protein          │ │
│  └───────────────────────────────┘ │
│  ┌───────────────────────────────┐ │
│  │ 🏃 30 min run          6:00 PM │ │  ← Workout Item
│  │ 300 cal burned                 │ │
│  └───────────────────────────────┘ │
├─────────────────────────────────────┤
│  📅 Yesterday - November 2          │  ← Previous Date
│  ┌───────────────────────────────┐ │
│  │ ...                            │ │
│  └───────────────────────────────┘ │
├─────────────────────────────────────┤
│         [View More]                 │  ← Pagination
└─────────────────────────────────────┘
```

---

## 📁 FILE STRUCTURE

```
flutter_app/lib/
├── models/
│   └── timeline_activity.dart          # Unified activity model
├── providers/
│   └── timeline_provider.dart          # Timeline state management
├── screens/
│   └── timeline/
│       ├── timeline_screen.dart        # Main timeline screen
│       ├── widgets/
│       │   ├── timeline_filter_bar.dart      # Filter chips
│       │   ├── timeline_section_header.dart  # Date headers
│       │   ├── timeline_item.dart            # Base activity item
│       │   ├── meal_timeline_item.dart       # Meal-specific UI
│       │   ├── workout_timeline_item.dart    # Workout-specific UI
│       │   ├── task_timeline_item.dart       # Task-specific UI
│       │   └── event_timeline_item.dart      # Event-specific UI
│       └── timeline_detail_sheet.dart  # Bottom sheet for details
└── services/
    └── timeline_service.dart           # API calls

app/
├── routers/
│   └── timeline.py                     # New timeline router
└── services/
    └── timeline_service.py             # Timeline business logic
```

---

## 🎨 UI COMPONENTS BREAKDOWN

### **1. Filter Bar**

```dart
class TimelineFilterBar extends StatelessWidget {
  final Set<String> selectedTypes;
  final Function(String) onToggle;
  
  @override
  Widget build(BuildContext context) {
    return SingleChildScrollView(
      scrollDirection: Axis.horizontal,
      child: Row(
        children: [
          FilterChip(
            label: Text('🍽️ Meals'),
            selected: selectedTypes.contains('meal'),
            onSelected: (_) => onToggle('meal'),
          ),
          FilterChip(
            label: Text('🏃 Workouts'),
            selected: selectedTypes.contains('workout'),
            onSelected: (_) => onToggle('workout'),
          ),
          FilterChip(
            label: Text('✅ Tasks'),
            selected: selectedTypes.contains('task'),
            onSelected: (_) => onToggle('task'),
          ),
          FilterChip(
            label: Text('📅 Events'),
            selected: selectedTypes.contains('event'),
            onSelected: (_) => onToggle('event'),
          ),
        ],
      ),
    );
  }
}
```

### **2. Section Header**

```dart
class TimelineSectionHeader extends StatelessWidget {
  final String title;
  final int count;
  
  @override
  Widget build(BuildContext context) {
    return Container(
      padding: EdgeInsets.all(16),
      color: Colors.grey[100],
      child: Row(
        mainAxisAlignment: MainAxisAlignment.spaceBetween,
        children: [
          Text(
            title,
            style: TextStyle(
              fontSize: 16,
              fontWeight: FontWeight.bold,
            ),
          ),
          Text(
            '$count items',
            style: TextStyle(color: Colors.grey),
          ),
        ],
      ),
    );
  }
}
```

### **3. Timeline Item (Base)**

```dart
class TimelineItem extends StatelessWidget {
  final TimelineActivity activity;
  final bool isExpanded;
  final VoidCallback onTap;
  
  @override
  Widget build(BuildContext context) {
    return InkWell(
      onTap: onTap,
      child: Container(
        padding: EdgeInsets.all(16),
        child: Row(
          children: [
            // Icon
            _buildIcon(),
            SizedBox(width: 12),
            // Content
            Expanded(
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  Text(
                    activity.title,
                    style: TextStyle(
                      fontSize: 16,
                      fontWeight: FontWeight.w600,
                    ),
                  ),
                  if (isExpanded) _buildExpandedDetails(),
                  if (!isExpanded) _buildCollapsedSummary(),
                ],
              ),
            ),
            // Time + Chevron
            Column(
              crossAxisAlignment: CrossAxisAlignment.end,
              children: [
                Text(
                  _formatTime(activity.timestamp),
                  style: TextStyle(color: Colors.grey),
                ),
                Icon(
                  isExpanded ? Icons.expand_less : Icons.expand_more,
                  color: Colors.grey,
                ),
              ],
            ),
          ],
        ),
      ),
    );
  }
}
```

---

## 🔄 DATA FLOW

### **1. Initial Load**

```
User opens Timeline Screen
  ↓
TimelineProvider.fetchTimeline()
  ↓
API: GET /timeline?types=meal,workout,task,event&limit=50
  ↓
Backend: Fetch from multiple collections
  - users/{userId}/fitness_logs (meals, workouts)
  - tasks (tasks)
  - events (events - if implemented)
  ↓
Backend: Merge + Sort by timestamp
  ↓
Backend: Return unified list
  ↓
Frontend: Group by date sections
  ↓
UI: Render grouped timeline
```

### **2. Filter Change**

```
User taps "Meals" filter chip
  ↓
TimelineProvider.toggleFilter('meal')
  ↓
Update selectedTypes set
  ↓
Re-fetch with new filters
  ↓
API: GET /timeline?types=workout,task,event&limit=50
  ↓
UI: Update display
```

### **3. Expand Item**

```
User taps timeline item
  ↓
TimelineProvider.toggleExpanded(activityId)
  ↓
Update _expandedStates map
  ↓
notifyListeners()
  ↓
UI: Rebuild with expanded details
```

### **4. Load More**

```
User taps "View More"
  ↓
TimelineProvider.fetchTimeline(loadMore: true)
  ↓
API: GET /timeline?offset=50&limit=50
  ↓
Append to existing activities
  ↓
UI: Show additional items
```

---

## 📊 GROUPING LOGIC

### **Date Sections**:

```dart
Map<String, List<TimelineActivity>> _groupByDate() {
  final now = DateTime.now();
  final today = DateTime(now.year, now.month, now.day);
  final yesterday = today.subtract(Duration(days: 1));
  
  Map<String, List<TimelineActivity>> grouped = {
    'Upcoming & Overdue': [],
    'Today': [],
    'Yesterday': [],
  };
  
  for (var activity in _activities) {
    final activityDate = DateTime(
      activity.timestamp.year,
      activity.timestamp.month,
      activity.timestamp.day,
    );
    
    // Overdue tasks
    if (activity.type == 'task' && 
        activity.status == 'pending' && 
        activityDate.isBefore(today)) {
      grouped['Upcoming & Overdue']!.add(activity);
    }
    // Today
    else if (activityDate == today) {
      grouped['Today']!.add(activity);
    }
    // Yesterday
    else if (activityDate == yesterday) {
      grouped['Yesterday']!.add(activity);
    }
    // Other dates
    else {
      final key = DateFormat('MMMM d, yyyy').format(activityDate);
      grouped.putIfAbsent(key, () => []);
      grouped[key]!.add(activity);
    }
  }
  
  // Remove empty sections
  grouped.removeWhere((key, value) => value.isEmpty);
  
  return grouped;
}
```

---

## 🎯 IMPLEMENTATION PLAN

### **Phase 1: Backend** (30 min)
1. Create `app/routers/timeline.py`
2. Create `app/services/timeline_service.py`
3. Implement unified timeline endpoint
4. Test with Postman

### **Phase 2: Models** (15 min)
1. Create `timeline_activity.dart` model
2. Add serialization/deserialization

### **Phase 3: Provider** (20 min)
1. Create `timeline_provider.dart`
2. Implement fetch, filter, pagination logic
3. Add grouping logic

### **Phase 4: UI Components** (45 min)
1. Create filter bar widget
2. Create section header widget
3. Create base timeline item widget
4. Create type-specific item widgets

### **Phase 5: Main Screen** (30 min)
1. Create timeline screen
2. Wire up provider
3. Implement scrolling + pagination

### **Phase 6: Testing** (20 min)
1. Test all activity types
2. Test filters
3. Test pagination
4. Test expand/collapse

**Total Estimated Time**: ~2.5 hours

---

## ✅ ACCEPTANCE CRITERIA

- [ ] Timeline shows meals, workouts, tasks, events
- [ ] Filter chips work (can toggle each type)
- [ ] Activities grouped by date sections
- [ ] Items can expand/collapse to show details
- [ ] "View More" loads additional items
- [ ] Smooth scrolling performance
- [ ] Proper timezone handling
- [ ] Empty states for no activities
- [ ] Loading states during fetch
- [ ] Error handling for API failures

---

**Ready to implement?** This will be a complete, production-ready timeline system.

