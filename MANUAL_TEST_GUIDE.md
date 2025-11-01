# 🧪 Manual Testing Guide

**Ready for Testing!** All automated tests pass ✅

---

## 🔐 Test User Credentials

**Email:** `testuser@example.com`  
**Password:** `Test1234!`

---

## 📝 Test Scenarios

### 1. Simple Food Logging ✨
Test the basic food logging functionality.

**Input:** `2 boiled eggs`

**Expected:**
- 1 meal logged
- ~140 calories
- ~12g protein
- Meal type: breakfast/lunch/dinner (based on time)

---

### 2. Complex Multi-Food Input 🎯
Test the NEW multi-food parser!

**Input:** `i ate 2 eggs in the morning, 1 bowl of rice and curd for lunch, 5 pistachios afternoon, 200g spinach dinner`

**Expected:**
- 5-6 separate meals logged
- Each with correct meal type (breakfast/lunch/snack/dinner)
- Accurate macros for each:
  - 2 eggs: 140 cal, 12g protein
  - 1 bowl rice: 260 cal, 5.4g protein
  - 1 bowl curd: 120 cal, 7g protein
  - 5 pistachios: 15 cal, 0.6g protein
  - 200g spinach: 46 cal, 5.8g protein
- Total: ~841 calories

---

### 3. Indian Food 🇮🇳
Test the Indian food database.

**Input:** `2 rotis with dal`

**Expected:**
- 2 separate items or 1 combined meal
- Roti: ~120 cal each = 240 cal total
- Dal: ~210 cal (1 bowl)
- Total: ~450 calories

---

### 4. Meal Type Classification 🕐
Test automatic meal type detection.

**Input:** `breakfast: 2 eggs, lunch: chicken biryani, dinner: dal khichdi`

**Expected:**
- 3 separate meals
- Correctly classified as breakfast, lunch, dinner
- Each with accurate macros

---

### 5. Portion Sizes 📏
Test different portion formats.

**Inputs to try:**
- `100g chicken` → ~165 cal
- `1 bowl rice` → ~260 cal
- `2 rotis` → ~240 cal
- `5 almonds` → ~35 cal
- `1 banana` → ~105 cal

---

## ✅ Verification Checklist

After each test, verify:

- [ ] **Dashboard Updates:** Calories and macros update correctly
- [ ] **Meal Breakdown:** Meals show with correct type (breakfast/lunch/dinner/snack)
- [ ] **Macro Accuracy:** Protein/carbs/fat are reasonable
- [ ] **No Errors:** No "failed to retry" or crash messages
- [ ] **Response Time:** Chat responds in < 3 seconds
- [ ] **Multiple Foods:** Complex inputs split into separate meals

---

## 🐛 Known Limitations

1. **LLM Fallback:** If OpenAI API key is not configured, some foods may show as "estimated"
2. **Food Database:** Currently 50+ foods, expanding to 500+
3. **Preparation Methods:** "fried" vs "boiled" not yet fully implemented

---

## 📊 What to Look For

### ✅ Good Signs:
- Multiple meals from one input
- Accurate calorie counts (within 10%)
- Correct meal type classification
- Fast response times (< 3s)
- No crashes or errors

### ❌ Red Flags:
- All foods logged as one meal
- Wildly inaccurate calories (off by >50%)
- "Failed to retry" errors
- Slow responses (> 5s)
- Missing meal types

---

## 🎯 Success Criteria

**The chat assistant is working well if:**

1. ✅ Complex inputs split into 4+ separate meals
2. ✅ Meal types auto-detected correctly
3. ✅ Indian foods have accurate macros
4. ✅ Dashboard updates immediately
5. ✅ No crashes or errors

---

## 📝 Feedback Template

When testing, note:

```
Test: [Simple/Complex/Indian/etc.]
Input: [what you typed]
Result: [what happened]
Expected: [what should happen]
Issue: [if any]
```

**Example:**
```
Test: Complex Multi-Food
Input: "2 eggs morning, rice lunch"
Result: 2 separate meals logged correctly
Expected: 2 meals with breakfast/lunch types
Issue: None! ✅
```

---

## 🚀 Ready to Test!

1. Open: http://localhost:8080
2. Sign up with test credentials
3. Complete onboarding
4. Test the chat assistant
5. Report any issues

**All systems are GO! 🎉**

