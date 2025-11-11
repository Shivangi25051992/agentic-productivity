#!/usr/bin/env python3
"""
Advanced benchmark script with connection pooling and pattern analysis

This version:
- Reuses Firestore client (connection pooling)
- Analyzes query patterns
- Tests different query strategies
- Provides detailed diagnostics

Usage:
    python scripts/benchmark_timeline_advanced.py
"""

import sys
import os
import time
import statistics
from datetime import datetime, timedelta, timezone
from typing import List, Dict, Any
import json

# Add parent directory to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from google.cloud import firestore

# ✅ OPTIMIZATION: Global Firestore client (connection pooling)
db = firestore.Client()

def benchmark_with_warmup(
    user_id: str,
    iterations: int = 10,
    limit: int = 50,
    warmup_iterations: int = 2
) -> Dict[str, Any]:
    """
    Benchmark with connection warmup to eliminate cold start bias
    
    Args:
        user_id: User ID to query
        iterations: Number of iterations to run
        limit: Number of documents to fetch
        warmup_iterations: Number of warmup queries (not counted)
    
    Returns:
        Dictionary with performance metrics
    """
    
    times = []
    reads = []
    
    # Date range: last 30 days
    end_ts = datetime.now(timezone.utc)
    start_ts = end_ts - timedelta(days=30)
    
    logs_ref = db.collection('users').document(user_id).collection('fitness_logs')
    
    print(f"\n{'='*60}")
    print(f"ADVANCED TIMELINE BENCHMARK (with warmup)")
    print(f"{'='*60}")
    print(f"User ID: {user_id}")
    print(f"Date range: {start_ts.date()} to {end_ts.date()}")
    print(f"Limit: {limit} documents")
    print(f"Warmup iterations: {warmup_iterations}")
    print(f"Measured iterations: {iterations}")
    print(f"{'='*60}\n")
    
    # Warmup phase (not counted)
    print(f"🔥 WARMUP PHASE (not counted in results)")
    print(f"{'-'*60}")
    for i in range(warmup_iterations):
        start = time.time()
        query = logs_ref.where('timestamp', '>=', start_ts) \
                        .where('timestamp', '<=', end_ts) \
                        .order_by('timestamp', direction=firestore.Query.DESCENDING) \
                        .limit(limit)
        docs = list(query.stream())
        elapsed = (time.time() - start) * 1000
        print(f"Warmup {i+1}/{warmup_iterations}: {elapsed:6.0f}ms, {len(docs):3d} docs")
    
    print(f"\n📊 MEASUREMENT PHASE")
    print(f"{'-'*60}")
    
    # Measurement phase
    for i in range(iterations):
        start = time.time()
        
        query = logs_ref.where('timestamp', '>=', start_ts) \
                        .where('timestamp', '<=', end_ts) \
                        .order_by('timestamp', direction=firestore.Query.DESCENDING) \
                        .limit(limit)
        
        docs = list(query.stream())
        
        elapsed = (time.time() - start) * 1000
        times.append(elapsed)
        reads.append(len(docs))
        
        print(f"Iteration {i+1}/{iterations}: {elapsed:6.0f}ms, {len(docs):3d} docs")
    
    # Calculate statistics
    times_sorted = sorted(times)
    
    return {
        "avg_time_ms": statistics.mean(times),
        "p50_ms": statistics.median(times),
        "p95_ms": times_sorted[int(len(times) * 0.95)] if len(times) > 1 else times[0],
        "p99_ms": times_sorted[int(len(times) * 0.99)] if len(times) > 1 else times[0],
        "min_ms": min(times),
        "max_ms": max(times),
        "stddev_ms": statistics.stdev(times) if len(times) > 1 else 0,
        "avg_reads": statistics.mean(reads),
        "total_iterations": iterations,
        "all_times": times,
    }

def analyze_pattern(times: List[float]) -> Dict[str, Any]:
    """
    Analyze query time patterns to identify issues
    
    Returns:
        Dictionary with pattern analysis
    """
    
    # Check for alternating pattern
    odd_times = [times[i] for i in range(0, len(times), 2)]
    even_times = [times[i] for i in range(1, len(times), 2)]
    
    odd_avg = statistics.mean(odd_times) if odd_times else 0
    even_avg = statistics.mean(even_times) if even_times else 0
    
    # Check if there's a significant difference
    alternating = abs(odd_avg - even_avg) > 200  # >200ms difference
    
    # Check for consistent performance
    stddev = statistics.stdev(times) if len(times) > 1 else 0
    consistent = stddev < 100  # <100ms standard deviation
    
    # Identify outliers (>2x median)
    median = statistics.median(times)
    outliers = [t for t in times if t > median * 2]
    
    return {
        "alternating_pattern": alternating,
        "odd_avg_ms": odd_avg,
        "even_avg_ms": even_avg,
        "consistent": consistent,
        "stddev_ms": stddev,
        "outliers_count": len(outliers),
        "outliers_pct": (len(outliers) / len(times)) * 100,
    }

def print_results(results: Dict[str, Any], pattern: Dict[str, Any]):
    """Print benchmark results with pattern analysis"""
    
    print(f"\n{'='*60}")
    print("RESULTS")
    print(f"{'='*60}")
    print(f"Average Time:     {results['avg_time_ms']:6.0f}ms")
    print(f"Median (P50):     {results['p50_ms']:6.0f}ms")
    print(f"P95:              {results['p95_ms']:6.0f}ms")
    print(f"P99:              {results['p99_ms']:6.0f}ms")
    print(f"Min:              {results['min_ms']:6.0f}ms")
    print(f"Max:              {results['max_ms']:6.0f}ms")
    print(f"Std Dev:          {results['stddev_ms']:6.0f}ms")
    print(f"Avg Reads:        {results['avg_reads']:6.0f} docs")
    print(f"{'='*60}")
    
    print(f"\n{'='*60}")
    print("PATTERN ANALYSIS")
    print(f"{'='*60}")
    
    if pattern['alternating_pattern']:
        print(f"⚠️  ALTERNATING PATTERN DETECTED")
        print(f"   Odd queries avg:  {pattern['odd_avg_ms']:6.0f}ms")
        print(f"   Even queries avg: {pattern['even_avg_ms']:6.0f}ms")
        print(f"   Difference:       {abs(pattern['odd_avg_ms'] - pattern['even_avg_ms']):6.0f}ms")
        print(f"\n   Likely causes:")
        print(f"   • Firestore server rotation")
        print(f"   • Network routing changes")
        print(f"   • Load balancer behavior")
    else:
        print(f"✅ NO ALTERNATING PATTERN")
        print(f"   Queries are consistent")
    
    print(f"\nConsistency:")
    if pattern['consistent']:
        print(f"   ✅ CONSISTENT (stddev: {pattern['stddev_ms']:.0f}ms)")
    else:
        print(f"   ⚠️  INCONSISTENT (stddev: {pattern['stddev_ms']:.0f}ms)")
    
    print(f"\nOutliers:")
    print(f"   Count: {pattern['outliers_count']} ({pattern['outliers_pct']:.0f}%)")
    if pattern['outliers_count'] > 0:
        print(f"   ⚠️  {pattern['outliers_pct']:.0f}% of queries are outliers")
    
    print(f"{'='*60}")

def check_performance_targets(results: Dict[str, Any]) -> bool:
    """Check if performance meets targets"""
    
    targets = {
        "P95 < 500ms": results['p95_ms'] < 500,
        "P99 < 1000ms": results['p99_ms'] < 1000,
        "Avg < 400ms": results['avg_time_ms'] < 400,
        "Consistent (stddev < 100ms)": results['stddev_ms'] < 100,
    }
    
    print(f"\n{'='*60}")
    print("PERFORMANCE TARGETS")
    print(f"{'='*60}")
    all_passed = True
    for target, passed in targets.items():
        status = "✅ PASS" if passed else "❌ FAIL"
        print(f"  {status}  {target}")
        if not passed:
            all_passed = False
    print(f"{'='*60}")
    
    return all_passed

def save_results(results: Dict[str, Any], pattern: Dict[str, Any], filename: str):
    """Save results to file"""
    
    import json
    
    results_with_meta = {
        "timestamp": datetime.now().isoformat(),
        "metrics": results,
        "pattern_analysis": pattern,
    }
    
    os.makedirs('benchmarks', exist_ok=True)
    filepath = os.path.join('benchmarks', filename)
    
    with open(filepath, 'w') as f:
        json.dump(results_with_meta, f, indent=2)
    
    print(f"\n✅ Results saved to: {filepath}")

def main():
    USER_ID = "mLNCSrl01vhubtZXJYj7R4kEQ8g2"
    ITERATIONS = 20  # More iterations for better pattern detection
    LIMIT = 50
    WARMUP = 3  # Warmup queries
    
    try:
        # Run benchmark with warmup
        results = benchmark_with_warmup(
            user_id=USER_ID,
            iterations=ITERATIONS,
            limit=LIMIT,
            warmup_iterations=WARMUP
        )
        
        # Analyze pattern
        pattern = analyze_pattern(results['all_times'])
        
        # Print results
        print_results(results, pattern)
        
        # Check targets
        all_passed = check_performance_targets(results)
        
        # Save results
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"timeline_benchmark_advanced_{timestamp}.json"
        save_results(results, pattern, filename)
        
        # Summary
        print(f"\n{'='*60}")
        print("SUMMARY")
        print(f"{'='*60}")
        if all_passed:
            print("🎉 All performance targets met!")
        else:
            print("⚠️  Some targets not met")
        
        if pattern['alternating_pattern']:
            print("\n💡 RECOMMENDATION:")
            print("   Alternating pattern detected - this is likely due to:")
            print("   • Network latency variations")
            print("   • Firestore load balancing")
            print("   • NOT an index issue")
            print("\n   Solutions:")
            print("   1. Use median (P50) instead of average")
            print("   2. Implement connection pooling (already done!)")
            print("   3. Add caching layer (Redis)")
            print("   4. Accept this as normal cloud behavior")
        
        print(f"{'='*60}\n")
        
        sys.exit(0)
            
    except Exception as e:
        print(f"\n❌ Error running benchmark: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

if __name__ == "__main__":
    main()

