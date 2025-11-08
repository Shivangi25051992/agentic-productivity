# Plan Selection UI - Zero Regression Design

## 🎯 Goal
Allow users to switch between their 3 generated meal plans while maintaining the exact same UI/UX.

## 🎨 Design Approach: Minimal, Intuitive, Zero Regression

### Current UI:
```
┌─────────────────────────────────────────┐
│  Your Plan                              │
│  Fasting & Meal Planning                │
│                                          │
│  [Fasting] [Meal Plan] ← tabs           │
│                                          │
│  Mon Tue Wed Thu Fri Sat Sun ← days     │
│                                          │
│  Saturday                    4 meals     │
│  🔥 Calories  💪 Protein  💧 Fat        │
│  ████████     ████████     ████████     │
│                                          │
│  [Meals list]                           │
│                                          │
│  [Generate Plan] [Grocery List]         │
└─────────────────────────────────────────┘
```

### Proposed UI (Minimal Addition):
```
┌─────────────────────────────────────────┐
│  Your Plan                              │
│  Fasting & Meal Planning                │
│                                          │
│  [Fasting] [Meal Plan] ← tabs           │
│                                          │
│  ┌─ Plan Selector (NEW) ────────────┐  │
│  │ 🍽️ Plan 1: High Protein  [✓]    │  │
│  │ 📅 Nov 3-9 • 28 meals • Active   │  │
│  │ [Switch Plan ▼]                   │  │
│  └───────────────────────────────────┘  │
│                                          │
│  Mon Tue Wed Thu Fri Sat Sun ← days     │
│  ...rest stays the same...              │
└─────────────────────────────────────────┘
```

## 📋 Implementation Plan

### Phase 1: Backend (Already Done ✅)
- ✅ `getMealPlans()` API exists
- ✅ Plans have `is_active` flag
- ✅ Plans stored in user subcollection

### Phase 2: Frontend (To Do)

#### Step 1: Load All Plans (Not Just Active)
**File**: `meal_planning_tab.dart`
**Change**: Load all plans for current week, not just active one

```dart
// BEFORE:
Future<void> _loadCurrentWeekPlan() async {
  final plan = await _mealPlanningApi!.getCurrentWeekPlan();
  // ... load single plan
}

// AFTER:
List<Map<String, dynamic>> _allPlans = [];
String? _selectedPlanId;

Future<void> _loadAllWeekPlans() async {
  final plans = await _mealPlanningApi!.getMealPlans(
    activeOnly: false,  // Get all plans for this week
    limit: 10
  );
  
  // Filter to current week only
  final currentWeekPlans = plans.where((plan) {
    // Check if plan is for current week
    return _isCurrentWeek(plan['week_start_date']);
  }).toList();
  
  setState(() {
    _allPlans = currentWeekPlans;
    _selectedPlanId = currentWeekPlans.firstWhere(
      (p) => p['is_active'] == true,
      orElse: () => currentWeekPlans.first
    )['id'];
    _loadPlanData(_selectedPlanId!);
  });
}
```

#### Step 2: Add Plan Selector Widget
**Location**: Above the day selector
**Design**: Collapsible dropdown (starts collapsed)

```dart
Widget _buildPlanSelector() {
  if (_allPlans.length <= 1) {
    return SizedBox.shrink(); // Hide if only 1 plan
  }
  
  final selectedPlan = _allPlans.firstWhere(
    (p) => p['id'] == _selectedPlanId,
    orElse: () => _allPlans.first
  );
  
  return Container(
    margin: EdgeInsets.all(16),
    padding: EdgeInsets.all(16),
    decoration: BoxDecoration(
      color: Colors.white,
      borderRadius: BorderRadius.circular(12),
      border: Border.all(color: Color(0xFFE5E7EB)),
    ),
    child: Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        Row(
          children: [
            Icon(Icons.restaurant_menu, color: Color(0xFF6366F1)),
            SizedBox(width: 8),
            Expanded(
              child: Text(
                _getPlanLabel(selectedPlan),
                style: TextStyle(
                  fontSize: 16,
                  fontWeight: FontWeight.w600,
                ),
              ),
            ),
            if (_allPlans.length > 1)
              TextButton(
                onPressed: _showPlanSwitcher,
                child: Text('Switch Plan'),
              ),
          ],
        ),
        SizedBox(height: 4),
        Text(
          '${_allPlans.length} plans available • ${selectedPlan['meals'].length} meals',
          style: TextStyle(
            fontSize: 12,
            color: Color(0xFF6B7280),
          ),
        ),
      ],
    ),
  );
}
```

#### Step 3: Plan Switcher Bottom Sheet
**Trigger**: Click "Switch Plan" button
**Design**: Bottom sheet with plan cards

```dart
void _showPlanSwitcher() {
  showModalBottomSheet(
    context: context,
    shape: RoundedRectangleBorder(
      borderRadius: BorderRadius.vertical(top: Radius.circular(20)),
    ),
    builder: (context) => Container(
      padding: EdgeInsets.all(24),
      child: Column(
        mainAxisSize: MainAxisSize.min,
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Text(
            'Choose Your Meal Plan',
            style: TextStyle(
              fontSize: 20,
              fontWeight: FontWeight.bold,
            ),
          ),
          SizedBox(height: 8),
          Text(
            'You have ${_allPlans.length} plans for this week',
            style: TextStyle(
              fontSize: 14,
              color: Color(0xFF6B7280),
            ),
          ),
          SizedBox(height: 16),
          ...\_allPlans.map((plan) => _buildPlanCard(plan)).toList(),
        ],
      ),
    ),
  );
}

Widget _buildPlanCard(Map<String, dynamic> plan) {
  final isSelected = plan['id'] == _selectedPlanId;
  final dietaryPrefs = (plan['dietary_preferences'] as List?)
      ?.map((p) => p.toString())
      .join(', ') ?? 'Balanced';
  
  return GestureDetector(
    onTap: () {
      _switchToPlan(plan['id']);
      Navigator.pop(context);
    },
    child: Container(
      margin: EdgeInsets.only(bottom: 12),
      padding: EdgeInsets.all(16),
      decoration: BoxDecoration(
        color: isSelected ? Color(0xFF6366F1).withOpacity(0.1) : Colors.white,
        borderRadius: BorderRadius.circular(12),
        border: Border.all(
          color: isSelected ? Color(0xFF6366F1) : Color(0xFFE5E7EB),
          width: isSelected ? 2 : 1,
        ),
      ),
      child: Row(
        children: [
          Container(
            width: 48,
            height: 48,
            decoration: BoxDecoration(
              color: Color(0xFF6366F1).withOpacity(0.1),
              borderRadius: BorderRadius.circular(12),
            ),
            child: Icon(
              Icons.restaurant_menu,
              color: Color(0xFF6366F1),
            ),
          ),
          SizedBox(width: 12),
          Expanded(
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                Row(
                  children: [
                    Text(
                      'Plan ${_allPlans.indexOf(plan) + 1}',
                      style: TextStyle(
                        fontSize: 16,
                        fontWeight: FontWeight.w600,
                      ),
                    ),
                    if (isSelected) ...[
                      SizedBox(width: 8),
                      Container(
                        padding: EdgeInsets.symmetric(horizontal: 8, vertical: 2),
                        decoration: BoxDecoration(
                          color: Color(0xFF10B981),
                          borderRadius: BorderRadius.circular(4),
                        ),
                        child: Text(
                          'Active',
                          style: TextStyle(
                            fontSize: 10,
                            color: Colors.white,
                            fontWeight: FontWeight.w600,
                          ),
                        ),
                      ),
                    ],
                  ],
                ),
                SizedBox(height: 4),
                Text(
                  dietaryPrefs,
                  style: TextStyle(
                    fontSize: 12,
                    color: Color(0xFF6B7280),
                  ),
                ),
                Text(
                  '${plan['meals']?.length ?? 0} meals • ${_formatDate(plan['created_at'])}',
                  style: TextStyle(
                    fontSize: 11,
                    color: Color(0xFF9CA3AF),
                  ),
                ),
              ],
            ),
          ),
          if (isSelected)
            Icon(
              Icons.check_circle,
              color: Color(0xFF10B981),
            ),
        ],
      ),
    ),
  );
}
```

#### Step 4: Switch Plan Logic
**Function**: Update state and reload meals

```dart
void _switchToPlan(String planId) {
  setState(() {
    _selectedPlanId = planId;
    _isLoading = true;
  });
  
  _loadPlanData(planId);
  
  // Optional: Mark as active in backend
  _mealPlanningApi!.setActivePlan(planId);
}

Future<void> _loadPlanData(String planId) async {
  final plan = _allPlans.firstWhere((p) => p['id'] == planId);
  
  // Parse meals (existing logic)
  final parsedMeals = _parseMeals(plan);
  final calculatedTotals = _calculateDailyTotals(plan);
  
  setState(() {
    _currentPlanId = planId;
    _weekMeals = parsedMeals;
    _dailyTotals = calculatedTotals;
    _isLoading = false;
  });
}
```

## 🎯 Zero Regression Checklist

### What Stays the Same:
- ✅ Day selector (Mon-Sun)
- ✅ Daily summary card (Calories, Protein, Fat)
- ✅ Meal list display
- ✅ Recipe detail navigation
- ✅ Generate Plan button
- ✅ Grocery List button
- ✅ All existing functionality

### What's New (Additive Only):
- ✅ Plan selector (only shows if multiple plans exist)
- ✅ "Switch Plan" button
- ✅ Plan switcher bottom sheet
- ✅ Visual indicator for active plan

### Edge Cases Handled:
- ✅ Only 1 plan: Selector hidden (no UI change)
- ✅ No plans: Shows empty state (existing behavior)
- ✅ Loading state: Shows spinner (existing behavior)
- ✅ Error state: Shows error message (existing behavior)

## 📊 User Flow

### Scenario 1: User with 1 Plan (Most Common)
```
1. Open Meal Planning tab
2. See their plan (NO CHANGE - selector hidden)
3. Use app normally
```
**Impact**: ZERO - UI looks exactly the same

### Scenario 2: User with 2-3 Plans
```
1. Open Meal Planning tab
2. See small plan selector at top
3. Click "Switch Plan"
4. See bottom sheet with all plans
5. Tap a different plan
6. Meals update instantly
7. Continue using app
```
**Impact**: Minimal - One small widget added, optional interaction

### Scenario 3: Generate 4th Plan (Hit Limit)
```
1. Click "Generate Plan"
2. See error: "You've reached your limit..."
3. See "Upgrade to Premium" button
4. Can still switch between existing 3 plans
```
**Impact**: Clear upgrade path

## 🎨 Visual Design

### Plan Selector (Collapsed):
```
┌────────────────────────────────────┐
│ 🍽️ Plan 1: High Protein  [Switch]│
│ 3 plans available • 28 meals       │
└────────────────────────────────────┘
```

### Plan Switcher (Bottom Sheet):
```
┌────────────────────────────────────┐
│ Choose Your Meal Plan              │
│ You have 3 plans for this week     │
│                                    │
│ ┌──────────────────────────────┐  │
│ │ 🍽️  Plan 1: High Protein    │  │
│ │     28 meals • Nov 8  [✓]   │  │
│ └──────────────────────────────┘  │
│                                    │
│ ┌──────────────────────────────┐  │
│ │ 🍽️  Plan 2: Keto            │  │
│ │     28 meals • Nov 7        │  │
│ └──────────────────────────────┘  │
│                                    │
│ ┌──────────────────────────────┐  │
│ │ 🍽️  Plan 3: Vegetarian      │  │
│ │     28 meals • Nov 6        │  │
│ └──────────────────────────────┘  │
└────────────────────────────────────┘
```

## 🚀 Implementation Steps (One Go)

1. ✅ Add state variables (`_allPlans`, `_selectedPlanId`)
2. ✅ Update `_loadCurrentWeekPlan()` to `_loadAllWeekPlans()`
3. ✅ Add `_buildPlanSelector()` widget
4. ✅ Add `_showPlanSwitcher()` bottom sheet
5. ✅ Add `_buildPlanCard()` widget
6. ✅ Add `_switchToPlan()` logic
7. ✅ Add `_loadPlanData()` helper
8. ✅ Insert `_buildPlanSelector()` in build tree (above day selector)
9. ✅ Test with 1 plan (selector hidden)
10. ✅ Test with 3 plans (selector visible, switching works)

## 💡 Key Benefits

1. **Zero Regression**: Existing UI unchanged when user has 1 plan
2. **Intuitive**: "Switch Plan" is clear and discoverable
3. **Minimal**: Only adds UI when needed (2+ plans)
4. **Fast**: No API calls on switch (data already loaded)
5. **Beautiful**: Matches existing design language
6. **Scalable**: Works with 1-10 plans (though limit is 3)

## 🧪 Testing Checklist

- [ ] User with 0 plans: Shows empty state
- [ ] User with 1 plan: Selector hidden, works normally
- [ ] User with 2 plans: Selector shows, can switch
- [ ] User with 3 plans: Selector shows, can switch
- [ ] Switch plan: Meals update correctly
- [ ] Switch plan: Nutrition totals update
- [ ] Switch plan: Active indicator shows
- [ ] Generate 4th plan: Shows upgrade message
- [ ] All existing features still work

---

**Ready to implement in one go with zero regression!** 🚀


