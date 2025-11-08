# 🧪 Performance Test Suite - Chat Classification

## Test Execution Plan

### How to Run Tests:
1. Send each prompt in chat (one at a time)
2. Wait for response
3. Check timing logs immediately after each test

### Command to View Timing:
```bash
tail -50 /tmp/backend.log | grep "⏱️" | tail -10
```

---

## 🎯 Test Cases

### **Test 1: Single Food Item (Cache Hit)**
**Prompt:** `1 banana`

**Expected Behavior:**
- ✅ Cache HIT (banana in food database)
- ⏱️ No LLM call (STEP 3 = 0ms)
- 📊 Fast response

**Expected Timing:**
```
STEP 1 - Save user message:   ~2000ms ❌ (needs fix)
STEP 2 - Cache lookup:         ~300ms  ✅ (CACHE HIT)
STEP 3 - LLM classification:   0ms     ✅ (SKIPPED)
STEP 4 - DB persistence:       ~300ms  ✅
STEP 5 - Get user context:     ~1000ms ⚠️
STEP 6 - Generate response:    <10ms   ✅
STEP 7 - Save AI response:     ~1000ms ❌ (needs fix)
───────────────────────────────────────
TOTAL: 4-5 seconds
```

**Focus:** Tests cache efficiency + Firestore bottleneck

---

### **Test 2: Multiple Foods**
**Prompt:** `2 eggs and 1 slice of bread for breakfast`

**Expected Behavior:**
- ⚠️ Likely Cache MISS (combo requires parsing)
- ⏱️ LLM call needed (STEP 3 = 8-12s)
- 📊 Multiple items grouped into one meal

**Expected Timing:**
```
STEP 1 - Save user message:   ~2000ms ❌
STEP 2 - Cache lookup:         ~500ms  ⚠️ (might try fuzzy match)
STEP 3 - LLM classification:   8000-12000ms ⚠️ (OpenAI call)
STEP 4 - DB persistence:       ~400ms  ✅
STEP 5 - Get user context:     ~1000ms ⚠️
STEP 6 - Generate response:    <10ms   ✅
STEP 7 - Save AI response:     ~1000ms ❌
───────────────────────────────────────
TOTAL: 15-20 seconds
```

**Focus:** Tests LLM performance + multi-item parsing

---

### **Test 3: Multi-Category (Meal + Workout)**
**Prompt:** `had oatmeal for breakfast and ran 5k`

**Expected Behavior:**
- ❌ Cache MISS (complex, multi-category)
- ⏱️ LLM classification required
- 📊 Creates 2 separate logs (1 meal + 1 workout)

**Expected Timing:**
```
STEP 1 - Save user message:   ~2000ms ❌
STEP 2 - Cache lookup:         ~200ms  ✅ (quick miss)
STEP 3 - LLM classification:   8000-12000ms ⚠️
STEP 4 - DB persistence:       ~500ms  ⚠️ (2 logs)
STEP 5 - Get user context:     ~1000ms ⚠️
STEP 6 - Generate response:    <10ms   ✅
STEP 7 - Save AI response:     ~1000ms ❌
───────────────────────────────────────
TOTAL: 15-20 seconds
```

**Focus:** Tests multi-category parsing + multiple DB writes

---

### **Test 4: Complex Multi-Category (Meal + Water + Supplement)**
**Prompt:** `grilled chicken salad, 2 glasses of water, and vitamin D`

**Expected Behavior:**
- ❌ Cache MISS (complex combo)
- ⏱️ LLM classification with multiple categories
- 📊 Creates 3 separate logs (meal, water, supplement)

**Expected Timing:**
```
STEP 1 - Save user message:   ~2000ms ❌
STEP 2 - Cache lookup:         ~200ms  ✅
STEP 3 - LLM classification:   10000-15000ms ❌ (complex parse)
STEP 4 - DB persistence:       ~600ms  ⚠️ (3 logs)
STEP 5 - Get user context:     ~1000ms ⚠️
STEP 6 - Generate response:    <10ms   ✅
STEP 7 - Save AI response:     ~1000ms ❌
───────────────────────────────────────
TOTAL: 18-25 seconds
```

**Focus:** Stress test - all fitness log types

---

### **Test 5: Non-Fitness Category (Task/Reminder)**
**Prompt:** `remind me to meal prep on Sunday`

**Expected Behavior:**
- ❌ Cache MISS (not food-related)
- ⏱️ LLM classification to detect "task" category
- 📊 Creates 1 task (no fitness log)

**Expected Timing:**
```
STEP 1 - Save user message:   ~2000ms ❌
STEP 2 - Cache lookup:         ~100ms  ✅ (quick miss)
STEP 3 - LLM classification:   6000-10000ms ⚠️
STEP 4 - DB persistence:       ~300ms  ✅ (1 task)
STEP 5 - Get user context:     ~1000ms ⚠️
STEP 6 - Generate response:    <10ms   ✅
STEP 7 - Save AI response:     ~1000ms ❌
───────────────────────────────────────
TOTAL: 12-18 seconds
```

**Focus:** Tests task creation path + non-meal categories

---

## 📊 Summary Table

| Test | Prompt | Cache | LLM Call | Expected Time | Categories |
|------|--------|-------|----------|---------------|------------|
| 1 | `1 banana` | ✅ HIT | ❌ No | 4-5s | Meal |
| 2 | `2 eggs and 1 slice of bread for breakfast` | ❌ MISS | ✅ Yes | 15-20s | Meal (multi-item) |
| 3 | `had oatmeal for breakfast and ran 5k` | ❌ MISS | ✅ Yes | 15-20s | Meal + Workout |
| 4 | `grilled chicken salad, 2 glasses of water, and vitamin D` | ❌ MISS | ✅ Yes | 18-25s | Meal + Water + Supplement |
| 5 | `remind me to meal prep on Sunday` | ❌ MISS | ✅ Yes | 12-18s | Task |

---

## 🎯 Key Metrics to Track

For each test, record:

1. **Total Time** - From `⏱️ [...] ✅ TOTAL TIME: XXXms`
2. **LLM Time** - From `STEP 3 - LLM classification: XXXms`
3. **Cache Result** - From `STEP 2 - Cache lookup: XXXms (hit=True/False)`
4. **Firestore Times** - From STEP 1, 5, 7 (should be fast!)
5. **Context Time** - From STEP 5 (should be <1s)

---

## 🚨 Known Issues (Pre-Fix)

### **Issue 1: Firestore Blocking (HIGH PRIORITY)** ❌
- **Symptoms:** STEP 1, 5, 7 each take 1-2 seconds
- **Cause:** Using synchronous `firestore.Client()` in async code
- **Impact:** +5-8 seconds per request
- **Fix:** Wrap in `asyncio.to_thread()` or use `AsyncClient`

### **Issue 2: LLM Slow (MEDIUM PRIORITY)** ⚠️
- **Symptoms:** STEP 3 takes 8-15 seconds
- **Cause:** OpenAI API latency, large token usage
- **Impact:** +5-10 seconds on cache misses
- **Fix:** Optimize prompt, use faster model (gpt-4o-mini), cache common queries

### **Issue 3: Cache Lookup Slow (LOW PRIORITY)** ⚠️
- **Symptoms:** STEP 2 sometimes takes 2-3 seconds
- **Cause:** Firestore food database query
- **Impact:** +2s on first lookup
- **Fix:** In-memory cache for common foods

---

## 🚀 Expected Results After Fixes

| Test | Current Time | After Fix | Improvement |
|------|--------------|-----------|-------------|
| Test 1 (Cache Hit) | 4-5s | **1-2s** | ✅ 60% faster |
| Test 2 (Multi-item) | 15-20s | **6-8s** | ✅ 60% faster |
| Test 3 (Multi-cat) | 15-20s | **6-8s** | ✅ 60% faster |
| Test 4 (Complex) | 18-25s | **8-10s** | ✅ 55% faster |
| Test 5 (Task) | 12-18s | **5-7s** | ✅ 60% faster |

**Target:** <5s for cache hits, <8s for LLM calls

---

## 📝 Test Execution Log Template

```
=== PERFORMANCE TEST RESULTS ===
Date: [DATE]
Version: [COMMIT/BRANCH]

Test 1 (1 banana):
- Total: XXXms
- Cache: HIT/MISS
- LLM: XXXms
- Breakdown: [paste ⏱️ BREAKDOWN line]
- Status: ✅/❌
- Notes: [observations]

Test 2 (2 eggs and bread):
- Total: XXXms
- Cache: HIT/MISS
- LLM: XXXms
- Breakdown: [paste ⏱️ BREAKDOWN line]
- Status: ✅/❌
- Notes: [observations]

[... repeat for all 5 tests ...]

=== SUMMARY ===
Average Total Time: XXXms
Cache Hit Rate: XX%
Average LLM Time: XXXms
Slowest Step: [STEP X]
Recommendation: [what to fix next]
```

---

## ✅ Ready to Execute!

**Next Steps:**
1. User sends Test 1: `1 banana`
2. Assistant captures timing logs
3. Repeat for Tests 2-5
4. Analyze results
5. Prioritize fixes based on data

**Command to monitor:**
```bash
tail -f /tmp/backend.log | grep "⏱️"
```

