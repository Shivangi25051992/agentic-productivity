# 📊 Benchmark Guide - Measure Performance Improvements

**Task 1.1 Progress**: Steps 1.1.3-1.1.6

---

## 🎯 **OBJECTIVE**

Measure timeline query performance before and after index optimization to verify **8x improvement**.

---

## 📋 **STEPS**

### **Step 1.1.4: Run Baseline Benchmark** (15 min)

**What**: Measure current performance (before indexes are fully built)

**Command**:
```bash
cd /Users/pchintanwar/Documents/Projects-AIProductivity/agentic-productivity

# Run benchmark
python scripts/benchmark_timeline.py
```

**Expected Output**:
```
============================================================
TIMELINE QUERY PERFORMANCE BENCHMARK
============================================================
User ID: mLNCSrl01vhubtZXJYj7R4kEQ8g2
Iterations: 10
Limit: 50 documents
============================================================

Running 10 iterations...
Date range: 2025-10-11 to 2025-11-10
Limit: 50 documents
------------------------------------------------------------
Iteration 1/10:   2341ms,  50 docs
Iteration 2/10:   2198ms,  50 docs
Iteration 3/10:   2456ms,  50 docs
...

============================================================
RESULTS
============================================================
Average Time:      2287ms
Median (P50):      2298ms
P95:               2456ms
P99:               2456ms
Min:               2198ms
Max:               2456ms
Avg Reads:           50 docs
============================================================

PERFORMANCE TARGETS:
  ❌ FAIL  P95 < 500ms
  ❌ FAIL  P99 < 1000ms
  ❌ FAIL  Avg < 400ms

⚠️  Some performance targets not met
   This is expected BEFORE indexes are built
   Run again after indexes are enabled

✅ Results saved to: benchmarks/timeline_benchmark_20251110_180000.json
```

**What this means**:
- ❌ Slow performance (expected - indexes not built yet)
- ✅ Baseline captured for comparison
- ✅ Results saved automatically

---

### **Step 1.1.5: Wait for Indexes to Build** (10-15 min)

**What**: Monitor index build progress in Firebase Console

**Action**:
1. Open Firebase Console: https://console.firebase.google.com/project/productivityai-mvp/firestore/indexes
2. Check status of indexes:
   - 🟡 **Building** → Wait
   - 🟢 **Enabled** → Ready to proceed!

**How to check from terminal**:
```bash
# Check index status
firebase firestore:indexes

# Or watch continuously (updates every 2 minutes)
watch -n 120 'firebase firestore:indexes'
```

**Expected Output**:
```
Indexes for database (default):

✅ (fitness_logs) -- user_id ASC timestamp DESC [Enabled]
✅ (fitness_logs) -- user_id ASC log_type ASC timestamp DESC [Enabled]
✅ (tasks) -- user_id ASC due_date DESC [Enabled]
✅ (tasks) -- user_id ASC status ASC due_date DESC [Enabled]
...
```

**When ready**: All indexes show **[Enabled]** ✅

---

### **Step 1.1.6: Run Post-Optimization Benchmark** (15 min)

**What**: Measure performance after indexes are enabled

**Command**:
```bash
cd /Users/pchintanwar/Documents/Projects-AIProductivity/agentic-productivity

# Run benchmark again
python scripts/benchmark_timeline.py
```

**Expected Output** (after indexes):
```
============================================================
TIMELINE QUERY PERFORMANCE BENCHMARK
============================================================

Running 10 iterations...
------------------------------------------------------------
Iteration 1/10:    287ms,  50 docs  ⚡
Iteration 2/10:    245ms,  50 docs  ⚡
Iteration 3/10:    298ms,  50 docs  ⚡
...

============================================================
RESULTS
============================================================
Average Time:       287ms  ⚡ (8x faster!)
Median (P50):       278ms
P95:                356ms
P99:                398ms
Min:                245ms
Max:                398ms
Avg Reads:           50 docs
============================================================

PERFORMANCE TARGETS:
  ✅ PASS  P95 < 500ms
  ✅ PASS  P99 < 1000ms
  ✅ PASS  Avg < 400ms

🎉 All performance targets met!

✅ Results saved to: benchmarks/timeline_benchmark_20251110_183000.json
```

**What this means**:
- ✅ **8x faster!** (2287ms → 287ms)
- ✅ All targets met
- ✅ Optimization successful!

---

### **Step 1.1.7: Compare Results** (5 min)

**What**: Side-by-side comparison of before/after

**Command**:
```bash
# Compare the two benchmark files
python scripts/compare_benchmarks.py \
  benchmarks/timeline_benchmark_20251110_180000.json \
  benchmarks/timeline_benchmark_20251110_183000.json
```

**Expected Output**:
```
======================================================================
BENCHMARK COMPARISON
======================================================================
Before: 2025-11-10T18:00:00
After:  2025-11-10T18:30:00
======================================================================

Metric               Before      After       Change     Speedup
----------------------------------------------------------------------
Average Time         2287ms      287ms      -87.5%       8.0x
Median (P50)         2298ms      278ms      -87.9%       8.3x
P95                  2456ms      356ms      -85.5%       6.9x
P99                  2456ms      398ms      -83.8%       6.2x
Min                  2198ms      245ms      -88.9%       9.0x
Max                  2456ms      398ms      -83.8%       6.2x
======================================================================

PERFORMANCE TARGETS:
----------------------------------------------------------------------
P95 < 500ms          Before: ❌ (2456ms)  After: ✅ (356ms)
P99 < 1000ms         Before: ❌ (2456ms)  After: ✅ (398ms)
Avg < 400ms          Before: ❌ (2287ms)  After: ✅ (287ms)
======================================================================

SUMMARY:
  🚀 8.0x faster on average
  📉 88% reduction in query time
  ✅ All performance targets met!
```

---

## 🎯 **SUCCESS CRITERIA**

### **Must Have**:
- ✅ P95 < 500ms
- ✅ P99 < 1000ms
- ✅ Avg < 400ms
- ✅ 5x+ speedup improvement

### **Target**:
- 🎯 8-10x speedup
- 🎯 P95 < 400ms
- 🎯 Avg < 300ms

---

## 🐛 **TROUBLESHOOTING**

### **Issue 1: "No module named 'google.cloud'"**

**Solution**:
```bash
# Install Google Cloud Firestore
pip install google-cloud-firestore
```

---

### **Issue 2: "DefaultCredentialsError"**

**Solution**:
```bash
# Re-authenticate with Google Cloud
gcloud auth application-default login
```

---

### **Issue 3: "No documents found"**

**Possible causes**:
1. User ID is incorrect
2. No data in database
3. Date range too narrow

**Solution**:
```bash
# Check if user has data
python -c "
from google.cloud import firestore
db = firestore.Client()
logs = db.collection('users').document('mLNCSrl01vhubtZXJYj7R4kEQ8g2').collection('fitness_logs').limit(1).stream()
print('Has data:', len(list(logs)) > 0)
"
```

---

### **Issue 4: Indexes still building**

**Symptoms**:
- Performance not improved
- Still failing targets

**Solution**:
- Wait longer (can take 10-20 min for large datasets)
- Check Firebase Console for index status
- Run benchmark again after all indexes show "Enabled"

---

### **Issue 5: Performance improved but not 8x**

**Possible causes**:
1. Network latency
2. Cold start (first query slower)
3. Firestore caching

**Solution**:
- Run benchmark multiple times
- Use average of multiple runs
- 5-6x is still good (target is 5x+)

---

## 📊 **INTERPRETING RESULTS**

### **Good Results** ✅
```
Before: 2000-3000ms
After:  200-400ms
Speedup: 6-10x
```

### **Acceptable Results** ⚠️
```
Before: 2000-3000ms
After:  400-600ms
Speedup: 4-5x
```

### **Poor Results** ❌
```
Before: 2000-3000ms
After:  1000-1500ms
Speedup: 2-3x
```

**If poor results**:
- Check indexes are enabled
- Check network connection
- Try running benchmark again
- Check Firestore quotas

---

## 🚀 **NEXT STEPS AFTER BENCHMARKING**

Once benchmarks show **8x improvement**:

1. ✅ **Step 1.1.7**: Create automated tests (1 hour)
2. ✅ **Step 1.1.8**: Document rollback plan (30 min)
3. ✅ **Step 1.1.9**: Deploy to staging (30 min)
4. ✅ **Step 1.1.10**: Deploy to production (30 min)

**Total time remaining**: ~3 hours to complete Task 1.1

---

## 📝 **NOTES**

- Benchmarks are saved automatically in `benchmarks/` directory
- Each benchmark has a timestamp in filename
- Keep baseline benchmarks for future comparison
- Run benchmarks periodically to track performance over time

---

**Status**: ✅ Scripts created and ready  
**Next**: Run baseline benchmark (Step 1.1.4)  
**ETA**: ~30 minutes to see 8x improvement

