# 🚀 Sprint Plan - Selected Priorities
**Date**: November 2, 2025  
**Status**: Ready to Execute

---

## 📋 SELECTED ITEMS

### P0 - Critical (2 items)
- ✅ **P0-2**: Timezone Issue (3-4h)
- ✅ **P0-5**: Workout Calories Not Reflected (3-4h)

### P1 - High Priority (5 items)
- ✅ **P1-1**: Sleep Tracking (6-8h)
- ✅ **P1-2**: Water Tracking (4-6h)
- ✅ **P1-3**: Intermittent Fasting Support (8-10h)
- ✅ **P1-4**: Goal Timeline & Milestones (10-12h)
- ✅ **P1-7**: Multivitamin/Supplement Tracking (6-8h)

### P2 - Medium Priority (2 items)
- ✅ **P2-5**: Default User Time Detection (2h)
- ✅ **P2-6**: Profile Update Capability (4-6h)

**Total**: 9 items | **Effort**: ~46-62 hours | **Timeline**: 1-2 weeks

---

## 🎯 EXECUTION ORDER (Optimized)

### Phase 1: Foundation (Day 1-2) - ~9-12 hours
**Goal**: Fix core issues and enable other features

1. **P0-2: Timezone Detection** (3-4h) 🌍
   - Detect user timezone on frontend
   - Store in user profile
   - Use for all time-based operations
   - **Enables**: Correct meal classification

2. **P2-5: Default User Time Detection** (2h) ⏰
   - Auto-detect current time
   - Set default values
   - **Note**: Overlaps with P0-2, do together

3. **P2-6: Profile Update Capability** (4-6h) ⚙️
   - Add profile edit screen
   - Update API endpoints
   - **Enables**: Users to change settings

### Phase 2: Tracking Features (Day 3-5) - ~19-26 hours
**Goal**: Implement new tracking capabilities

4. **P1-2: Water Tracking** (4-6h) 💧
   - Quick win, simple implementation
   - Add to chat parsing
   - Dashboard widget

5. **P1-7: Supplement Tracking** (6-8h) 💊
   - Similar to water tracking
   - Add reminders

6. **P1-1: Sleep Tracking** (6-8h) 😴
   - Chat parsing for sleep logs
   - Dashboard widget
   - Quality trends

7. **P0-5: Workout Calories Display** (3-4h) 🏃
   - Add workouts to timeline
   - Adjust calorie budget

### Phase 3: Advanced Features (Day 6-10) - ~18-24 hours
**Goal**: Implement differentiators

8. **P1-3: Intermittent Fasting** (8-10h) 🕐
   - Profile type
   - Fasting timer
   - Notifications

9. **P1-4: Goal Timeline & Milestones** (10-12h) 📅
   - Calculate timeline
   - Track milestones
   - Adjust predictions

---

## 📅 DETAILED SCHEDULE

### Day 1 (Nov 3): Foundation Setup
**Hours**: 5-6h

**Morning** (3-4h):
- [ ] P0-2: Implement timezone detection
  - Frontend: Detect timezone
  - Backend: Store in profile
  - Update meal classification logic

**Afternoon** (2h):
- [ ] P2-5: Auto time detection
  - Integrate with P0-2
  - Set defaults

**Deliverable**: Timezone working correctly

---

### Day 2 (Nov 4): Profile & Quick Wins
**Hours**: 8-12h

**Morning** (4-6h):
- [ ] P2-6: Profile update capability
  - Create edit profile screen
  - Update API endpoints
  - Test changes persist

**Afternoon** (4-6h):
- [ ] P1-2: Water tracking
  - Add water entity extraction
  - Create water logs collection
  - Dashboard widget

**Deliverable**: Profile editable, water tracking live

---

### Day 3 (Nov 5): More Tracking
**Hours**: 9-12h

**Morning** (6-8h):
- [ ] P1-7: Supplement tracking
  - Entity extraction
  - Supplement schedule
  - Reminders

**Afternoon** (3-4h):
- [ ] P0-5: Workout calories display
  - Add workouts to timeline
  - Calculate calories burned
  - Adjust available calories

**Deliverable**: Supplements & workouts visible

---

### Day 4 (Nov 6): Sleep Tracking
**Hours**: 6-8h

**All Day**:
- [ ] P1-1: Sleep tracking
  - Sleep entity extraction
  - Sleep logs collection
  - Dashboard widget
  - Quality indicators

**Deliverable**: Sleep tracking complete

---

### Day 5-7 (Nov 7-9): Intermittent Fasting
**Hours**: 8-10h

**Spread over 3 days**:
- [ ] P1-3: Intermittent fasting
  - Add IF profile option
  - Fasting timer widget
  - Eating window logic
  - Notifications
  - Streak tracking

**Deliverable**: IF support complete

---

### Day 8-10 (Nov 10-12): Goal Timeline
**Hours**: 10-12h

**Spread over 3 days**:
- [ ] P1-4: Goal timeline & milestones
  - Calculate expected timeline
  - Weekly milestones
  - Progress tracking
  - Adjustment logic
  - Celebration UI

**Deliverable**: Timeline & milestones live

---

## 🔧 IMPLEMENTATION DETAILS

### P0-2 & P2-5: Timezone Detection

**Frontend** (`flutter_app/lib/services/timezone_service.dart`):
```dart
class TimezoneService {
  static String getUserTimezone() {
    // Get user's timezone
    return DateTime.now().timeZoneName;
  }
  
  static String getIANATimezone() {
    // Use intl package
    return Intl.getCurrentTimeZone();
  }
}
```

**Backend** (`app/services/timezone_service.py`):
```python
from datetime import datetime
import pytz

def convert_to_user_timezone(utc_time, user_timezone):
    """Convert UTC time to user's timezone"""
    tz = pytz.timezone(user_timezone)
    return utc_time.astimezone(tz)

def get_user_local_time(user_id):
    """Get current time in user's timezone"""
    profile = get_user_profile(user_id)
    tz = pytz.timezone(profile.get('timezone', 'UTC'))
    return datetime.now(tz)
```

**Update Profile Schema**:
```python
{
  "timezone": "America/New_York",  # IANA timezone
  "timezone_offset": -5,  # Hours from UTC
  "auto_detected": true
}
```

---

### P2-6: Profile Update

**Frontend** (`flutter_app/lib/screens/profile/edit_profile_screen.dart`):
```dart
class EditProfileScreen extends StatefulWidget {
  // Form with all profile fields
  // Save button calls API
}
```

**Backend** (`app/routers/profile.py`):
```python
@router.put("/me")
async def update_profile(
    profile_update: ProfileUpdate,
    current_user: User = Depends(get_current_user)
):
    # Update user profile
    # Validate changes
    # Return updated profile
```

---

### P1-2: Water Tracking

**Entity Extraction**:
```python
# Add to system prompt
"If user mentions water/drinks:
- Extract quantity (glasses, liters, ml)
- Convert to standard unit (ml)
- Log as water intake"
```

**Dashboard Widget**:
```dart
class WaterWidget extends StatelessWidget {
  // Show 8 glass icons
  // Fill based on intake
  // Progress percentage
}
```

---

### P1-7: Supplement Tracking

**Similar to water, but with**:
- Supplement name
- Dosage
- Time of day
- Reminder notifications

---

### P1-1: Sleep Tracking

**Entity Extraction**:
```python
# Patterns:
"slept 7 hours"
"woke up at 6am, slept at 11pm"
"good sleep last night"
```

**Dashboard Widget**:
```dart
class SleepWidget extends StatelessWidget {
  // Show hours slept
  // Sleep quality indicator
  // Weekly trend
}
```

---

### P0-5: Workout Display

**Timeline Integration**:
```dart
// Add workout items to timeline
if (item.category == 'workout') {
  return WorkoutCard(
    activity: item.data['activity'],
    duration: item.data['duration'],
    caloriesBurned: item.data['calories_burned'],
  );
}
```

**Calorie Adjustment**:
```dart
// Available calories = Target + Burned - Consumed
final availableCalories = 
  targetCalories + 
  totalCaloriesBurned - 
  totalCaloriesConsumed;
```

---

### P1-3: Intermittent Fasting

**Profile Type**:
```python
{
  "fasting_type": "16:8",  # or "18:6", "20:4", "OMAD"
  "eating_window_start": "12:00",
  "eating_window_end": "20:00",
  "fasting_start": "20:00",
  "current_streak": 5
}
```

**Timer Widget**:
```dart
class FastingTimerWidget extends StatelessWidget {
  // Circular progress
  // Time remaining
  // "Fasting" or "Eating Window"
  // Streak counter
}
```

---

### P1-4: Goal Timeline

**Calculation**:
```python
def calculate_timeline(current_weight, target_weight, daily_deficit):
    """
    Calculate weeks needed to reach goal
    Safe weight loss: 0.5-1kg per week
    """
    weight_to_lose = current_weight - target_weight
    weekly_loss = (daily_deficit * 7) / 7700  # calories to kg
    weeks_needed = weight_to_lose / weekly_loss
    return weeks_needed
```

**Milestones**:
```python
# Every 5% of goal
milestones = [
    {"percent": 25, "weight": 77.5, "week": 3},
    {"percent": 50, "weight": 75, "week": 6},
    {"percent": 75, "weight": 72.5, "week": 9},
    {"percent": 100, "weight": 70, "week": 12}
]
```

---

## 🧪 TESTING PLAN

### After Each Feature
1. **Unit tests** for new functions
2. **Integration tests** for API endpoints
3. **Manual testing** on local
4. **Deploy to staging**
5. **User acceptance testing**

### Test Cases

**Timezone**:
- [ ] User in different timezones see correct meal times
- [ ] Breakfast at 8am logs as breakfast, not lunch

**Water**:
- [ ] "drank 2 glasses of water" logs correctly
- [ ] Dashboard shows 2/8 glasses

**Sleep**:
- [ ] "slept 7 hours" logs correctly
- [ ] Dashboard shows sleep quality

**Workouts**:
- [ ] "ran 2km" shows in timeline
- [ ] Calories burned adjust available calories

**IF**:
- [ ] Timer shows correct time remaining
- [ ] Notifications at window start/end

**Timeline**:
- [ ] Shows expected weeks to goal
- [ ] Milestones update based on progress

---

## 📊 SUCCESS METRICS

### After Sprint
- [ ] All 9 features deployed
- [ ] 0 critical bugs
- [ ] User feedback positive
- [ ] Performance maintained

### KPIs
- [ ] Timezone accuracy: 100%
- [ ] Water tracking adoption: >50%
- [ ] Sleep tracking adoption: >40%
- [ ] IF feature adoption: >30%
- [ ] Timeline feature engagement: >60%

---

## 🚀 DEPLOYMENT STRATEGY

### Incremental Deployment
**Week 1**: P0-2, P2-5, P2-6, P1-2
**Week 2**: P1-7, P0-5, P1-1, P1-3, P1-4

### Rollback Plan
- Each feature has feature flag
- Can disable individually
- Database migrations are reversible

---

## 📝 NEXT STEPS

1. **Approve this plan**
2. **Start Day 1**: Timezone detection
3. **Daily standups**: Review progress
4. **Deploy incrementally**: Don't wait for all features
5. **Collect feedback**: Adjust as needed

---

**Status**: 📋 Ready to Start  
**Start Date**: November 3, 2025  
**Expected Completion**: November 12, 2025  
**Total Effort**: ~46-62 hours

---

*Let's build! 🚀*

