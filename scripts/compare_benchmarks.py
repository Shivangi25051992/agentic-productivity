#!/usr/bin/env python3
"""
Compare benchmark results before and after optimization

Usage:
    python scripts/compare_benchmarks.py <before_file> <after_file>
    
Example:
    python scripts/compare_benchmarks.py \
        benchmarks/timeline_benchmark_20251110_180000.json \
        benchmarks/timeline_benchmark_20251110_183000.json
"""

import sys
import json
import os

def load_benchmark(filepath: str) -> dict:
    """Load benchmark results from file"""
    with open(filepath, 'r') as f:
        return json.load(f)

def calculate_improvement(before: float, after: float) -> tuple:
    """Calculate improvement percentage and speedup factor"""
    improvement_pct = ((before - after) / before) * 100
    speedup = before / after if after > 0 else 0
    return improvement_pct, speedup

def compare_benchmarks(before_file: str, after_file: str):
    """Compare two benchmark results"""
    
    # Load results
    before = load_benchmark(before_file)
    after = load_benchmark(after_file)
    
    before_metrics = before['metrics']
    after_metrics = after['metrics']
    
    print("=" * 70)
    print("BENCHMARK COMPARISON")
    print("=" * 70)
    print(f"Before: {before['timestamp']}")
    print(f"After:  {after['timestamp']}")
    print("=" * 70)
    print()
    
    # Compare metrics
    metrics = [
        ("Average Time", "avg_time_ms", "ms"),
        ("Median (P50)", "p50_ms", "ms"),
        ("P95", "p95_ms", "ms"),
        ("P99", "p99_ms", "ms"),
        ("Min", "min_ms", "ms"),
        ("Max", "max_ms", "ms"),
    ]
    
    print(f"{'Metric':<20} {'Before':>10} {'After':>10} {'Change':>12} {'Speedup':>10}")
    print("-" * 70)
    
    for name, key, unit in metrics:
        before_val = before_metrics[key]
        after_val = after_metrics[key]
        improvement_pct, speedup = calculate_improvement(before_val, after_val)
        
        change_str = f"{improvement_pct:+.1f}%"
        speedup_str = f"{speedup:.1f}x"
        
        print(f"{name:<20} {before_val:>8.0f}{unit:>2} {after_val:>8.0f}{unit:>2} "
              f"{change_str:>12} {speedup_str:>10}")
    
    print("=" * 70)
    print()
    
    # Performance targets
    print("PERFORMANCE TARGETS:")
    print("-" * 70)
    
    targets = [
        ("P95 < 500ms", "p95_ms", 500),
        ("P99 < 1000ms", "p99_ms", 1000),
        ("Avg < 400ms", "avg_time_ms", 400),
    ]
    
    for name, key, threshold in targets:
        before_val = before_metrics[key]
        after_val = after_metrics[key]
        
        before_pass = "✅" if before_val < threshold else "❌"
        after_pass = "✅" if after_val < threshold else "❌"
        
        print(f"{name:<20} Before: {before_pass} ({before_val:.0f}ms)  "
              f"After: {after_pass} ({after_val:.0f}ms)")
    
    print("=" * 70)
    print()
    
    # Summary
    avg_improvement_pct, avg_speedup = calculate_improvement(
        before_metrics['avg_time_ms'],
        after_metrics['avg_time_ms']
    )
    
    print("SUMMARY:")
    print(f"  🚀 {avg_speedup:.1f}x faster on average")
    print(f"  📉 {avg_improvement_pct:.0f}% reduction in query time")
    
    if after_metrics['p95_ms'] < 500:
        print(f"  ✅ All performance targets met!")
    else:
        print(f"  ⚠️  Some targets not yet met (indexes may still be building)")
    
    print()

def main():
    if len(sys.argv) != 3:
        print("Usage: python scripts/compare_benchmarks.py <before_file> <after_file>")
        print()
        print("Example:")
        print("  python scripts/compare_benchmarks.py \\")
        print("    benchmarks/timeline_benchmark_20251110_180000.json \\")
        print("    benchmarks/timeline_benchmark_20251110_183000.json")
        sys.exit(1)
    
    before_file = sys.argv[1]
    after_file = sys.argv[2]
    
    # Check files exist
    if not os.path.exists(before_file):
        print(f"❌ Error: File not found: {before_file}")
        sys.exit(1)
    
    if not os.path.exists(after_file):
        print(f"❌ Error: File not found: {after_file}")
        sys.exit(1)
    
    # Compare
    compare_benchmarks(before_file, after_file)

if __name__ == "__main__":
    main()

