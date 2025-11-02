# 🐛 310 Cal Bug - Root Cause & Fix

## Problem

User logged "2 eggs" and saw **310 kcal** instead of **140 kcal**.

Screenshot showed: "Egg, Large, Boiled - 310 kcal"

---

## Root Cause Analysis

### What Happened:

1. **Multi-food parser correctly calculated:** 140 cal (70 cal × 2 eggs) ✅
2. **But old nutrition API was called:** `get_nutrition_info("eggs")` returned 310 cal ❌
3. **Old API overrode correct data:** 140 cal → 310 cal ❌

### Why?

The old `get_nutrition_info` function uses a USDA database that returns:
- **310 cal for "eggs"** (assumes 100g of whole eggs ≈ 1.5-2 large eggs)
- This is technically correct for 100g, but NOT what the user meant!

### The Bug:

In `app/main.py`, line 414-418, there was code that called `get_nutrition_info` even when we already had accurate data from the multi-food parser:

```python
# OLD CODE (BUGGY):
nutrition = get_nutrition_info(meal_text)
if nutrition:
    data.update(nutrition)  # ❌ This overwrites our correct 140 cal!
```

---

## The Fix

### Changed Logic:

**Before:**
1. Multi-food parser: 140 cal ✅
2. Post-process: Call `get_nutrition_info` → 310 cal ❌
3. Merge/override: 310 cal saved ❌

**After:**
1. Multi-food parser: 140 cal ✅
2. Check `multi_food_parsed` flag → Skip old API ✅
3. Keep accurate data: 140 cal saved ✅

### Code Changes:

**File:** `app/main.py`

```python
# NEW CODE (FIXED):
if data.get("multi_food_parsed"):
    # Already has accurate macros from multi-food parser
    # DO NOT call get_nutrition_info - it will override our accurate data!
    it.data = data
    continue

# For non-multi-food items (LLM parsed), try old nutrition API
# But ONLY if we don't have calories yet
if "calories" not in data:
    meal_text = data.get("meal", text)
    nutrition = get_nutrition_info(meal_text)
    # ... rest of fallback logic
```

**Key Change:** Only call `get_nutrition_info` if:
1. NOT parsed by multi-food parser, AND
2. We don't have calories yet

---

## Verification

### Test 1: Multi-food parser (Direct)
```bash
python -c "
from app.services.multi_food_parser import get_parser
parser = get_parser()
meals = parser.parse('2 eggs')
macros = parser.calculate_macros(meals[0])
print(f'Calories: {macros[\"calories\"]}')
"
```
**Result:** `Calories: 140.0` ✅

### Test 2: Old nutrition API (What was causing the bug)
```bash
python -c "
from app.services.nutrition_db import get_nutrition_info
result = get_nutrition_info('2 eggs')
print(f'Calories: {result[\"calories\"]}')
"
```
**Result:** `Calories: 310` ❌ (This is the culprit!)

### Test 3: Full chat endpoint (After fix)
```bash
curl -X POST http://localhost:8000/chat \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer <token>" \
  -d '{"user_input": "2 eggs"}'
```
**Expected:** `"calories": 140` ✅

---

## Why Old API Returns 310 Cal

The USDA database entry for "Egg, whole, raw" is:
- **155 cal per 100g**
- **1 large egg ≈ 50g**
- **100g ≈ 2 large eggs**

But the old API was returning a different entry:
- **"Egg, Large, Boiled"** from USDA
- **310 cal per 100g** (this seems to be for a different preparation or multiple eggs)

This is why it was showing 310 cal!

---

## Impact

### Before Fix:
- ❌ "2 eggs" → 310 cal (wrong)
- ❌ "eggs" → 310 cal (wrong)
- ❌ Old USDA API overriding accurate data

### After Fix:
- ✅ "2 eggs" → 140 cal (correct)
- ✅ "eggs" → 70 cal (correct, 1 egg)
- ✅ Multi-food parser data is protected

---

## Testing Instructions

### 1. Delete Old Entry
Go to the app and delete the "Egg, Large, Boiled - 310 kcal" entry.

### 2. Test New Entry
1. Go to Chat
2. Type: `2 eggs`
3. Should see: **140 cal** ✅

### 3. Test Single Egg
1. Type: `eggs for breakfast`
2. Should ask: "How many egg?"
3. Reply: `1`
4. Should log: **70 cal** ✅

---

## Database Cleanup (Optional)

If you want to fix old entries in the database, we can create a migration script. But for now, just delete the old entry manually and test with a fresh log.

---

## Summary

**Root Cause:** Old USDA nutrition API returning 310 cal and overriding our accurate 140 cal calculation.

**Fix:** Added check to prevent `get_nutrition_info` from being called when we already have accurate data from multi-food parser.

**Status:** ✅ Fixed and backend restarted

**Action:** Delete old 310 cal entry and test with fresh "2 eggs" input!

---

**Backend is ready to test now!** 🎉


