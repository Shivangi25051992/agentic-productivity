# 🧪 Backend Testing Guide - Expandable Chat

**Date:** November 6, 2025  
**Backend:** Running on `http://localhost:8000`  
**Branch:** `feature/expandable-chat`

---

## 📋 Test Plan

We'll test **5 prompts** to verify:
1. ✅ Response includes expandable fields (summary, suggestion, details, expandable)
2. ✅ Post-processing is fast (< 1ms)
3. ✅ Performance maintained (~9.7s total)
4. ✅ Chat history saves correctly
5. ✅ Different categories work (meal, workout, water, task)
6. ✅ Backward compatibility (old messages still work)

---

## 🎯 Test Prompts

### **Test 1: Simple Meal (Cache Hit)**
**Input:** `"1 banana"`

**Expected Response:**
```json
{
  "items": [],
  "original": "1 banana",
  "message": "🍌 1 banana logged! 105 kcal\n\n...",
  
  // ✨ NEW FIELDS:
  "summary": "🍌 1 banana logged! 105 kcal",
  "suggestion": "Great potassium source! Add protein for satiety.",
  "details": {
    "nutrition": {
      "calories": 105,
      "protein_g": 1,
      "carbs_g": 27,
      "fat_g": 0
    },
    "progress": {
      "daily_calories": 105,
      "daily_goal": 2000,
      "remaining": 1895,
      "protein_today": 1,
      "progress_percent": 5.3
    },
    "insights": "Consider adding protein for a more balanced meal."
  },
  "expandable": true,
  "needs_clarification": false
}
```

**What to Verify:**
- ✅ `summary` is concise (< 100 chars)
- ✅ `suggestion` is relevant to context
- ✅ `details.nutrition` has all 4 macros
- ✅ `details.progress` shows daily totals
- ✅ `expandable` is `true`
- ✅ Response time < 10s

---

### **Test 2: Multi-Item Meal**
**Input:** `"2 eggs and bread for breakfast"`

**Expected Response:**
```json
{
  "summary": "🍳 2 eggs and bread logged! ~250 kcal",
  "suggestion": "Good start! Stay balanced throughout the day.",
  "details": {
    "nutrition": {
      "calories": 250,
      "protein_g": 15,
      "carbs_g": 30,
      "fat_g": 8
    },
    "progress": {
      "daily_calories": 250,
      "remaining": 1750,
      "progress_percent": 12.5
    }
  },
  "expandable": true
}
```

**What to Verify:**
- ✅ Multiple items handled correctly
- ✅ Calories summed correctly
- ✅ Meal type inferred (breakfast)
- ✅ Suggestion contextual (early in day)

---

### **Test 3: Multi-Category (Meal + Workout)**
**Input:** `"oatmeal and ran 5k"`

**Expected Response:**
- Primary category: `meal` or `workout` (based on order)
- Summary reflects primary category
- Suggestion relevant to both activities
- Details include both meal and workout data

**What to Verify:**
- ✅ Multi-category handled
- ✅ Primary category determined correctly
- ✅ Both items logged to DB
- ✅ Appropriate suggestion

---

### **Test 4: Complex Multi-Category**
**Input:** `"chicken salad, water, vitamin D"`

**Expected Response:**
- Primary category: `meal`
- Summary: Meal-focused
- Suggestion: Balanced/comprehensive
- Details include all 3 categories

**What to Verify:**
- ✅ 3 categories handled (meal, water, supplement)
- ✅ All items logged to DB
- ✅ Nutrition from meal only
- ✅ Water and supplement acknowledged

---

### **Test 5: Task (Non-Meal)**
**Input:** `"remind meal prep Sunday"`

**Expected Response:**
```json
{
  "summary": "📝 Task created: meal prep Sunday",
  "suggestion": "Task saved! You've got this! 📝",
  "details": {
    "items": [{
      "category": "task",
      "data": {
        "title": "meal prep Sunday"
      }
    }]
  },
  "expandable": true
}
```

**What to Verify:**
- ✅ Non-meal category works
- ✅ Task-specific summary
- ✅ Task-specific suggestion
- ✅ No nutrition data (expected)
- ✅ Task saved to DB

---

## 🚀 How to Test

### **Step 1: Open Chat in Browser**
1. Go to `http://localhost:9000` (Flutter app)
2. Make sure you're logged in
3. Open DevTools (F12) → Network tab
4. Filter for `/chat` endpoint

### **Step 2: Send Test Prompts**
Send each prompt one by one in the chat interface.

### **Step 3: Monitor Backend Logs**
```bash
tail -f /tmp/backend_expandable.log | grep -E "⏱️|✨|💾|summary|suggestion"
```

Look for:
- ⏱️ Timing logs (should show < 1ms for post-processing)
- ✨ NEW fields being created
- 💾 Save messages with expandable fields

### **Step 4: Check Response in DevTools**
In browser DevTools → Network → `/chat` response:
1. Verify all 4 new fields present
2. Check `summary` is concise
3. Check `suggestion` is relevant
4. Check `details` has nutrition/progress/insights
5. Check `expandable` is `true`

### **Step 5: Verify Chat History**
After sending all 5 prompts:
```bash
# Get chat history (use your auth token)
curl -X GET "http://localhost:8000/chat/history?limit=10" \
  -H "Authorization: Bearer YOUR_TOKEN" | jq
```

Verify:
- ✅ New messages have `summary`, `suggestion`, `details`, `expandable`
- ✅ Old messages (if any) still work without these fields
- ✅ All 5 prompts saved correctly

---

## 📊 Performance Checklist

For EACH test prompt, verify:

| Metric | Target | Pass/Fail |
|--------|--------|-----------|
| Response includes `summary` | Yes | [ ] |
| Response includes `suggestion` | Yes | [ ] |
| Response includes `details` | Yes | [ ] |
| Response includes `expandable` | Yes | [ ] |
| Summary is concise (< 100 chars) | Yes | [ ] |
| Suggestion is relevant | Yes | [ ] |
| Details has nutrition (if meal) | Yes | [ ] |
| Details has progress | Yes | [ ] |
| Total response time | < 10s | [ ] |
| Backend logs show timing | Yes | [ ] |
| Chat history saves correctly | Yes | [ ] |

---

## 🔍 What to Look For in Logs

**Good Signs (✅):**
```
⏱️ [abc123] STEP 6 - Generate response: 5ms
✨ Post-processing expandable fields...
💾 Saving AI message to history: user_id=xyz, message_length=450
⏱️ [abc123] ✅ TOTAL TIME: 9700ms
```

**Bad Signs (❌):**
```
⏱️ [abc123] STEP 6 - Generate response: 1000ms  // Too slow!
ERROR: KeyError: 'summary'  // Missing field!
⏱️ [abc123] ✅ TOTAL TIME: 15000ms  // Regression!
```

---

## 🐛 Common Issues & Fixes

### **Issue 1: Response missing expandable fields**
**Symptom:** Response has `message` but no `summary`, `suggestion`, etc.

**Fix:** Check if `items` is empty (expandable only for actionable items)

**Check:**
```python
# In app/services/chat_response_generator.py
if items:  # This condition determines if expandable
    summary = self._extract_summary(...)
```

### **Issue 2: Summary is too long**
**Symptom:** Summary is full response text

**Fix:** Check `_extract_summary` logic (first line extraction)

### **Issue 3: Suggestion is generic**
**Symptom:** Suggestion is always "Keep up the great work!"

**Fix:** Check `user_context` is being passed correctly

### **Issue 4: Response time increased**
**Symptom:** Total time > 10s

**Check:** Post-processing should be < 1ms. If higher, check helper functions.

### **Issue 5: Chat history doesn't save expandable fields**
**Symptom:** History only has `content`, no `summary`

**Fix:** Check `save_message` call in `/chat` endpoint includes new params

---

## ✅ Success Criteria

**Backend test is SUCCESSFUL if:**
- [ ] All 5 prompts return responses with expandable fields
- [ ] Summaries are concise and emoji-rich
- [ ] Suggestions are contextual and relevant
- [ ] Details include nutrition, progress, insights (where applicable)
- [ ] Response time averages ~9.7s (no regression)
- [ ] Chat history saves all new fields correctly
- [ ] No errors in backend logs
- [ ] Different categories work (meal, workout, water, supplement, task)

**If ALL criteria pass → Proceed to Frontend implementation**

**If ANY criteria fail → Debug and fix before proceeding**

---

## 🎯 Next After Testing

**If tests pass:**
1. ✅ Mark "Backend: Test with 5 test prompts" as complete
2. 🚀 Proceed to Frontend implementation
3. 📝 Create Flutter widgets for expandable UI

**If tests fail:**
1. 🐛 Review logs and identify issue
2. 🔧 Fix the specific helper function or endpoint
3. 🔄 Re-test until all criteria pass

---

## 📝 Test Results Template

Copy this and fill in after testing:

```
# Backend Test Results

**Date:** November 6, 2025
**Tester:** [Your Name]

## Test 1: "1 banana"
- Response time: _____ms
- Has summary: [ ] Yes [ ] No
- Has suggestion: [ ] Yes [ ] No
- Has details: [ ] Yes [ ] No
- Expandable: [ ] Yes [ ] No
- Notes: _____________________

## Test 2: "2 eggs and bread for breakfast"
- Response time: _____ms
- Has summary: [ ] Yes [ ] No
- Multi-item handled: [ ] Yes [ ] No
- Notes: _____________________

## Test 3: "oatmeal and ran 5k"
- Response time: _____ms
- Multi-category handled: [ ] Yes [ ] No
- Notes: _____________________

## Test 4: "chicken salad, water, vitamin D"
- Response time: _____ms
- 3 categories handled: [ ] Yes [ ] No
- Notes: _____________________

## Test 5: "remind meal prep Sunday"
- Response time: _____ms
- Task category works: [ ] Yes [ ] No
- Notes: _____________________

## Overall
- Average response time: _____ms
- Performance regression: [ ] Yes [ ] No
- All tests passed: [ ] Yes [ ] No
- Ready for frontend: [ ] Yes [ ] No

## Issues Found:
1. _____________________
2. _____________________

## Conclusion:
[ ] PASS - Proceed to frontend
[ ] FAIL - Fix issues before proceeding
```

---

**Ready to test! Let me know when you start, and I'll monitor the logs with you! 🚀**

