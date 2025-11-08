# Analytics Dashboard - Systematic Test Plan

**Feature:** User-Facing Feedback Analytics Dashboard  
**Branch:** `feature/analytics-dashboard`  
**Risk Level:** VERY LOW (read-only, isolated, new feature)  
**Status:** ✅ Both servers running

---

## 🚀 Server Status

### Backend Server
- **Status:** ✅ Running
- **URL:** http://localhost:8000
- **Port:** 8000
- **Endpoint:** GET `/analytics/feedback-summary`

### Frontend Server
- **Status:** ✅ Running
- **URL:** http://localhost:9001
- **Port:** 9001
- **Screen:** `FeedbackAnalyticsScreen` (accessible from Profile)

---

## 📋 Test Checklist

### Test 1: Navigation to Analytics Dashboard
**Objective:** Verify user can access the analytics screen from their profile

**Steps:**
1. Open browser: http://localhost:9001
2. Login with your test account (test@test11.com or test15)
3. Navigate to Profile screen (bottom navigation)
4. Scroll down to find "My Feedback" button
5. Click "My Feedback" button

**Expected Result:**
- ✅ Button is visible with analytics icon
- ✅ Clicking button navigates to Feedback Analytics screen
- ✅ No errors in console
- ✅ Screen shows loading indicator initially

**Actual Result:** [USER TO FILL]

---

### Test 2: Analytics Data Loading (User with Feedback)
**Objective:** Verify analytics loads correctly for user with existing feedback

**Pre-condition:** Use account with feedback history (test@test11.com)

**Steps:**
1. Navigate to "My Feedback" from Profile
2. Wait for data to load
3. Observe the displayed metrics

**Expected Result:**
- ✅ Loading spinner appears initially
- ✅ Data loads within 2-3 seconds
- ✅ Screen shows:
  - Total feedback count (number > 0)
  - Satisfaction score (percentage)
  - Feedback rate (42% placeholder for now)
  - Category breakdown (meal, workout, water, etc.)
  - Recent feedback list (last 10 items)
- ✅ No error messages
- ✅ Console shows: `✅ [ANALYTICS] Loaded successfully`

**Actual Result:** [USER TO FILL]

---

### Test 3: Analytics Data Display (New User)
**Objective:** Verify analytics handles zero feedback gracefully

**Pre-condition:** Use fresh account with no feedback (create new test account)

**Steps:**
1. Create new test account (test16@test.com)
2. Navigate to Profile → My Feedback
3. Observe the displayed state

**Expected Result:**
- ✅ Screen loads without errors
- ✅ Shows "No feedback yet" or zero state
- ✅ Total feedback: 0
- ✅ Satisfaction score: 0% or "N/A"
- ✅ Empty category breakdown
- ✅ Empty recent feedback list
- ✅ Friendly message encouraging user to provide feedback

**Actual Result:** [USER TO FILL]

---

### Test 4: Backend Endpoint Direct Test
**Objective:** Verify backend endpoint returns correct data structure

**Steps:**
1. Open browser DevTools (F12)
2. Go to Console tab
3. Run this command:
```javascript
fetch('http://localhost:8000/analytics/feedback-summary', {
  headers: {
    'Authorization': 'Bearer ' + localStorage.getItem('token')
  }
})
.then(r => r.json())
.then(data => console.log('Analytics Data:', data))
```

**Expected Result:**
- ✅ Status: 200 OK
- ✅ Response structure:
```json
{
  "status": "success",
  "summary": {
    "total_feedback": <number>,
    "helpful_count": <number>,
    "not_helpful_count": <number>,
    "satisfaction_score": <number>,
    "feedback_rate": 42
  },
  "category_breakdown": {
    "meal": {
      "total": <number>,
      "helpful": <number>,
      "not_helpful": <number>,
      "satisfaction": <number>
    },
    ...
  },
  "recent_feedback": [...]
}
```

**Actual Result:** [USER TO FILL]

---

### Test 5: Console Logs Verification
**Objective:** Verify proper logging and no errors

**Steps:**
1. Open browser DevTools → Console
2. Navigate to My Feedback screen
3. Review console output

**Expected Result:**
- ✅ Frontend logs:
  - `📊 [ANALYTICS] Loading analytics...`
  - `🔵 [API SERVICE] GET /analytics/feedback-summary`
  - `✅ [API SERVICE] Response status: 200`
  - `✅ [ANALYTICS] Loaded successfully`
- ✅ No red error messages
- ✅ No CORS errors
- ✅ No 404 or 500 errors

**Actual Result:** [USER TO FILL]

---

### Test 6: Backend Logs Verification
**Objective:** Verify backend processes request correctly

**Steps:**
1. In terminal, run:
```bash
tail -f /Users/pchintanwar/Documents/Projects-AIProductivity/agentic-productivity/backend.log
```
2. Navigate to My Feedback screen in browser
3. Observe backend logs

**Expected Result:**
- ✅ Backend logs show:
  - `📊 [ANALYTICS] Fetching feedback for user: <user_id>`
  - `✅ [ANALYTICS] Aggregated <N> feedback entries`
  - `Satisfaction: <X>%`
  - `Categories: <N>`
- ✅ No Python exceptions or tracebacks
- ✅ Response time < 2 seconds

**Actual Result:** [USER TO FILL]

---

### Test 7: UI/UX Verification
**Objective:** Verify screen looks good and is user-friendly

**Steps:**
1. Navigate to My Feedback screen
2. Review visual design and layout

**Expected Result:**
- ✅ Clean, modern design
- ✅ Clear section headers
- ✅ Readable fonts and colors
- ✅ Proper spacing and alignment
- ✅ Responsive layout (resize browser window)
- ✅ Back button works correctly
- ✅ Matches app theme (light/dark mode if applicable)

**Actual Result:** [USER TO FILL]

---

### Test 8: Error Handling
**Objective:** Verify graceful error handling

**Steps:**
1. Stop backend server temporarily:
```bash
pkill -f "uvicorn app.main:app"
```
2. Navigate to My Feedback screen
3. Observe error state
4. Restart backend:
```bash
cd /Users/pchintanwar/Documents/Projects-AIProductivity/agentic-productivity && source venv/bin/activate && python -m uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```

**Expected Result:**
- ✅ Shows friendly error message (not technical error)
- ✅ Retry button or back navigation available
- ✅ No app crash
- ✅ Console shows error but app remains functional

**Actual Result:** [USER TO FILL]

---

### Test 9: Regression Testing
**Objective:** Ensure new feature doesn't break existing functionality

**Steps:**
1. Test existing features:
   - Chat functionality
   - Meal logging
   - Feedback buttons (like/dislike)
   - Alternative picker
   - Profile screen
   - Timeline

**Expected Result:**
- ✅ All existing features work as before
- ✅ No new errors in console
- ✅ No performance degradation
- ✅ No visual glitches

**Actual Result:** [USER TO FILL]

---

### Test 10: Data Accuracy
**Objective:** Verify analytics data matches actual feedback given

**Steps:**
1. Login with test@test11.com
2. Note current analytics numbers
3. Give feedback on 2 new messages:
   - 1 helpful
   - 1 not helpful
4. Refresh My Feedback screen
5. Verify numbers updated correctly

**Expected Result:**
- ✅ Total feedback increases by 2
- ✅ Helpful count increases by 1
- ✅ Not helpful count increases by 1
- ✅ Satisfaction score recalculates correctly
- ✅ Recent feedback shows new entries at top

**Actual Result:** [USER TO FILL]

---

## 🎯 Success Criteria

**All tests must pass for feature to be production-ready:**

- [ ] Test 1: Navigation works
- [ ] Test 2: Data loads for existing users
- [ ] Test 3: Handles zero state gracefully
- [ ] Test 4: Backend endpoint returns correct structure
- [ ] Test 5: Frontend logs are clean
- [ ] Test 6: Backend logs are clean
- [ ] Test 7: UI looks professional
- [ ] Test 8: Error handling is graceful
- [ ] Test 9: No regressions
- [ ] Test 10: Data is accurate

---

## 🐛 Bug Tracking

**If any test fails, log here:**

| Test # | Issue | Severity | Status |
|--------|-------|----------|--------|
| | | | |

---

## 📊 Test Results Summary

**Tester:** [USER TO FILL]  
**Date:** [USER TO FILL]  
**Time:** [USER TO FILL]  
**Browser:** Chrome  
**Account Used:** test@test11.com, test15  

**Overall Result:** [ ] PASS / [ ] FAIL  
**Ready for Production:** [ ] YES / [ ] NO  

**Notes:**
[USER TO FILL]

---

## 🚀 Next Steps After Testing

**If all tests pass:**
1. Commit the analytics screen fix (ApiService instantiation)
2. Merge `feature/analytics-dashboard` to main
3. Update COMPREHENSIVE_DEFECT_FEEDBACK_REPORT.md (mark FR-025 as COMPLETED)
4. Move to next quick win or critical fix

**If any test fails:**
1. Log the issue in bug tracking table above
2. Fix the issue
3. Re-run failed test
4. Re-run regression tests (Test 9)
5. Repeat until all pass


