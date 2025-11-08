"""
Automated Backend Performance Test for Chat Classification

Tests various prompts and measures LLM Router performance
"""

import asyncio
import time
import sys
from typing import List, Dict, Any

# Add app to path
sys.path.insert(0, '/Users/pchintanwar/Documents/Projects-AIProductivity/agentic-productivity')

from app.services.llm.llm_router import LLMRouter
from app.models.llm_config import LLMRequest
from app.services.database import get_firestore_client


# Test prompts
TEST_PROMPTS = [
    {
        "name": "Simple Meal",
        "input": "2 eggs for breakfast",
        "expected_items": 1,
        "expected_categories": ["meal"]
    },
    {
        "name": "Multi-Item (4 items)",
        "input": "2 boiled eggs and 1 slice whole wheat toast for breakfast\nran 5km in 30 minutes\ntook 1 multivitamin tablet\ndrank 3 glasses of water",
        "expected_items": 4,
        "expected_categories": ["meal", "workout", "supplement", "water"]
    },
    {
        "name": "Complex Meal",
        "input": "grilled chicken breast 200g with steamed broccoli 1 cup and brown rice half cup for lunch",
        "expected_items": 3,
        "expected_categories": ["meal"]
    },
    {
        "name": "Typos Test",
        "input": "2 egg omlet for brekfast\nran 5k todya\nvitmin c tabelt",
        "expected_items": 3,
        "expected_categories": ["meal", "workout", "supplement"]
    },
    {
        "name": "Stress Test (15+ items)",
        "input": "woke up had 2 eggs and coffee for breakfast then ran 5km took my vitamin d 1000 IU and omega 3 drank 2 glasses of water had grilled chicken 200g with brown rice 1 cup and broccoli for lunch afternoon snack was 1 apple and 10 almonds did 30 min yoga drank 1 liter of water had salmon 150g with quinoa half cup and mixed vegetables for dinner took multivitamin before bed drank another glass of water",
        "expected_items": 15,
        "expected_categories": ["meal", "workout", "supplement", "water"]
    }
]


async def test_chat_prompt(router: LLMRouter, test_case: Dict[str, Any]) -> Dict[str, Any]:
    """
    Test a single chat prompt
    
    Returns performance metrics and results
    """
    print(f"\n{'='*80}")
    print(f"🧪 Testing: {test_case['name']}")
    print(f"{'='*80}")
    print(f"Input: {test_case['input'][:100]}{'...' if len(test_case['input']) > 100 else ''}")
    
    # Build system prompt (simplified version)
    system_prompt = """You are an expert fitness/nutrition assistant.
Parse the input and return a JSON with:
{
  "items": [
    {
      "category": "meal|workout|water|supplement",
      "summary": "brief description",
      "data": {"calories": 0, "item": "name"}
    }
  ]
}"""
    
    user_prompt = f"Input: {test_case['input']}"
    
    # Create request
    request = LLMRequest(
        system_prompt=system_prompt,
        user_prompt=user_prompt,
        temperature=0.2,
        max_tokens=4000,
        response_format="json",
        user_id="test_user",
        request_type="chat_classification"
    )
    
    # Measure performance
    start_time = time.perf_counter()
    
    try:
        response = await router.route_request(request)
        
        elapsed_ms = int((time.perf_counter() - start_time) * 1000)
        
        # Parse response
        import json
        try:
            data = json.loads(response.content)
            items_parsed = len(data.get("items", []))
        except:
            items_parsed = 0
            data = {}
        
        # Results
        result = {
            "success": True,
            "provider": response.provider_used,
            "model": response.model_used,
            "tokens_used": response.tokens_used,
            "response_time_ms": elapsed_ms,
            "items_parsed": items_parsed,
            "expected_items": test_case["expected_items"],
            "data": data
        }
        
        # Print results
        print(f"\n✅ SUCCESS")
        print(f"   Provider: {response.provider_used}")
        print(f"   Model: {response.model_used}")
        print(f"   Tokens: {response.tokens_used}")
        print(f"   Time: {elapsed_ms}ms ({elapsed_ms/1000:.2f}s)")
        print(f"   Items Parsed: {items_parsed} (expected {test_case['expected_items']})")
        
        # Performance rating
        if elapsed_ms < 2000:
            rating = "🟢 EXCELLENT"
        elif elapsed_ms < 5000:
            rating = "🟡 GOOD"
        elif elapsed_ms < 10000:
            rating = "🟠 SLOW"
        else:
            rating = "🔴 VERY SLOW"
        
        print(f"   Performance: {rating}")
        
        return result
        
    except Exception as e:
        elapsed_ms = int((time.perf_counter() - start_time) * 1000)
        
        print(f"\n❌ FAILED: {str(e)}")
        print(f"   Time: {elapsed_ms}ms")
        
        return {
            "success": False,
            "error": str(e),
            "response_time_ms": elapsed_ms,
            "items_parsed": 0,
            "expected_items": test_case["expected_items"]
        }


async def run_all_tests():
    """Run all chat performance tests"""
    print("\n" + "="*80)
    print("🚀 PHASE 1 - CHAT PERFORMANCE AUTOMATED TESTS")
    print("="*80)
    
    # Initialize router
    print("\n📍 Initializing LLM Router...")
    db = get_firestore_client()
    router = LLMRouter(db=db)
    print("✅ Router initialized")
    
    # Run tests
    results = []
    for test_case in TEST_PROMPTS:
        result = await test_chat_prompt(router, test_case)
        results.append(result)
        
        # Wait a bit between tests
        await asyncio.sleep(1)
    
    # Summary
    print("\n" + "="*80)
    print("📊 PERFORMANCE SUMMARY")
    print("="*80)
    
    successful_tests = [r for r in results if r["success"]]
    failed_tests = [r for r in results if not r["success"]]
    
    print(f"\n✅ Passed: {len(successful_tests)}/{len(results)}")
    print(f"❌ Failed: {len(failed_tests)}/{len(results)}")
    
    if successful_tests:
        avg_time = sum(r["response_time_ms"] for r in successful_tests) / len(successful_tests)
        min_time = min(r["response_time_ms"] for r in successful_tests)
        max_time = max(r["response_time_ms"] for r in successful_tests)
        total_tokens = sum(r["tokens_used"] for r in successful_tests)
        
        print(f"\n⏱️  Response Times:")
        print(f"   Average: {avg_time:.0f}ms ({avg_time/1000:.2f}s)")
        print(f"   Fastest: {min_time}ms ({min_time/1000:.2f}s)")
        print(f"   Slowest: {max_time}ms ({max_time/1000:.2f}s)")
        
        print(f"\n🎯 Tokens Used:")
        print(f"   Total: {total_tokens}")
        print(f"   Average: {total_tokens/len(successful_tests):.0f} per request")
        
        # Performance verdict
        print(f"\n🏆 OVERALL VERDICT:")
        if avg_time < 3000:
            print(f"   🟢 EXCELLENT - Chat is fast and responsive!")
        elif avg_time < 6000:
            print(f"   🟡 GOOD - Acceptable performance for complex AI")
        elif avg_time < 12000:
            print(f"   🟠 NEEDS IMPROVEMENT - Consider prompt optimization")
        else:
            print(f"   🔴 CRITICAL - Performance needs immediate attention")
    
    if failed_tests:
        print(f"\n❌ Failed Tests:")
        for i, r in enumerate(failed_tests):
            print(f"   {i+1}. {r.get('error', 'Unknown error')}")
    
    print("\n" + "="*80)
    print("✅ Testing Complete")
    print("="*80 + "\n")
    
    return results


if __name__ == "__main__":
    asyncio.run(run_all_tests())

