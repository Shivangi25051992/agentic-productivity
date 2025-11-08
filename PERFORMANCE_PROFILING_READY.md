# ⏱️ Performance Profiling - READY FOR TESTING

## ✅ What We Just Implemented

Added **high-resolution timing logs** (using `time.perf_counter()`) at EVERY step of the chat flow:

### Instrumented Steps:
1. **STEP 1**: Save user message to Firestore
2. **STEP 2**: Cache lookup (fuzzy food matching)
3. **STEP 3**: LLM classification (OpenAI via Router)
4. **STEP 4**: Database persistence (Firestore writes)
5. **STEP 5**: Get user context (2 Firestore queries)
6. **STEP 6**: Generate response (template formatting)
7. **STEP 7**: Save AI response to Firestore
8. **TOTAL**: End-to-end request time + detailed breakdown

---

## 🧪 HOW TO TEST

### 1. Send a test message in chat:
```
"2 eggs for breakfast"
```

### 2. Check the backend logs immediately:
The logs will now show:
```
⏱️ [1699123456789] START - Input: '2 eggs for breakfast'
⏱️ [1699123456789] STEP 1 - Save user message: 150ms
⏱️ [1699123456789] STEP 2 - Cache lookup: 100ms (hit=False)
⏱️ [1699123456789] STEP 3 - LLM classification: 4200ms
⏱️ [1699123456789] STEP 4 - DB persistence: 500ms
⏱️ [1699123456789] STEP 5 - Get user context: 1800ms ← WATCH THIS!
⏱️ [1699123456789] STEP 6 - Generate response: 50ms
⏱️ [1699123456789] STEP 7 - Save AI response: 200ms
⏱️ [1699123456789] ✅ TOTAL TIME: 7000ms
⏱️ [1699123456789] BREAKDOWN: Save msg=150ms, Cache=100ms, LLM=4200ms, DB=500ms, Context=1800ms, Response=50ms, Save AI=200ms
```

---

## 🎯 WHAT TO LOOK FOR

### Expected Total Time:
- **With optimizations**: 5-7 seconds
- **Current (before optimization)**: 15-21 seconds

### Key Questions:
1. **Does the BREAKDOWN add up to the TOTAL?**
   - If NO → There's a hidden blocking operation!
   - If YES → We've found where the time goes!

2. **Which step is slow?**
   - STEP 3 (LLM): 4-5s is NORMAL (can't optimize much)
   - STEP 5 (Context): Should be ~1-2s, if 5-10s → BIG PROBLEM!
   - STEP 4 (DB): Should be <1s, if 3-5s → Firestore slow
   - Any other step >1s → Investigation needed

3. **Is there a GAP?**
   - Example: BREAKDOWN shows 7s but TOTAL shows 15s
   - Gap = 8s of missing time (hidden await, blocking code, network)

---

## 🔍 WHAT'S LIKELY TO BE SLOW

### Based on expert analysis:

**1. User Context Queries (STEP 5)** ⚠️
- Currently making 2+ separate Firestore queries
- Each query might be slow due to:
  - Unindexed fields
  - Large result sets
  - Network latency

**Fix**: Batch queries, cache results for 5 minutes

**2. LLM Router Quota Update** 🚨 (Hidden in STEP 3)
- Router might be making synchronous quota update after classification
- This could be a blocking Firestore write AFTER the AI call

**Fix**: Move quota updates to background task

**3. Async Event Loop Congestion** 🚨
- Multiple awaits competing for resources
- Context switches between coroutines

**Fix**: Profile individual service methods, use asyncio.gather() for parallel ops

---

## 📊 EXPECTED RESULTS

### Best Case (if optimized):
```
STEP 1: 100-200ms   (Firestore write)
STEP 2: 50-100ms    (Cache lookup)
STEP 3: 2500-3500ms (OpenAI API - can't optimize much)
STEP 4: 300-500ms   (DB writes)
STEP 5: 500-1000ms  (Context queries - CACHED)
STEP 6: 50-100ms    (String formatting)
STEP 7: 100-200ms   (Firestore write)
──────────────────
TOTAL: 3600-5600ms  ✅ TARGET!
```

### Worst Case (current):
```
STEP 1: 200ms
STEP 2: 100ms
STEP 3: 4500ms
STEP 4: 800ms
STEP 5: 8000ms ← PROBLEM!
STEP 6: 100ms
STEP 7: 300ms
──────────────
TOTAL: 14000ms (14s) ❌
```

---

## 🚀 NEXT STEPS AFTER TESTING

Once we identify the bottleneck from the logs:

### If STEP 5 (Context) is slow:
1. Add timing logs INSIDE `context_service.py`
2. Cache user context for 5 minutes
3. Batch today's + week's queries into one

### If STEP 3 (LLM) includes hidden quota updates:
1. Add timing logs INSIDE `llm_router.py`
2. Move `_update_quota()` to background task
3. Use `asyncio.create_task()` for fire-and-forget

### If there's a GAP (BREAKDOWN ≠ TOTAL):
1. Check for hidden blocking I/O
2. Profile with `cProfile` or `py-spy`
3. Look for synchronous DB calls in async code

---

## ✅ READY TO TEST!

**ACTION REQUIRED:**
1. Send "2 eggs for breakfast" in chat
2. Immediately check `/tmp/backend.log` for timing logs
3. Share the `⏱️` lines here so we can analyze!

**Command to view logs:**
```bash
tail -50 /tmp/backend.log | grep "⏱️"
```

---

## 🎯 YOUR EXPERT FEEDBACK WAS SPOT-ON:

> "Add time.monotonic() or logging timer at every step and sub-step"

✅ DONE! Using `time.perf_counter()` (even more accurate than `monotonic()`)

> "Test under load (10–100 concurrent users)"

⏭️ NEXT: After we fix the single-request bottleneck

> "Batch queries, cache context for 2–5 minutes"

⏭️ NEXT: Once we confirm context queries are the problem

> "Move quota/metrics updates to async background task"

⏭️ NEXT: If quota updates are synchronous in LLM Router

**Let's find that missing 8-10 seconds! 🔍**

