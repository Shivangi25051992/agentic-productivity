# Zero Regression Test Plan - Phase 2 Complete

## ✅ **Successfully Tested (Just Now):**
1. ✅ Dashboard updates with calories
2. ✅ Today's Meals card shows items
3. ✅ Timeline populated correctly
4. ✅ Chat history retention (24h+)
5. ✅ **Confidence score persists after navigation** ← JUST FIXED!

---

## 🧪 **COMPREHENSIVE REGRESSION TEST SUITE**

### **Priority 1: Core Chat Functionality (CRITICAL)**

#### **Test 1.1: Chat Classification - Food Items**
- [ ] Send: "2 eggs"
  - Expected: Meal logged, 140 calories, dashboard updates
  - Check: Summary, suggestion, confidence score visible
  - Check: Expandable "More details" works

#### **Test 1.2: Chat Classification - Workout**
- [ ] Send: "ran 5k"
  - Expected: Workout logged, calories burned shown
  - Check: Timeline shows workout entry
  - Check: Dashboard reflects workout

#### **Test 1.3: Chat Classification - Water**
- [ ] Send: "drank 2 glasses of water"
  - Expected: Water logged (500ml)
  - Check: Timeline shows water entry
  - Check: Water goal progress updates

#### **Test 1.4: Chat Classification - Supplement**
- [ ] Send: "took vitamin D"
  - Expected: Supplement logged
  - Check: Timeline shows supplement entry

#### **Test 1.5: Chat Classification - Task**
- [ ] Send: "remind me to workout at 6pm"
  - Expected: Task created with reminder
  - Check: Tasks list updates

---

### **Priority 2: Phase 2 Explainable AI Features (NEW)**

#### **Test 2.1: Confidence Score Display**
- [ ] Send any food item
- [ ] Verify confidence badge appears (e.g., "🟢 HIGH")
- [ ] Verify percentage shown (e.g., 85%)
- [ ] Verify badge is tappable

#### **Test 2.2: Confidence Score Persistence**
- [ ] Send food item, note confidence score
- [ ] Navigate to Home → Plan → Chat
- [ ] **CRITICAL:** Verify confidence score still shows
- [ ] Scroll chat history, all messages retain scores

#### **Test 2.3: "Why?" Button & Explanation**
- [ ] Click "Why?" button on any message
- [ ] Verify bottom sheet appears
- [ ] Check explanation has:
  - [ ] Reasoning section
  - [ ] Data sources
  - [ ] Assumptions
  - [ ] Confidence breakdown
- [ ] Close and reopen, verify works consistently

#### **Test 2.4: Alternative Suggestions (Low Confidence)**
- [ ] Send ambiguous input: "rice"
- [ ] Verify alternatives appear if confidence < 85%
- [ ] Select an alternative
- [ ] Verify "Confirm" button works (no infinite loading)
- [ ] Verify selection message appears

#### **Test 2.5: Feedback Buttons (👍 👎)**
- [ ] Log any food
- [ ] Click 👍 (thumbs up)
- [ ] Verify success message appears
- [ ] Check browser console (F12) for feedback log

#### **Test 2.6: Negative Feedback Form**
- [ ] Log any food
- [ ] Click 👎 (thumbs down)
- [ ] **CRITICAL:** Try to check multiple checkboxes
- [ ] Verify checkboxes are clickable (not read-only)
- [ ] Type in "Tell us more" field
- [ ] Click Submit
- [ ] Verify success message
- [ ] Check console for captured feedback

---

### **Priority 3: Dashboard & Data Display**

#### **Test 3.1: Calorie Counter**
- [ ] Start fresh: Click "Wipe All Logs"
- [ ] Verify dashboard shows 0/[goal] calories
- [ ] Log "2 eggs" (140 cal)
- [ ] **CRITICAL:** Dashboard updates to 140/[goal]
- [ ] Log "1 banana" (105 cal)
- [ ] **CRITICAL:** Dashboard shows 245/[goal] (cumulative)

#### **Test 3.2: Today's Meals Card**
- [ ] Verify "Breakfast" section shows logged items
- [ ] Verify "Lunch" section shows logged items
- [ ] Verify "Snack" section shows logged items
- [ ] Verify "Dinner" section shows logged items
- [ ] Check each card shows:
  - [ ] Food name
  - [ ] Calories
  - [ ] Time (in user's timezone, not UTC)

#### **Test 3.3: Progress Bar**
- [ ] Verify progress bar fills based on calories/goal
- [ ] Verify color changes (green → yellow → red as approaching/exceeding goal)
- [ ] Verify percentage shown matches calculation

---

### **Priority 4: Timeline Feature**

#### **Test 4.1: Timeline Population**
- [ ] Click "Timeline" button
- [ ] Verify all logged items appear chronologically
- [ ] Check icons:
  - [ ] 🍽️ for meals
  - [ ] 💪 for workouts
  - [ ] 💧 for water
  - [ ] 💊 for supplements

#### **Test 4.2: Timeline Filtering**
- [ ] Click "Meals" filter → Only meals show
- [ ] Click "Workouts" filter → Only workouts show
- [ ] Click "Water" filter → Only water shows
- [ ] Click "All" → Everything shows

#### **Test 4.3: Timeline Time Display**
- [ ] Verify times are in user's local timezone
- [ ] Verify "X minutes ago" format for recent items
- [ ] Verify actual time for older items

---

### **Priority 5: Chat History & Persistence**

#### **Test 5.1: Chat History Retention**
- [ ] Send 5 different messages
- [ ] Refresh browser (F5)
- [ ] **CRITICAL:** All 5 messages still visible
- [ ] Verify order is preserved

#### **Test 5.2: Chat History After Navigation**
- [ ] Send message in chat
- [ ] Navigate to Home → Plan → Settings → Back to Chat
- [ ] **CRITICAL:** Chat history intact
- [ ] Verify expandable bubbles still work
- [ ] Verify confidence scores still show

#### **Test 5.3: Chat Scroll Behavior**
- [ ] Send message
- [ ] Verify auto-scroll to bottom
- [ ] Scroll up manually
- [ ] Send another message
- [ ] Verify auto-scroll to new message

---

### **Priority 6: Meal Planning Feature**

#### **Test 6.1: View Current Week Plan**
- [ ] Go to Plan tab → Meal Planning
- [ ] Verify current week meals display
- [ ] Check each day shows 3 meals
- [ ] Verify calories per meal shown

#### **Test 6.2: Generate New Plan**
- [ ] Click "Generate New Plan"
- [ ] Select dietary preference (e.g., High Protein)
- [ ] Click Generate
- [ ] Verify new plan appears
- [ ] Verify old plan is marked inactive

#### **Test 6.3: Day Selection**
- [ ] Click "Mon" → Verify Monday's meals
- [ ] Click "Tue" → Verify Tuesday's meals (not Monday!)
- [ ] Click "Wed" → Verify Wednesday's meals
- [ ] **CRITICAL:** No cross-day display issues

---

### **Priority 7: Fasting Feature**

#### **Test 7.1: Start Fast**
- [ ] Chat: "start fast"
- [ ] Verify fasting session starts
- [ ] Check Plan tab shows active fast
- [ ] Verify timer is running

#### **Test 7.2: Fast Status**
- [ ] Chat: "fasting status"
- [ ] Verify current progress shown
- [ ] Verify hours elapsed
- [ ] Verify fasting stage (anabolic, catabolic, etc.)

#### **Test 7.3: Stop Fast**
- [ ] Chat: "stop fast"
- [ ] Verify fast ends
- [ ] Verify duration shown
- [ ] Check Plan tab shows no active fast

---

### **Priority 8: User Profile & Settings**

#### **Test 8.1: View Profile**
- [ ] Go to Profile tab
- [ ] Verify user data loads
- [ ] Check calorie goal displayed
- [ ] Check fitness goal displayed

#### **Test 8.2: Wipe All Logs**
- [ ] Log some data (food, workout, etc.)
- [ ] Go to Settings → "Wipe All Logs"
- [ ] Click confirm
- [ ] Wait 15-20 seconds (backend takes time)
- [ ] Verify success message (ignore if error message but data deleted)
- [ ] Check dashboard shows 0 calories
- [ ] Check timeline is empty
- [ ] **CRITICAL:** Profile/goals still intact

---

### **Priority 9: Performance & Responsiveness**

#### **Test 9.1: Chat Response Time**
- [ ] Send "2 eggs"
- [ ] Measure time from send to response
- [ ] **Expected:** < 3 seconds
- [ ] **Acceptable:** < 5 seconds
- [ ] **FAIL:** > 10 seconds

#### **Test 9.2: Dashboard Load Time**
- [ ] Navigate to Home tab
- [ ] Measure time to show data
- [ ] **Expected:** < 1 second
- [ ] **FAIL:** > 3 seconds

#### **Test 9.3: Timeline Load Time**
- [ ] Click Timeline button
- [ ] Measure time to populate
- [ ] **Expected:** < 2 seconds
- [ ] **FAIL:** > 5 seconds

---

### **Priority 10: Error Handling**

#### **Test 10.1: Network Interruption**
- [ ] Open DevTools → Network tab
- [ ] Throttle to "Slow 3G"
- [ ] Send message
- [ ] Verify graceful handling (loading indicator)
- [ ] Restore network
- [ ] Verify message eventually sends

#### **Test 10.2: Invalid Input**
- [ ] Send gibberish: "asdfasdf"
- [ ] Verify AI handles gracefully
- [ ] Verify no crash

#### **Test 10.3: Backend Down**
- [ ] (Don't actually test this - just note it's handled)
- [ ] Expected: Error message, retry option

---

## 📊 **Test Execution Plan**

### **Phase 1: Core Functionality (15 min)**
Run Priority 1 + Priority 3 tests
- Focus: Chat, Dashboard, Basic data flow
- Goal: Ensure fundamentals work

### **Phase 2: Phase 2 Features (15 min)**
Run Priority 2 tests
- Focus: Confidence scores, explanations, feedback
- Goal: Ensure new features work and persist

### **Phase 3: Extended Features (15 min)**
Run Priority 4, 5, 6, 7 tests
- Focus: Timeline, history, meal planning, fasting
- Goal: Ensure existing features not broken

### **Phase 4: Edge Cases & Performance (10 min)**
Run Priority 8, 9, 10 tests
- Focus: Settings, speed, error handling
- Goal: Ensure robustness

**Total Estimated Time:** 55 minutes for complete suite

---

## ✅ **Success Criteria**

### **Zero Regression = ALL of these:**
1. ✅ All Priority 1 tests pass (Chat classification)
2. ✅ All Priority 2 tests pass (Phase 2 features)
3. ✅ All Priority 3 tests pass (Dashboard accuracy)
4. ✅ Dashboard shows correct calories (cumulative)
5. ✅ Confidence scores persist after navigation
6. ✅ Feedback checkboxes are clickable
7. ✅ No critical errors in console
8. ✅ Performance < 5 seconds per chat
9. ✅ Timeline populates correctly
10. ✅ Profile/goals preserved after wipe

### **Acceptable Issues (Not Blockers):**
- ⚠️ Feedback not saved to DB (Phase 3 work)
- ⚠️ AI Insights showing incorrect data (known bug, backlogged)
- ⚠️ Wipe logs showing error message (but data deletes successfully)
- ⚠️ Minor UI glitches that don't affect functionality

---

## 🐛 **Bug Tracking Template**

If you find a regression:

```
**Test:** [Test number/name]
**Issue:** [What broke]
**Expected:** [What should happen]
**Actual:** [What happened]
**Steps:**
1. [Step 1]
2. [Step 2]
3. [Step 3]

**Console Errors:** [Paste from F12 console]
**Backend Logs:** [If available from monitoring]
**Severity:** Critical / Important / Minor
```

---

## 📋 **Quick Test Checklist (5-Minute Smoke Test)**

If you're short on time, test ONLY these:

- [ ] Send "2 eggs" → Dashboard shows 140 calories
- [ ] Confidence score visible
- [ ] Navigate away and back → Score still there
- [ ] Click 👎 → Checkboxes work
- [ ] Timeline has entries
- [ ] Chat history persists after refresh

If all 6 pass → **Core functionality intact!**

---

## 🎯 **Next Steps After Testing**

### **If Zero Regression (All Pass):**
1. Mark Phase 2 as "Production Ready"
2. Deploy to production OR
3. Move to Phase 3: Continuous Learning

### **If Minor Issues (<3 bugs):**
1. Log bugs in backlog
2. Fix critical ones only
3. Proceed to Phase 3

### **If Major Regression (>5 bugs):**
1. Stop and analyze
2. Revert recent changes if needed
3. Fix systematically
4. Re-test before proceeding

---

**Created:** 2025-11-07
**Status:** Ready for execution
**Estimated Time:** 55 minutes (full suite) or 5 minutes (smoke test)




