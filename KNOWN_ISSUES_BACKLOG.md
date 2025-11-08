# Known Issues & Backlog

Track of identified issues, their root cause analysis, and prioritization for future fixes.

---

## 🐛 Active Issues

### Issue #1: 5-calorie discrepancy between Dashboard and Chat Progress Bar
**Severity:** Low  
**Priority:** P3 (Nice to have)  
**Reported:** 2024-11-06  
**Status:** Documented, Not Started  

#### **Symptoms:**
- Dashboard shows: **1663 kcal**
- Chat progress bar shows: **1658 kcal**
- Discrepancy: **5 kcal** (~0.3% difference)

#### **Root Cause Analysis:**

**Investigation Steps:**
1. Both dashboard and chat use `get_today_calories_realtime()` for real-time data
2. Both query the same Firestore collection: `users/{userId}/fitness_logs`
3. Both sum `log.calories` for `log_type == "meal"`

**Potential Root Causes (Ranked by Likelihood):**

1. **Rounding Inconsistencies (HIGH):**
   - Chat response generator rounds to integers: `int(calories)`
   - Dashboard may use `round(calories, 1)` or different rounding
   - Over 15+ logged items, small rounding differences accumulate
   - **Example:** 62.4 vs 62.5 kcal × 15 items = 1.5-7.5 kcal difference

2. **Query Timing Race Condition (MEDIUM):**
   - Dashboard query runs on page load
   - Chat query runs after message processing
   - If items are being saved asynchronously, queries might catch DB in different states
   - **Likelihood:** Low (both use synchronous realtime queries now)

3. **Subcollection vs Main Collection (LOW):**
   - Some items might be in old flat `fitness_logs` collection
   - Others in new `users/{userId}/fitness_logs` subcollection
   - Dashboard might aggregate both, chat only queries subcollection
   - **Likelihood:** Low (wipe all logs cleared everything)

4. **Cache Inconsistency (VERY LOW):**
   - Context service cache is bypassed for realtime queries
   - Both use same non-cached `get_today_calories_realtime()` method
   - **Likelihood:** Very low

5. **Floating Point Precision (VERY LOW):**
   - Python's float operations can introduce tiny errors
   - Over many additions: 1.1 + 1.1 + 1.1 != 3.3 exactly
   - **Likelihood:** Very low (would be < 0.1 kcal)

#### **Recommended Fix:**

**Option A: Standardize Rounding (1 hour)**
```python
# Everywhere in codebase, use consistent rounding:
calories = round(float(calories), 1)  # 1 decimal place
```
- Update `context_service.py`, `chat_response_generator.py`, dashboard calculations
- Ensure all calorie sums use same precision

**Option B: Single Source of Truth (2 hours)**
- Create a `CalorieService` that calculates daily totals ONCE
- Cache result for 10 seconds
- Both dashboard and chat query this service
- Guarantees exact same calculation

**Option C: Accept Minor Discrepancy (0 hours)**
- Document as "known minor variance"
- Add tooltip: "Slight differences due to rounding"
- Focus on more impactful features

#### **Workaround:**
None needed - discrepancy is negligible for user experience.

#### **Testing Plan (when fixed):**
1. Wipe all logs
2. Log 10 different items with decimal calories (e.g., 62.4 kcal)
3. Verify dashboard == chat progress bar
4. Repeat with 50+ items to test accumulation

---

## 📋 Backlog Items

*(Add future issues here)*

---

## ✅ Resolved Issues

*(Add resolved issues here for historical tracking)*

