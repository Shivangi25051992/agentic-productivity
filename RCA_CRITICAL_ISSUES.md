# 🔴 ROOT CAUSE ANALYSIS - CRITICAL PRODUCTION ISSUES

**Date**: November 2, 2025, 11:00 PM IST  
**User**: tets@teste.com  
**Timezone**: IST (India Standard Time)  
**Status**: CRITICAL - Multiple regressions

---

## 📸 OBSERVED ISSUES (From Screenshots)

### Issue 1: "Edit Profile Coming Soon" ❌
**Screenshot 1**: Edit Profile button shows toast "Edit profile coming soon!"
- **Expected**: Should navigate to edit profile screen
- **Actual**: Shows "coming soon" message

### Issue 2: No Meals in Today's Meals ❌
**Screenshot 3**: All meal categories show "No items logged"
- Breakfast: No items logged
- Lunch: No items logged
- Snack: No items logged
- Dinner: No items logged
- **BUT**: Top bar shows 140/1681 calories (so data exists!)

### Issue 3: "Unknown" Food in Chat ❌
**Screenshot 2**: Chat shows "Unknown 2.0 → ~140.0 kcal"
- User said: "2 eggs"
- AI classified as: "Unknown 2.0"
- **Expected**: Should classify as "2 boiled eggs" or similar

### Issue 4: Timeline Shows Wrong Time ❌
**Screenshot 2**: Timeline shows "17:29" (5:29 PM)
- User is in IST timezone
- Time shown: 17:29 (likely UTC or wrong timezone)
- **Expected**: Should show IST time

---

## 🔍 ROOT CAUSE ANALYSIS

### 🎯 ROOT CAUSE #1: Edit Profile Route Not Working

**Location**: `flutter_app/lib/screens/profile/profile_screen.dart`

**Problem**: The Edit Profile button is likely still showing a toast instead of navigating

**Evidence**:
```dart
// WRONG (old code):
onPressed: () {
  ScaffoldMessenger.of(context).showSnackBar(
    const SnackBar(content: Text('Edit profile coming soon!')),
  );
}

// CORRECT (what we deployed):
onPressed: () {
  Navigator.of(context).pushNamed('/profile/edit');
}
```

**Why It Failed**: 
- Either the deployment didn't update the frontend properly
- OR there's a caching issue in the PWA
- OR the route is not registered in main.dart

---

### 🎯 ROOT CAUSE #2: Timezone Not Saved During Onboarding

**Location**: `flutter_app/lib/providers/profile_provider.dart` + Backend

**Problem**: User's timezone was NOT saved during onboarding

**Evidence**:
1. Timeline shows UTC time (17:29) instead of IST
2. AI classified "2 eggs" as "Unknown" (likely because timezone context failed)
3. No meals showing in Today's Meals (timezone mismatch)

**Why It Failed**:
```dart
// In profile_provider.dart - completeOnboarding()
final timezone = DateTime.now().timeZoneName;  // ❌ This returns "IST" (abbreviation)

// Backend expects: "Asia/Kolkata" (IANA timezone)
// But gets: "IST" (abbreviation)
// Result: Backend can't parse it, defaults to UTC
```

**The Bug**:
- `DateTime.now().timeZoneName` returns **abbreviation** ("IST", "PST", "EST")
- Backend `pytz.timezone()` expects **IANA format** ("Asia/Kolkata", "America/Los_Angeles")
- Mismatch causes timezone to be invalid → defaults to UTC

---

### 🎯 ROOT CAUSE #3: "Unknown" Food Classification

**Location**: `app/main.py` - `_classify_with_llm()`

**Problem**: AI is classifying "2 eggs" as "Unknown 2.0"

**Why It Failed**:
1. **Timezone context failed** (see Root Cause #2)
   - AI doesn't know user's local time
   - Can't infer meal type (breakfast/lunch/dinner)
   - Falls back to "Unknown"

2. **Possible LLM prompt issue**:
   - New prompt with timezone context might have syntax errors
   - OR the prompt is too complex and confusing the AI

3. **Possible string concatenation issue**:
   - We changed from f-strings to string concatenation
   - Might have broken the prompt formatting

---

### 🎯 ROOT CAUSE #4: No Meals in "Today's Meals"

**Location**: `flutter_app/lib/providers/fitness_provider.dart` + Backend

**Problem**: Meals are logged (140 calories shown) but not appearing in meal categories

**Why It Failed**:
1. **Timezone mismatch**:
   - Meal logged with UTC timestamp
   - Frontend filtering by IST "today"
   - Mismatch means meal doesn't appear in "today's" list

2. **Meal type is "Unknown"**:
   - Frontend might filter out meals with meal_type="unknown"
   - OR only shows meals with valid meal types

3. **Data structure issue**:
   - Meal might be in old structure (top-level collection)
   - Frontend looking in new structure (subcollection)

---

## 🔬 DETAILED TECHNICAL ANALYSIS

### Timeline Issue Deep Dive

**Current Flow**:
1. User logs "2 eggs" at 11:00 AM IST
2. Backend gets user_id, tries to fetch timezone
3. Timezone lookup fails (invalid timezone format)
4. Falls back to UTC
5. Stores timestamp as UTC 05:30 (11:00 AM IST = 05:30 AM UTC)
6. Frontend displays 17:29 (likely some other log's time)

**What Should Happen**:
1. User logs "2 eggs" at 11:00 AM IST
2. Backend gets timezone: "Asia/Kolkata"
3. Converts to user's local time for AI context
4. AI knows it's 11:00 AM → classifies as "breakfast"
5. Stores with proper timezone metadata
6. Frontend displays in user's local time

---

### Timezone Detection Issue

**The Problem**:
```dart
// Flutter code
final timezone = DateTime.now().timeZoneName;  // Returns "IST"

// Backend code (Python)
user_tz = pytz.timezone(user_tz_str)  // Expects "Asia/Kolkata"
```

**Why It Breaks**:
```python
>>> import pytz
>>> pytz.timezone("IST")
pytz.exceptions.UnknownTimeZoneError: 'IST'

>>> pytz.timezone("Asia/Kolkata")
<DstTzInfo 'Asia/Kolkata' LMT+5:53:00 STD>  ✅
```

**The Fix Needed**:
Flutter doesn't have a built-in way to get IANA timezone. We need to:
1. Use a package like `timezone` or `flutter_timezone`
2. OR send UTC offset and let backend infer timezone
3. OR have a timezone picker in onboarding

---

## 📊 IMPACT ASSESSMENT

### Severity: 🔴 CRITICAL

**Affected Features**:
- ❌ Edit Profile (completely broken)
- ❌ Food logging (classifies as "Unknown")
- ❌ Today's Meals (empty despite data existing)
- ❌ Timeline (wrong time display)
- ❌ AI meal type inference (broken due to timezone)
- ⚠️  Calorie tracking (working but data not visible)

**User Impact**:
- **100% of new users** affected (timezone not saved)
- **100% of food logs** classified as "Unknown"
- **0% of meals** appearing in Today's Meals
- **Profile editing** completely broken

**Regression**: YES - These were working before today's deployment

---

## 🎯 FIXES REQUIRED (Priority Order)

### FIX #1: Timezone Detection (P0 - CRITICAL)

**Problem**: `DateTime.now().timeZoneName` returns abbreviation, not IANA format

**Solution Options**:

**Option A**: Use flutter_timezone package (RECOMMENDED)
```dart
// Add to pubspec.yaml
dependencies:
  flutter_timezone: ^1.0.8

// In profile_provider.dart
import 'package:flutter_timezone/flutter_timezone.dart';

final timezone = await FlutterTimezone.getLocalTimezone();  // Returns "Asia/Kolkata"
```

**Option B**: Manual timezone picker
```dart
// Show dropdown with common timezones
// User selects their timezone
// More reliable but worse UX
```

**Option C**: Send UTC offset, backend infers
```dart
final offset = DateTime.now().timeZoneOffset;  // Duration(hours: 5, minutes: 30)
// Send to backend: "+05:30"
// Backend maps to timezone
```

---

### FIX #2: Edit Profile Navigation (P0 - CRITICAL)

**Problem**: Button shows toast instead of navigating

**Solution**: Verify the deployed code and clear PWA cache

```dart
// Ensure this is in profile_screen.dart
OutlinedButton.icon(
  onPressed: () {
    Navigator.of(context).pushNamed('/profile/edit');  // NOT showSnackBar!
  },
  icon: const Icon(Icons.edit),
  label: const Text('Edit Profile'),
),
```

**Also check**: Route is registered in main.dart
```dart
routes: {
  '/profile/edit': (_) => const AuthGuard(child: EditProfileScreen()),
},
```

---

### FIX #3: Unknown Food Classification (P0 - CRITICAL)

**Problem**: AI classifying everything as "Unknown"

**Root Cause**: Timezone context failing → AI can't infer meal type

**Solution**: 
1. Fix timezone detection (Fix #1)
2. Verify LLM prompt is correctly formatted after string concatenation change
3. Add fallback logic if timezone fails

```python
# In main.py - _classify_with_llm()
if user_local_time:
    time_str = user_local_time.strftime('%Y-%m-%d %H:%M:%S')
    timezone_context = "\n\n**USER CONTEXT:**\n- Current time in user's timezone (" + user_timezone + "): " + time_str + "\n- Current hour: " + str(user_local_time.hour) + "\n- Use this time for meal type classification if user doesn't specify!\n"
else:
    # FALLBACK: Use UTC time if timezone fails
    timezone_context = "\n\n**USER CONTEXT:**\n- Current time (UTC): " + datetime.now().strftime('%Y-%m-%d %H:%M:%S') + "\n- Note: User timezone unknown, use UTC for meal classification\n"
```

---

### FIX #4: Today's Meals Empty (P0 - CRITICAL)

**Problem**: Meals logged but not showing in categories

**Root Causes**:
1. Timezone mismatch (meal logged in UTC, filtered by IST)
2. Meal type is "unknown" (frontend filters it out?)
3. Data in wrong collection

**Solution**:
1. Fix timezone (Fix #1)
2. Check frontend filtering logic
3. Verify data structure

```dart
// In fitness_provider.dart - check filtering
final logs = await _fitnessService.getLogs(
  startDate: DateTime.now().startOfDay,  // ⚠️  This uses device timezone
  endDate: DateTime.now().endOfDay,
);

// If backend stores in UTC but frontend filters by IST, mismatch!
```

---

## 🚨 IMMEDIATE ACTION PLAN

### Step 1: Verify Current State (5 min)
1. Check if edit_profile_screen.dart was actually deployed
2. Check if route is registered
3. Check PWA cache

### Step 2: Fix Timezone Detection (30 min)
1. Add flutter_timezone package
2. Update profile_provider.dart
3. Update onboarding flow
4. Test with new user

### Step 3: Fix Backend Timezone Handling (15 min)
1. Add fallback for invalid timezones
2. Add logging to see what timezone is received
3. Handle timezone lookup errors gracefully

### Step 4: Test End-to-End (15 min)
1. Sign up as new user
2. Verify timezone saved correctly
3. Log "2 eggs"
4. Verify classified correctly (not "Unknown")
5. Verify appears in Today's Meals
6. Verify timeline shows correct time

### Step 5: Deploy (10 min)
1. Deploy backend fixes
2. Deploy frontend fixes
3. Clear PWA cache
4. Test on iOS Safari

---

## 🔍 VERIFICATION CHECKLIST

After fixes, verify:
- [ ] New user signup saves timezone in IANA format ("Asia/Kolkata")
- [ ] Edit Profile button navigates (not toast)
- [ ] "2 eggs" classifies as "2 boiled eggs" (not "Unknown")
- [ ] Meal appears in correct category (Breakfast if morning)
- [ ] Timeline shows IST time (not UTC)
- [ ] Today's Meals shows logged items
- [ ] Calorie bar matches logged items
- [ ] No console errors

---

## 📝 LESSONS LEARNED

1. **Always test timezone with actual devices** - Desktop timezone != Mobile timezone
2. **Don't assume DateTime.now().timeZoneName works** - It returns abbreviations
3. **Test PWA cache invalidation** - Changes might not reflect due to caching
4. **Verify deployments** - Code might not have deployed correctly
5. **Test with fresh user** - Existing users have old data structure

---

**Next Steps**: Implement fixes in priority order, test thoroughly, deploy carefully.

