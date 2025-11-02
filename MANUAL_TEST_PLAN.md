# 🧪 Manual Test Plan - P0 Bug Fixes
**Date**: November 2, 2025  
**Tester**: User  
**Environment**: Production (https://productivityai-mvp.web.app)

---

## ⚠️ IMPORTANT: Test on PRODUCTION Before Deploying Changes

**Current Status**: Changes are ready but NOT deployed yet  
**Action Required**: Test existing functionality FIRST, then deploy fixes

---

## 📋 PRE-DEPLOYMENT TESTS (Test Current Production)

### Test 1: Verify Existing Meal Logging Works
**Purpose**: Ensure current production is working before we deploy changes

**Steps**:
1. Open app: https://productivityai-mvp.web.app
2. Login with your credentials
3. Navigate to "AI Assistant" (chat screen)
4. Type: `2 eggs for breakfast`
5. Send message

**Expected Result**:
- ✅ Message sent successfully
- ✅ AI responds with confirmation
- ✅ Meal card appears showing "2 eggs for breakfast"
- ✅ Macros displayed: ~140 cal, ~12g protein
- ✅ Meal appears in home screen timeline

**Actual Result**: ________________

**Status**: ☐ PASS  ☐ FAIL

---

### Test 2: Verify Multi-line Logging Works
**Steps**:
1. In chat, type:
```
2 eggs
toast
coffee
```
2. Send message

**Expected Result**:
- ✅ AI logs all 3 items separately
- ✅ Each item shows in timeline
- ✅ Macros calculated for each

**Actual Result**: ________________

**Status**: ☐ PASS  ☐ FAIL

---

### Test 3: Verify Chat History Persists
**Steps**:
1. Send a message in chat
2. Navigate away (go to Home screen)
3. Return to AI Assistant

**Expected Result**:
- ✅ Previous messages still visible
- ✅ Chat history loaded

**Actual Result**: ________________

**Status**: ☐ PASS  ☐ FAIL

---

### Test 4: Verify Mobile Back Button (Current Bug)
**Device**: iOS Safari (PWA mode - added to home screen)

**Steps**:
1. Open app from home screen icon
2. Navigate to AI Assistant
3. Click back arrow in top-left

**Expected Result (Current Bug)**:
- ❌ White page appears
- ❌ Can't navigate back to home

**Actual Result**: ________________

**Status**: ☐ BUG CONFIRMED  ☐ ALREADY FIXED

---

### Test 5: Verify AI Hallucination (Current Bug)
**Steps**:
1. In chat, type: `create a diet plan for me`
2. Send message

**Expected Result (Current Bug)**:
- ❌ AI creates fake diet plan
- ❌ AI suggests meals (feature doesn't exist)
- ❌ User gets confused

**Actual Result**: ________________

**Status**: ☐ BUG CONFIRMED  ☐ ALREADY FIXED

---

## 🚀 POST-DEPLOYMENT TESTS (After Deploying Fixes)

### Fix 1: Mobile Back Button - REGRESSION TEST

#### Test 6: Desktop Browser Back Button
**Device**: Desktop (Chrome/Safari/Firefox)

**Steps**:
1. Navigate: Home → AI Assistant
2. Click back arrow
3. Verify you return to Home screen

**Expected Result**:
- ✅ Returns to Home screen
- ✅ No white page
- ✅ Home screen shows all data (macros, timeline, etc.)

**Actual Result**: ________________

**Status**: ☐ PASS  ☐ FAIL

---

#### Test 7: iOS Safari Back Button (PWA)
**Device**: iPhone with app added to home screen

**Steps**:
1. Open app from home screen icon
2. Navigate to AI Assistant
3. Click back arrow in top-left

**Expected Result**:
- ✅ Returns to Home screen
- ✅ NO white page (bug fixed!)
- ✅ Home screen shows all data

**Actual Result**: ________________

**Status**: ☐ PASS  ☐ FAIL

---

#### Test 8: Android Chrome Back Button (PWA)
**Device**: Android with app added to home screen

**Steps**:
1. Open app from home screen icon
2. Navigate to AI Assistant
3. Click back arrow

**Expected Result**:
- ✅ Returns to Home screen
- ✅ No white page
- ✅ Home screen shows all data

**Actual Result**: ________________

**Status**: ☐ PASS  ☐ FAIL

---

#### Test 9: Navigation from Profile → Chat → Back
**Steps**:
1. Navigate: Home → Profile
2. Navigate: Profile → AI Assistant
3. Click back arrow

**Expected Result**:
- ✅ Returns to Home screen (not Profile)
- ⚠️ Note: This is expected behavior with pushReplacementNamed

**Actual Result**: ________________

**Status**: ☐ PASS  ☐ FAIL

---

### Fix 2: AI Guardrails - REGRESSION TEST

#### Test 10: Basic Meal Logging Still Works
**Steps**:
1. In chat, type: `2 eggs for breakfast`
2. Send message

**Expected Result**:
- ✅ AI logs meal correctly
- ✅ Meal type: breakfast
- ✅ Macros: ~140 cal, ~12g protein
- ✅ Meal appears in timeline

**Actual Result**: ________________

**Status**: ☐ PASS  ☐ FAIL

---

#### Test 11: Multi-line Logging Still Works
**Steps**:
1. In chat, type:
```
2 eggs
toast
coffee
```
2. Send message

**Expected Result**:
- ✅ All 3 items logged
- ✅ Each item in timeline
- ✅ Macros calculated

**Actual Result**: ________________

**Status**: ☐ PASS  ☐ FAIL

---

#### Test 12: Typo Correction Still Works
**Steps**:
1. In chat, type: `omlet and banan`
2. Send message

**Expected Result**:
- ✅ AI corrects: omlet → omelet
- ✅ AI corrects: banan → banana
- ✅ Items logged correctly

**Actual Result**: ________________

**Status**: ☐ PASS  ☐ FAIL

---

#### Test 13: Explicit Meal Type Respected
**Steps**:
1. In chat, type: `2 eggs for lunch`
2. Send message
3. Check meal type in timeline

**Expected Result**:
- ✅ Meal type: LUNCH (not breakfast!)
- ✅ AI respects explicit user input

**Actual Result**: ________________

**Status**: ☐ PASS  ☐ FAIL

---

#### Test 14: Time-based Inference Still Works
**Steps**:
1. At 8:00 AM, type: `2 eggs`
2. Send message
3. Check meal type

**Expected Result**:
- ✅ Meal type: breakfast (inferred from time)

**Actual Result**: ________________

**Status**: ☐ PASS  ☐ FAIL

---

#### Test 15: AI Rejects Unsupported Feature (Diet Plan)
**Steps**:
1. In chat, type: `create a diet plan for me`
2. Send message

**Expected Result**:
- ✅ AI responds with friendly message
- ✅ Message mentions "coming soon" or "not supported yet"
- ✅ AI suggests logging meals instead
- ✅ NO fake diet plan created
- ✅ NO items logged

**Example Response**:
> "I love that question! 🎯 Right now, I'm focused on helping you log meals and track your macros. Diet plans are coming soon - we're building something exciting! For now, I can help you log what you eat and track your progress. What would you like to log today?"

**Actual Result**: ________________

**Status**: ☐ PASS  ☐ FAIL

---

#### Test 16: AI Rejects Unsupported Feature (Meal Suggestions)
**Steps**:
1. In chat, type: `suggest meals for today`
2. Send message

**Expected Result**:
- ✅ AI responds with friendly message
- ✅ Message mentions "coming soon"
- ✅ AI suggests logging meals instead
- ✅ NO meal suggestions provided
- ✅ NO items logged

**Actual Result**: ________________

**Status**: ☐ PASS  ☐ FAIL

---

#### Test 17: AI Rejects Unsupported Feature (Workout Plan)
**Steps**:
1. In chat, type: `create a workout plan for me`
2. Send message

**Expected Result**:
- ✅ AI responds with friendly message
- ✅ Message mentions "coming soon"
- ✅ NO workout plan created

**Actual Result**: ________________

**Status**: ☐ PASS  ☐ FAIL

---

### Fix 3: Locked Areas - NO REGRESSION

#### Test 18: Dashboard Still Works
**Steps**:
1. Navigate to Home screen
2. Verify all sections visible

**Expected Result**:
- ✅ Macro bars visible (protein, carbs, fat)
- ✅ Calorie progress visible
- ✅ Today's meals section visible
- ✅ Timeline visible
- ✅ Data loads correctly

**Actual Result**: ________________

**Status**: ☐ PASS  ☐ FAIL

---

#### Test 19: Timeline View Still Works
**Steps**:
1. Log a meal via chat
2. Go to Home screen
3. Check timeline

**Expected Result**:
- ✅ Meal appears in timeline
- ✅ Meal card is expandable
- ✅ Clicking card shows details
- ✅ Macros displayed correctly

**Actual Result**: ________________

**Status**: ☐ PASS  ☐ FAIL

---

#### Test 20: Profile Still Works
**Steps**:
1. Navigate to Profile
2. Verify data loads

**Expected Result**:
- ✅ User name visible
- ✅ Email visible
- ✅ Goals visible
- ✅ Preferences visible

**Actual Result**: ________________

**Status**: ☐ PASS  ☐ FAIL

---

## 📊 TEST SUMMARY

### Pre-Deployment Tests (Current Production)
- Test 1: ☐ PASS  ☐ FAIL
- Test 2: ☐ PASS  ☐ FAIL
- Test 3: ☐ PASS  ☐ FAIL
- Test 4: ☐ BUG CONFIRMED
- Test 5: ☐ BUG CONFIRMED

### Post-Deployment Tests (After Fix)
**Fix 1: Mobile Back Button**
- Test 6: ☐ PASS  ☐ FAIL
- Test 7: ☐ PASS  ☐ FAIL
- Test 8: ☐ PASS  ☐ FAIL
- Test 9: ☐ PASS  ☐ FAIL

**Fix 2: AI Guardrails**
- Test 10: ☐ PASS  ☐ FAIL
- Test 11: ☐ PASS  ☐ FAIL
- Test 12: ☐ PASS  ☐ FAIL
- Test 13: ☐ PASS  ☐ FAIL
- Test 14: ☐ PASS  ☐ FAIL
- Test 15: ☐ PASS  ☐ FAIL
- Test 16: ☐ PASS  ☐ FAIL
- Test 17: ☐ PASS  ☐ FAIL

**Fix 3: No Regression**
- Test 18: ☐ PASS  ☐ FAIL
- Test 19: ☐ PASS  ☐ FAIL
- Test 20: ☐ PASS  ☐ FAIL

---

## ✅ DEPLOYMENT DECISION

**Total Tests**: 20  
**Passed**: ___ / 20  
**Failed**: ___ / 20  
**Pass Rate**: ___%

**Decision**:
- ☐ ✅ APPROVED - Deploy to production
- ☐ ❌ REJECTED - Fix issues first
- ☐ ⚠️ CONDITIONAL - Deploy with monitoring

**Notes**: ________________________________________________

---

## 🚀 DEPLOYMENT STEPS (If Approved)

1. **Commit changes**:
```bash
git add -A
git commit -m "fix: P0 bugs - mobile back button + AI guardrails"
git push origin main
```

2. **Deploy backend**:
```bash
./auto_deploy.sh cloud
```

3. **Deploy frontend**:
```bash
cd flutter_app
flutter build web --release
firebase deploy --only hosting
```

4. **Monitor logs**:
- Check Cloud Run logs for errors
- Monitor user feedback
- Watch for new bug reports

5. **Rollback if needed**:
```bash
git revert HEAD
./auto_deploy.sh cloud
```

---

## 📝 TEST DATA

**Test Account**:
- Email: shivganga25shingatwar@gmail.com
- Password: [Your password]

**Test Devices**:
- Desktop: Chrome, Safari, Firefox
- Mobile: iOS Safari (PWA), Android Chrome (PWA)

**Test Meals**:
- Simple: "2 eggs for breakfast"
- Multi-line: "2 eggs\ntoast\ncoffee"
- Typos: "omlet and banan"
- Explicit: "2 eggs for lunch"
- Time-based: "2 eggs" (at 8am)

**Test Unsupported Features**:
- "create a diet plan for me"
- "suggest meals for today"
- "create a workout plan for me"
- "track my stocks"

---

**Tester Signature**: ________________  
**Date**: ________________  
**Time**: ________________

---

*Created: November 2, 2025*  
*Version: 1.0*  
*Status: Ready for Testing*

