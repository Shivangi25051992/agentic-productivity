# RCA: Dashboard Blank - Timezone Mismatch Issue

## Status: 🔍 ROOT CAUSE IDENTIFIED

## Issue
Dashboard showing blank/no data even though user has logged meals, workouts, and other activities.

## User Observation
> "I suspect it might be related to timezone?"

**✅ CORRECT!** Excellent observation by the user.

## Root Cause Analysis

### The Problem: Timezone Mismatch in Date Range Queries

**Frontend (Flutter) - `dashboard_provider.dart` (Lines 129-131):**
```dart
// Get start and end of the selected day
final startOfDay = DateTime(_selectedDate.year, _selectedDate.month, _selectedDate.day);
final endOfDay = startOfDay.add(const Duration(days: 1));
```

**API Service - `api_service.dart` (Lines 144-146):**
```dart
final resp = await _dio.get('/fitness/logs', queryParameters: {
  if (startDate != null) 'start': startDate.toIso8601String(),
  if (endDate != null) 'end': endDate.toIso8601String(),
});
```

**Backend - `database.py` (Lines 298-300):**
```python
if start_ts is not None:
    query = query.where("timestamp", ">=", start_ts)
if end_ts is not None:
    query = query.where("timestamp", "<=", end_ts)
```

### The Mismatch Explained

1. **User Profile:**
   - User is in `Asia/Kolkata` timezone (UTC+5:30)
   - Profile shows: `"timezone":"Asia/Kolkata"`

2. **Frontend Creates Local DateTime:**
   - `DateTime(2025, 11, 8, 0, 0, 0)` creates a **local** DateTime
   - In IST, this represents: `2025-11-08T00:00:00+05:30`

3. **toIso8601String() Loses Timezone:**
   - `DateTime(2025, 11, 8).toIso8601String()` returns: `"2025-11-08T00:00:00.000"`
   - **NO TIMEZONE SUFFIX!** (not `+05:30` or `Z`)

4. **Backend Interprets as UTC:**
   - Backend receives: `"2025-11-08T00:00:00.000"`
   - Python's `datetime.fromisoformat()` treats this as **UTC** (no timezone = UTC)
   - So the query searches: `2025-11-08T00:00:00 UTC` to `2025-11-09T00:00:00 UTC`

5. **Data is Stored in Different Time Window:**
   - User logs "ran 5 km" at 12:11 AM IST (Nov 8)
   - This is stored as: `2025-11-07T18:41:00 UTC` (Nov 7 in UTC!)
   - Query for Nov 8 UTC misses data from Nov 7 UTC

### Visual Timeline

```
User Action (IST):     Nov 8, 2025 12:11 AM
                       ↓
Stored in DB (UTC):    Nov 7, 2025 18:41 UTC  ← Actual timestamp
                       
Dashboard Query:       Nov 8, 2025 00:00 UTC to Nov 9, 2025 00:00 UTC
                       ↓
Result:                NO DATA FOUND (looking at wrong day!)
```

### Why This Wasn't Caught Earlier

1. **Timeline works:** Timeline might be using different date handling or broader queries
2. **Chat works:** Chat doesn't filter by date, shows all recent messages
3. **First noticed on fresh account:** Test15 account has limited data, making the gap obvious
4. **Time of day matters:** Issue is most visible when testing late at night or early morning (near day boundaries)

## Impact

**Severity:** 🔴 HIGH
- Dashboard completely blank for users in non-UTC timezones
- Affects all dashboard metrics (calories, macros, water, workouts)
- Data exists but is invisible to users

**Affected Users:**
- Any user NOT in UTC timezone (most of the world!)
- Particularly severe for users in Asia (UTC+5:30 to UTC+9)

**Affected Features:**
- ❌ Dashboard home screen (blank)
- ❌ Daily stats (all zeros)
- ❌ Progress bars (no data)
- ❌ Activity timeline on dashboard
- ✅ Chat (works - no date filtering)
- ✅ Timeline screen (might work if using different logic)

## Solution Options

### Option 1: Convert to UTC in Frontend (RECOMMENDED)
**Pros:**
- Clean separation of concerns
- Backend stays timezone-agnostic
- Consistent with REST API best practices

**Cons:**
- Requires frontend changes
- Need to handle user timezone correctly

**Implementation:**
```dart
// In dashboard_provider.dart
final startOfDay = DateTime(_selectedDate.year, _selectedDate.month, _selectedDate.day);
final startOfDayUtc = startOfDay.toUtc(); // Convert to UTC
final endOfDayUtc = startOfDayUtc.add(const Duration(days: 1));

final logs = await apiService.getFitnessLogs(
  startDate: startOfDayUtc,  // Send UTC
  endDate: endOfDayUtc,
);
```

### Option 2: Backend Converts from User Timezone
**Pros:**
- Frontend stays simple
- Backend has user timezone from profile

**Cons:**
- Backend needs to parse timezone-naive strings
- More complex backend logic
- Inconsistent with other endpoints

### Option 3: Always Use User's Timezone-Aware Dates
**Pros:**
- Most accurate
- Respects user's local time

**Cons:**
- Requires timezone suffix in ISO strings
- More complex parsing on both ends

## Recommended Fix: Option 1 (Convert to UTC in Frontend)

### Changes Required

**File:** `flutter_app/lib/providers/dashboard_provider.dart`

**Change Lines 129-140:**
```dart
// BEFORE:
final startOfDay = DateTime(_selectedDate.year, _selectedDate.month, _selectedDate.day);
final endOfDay = startOfDay.add(const Duration(days: 1));

// AFTER:
// Get start and end of the selected day in LOCAL time, then convert to UTC
final startOfDayLocal = DateTime(_selectedDate.year, _selectedDate.month, _selectedDate.day);
final endOfDayLocal = startOfDayLocal.add(const Duration(days: 1));

// Convert to UTC for API query (backend stores all timestamps in UTC)
final startOfDay = startOfDayLocal.toUtc();
final endOfDay = endOfDayLocal.toUtc();

print('🔍 Fetching data for ${DateFormat('yyyy-MM-dd').format(_selectedDate)} (local)');
print('🔍 UTC range: ${startOfDay.toIso8601String()} to ${endOfDay.toIso8601String()}');
```

### Testing

**Test Case 1: User in IST (UTC+5:30)**
- Local: Nov 8, 2025 00:00:00 IST
- UTC Query: Nov 7, 2025 18:30:00 UTC to Nov 8, 2025 18:30:00 UTC
- Should capture all logs from Nov 8 IST

**Test Case 2: User in PST (UTC-8:00)**
- Local: Nov 8, 2025 00:00:00 PST
- UTC Query: Nov 8, 2025 08:00:00 UTC to Nov 9, 2025 08:00:00 UTC
- Should capture all logs from Nov 8 PST

**Test Case 3: User in UTC**
- Local: Nov 8, 2025 00:00:00 UTC
- UTC Query: Nov 8, 2025 00:00:00 UTC to Nov 9, 2025 00:00:00 UTC
- Should work as before (no change)

## Deployment

**Risk:** 🟡 MEDIUM
- Changes core data fetching logic
- Must test across multiple timezones
- Affects all dashboard users

**Rollback:** Easy
- Revert single file change
- No database changes

**Testing Required:**
1. Test in IST timezone (current user)
2. Test in UTC timezone
3. Test in negative offset timezone (PST, EST)
4. Test day boundary transitions (11:59 PM → 12:00 AM)

## Related Issues

- **Timeline Provider:** May have same issue (needs investigation)
- **Fasting Service:** May have same issue (needs investigation)
- **Task Date Filtering:** May have same issue (needs investigation)

## Next Steps

1. ✅ Identify root cause (DONE)
2. ⏳ Implement fix in `dashboard_provider.dart`
3. ⏳ Test with user in IST timezone
4. ⏳ Check other providers for same issue
5. ⏳ Deploy and verify dashboard shows data

---

**Priority:** 🔴 P0 (Critical - Dashboard completely broken for non-UTC users)
**Effort:** 🟢 Small (5-10 lines of code)
**Risk:** 🟡 Medium (Core data fetching)
**User Impact:** 🔴 HIGH (Dashboard is primary feature)


