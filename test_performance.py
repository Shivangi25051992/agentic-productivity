#!/usr/bin/env python3
"""
Performance Testing Suite
Tests response times for all critical endpoints
"""

import requests
import time
from statistics import mean, median
from typing import List, Dict
import json

BASE_URL = "http://localhost:8000"

# Test configuration
NUM_ITERATIONS = 10
PERFORMANCE_THRESHOLDS = {
    "health": 100,  # ms
    "chat": 2000,   # ms (with OpenAI call)
    "logs_today": 500,  # ms
    "chat_history": 500,  # ms
    "dashboard": 1000,  # ms
}

class PerformanceTest:
    def __init__(self):
        self.results = []
    
    def measure_request(self, method: str, endpoint: str, **kwargs) -> Dict:
        """Measure a single request"""
        start = time.time()
        
        try:
            if method == "GET":
                response = requests.get(f"{BASE_URL}{endpoint}", **kwargs)
            elif method == "POST":
                response = requests.post(f"{BASE_URL}{endpoint}", **kwargs)
            else:
                raise ValueError(f"Unsupported method: {method}")
            
            duration_ms = (time.time() - start) * 1000
            
            return {
                "success": response.status_code == 200,
                "status_code": response.status_code,
                "duration_ms": duration_ms,
                "size_bytes": len(response.content)
            }
        except Exception as e:
            duration_ms = (time.time() - start) * 1000
            return {
                "success": False,
                "error": str(e),
                "duration_ms": duration_ms
            }
    
    def run_test(self, name: str, method: str, endpoint: str, iterations: int = NUM_ITERATIONS, **kwargs):
        """Run multiple iterations of a test"""
        print(f"\n📊 Testing: {name}")
        print(f"   Endpoint: {method} {endpoint}")
        print(f"   Iterations: {iterations}")
        
        durations = []
        successes = 0
        
        for i in range(iterations):
            result = self.measure_request(method, endpoint, **kwargs)
            
            if result["success"]:
                successes += 1
                durations.append(result["duration_ms"])
                print(f"   ✅ Iteration {i+1}: {result['duration_ms']:.0f}ms")
            else:
                print(f"   ❌ Iteration {i+1}: Failed - {result.get('error', 'Unknown error')}")
        
        if durations:
            avg = mean(durations)
            med = median(durations)
            min_time = min(durations)
            max_time = max(durations)
            p95 = sorted(durations)[int(len(durations) * 0.95)] if len(durations) > 1 else durations[0]
            
            threshold = PERFORMANCE_THRESHOLDS.get(name.lower().replace(" ", "_"), 1000)
            passed = p95 <= threshold
            
            result_summary = {
                "name": name,
                "endpoint": endpoint,
                "iterations": iterations,
                "successes": successes,
                "avg_ms": round(avg, 2),
                "median_ms": round(med, 2),
                "min_ms": round(min_time, 2),
                "max_ms": round(max_time, 2),
                "p95_ms": round(p95, 2),
                "threshold_ms": threshold,
                "passed": passed
            }
            
            self.results.append(result_summary)
            
            status = "✅ PASSED" if passed else "❌ FAILED"
            print(f"\n   {status}")
            print(f"   Average: {avg:.0f}ms")
            print(f"   Median: {med:.0f}ms")
            print(f"   P95: {p95:.0f}ms (threshold: {threshold}ms)")
            print(f"   Min: {min_time:.0f}ms, Max: {max_time:.0f}ms")
        else:
            print(f"\n   ❌ All requests failed")
            self.results.append({
                "name": name,
                "endpoint": endpoint,
                "passed": False,
                "error": "All requests failed"
            })
    
    def print_summary(self):
        """Print test summary"""
        print("\n" + "=" * 70)
        print("🎯 PERFORMANCE TEST SUMMARY")
        print("=" * 70)
        
        passed = sum(1 for r in self.results if r.get("passed", False))
        total = len(self.results)
        
        print(f"\nTotal Tests: {total}")
        print(f"Passed: {passed}")
        print(f"Failed: {total - passed}")
        print(f"Success Rate: {(passed/total*100):.1f}%\n")
        
        print("┌─────────────────────────────┬─────────┬─────────┬─────────┬──────────┐")
        print("│ Test                        │ Avg (ms)│ P95 (ms)│ Limit   │ Status   │")
        print("├─────────────────────────────┼─────────┼─────────┼─────────┼──────────┤")
        
        for result in self.results:
            name = result["name"][:27].ljust(27)
            avg = f"{result.get('avg_ms', 0):.0f}".rjust(7)
            p95 = f"{result.get('p95_ms', 0):.0f}".rjust(7)
            threshold = f"{result.get('threshold_ms', 0)}".rjust(7)
            status = "✅ PASS" if result.get("passed", False) else "❌ FAIL"
            
            print(f"│ {name} │ {avg} │ {p95} │ {threshold} │ {status}  │")
        
        print("└─────────────────────────────┴─────────┴─────────┴─────────┴──────────┘")
        
        # Save results to JSON
        with open("performance_results.json", "w") as f:
            json.dump({
                "timestamp": time.time(),
                "summary": {
                    "total": total,
                    "passed": passed,
                    "failed": total - passed,
                    "success_rate": round(passed/total*100, 2)
                },
                "results": self.results
            }, f, indent=2)
        
        print("\n📄 Results saved to: performance_results.json")
        
        if passed == total:
            print("\n🎉 ALL PERFORMANCE TESTS PASSED!")
            return 0
        else:
            print(f"\n⚠️  {total - passed} test(s) failed")
            return 1


def main():
    """Run all performance tests"""
    print("=" * 70)
    print("🚀 PERFORMANCE TESTING SUITE")
    print("=" * 70)
    print(f"Base URL: {BASE_URL}")
    print(f"Iterations per test: {NUM_ITERATIONS}")
    
    tester = PerformanceTest()
    
    # Test 1: Health Check (should be very fast)
    tester.run_test(
        name="Health",
        method="GET",
        endpoint="/health",
        iterations=20
    )
    
    # Test 2: Chat History (page load performance)
    tester.run_test(
        name="Chat History",
        method="GET",
        endpoint="/chat/history?limit=50",
        iterations=10,
        timeout=5
    )
    
    # Test 3: Today's Logs (dashboard)
    tester.run_test(
        name="Logs Today",
        method="GET",
        endpoint="/logs/today",
        iterations=10,
        timeout=5
    )
    
    # Test 4: Chat Stats
    tester.run_test(
        name="Chat Stats",
        method="GET",
        endpoint="/chat/stats",
        iterations=10,
        timeout=5
    )
    
    # Test 5: Chat Message (with OpenAI - will be slow)
    print("\n⚠️  Note: Chat endpoint includes OpenAI call (expected to be slower)")
    tester.run_test(
        name="Chat",
        method="POST",
        endpoint="/chat",
        iterations=3,  # Fewer iterations due to cost
        json={"text": "I had a banana"},
        timeout=10
    )
    
    # Print summary
    exit_code = tester.print_summary()
    
    return exit_code


if __name__ == "__main__":
    try:
        exit_code = main()
        exit(exit_code)
    except KeyboardInterrupt:
        print("\n\n⚠️  Test interrupted by user")
        exit(1)
    except Exception as e:
        print(f"\n❌ Test suite failed: {e}")
        import traceback
        traceback.print_exc()
        exit(1)

