# Phase 1: Agentic AI Manual Testing Guide

**Date:** November 6, 2025  
**Feature:** LLM Router Integration with Chat Classification  
**Goal:** Verify zero regression and multi-provider routing works correctly

---

## 🎯 Testing Objectives

1. ✅ **Router initializes successfully** on backend startup
2. ✅ **Chat classification works** with router
3. ✅ **Fallback to OpenAI works** if router fails
4. ✅ **All chat categories work** (meal, workout, water, supplement)
5. ✅ **Multi-item parsing works** (multiple items in one message)
6. ✅ **Existing functionality preserved** (zero regression)

---

## 📋 Pre-Test Checklist

### Step 1: Check Environment Variables

```bash
cd /Users/pchintanwar/Documents/Projects-AIProductivity/agentic-productivity
cat .env | grep OPENAI_API_KEY
```

**Expected:** You should see your OpenAI API key (not empty)

### Step 2: Verify Branch

```bash
git branch
```

**Expected:** Should show `* feature/phase1-agentic-ai-foundation`

### Step 3: Check Latest Commit

```bash
git log --oneline -1
```

**Expected:** `100263ac feat(llm): Phase 1 COMPLETE - Chat Integration with Zero Regression`

---

## 🚀 Part 1: Backend Startup Test

### Step 1: Start Backend

```bash
cd /Users/pchintanwar/Documents/Projects-AIProductivity/agentic-productivity
source venv/bin/activate
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

### Step 2: Watch for Router Initialization

**Look for this log line:**

```
✅ [AGENTIC AI] LLM Router initialized successfully
```

**✅ PASS:** If you see this line  
**⚠️ FALLBACK:** If you see "Router initialization failed" - that's OK, it falls back to direct OpenAI  
**❌ FAIL:** If backend crashes or doesn't start

---

## 📱 Part 2: Frontend Setup

### Step 1: Open New Terminal

```bash
cd /Users/pchintanwar/Documents/Projects-AIProductivity/agentic-productivity/flutter_app
flutter run -d chrome
```

### Step 2: Wait for App to Load

**Expected:** App opens in Chrome, login screen appears

### Step 3: Login

- Use your Firebase credentials
- Navigate to **Chat** tab

---

## 🧪 Part 3: Chat Classification Tests

### Test Case 1: Simple Meal Entry (Breakfast)

**Input (Chat):**
```
2 eggs for breakfast
```

**Expected Backend Logs:**
```
🤖 [AGENTIC AI] Using LLM Router for chat classification
✅ [AGENTIC AI] Router success! Provider: openai, Tokens: ~150
```

**Expected Frontend:**
- ✅ Message sent successfully
- ✅ AI responds with confirmation
- ✅ Meal appears in dashboard (if you check Nutrition tab)

**What to Check:**
- [ ] Backend shows router logs
- [ ] No errors in backend
- [ ] No errors in frontend console
- [ ] AI responds appropriately

---

### Test Case 2: Workout Entry

**Input (Chat):**
```
ran 5km
```

**Expected Backend Logs:**
```
🤖 [AGENTIC AI] Using LLM Router for chat classification
✅ [AGENTIC AI] Router success! Provider: openai, Tokens: ~120
```

**Expected Frontend:**
- ✅ Workout logged
- ✅ AI confirms with calories burned estimate

**What to Check:**
- [ ] Router used successfully
- [ ] Workout category detected
- [ ] Duration and calories estimated

---

### Test Case 3: Water Tracking

**Input (Chat):**
```
drank 2 glasses of water
```

**Expected Backend Logs:**
```
🤖 [AGENTIC AI] Using LLM Router for chat classification
✅ [AGENTIC AI] Router success! Provider: openai, Tokens: ~100
```

**Expected Frontend:**
- ✅ Water logged (500ml)
- ✅ AI confirms quantity

**What to Check:**
- [ ] Water category detected
- [ ] Quantity converted to ml correctly
- [ ] Zero calories logged

---

### Test Case 4: Supplement Tracking

**Input (Chat):**
```
took vitamin d 1000 IU
```

**Expected Backend Logs:**
```
🤖 [AGENTIC AI] Using LLM Router for chat classification
✅ [AGENTIC AI] Router success! Provider: openai, Tokens: ~110
```

**Expected Frontend:**
- ✅ Supplement logged
- ✅ Dosage captured

**What to Check:**
- [ ] Supplement category detected
- [ ] Dosage captured correctly
- [ ] Minimal calories (5 kcal)

---

### Test Case 5: Multi-Item Entry (CRITICAL TEST)

**Input (Chat):**
```
2 eggs for breakfast
ran 5km
1 multivitamin tablet
drank 2 glasses of water
```

**Expected Backend Logs:**
```
🤖 [AGENTIC AI] Using LLM Router for chat classification
✅ [AGENTIC AI] Router success! Provider: openai, Tokens: ~250
```

**Expected Frontend:**
- ✅ ALL 4 items parsed separately
- ✅ 1 meal, 1 workout, 1 supplement, 1 water

**What to Check:**
- [ ] All 4 items detected
- [ ] Each item categorized correctly
- [ ] All items saved to dashboard

---

### Test Case 6: Clarification Needed

**Input (Chat):**
```
ate rice
```

**Expected Backend Logs:**
```
🤖 [AGENTIC AI] Using LLM Router for chat classification
✅ [AGENTIC AI] Router success! Provider: openai, Tokens: ~130
```

**Expected Frontend:**
- ✅ AI asks for clarification: "How much rice did you eat?"
- ✅ User can respond with quantity

**What to Check:**
- [ ] Clarification question asked
- [ ] Item still parsed (but low confidence)
- [ ] Can provide follow-up answer

---

### Test Case 7: Complex Meal with Details

**Input (Chat):**
```
grilled chicken breast 200g with brown rice 1 cup and steamed broccoli
```

**Expected Backend Logs:**
```
🤖 [AGENTIC AI] Using LLM Router for chat classification
✅ [AGENTIC AI] Router success! Provider: openai, Tokens: ~200
```

**Expected Frontend:**
- ✅ All 3 food items parsed
- ✅ Preparation methods captured (grilled, steamed)
- ✅ Quantities captured (200g, 1 cup)
- ✅ Total calories calculated

**What to Check:**
- [ ] Multiple food items split correctly
- [ ] Preparation methods captured
- [ ] Quantities parsed correctly
- [ ] Reasonable calorie estimates

---

## 🔄 Part 4: Fallback Testing (CRITICAL)

### Test Case 8: Router Fallback (Simulate Failure)

**Setup:** We'll temporarily break the router to test fallback

**Step 1: Stop Backend** (Ctrl+C)

**Step 2: Edit main.py temporarily**

```bash
# Open app/main.py
# Find line ~95: _llm_router = LLMRouter(db=dbsvc.get_firestore_client())
# Comment it out and force it to None:

# _llm_router = LLMRouter(db=dbsvc.get_firestore_client())
_llm_router = None  # Force fallback test
```

**Step 3: Restart Backend**

```bash
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

**Expected Logs:**
```
⚠️ [AGENTIC AI] LLM Router initialization failed (falling back to direct OpenAI): ...
```

**Step 4: Test Chat**

**Input:**
```
2 eggs for breakfast
```

**Expected:**
- ✅ **NO router logs** (router is None)
- ✅ Chat still works perfectly
- ✅ Uses direct OpenAI (existing code path)
- ✅ Same result as before

**What to Check:**
- [ ] No router logs appear
- [ ] Chat functionality unchanged
- [ ] No errors
- [ ] Results identical to with router

**Step 5: Restore main.py**

```bash
# Uncomment the router initialization
_llm_router = LLMRouter(db=dbsvc.get_firestore_client())
# _llm_router = None  # Force fallback test
```

**Step 6: Restart Backend**

**Expected:**
```
✅ [AGENTIC AI] LLM Router initialized successfully
```

---

## 📊 Part 5: Verify Data Persistence

### Test: Check Dashboard After Chat

**Step 1: Send a meal via chat**
```
grilled chicken 200g for lunch
```

**Step 2: Navigate to Nutrition/Dashboard tab**

**Expected:**
- ✅ Meal appears in today's log
- ✅ Correct calories and macros
- ✅ Correct meal type (lunch)

**What to Check:**
- [ ] Data saved to Firestore
- [ ] Appears in dashboard
- [ ] Correct timestamp
- [ ] Correct meal type

---

## 🔍 Part 6: Backend Logs Analysis

### What Good Logs Look Like

**Router Success:**
```
INFO:     127.0.0.1:xxxxx - "POST /chat HTTP/1.1" 200 OK
🤖 [AGENTIC AI] Using LLM Router for chat classification
✅ [AGENTIC AI] Router success! Provider: openai, Tokens: 150
```

**Router Fallback (if Firestore config missing):**
```
⚠️ [AGENTIC AI] Router failed, falling back to direct OpenAI: No active providers found
# ... then chat continues normally with OpenAI
```

**Router Not Initialized:**
```
⚠️ [AGENTIC AI] LLM Router initialization failed (falling back to direct OpenAI): ...
# ... then all chats use direct OpenAI
```

### What Bad Logs Look Like

**❌ FAIL - Chat Returns Error:**
```
ERROR:     Exception in ASGI application
# ... stack trace ...
```

**❌ FAIL - 500 Internal Server Error:**
```
INFO:     127.0.0.1:xxxxx - "POST /chat HTTP/1.1" 500 Internal Server Error
```

**❌ FAIL - Frontend Shows Error:**
```
Failed to send message
```

---

## ✅ Success Criteria Checklist

### Router Integration
- [ ] Backend starts successfully
- [ ] Router initialization logs appear
- [ ] Router is used for chat classification
- [ ] Provider and token usage logged

### Chat Functionality (Zero Regression)
- [ ] Meal entry works (breakfast/lunch/dinner/snack)
- [ ] Workout entry works
- [ ] Water tracking works
- [ ] Supplement tracking works
- [ ] Multi-item entry works (4+ items)
- [ ] Clarification flow works
- [ ] Complex meals parse correctly

### Fallback Safety
- [ ] Router failure falls back to OpenAI
- [ ] Chat works when router is None
- [ ] No errors when router unavailable
- [ ] Same results with/without router

### Data Persistence
- [ ] Meals saved to Firestore
- [ ] Appear in dashboard/nutrition tab
- [ ] Correct timestamps
- [ ] Correct categories and macros

### Error Handling
- [ ] No 500 errors
- [ ] No frontend crashes
- [ ] No backend crashes
- [ ] Graceful error messages (if any)

---

## 🐛 Troubleshooting

### Issue: Router Initialization Failed

**Possible Causes:**
1. Firestore connection issue
2. LLM config collection doesn't exist
3. No active providers configured

**Solution:**
- This is **EXPECTED** if you haven't added provider configs to Firestore yet
- Chat will fall back to direct OpenAI (existing behavior)
- To fix: Add provider configs to Firestore (see Phase 1 docs)

### Issue: "No active providers found"

**Possible Causes:**
- No LLM provider configs in Firestore
- All providers have `is_active: false`

**Solution:**
- Router falls back to OpenAI automatically
- To enable routing: Add provider configs to Firestore

### Issue: Chat Takes Longer Than Before

**Possible Cause:**
- Router tries Firestore lookup first (adds ~50-100ms)

**Expected Behavior:**
- First call: ~300-500ms (Firestore + OpenAI)
- Subsequent calls: ~250-400ms (cache hit)
- This is acceptable for multi-provider benefits

### Issue: Chat Returns 500 Error

**NOT EXPECTED** - This indicates a bug

**Steps:**
1. Check backend logs for full error
2. Copy error message
3. Share with developer
4. Test fallback (set `_llm_router = None`)

---

## 📝 Test Results Template

### Test Session Report

**Date:** _______________  
**Tester:** _______________  
**Branch:** `feature/phase1-agentic-ai-foundation`  
**Commit:** `100263ac`

#### Router Status
- [ ] Router initialized successfully
- [ ] Router used for classification
- [ ] Fallback tested and works

#### Chat Tests
- [ ] Test 1: Simple meal (PASS/FAIL)
- [ ] Test 2: Workout (PASS/FAIL)
- [ ] Test 3: Water (PASS/FAIL)
- [ ] Test 4: Supplement (PASS/FAIL)
- [ ] Test 5: Multi-item (PASS/FAIL)
- [ ] Test 6: Clarification (PASS/FAIL)
- [ ] Test 7: Complex meal (PASS/FAIL)
- [ ] Test 8: Fallback (PASS/FAIL)

#### Data Persistence
- [ ] Meals saved correctly (PASS/FAIL)
- [ ] Dashboard updated (PASS/FAIL)

#### Overall Result
- [ ] ✅ ALL TESTS PASSED - Zero regression confirmed
- [ ] ⚠️ SOME TESTS FAILED - Details: _______________
- [ ] ❌ CRITICAL FAILURE - Details: _______________

**Notes:**
_______________________________________________
_______________________________________________
_______________________________________________

---

## 🚀 Next Steps After Testing

### If All Tests Pass ✅
1. Merge feature branch to main
2. Deploy to staging/production
3. Monitor LLM usage in Firestore
4. Move to Phase 2 (Agentic Meal Planning)

### If Tests Fail ⚠️
1. Document failures in Test Results Template
2. Share with developer
3. Fix issues
4. Re-test

---

## 📞 Support

**Issues or Questions?**
- Check troubleshooting section above
- Review backend logs
- Check frontend console
- Document exact error messages

---

**Ready to start testing? Follow Part 1 above! 🎉**

