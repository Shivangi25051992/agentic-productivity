"""
Admin API - LLM Provider Management & Analytics
================================================
Requires admin authentication for all endpoints

Features:
- LLM provider configuration management
- Usage analytics and cost tracking
- System health monitoring
"""

from fastapi import APIRouter, Depends, HTTPException
from typing import List, Dict, Any, Optional
from datetime import datetime, timedelta
from app.models.user import User
from app.services.auth import get_current_user
from google.cloud import firestore
import os

router = APIRouter(prefix="/admin", tags=["admin"])


def require_admin(current_user: User = Depends(get_current_user)):
    """
    Verify user has admin role
    
    Security: Only users with 'role': 'admin' in Firestore can access
    """
    db = firestore.Client(project=os.getenv("GOOGLE_CLOUD_PROJECT"))
    user_doc = db.collection('users').document(current_user.user_id).get()
    
    if not user_doc.exists:
        raise HTTPException(status_code=403, detail="Access denied")
    
    user_data = user_doc.to_dict()
    if user_data.get('role') != 'admin':
        raise HTTPException(status_code=403, detail="Admin access required")
    
    return current_user


@router.get("/llm-providers")
async def get_llm_providers(admin: User = Depends(require_admin)):
    """
    Get all LLM provider configurations
    
    Returns current configuration for all providers including:
    - Enabled status
    - Priority order
    - Daily quota
    - Cost per 1k tokens
    """
    
    print(f"🔐 [ADMIN] LLM providers requested by: {admin.user_id}")
    
    db = firestore.Client(project=os.getenv("GOOGLE_CLOUD_PROJECT"))
    config_doc = db.collection('system_config').document('llm_providers').get()
    
    if config_doc.exists:
        providers = config_doc.to_dict()
        print(f"✅ [ADMIN] Returned {len(providers)} provider configs")
        return {"status": "success", "providers": providers}
    else:
        print("ℹ️ [ADMIN] No provider config found, returning empty")
        return {"status": "success", "providers": {}}


@router.put("/llm-providers/{provider_id}")
async def update_llm_provider(
    provider_id: str,
    config: Dict[str, Any],
    admin: User = Depends(require_admin)
):
    """
    Update LLM provider configuration
    
    Allows hot-reloading of provider settings:
    - enabled: bool
    - priority: int (1 = highest)
    - quota_per_day: int (optional)
    
    Changes take effect immediately (no restart required)
    """
    
    print(f"🔐 [ADMIN] Updating provider {provider_id} by: {admin.user_id}")
    print(f"   New config: {config}")
    
    # Validate provider_id
    valid_providers = ['openai_gpt4o_mini', 'openai_gpt4o', 'claude_35_sonnet', 'gemini_pro']
    if provider_id not in valid_providers:
        raise HTTPException(status_code=400, detail=f"Invalid provider_id. Must be one of: {valid_providers}")
    
    # Validate config fields
    if 'enabled' in config and not isinstance(config['enabled'], bool):
        raise HTTPException(status_code=400, detail="'enabled' must be boolean")
    
    if 'priority' in config and not isinstance(config['priority'], int):
        raise HTTPException(status_code=400, detail="'priority' must be integer")
    
    if 'quota_per_day' in config and config['quota_per_day'] is not None:
        if not isinstance(config['quota_per_day'], int):
            raise HTTPException(status_code=400, detail="'quota_per_day' must be integer or null")
    
    db = firestore.Client(project=os.getenv("GOOGLE_CLOUD_PROJECT"))
    config_ref = db.collection('system_config').document('llm_providers')
    
    # Update specific provider (merge to preserve other providers)
    config_ref.set({
        provider_id: config
    }, merge=True)
    
    print(f"✅ [ADMIN] Provider {provider_id} updated successfully")
    
    return {
        "status": "success",
        "message": f"Updated {provider_id}",
        "config": config
    }


@router.get("/llm-analytics")
async def get_llm_analytics(
    days: int = 7,
    user_id: Optional[str] = None,
    admin: User = Depends(require_admin)
):
    """
    Get LLM usage analytics
    
    Query parameters:
    - days: Number of days to analyze (default: 7)
    - user_id: Filter by specific user (optional)
    
    Returns:
    - Total generations
    - Total cost
    - Per-provider statistics
    - Recent generation logs
    """
    
    print(f"🔐 [ADMIN] Analytics requested by: {admin.user_id}")
    print(f"   Period: {days} days, User filter: {user_id or 'all'}")
    
    db = firestore.Client(project=os.getenv("GOOGLE_CLOUD_PROJECT"))
    
    # Query analytics for last N days
    start_date = datetime.now() - timedelta(days=days)
    
    analytics_query = db.collection('llm_analytics')\
        .where('timestamp', '>=', start_date)\
        .order_by('timestamp', direction=firestore.Query.DESCENDING)\
        .limit(1000)
    
    # Apply user filter if specified
    if user_id:
        analytics_query = analytics_query.where('user_id', '==', user_id)
    
    docs = analytics_query.stream()
    
    analytics = []
    total_cost = 0
    total_tokens_input = 0
    total_tokens_output = 0
    provider_stats = {}
    
    for doc in docs:
        data = doc.to_dict()
        analytics.append(data)
        
        # Aggregate stats
        total_cost += data.get('cost', 0)
        total_tokens_input += data.get('tokens_input', 0)
        total_tokens_output += data.get('tokens_output', 0)
        
        provider = data.get('provider', 'unknown')
        
        if provider not in provider_stats:
            provider_stats[provider] = {
                'count': 0,
                'total_cost': 0,
                'total_tokens_input': 0,
                'total_tokens_output': 0,
                'total_latency_ms': 0,
                'success_count': 0
            }
        
        provider_stats[provider]['count'] += 1
        provider_stats[provider]['total_cost'] += data.get('cost', 0)
        provider_stats[provider]['total_tokens_input'] += data.get('tokens_input', 0)
        provider_stats[provider]['total_tokens_output'] += data.get('tokens_output', 0)
        provider_stats[provider]['total_latency_ms'] += data.get('latency_ms', 0)
        
        if data.get('success', False):
            provider_stats[provider]['success_count'] += 1
    
    # Calculate averages
    for provider in provider_stats:
        stats = provider_stats[provider]
        if stats['count'] > 0:
            stats['avg_cost'] = stats['total_cost'] / stats['count']
            stats['avg_latency_ms'] = stats['total_latency_ms'] / stats['count']
            stats['success_rate'] = stats['success_count'] / stats['count']
    
    print(f"✅ [ADMIN] Analytics: {len(analytics)} generations, ${total_cost:.4f} total cost")
    
    return {
        "status": "success",
        "period_days": days,
        "user_filter": user_id,
        "summary": {
            "total_generations": len(analytics),
            "total_cost": round(total_cost, 4),
            "total_tokens_input": total_tokens_input,
            "total_tokens_output": total_tokens_output,
            "avg_cost_per_generation": round(total_cost / len(analytics), 4) if analytics else 0
        },
        "provider_stats": provider_stats,
        "recent_generations": analytics[:50]  # Last 50 for UI display
    }


@router.get("/system-health")
async def get_system_health(admin: User = Depends(require_admin)):
    """
    Get system health status
    
    Returns:
    - LLM provider availability
    - Recent error rates
    - System configuration status
    """
    
    print(f"🔐 [ADMIN] System health requested by: {admin.user_id}")
    
    db = firestore.Client(project=os.getenv("GOOGLE_CLOUD_PROJECT"))
    
    # Check provider config exists
    config_doc = db.collection('system_config').document('llm_providers').get()
    config_exists = config_doc.exists
    
    # Get recent analytics (last hour)
    one_hour_ago = datetime.now() - timedelta(hours=1)
    recent_query = db.collection('llm_analytics')\
        .where('timestamp', '>=', one_hour_ago)\
        .stream()
    
    recent_generations = list(recent_query)
    total_recent = len(recent_generations)
    failed_recent = sum(1 for doc in recent_generations if not doc.to_dict().get('success', False))
    
    error_rate = (failed_recent / total_recent * 100) if total_recent > 0 else 0
    
    health_status = {
        "status": "healthy" if error_rate < 5 else "degraded" if error_rate < 20 else "unhealthy",
        "config_exists": config_exists,
        "recent_generations_1h": total_recent,
        "recent_failures_1h": failed_recent,
        "error_rate_percent": round(error_rate, 2),
        "timestamp": datetime.now().isoformat()
    }
    
    print(f"✅ [ADMIN] System health: {health_status['status']}")
    
    return {
        "status": "success",
        "health": health_status
    }


@router.post("/test-llm-provider/{provider_id}")
async def test_llm_provider(
    provider_id: str,
    admin: User = Depends(require_admin)
):
    """
    Test a specific LLM provider
    
    Sends a simple test prompt to verify provider is working
    Returns generation time and cost
    """
    
    print(f"🔐 [ADMIN] Testing provider {provider_id} by: {admin.user_id}")
    
    # Validate provider_id
    valid_providers = ['openai_gpt4o_mini', 'openai_gpt4o', 'claude_35_sonnet', 'gemini_pro']
    if provider_id not in valid_providers:
        raise HTTPException(status_code=400, detail=f"Invalid provider_id. Must be one of: {valid_providers}")
    
    try:
        from app.services.llm_router import LLMRouter, LLMProvider
        
        router = LLMRouter()
        
        # Simple test prompt
        test_prompt = "Generate a simple JSON response: {\"test\": \"success\", \"message\": \"Provider is working\"}"
        system_instruction = "You are a test assistant. Respond with valid JSON only."
        
        # Try to generate
        result = await router.generate_meal_plan(
            prompt=test_prompt,
            system_instruction=system_instruction,
            user_id=admin.user_id,
            preferred_provider=LLMProvider(provider_id)
        )
        
        print(f"✅ [ADMIN] Provider {provider_id} test successful")
        
        return {
            "status": "success",
            "provider": provider_id,
            "test_result": "passed",
            "latency_ms": result.get('latency_ms', 0),
            "cost": result.get('cost', 0),
            "model_name": result.get('model_name', 'unknown')
        }
        
    except Exception as e:
        print(f"❌ [ADMIN] Provider {provider_id} test failed: {e}")
        
        return {
            "status": "error",
            "provider": provider_id,
            "test_result": "failed",
            "error": str(e)
        }

