#!/usr/bin/env python3
"""
Benchmark script for timeline query performance
Compares performance before and after optimization

Usage:
    python scripts/benchmark_timeline.py
    
Expected output:
    - Average query time
    - P50, P95, P99 percentiles
    - Number of documents read
    - Performance targets (PASS/FAIL)
"""

import sys
import os
import time
import statistics
from datetime import datetime, timedelta, timezone
from typing import List, Dict, Any

# Add parent directory to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from google.cloud import firestore

# Initialize Firestore
db = firestore.Client()

def benchmark_timeline_query(
    user_id: str,
    iterations: int = 10,
    limit: int = 50
) -> Dict[str, Any]:
    """
    Benchmark timeline query performance
    
    Args:
        user_id: User ID to query
        iterations: Number of iterations to run
        limit: Number of documents to fetch
    
    Returns:
        Dictionary with performance metrics:
        - avg_time_ms: Average query time
        - p50_ms, p95_ms, p99_ms: Percentiles
        - min_ms, max_ms: Min/max times
        - avg_reads: Average documents read
    """
    
    times = []
    reads = []
    
    # Date range: last 30 days
    end_ts = datetime.now(timezone.utc)
    start_ts = end_ts - timedelta(days=30)
    
    print(f"\nRunning {iterations} iterations...")
    print(f"Date range: {start_ts.date()} to {end_ts.date()}")
    print(f"Limit: {limit} documents")
    print("-" * 60)
    
    for i in range(iterations):
        start = time.time()
        
        # Query fitness_logs (same query as production)
        logs_ref = db.collection('users').document(user_id).collection('fitness_logs')
        query = logs_ref.where('timestamp', '>=', start_ts) \
                        .where('timestamp', '<=', end_ts) \
                        .order_by('timestamp', direction=firestore.Query.DESCENDING) \
                        .limit(limit)
        
        # Execute query
        docs = list(query.stream())
        
        elapsed = (time.time() - start) * 1000  # Convert to ms
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
        "avg_reads": statistics.mean(reads),
        "total_iterations": iterations,
        "all_times": times,  # For detailed analysis
    }

def print_results(results: Dict[str, Any]):
    """Print benchmark results in a formatted table"""
    
    print("\n" + "=" * 60)
    print("RESULTS")
    print("=" * 60)
    print(f"Average Time:     {results['avg_time_ms']:6.0f}ms")
    print(f"Median (P50):     {results['p50_ms']:6.0f}ms")
    print(f"P95:              {results['p95_ms']:6.0f}ms")
    print(f"P99:              {results['p99_ms']:6.0f}ms")
    print(f"Min:              {results['min_ms']:6.0f}ms")
    print(f"Max:              {results['max_ms']:6.0f}ms")
    print(f"Avg Reads:        {results['avg_reads']:6.0f} docs")
    print("=" * 60)

def check_performance_targets(results: Dict[str, Any]) -> bool:
    """
    Check if performance meets targets
    
    Targets:
    - P95 < 500ms
    - P99 < 1000ms
    - Avg < 400ms
    
    Returns:
        True if all targets met, False otherwise
    """
    
    targets = {
        "P95 < 500ms": results['p95_ms'] < 500,
        "P99 < 1000ms": results['p99_ms'] < 1000,
        "Avg < 400ms": results['avg_time_ms'] < 400,
    }
    
    print("\nPERFORMANCE TARGETS:")
    all_passed = True
    for target, passed in targets.items():
        status = "✅ PASS" if passed else "❌ FAIL"
        print(f"  {status}  {target}")
        if not passed:
            all_passed = False
    
    return all_passed

def save_results(results: Dict[str, Any], filename: str):
    """Save results to file for comparison"""
    
    import json
    
    # Add metadata
    results_with_meta = {
        "timestamp": datetime.now().isoformat(),
        "metrics": results,
    }
    
    os.makedirs('benchmarks', exist_ok=True)
    filepath = os.path.join('benchmarks', filename)
    
    with open(filepath, 'w') as f:
        json.dump(results_with_meta, f, indent=2)
    
    print(f"\n✅ Results saved to: {filepath}")

def main():
    """Main benchmark function"""
    
    # Configuration
    USER_ID = "mLNCSrl01vhubtZXJYj7R4kEQ8g2"  # kiki@kiki.com
    ITERATIONS = 10
    LIMIT = 50
    
    print("=" * 60)
    print("TIMELINE QUERY PERFORMANCE BENCHMARK")
    print("=" * 60)
    print(f"User ID: {USER_ID}")
    print(f"Iterations: {ITERATIONS}")
    print(f"Limit: {LIMIT} documents")
    print("=" * 60)
    
    try:
        # Run benchmark
        results = benchmark_timeline_query(
            user_id=USER_ID,
            iterations=ITERATIONS,
            limit=LIMIT
        )
        
        # Print results
        print_results(results)
        
        # Check targets
        all_passed = check_performance_targets(results)
        
        # Save results
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"timeline_benchmark_{timestamp}.json"
        save_results(results, filename)
        
        # Exit code
        if all_passed:
            print("\n🎉 All performance targets met!")
            sys.exit(0)
        else:
            print("\n⚠️  Some performance targets not met")
            print("   This is expected BEFORE indexes are built")
            print("   Run again after indexes are enabled")
            sys.exit(0)  # Don't fail - this is informational
            
    except Exception as e:
        print(f"\n❌ Error running benchmark: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

if __name__ == "__main__":
    main()

