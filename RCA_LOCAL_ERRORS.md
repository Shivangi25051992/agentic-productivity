# 🔍 Root Cause Analysis - Local Environment Errors

## Date: November 3, 2025
## Environment: Local Development (localhost:8000 backend, localhost:9090 frontend)

---

## 🚨 Critical Issues Identified

### Issue #1: `/tasks` Endpoint - 500 Internal Server Error
**Error:** `GET http://localhost:8000/tasks/?start_due=2025-11-03T00:00:00.000 500`

**Root Cause:**
- Firestore composite index missing for: `user_id + due_date (ASC/DESC)`
- When frontend sends `start_due` parameter, backend tries to filter on `due_date` field
- Query requires composite index: `(user_id, due_date, __name__)`
- For new users with no tasks, this query fails

**Solution:**
1. **Option A (Quick Fix):** Remove `due_date` filter from initial dashboard load
2. **Option B (Proper Fix):** Create composite index in Firestore
3. **Option C (Defensive):** Wrap query in try-catch, return empty array on error

**Recommended:** Option C (defensive) + Option A (remove unnecessary filter)

---

### Issue #2: `/insights` Endpoint - 500 Internal Server Error
**Error:** `GET http://localhost:8000/insights 500`

**Root Cause:**
- Similar to Issue #1 - `list_fitness_logs_by_user` is being called with `start_ts` filter
- For new users with no logs, the query might fail
- Missing error handling in the insights endpoint

**Solution:**
- Already has try-catch wrapper in `main.py` lines 140-142
- But the error is happening INSIDE the database query
- Need to ensure `list_fitness_logs_by_user` returns empty array instead of throwing

**Recommended:** Add defensive error handling in database query

---

### Issue #3: `setState() called after dispose()` Flutter Error
**Error:** Multiple instances in console logs

**Root Cause:**
- Asynchronous operations (API calls) completing after widget is disposed
- Happens in `_MobileFirstHomeScreenState` when user navigates away quickly
- Common Flutter lifecycle issue

**Solution:**
```dart
// In any async callback that calls setState:
if (mounted) {
  setState(() {
    // ... state updates
  });
}
```

**Files to Fix:**
- `flutter_app/lib/screens/home/mobile_first_home_screen.dart`
- Any widget with async operations + setState

---

### Issue #4: Timeline Time Incorrect + No Activity Logged (CONFIRMED BY USER)
**Error:** User states: "it is for sure timezone mismatch issue"

**Root Cause:**
- User's timezone is stored as "UTC" but should be "Asia/Kolkata" (IST)
- Firestore timestamps show correct offset (UTC+5:30) but timezone field is wrong
- Frontend `TimezoneHelper` is not being called during signup
- Dashboard displays times in UTC instead of user's local timezone

**Observations from User:**
- Firestore `created_at` and `updated_at` show: "2 November 2025 at 23:34:16 UTC+5:30" ✅
- But `timezone` field in user_profile shows: "UTC" ❌
- Timeline shows incorrect time (17:29 instead of local time)
- Activities not showing in timeline despite being logged

**Solution:**
1. Fix frontend timezone detection during signup
2. Ensure backend uses user's timezone for all time calculations
3. Fix timeline display to respect user timezone
4. Add timezone validation and fallback logic

---

## 📊 Port Information

### Application Ports:
| Port | Service | Purpose | URL |
|------|---------|---------|-----|
| **8000** | Backend API | FastAPI server (uvicorn) | http://localhost:8000 |
| **9090** | Frontend Web | Flutter web app | http://localhost:9090 |
| **8080** | ⚠️ RESERVED | Another JS app (user's) | DO NOT USE |

### Port Conflicts:
- Port 8080 was initially attempted for Flutter but conflicted with user's existing JS app
- Solution: Changed Flutter to port 9090

---

## 🎯 Priority Fix Order

### P0 (Critical - Blocks User Testing):
1. ✅ **Fix `/tasks` endpoint** - Remove unnecessary date filter OR add error handling
2. ✅ **Fix `/insights` endpoint** - Add defensive error handling
3. ⏳ **Fix timezone detection** - Ensure correct timezone is saved during signup
4. ⏳ **Fix timeline display** - Use user's timezone for all time displays

### P1 (High - UX Issues):
5. ⏳ **Fix `setState() after dispose()`** - Add mounted checks
6. ⏳ **Fix task response UX** - Make AI responses more conversational
7. ⏳ **Fix timeline time display** - Show local time, not UTC

---

## 🔧 Implementation Plan

### Step 1: Fix Database Queries (P0)
- Modify `list_tasks_by_user` to handle errors gracefully
- Modify `list_fitness_logs_by_user` to return empty array on error
- Remove unnecessary `start_due` filter from dashboard initial load

### Step 2: Fix Timezone Issues (P0)
- Verify `TimezoneHelper.getLocalTimezone()` is being called
- Add logging to track timezone detection flow
- Fix backend to use user's timezone for all calculations
- Fix frontend timeline to display in user's local time

### Step 3: Fix Flutter Lifecycle Issues (P1)
- Add `if (mounted)` checks before all `setState()` calls
- Especially in async callbacks

### Step 4: Test Everything
- Create new test user
- Complete signup flow
- Log meals, tasks, workouts
- Verify timeline shows correct local time
- Verify dashboard loads without errors

---

## 📝 Next Steps

1. Implement P0 fixes
2. Test locally with new user signup
3. Verify all endpoints return 200 OK
4. Verify timezone is correctly detected and stored
5. Verify timeline shows correct local time
6. Then proceed with P1 fixes

---

## ⚠️ Important Notes

- **DO NOT touch production** until local is fully working
- **DO NOT deploy** until all P0 fixes are tested locally
- **DO NOT create new features** until existing bugs are fixed
- **ALWAYS test with fresh user signup** to catch onboarding issues

---

## 🎯 Success Criteria

✅ New user can sign up without errors
✅ Dashboard loads without 500 errors
✅ Timeline shows activities in correct local time
✅ Tasks are created and displayed correctly
✅ Insights are generated without errors
✅ No `setState() after dispose()` errors in console

---

**Status:** Ready to implement fixes
**Next Action:** Fix database queries with defensive error handling

