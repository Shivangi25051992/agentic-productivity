"""
Fasting API Router - REST Endpoints
Clean API design with proper error handling and validation
"""

from fastapi import APIRouter, Depends, HTTPException, Query
from typing import List, Optional
from datetime import datetime

from app.models.fasting import (
    FastingSession,
    FastingProfile,
    FastingProtocol,
    StartFastingRequest,
    EndFastingRequest,
    FastingAnalytics,
    FastingSessionResponse,
)
from app.services.fasting_service import get_fasting_service, FastingService
from app.models.user import User
from app.services.auth import get_current_user

router = APIRouter(prefix="/fasting", tags=["fasting"])


# ============================================================================
# FASTING SESSION ENDPOINTS
# ============================================================================

@router.post("/start", response_model=FastingSession)
async def start_fasting(
    request: StartFastingRequest,
    current_user: User = Depends(get_current_user),
    service: FastingService = Depends(get_fasting_service)
):
    """
    Start a new fasting session
    
    - Automatically ends any active session
    - Validates protocol and duration
    - Returns the new session
    """
    try:
        session = await service.start_fasting_session(current_user.user_id, request)
        return session
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/end/{session_id}", response_model=FastingSession)
async def end_fasting(
    session_id: str,
    request: EndFastingRequest,
    current_user: User = Depends(get_current_user),
    service: FastingService = Depends(get_fasting_service)
):
    """
    End an active fasting session
    
    - Records completion metrics
    - Updates analytics
    - Returns completed session
    """
    try:
        session = await service.end_fasting_session(
            user_id=current_user.user_id,
            session_id=session_id,
            request=request
        )
        return session
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/current", response_model=Optional[FastingSessionResponse])
async def get_current_fast(
    current_user: User = Depends(get_current_user),
    service: FastingService = Depends(get_fasting_service)
):
    """
    Get currently active fasting session with details
    
    Returns:
    - Session data
    - Current metabolic stage
    - Progress percentage
    - Time remaining
    - Next stage prediction
    """
    session = await service.get_active_session(current_user.user_id)
    if not session:
        return None
    
    return await service.get_session_with_details(current_user.user_id, session.id)


@router.get("/sessions/{session_id}", response_model=FastingSessionResponse)
async def get_session(
    session_id: str,
    current_user: User = Depends(get_current_user),
    service: FastingService = Depends(get_fasting_service)
):
    """Get a specific fasting session with details"""
    session_response = await service.get_session_with_details(current_user.user_id, session_id)
    if not session_response:
        raise HTTPException(status_code=404, detail="Session not found")
    return session_response


@router.get("/history", response_model=List[FastingSession])
async def get_fasting_history(
    limit: int = Query(30, ge=1, le=100),
    current_user: User = Depends(get_current_user),
    service: FastingService = Depends(get_fasting_service)
):
    """
    Get fasting history
    
    Returns sessions in reverse chronological order (newest first)
    """
    sessions = await service.get_fasting_history(current_user.user_id, limit=limit)
    return sessions


# ============================================================================
# ANALYTICS ENDPOINTS
# ============================================================================

@router.get("/analytics", response_model=FastingAnalytics)
async def get_analytics(
    period_days: int = Query(30, ge=1, le=365),
    current_user: User = Depends(get_current_user),
    service: FastingService = Depends(get_fasting_service)
):
    """
    Get comprehensive fasting analytics
    
    Includes:
    - Completion rate
    - Average duration
    - Longest fast
    - Current streak
    - Break reason distribution
    - Energy/hunger patterns
    - Best time of day
    """
    analytics = await service.get_fasting_analytics(current_user.user_id, period_days)
    return analytics


# ============================================================================
# PROFILE ENDPOINTS
# ============================================================================

@router.get("/profile", response_model=Optional[FastingProfile])
async def get_profile(
    current_user: User = Depends(get_current_user),
    service: FastingService = Depends(get_fasting_service)
):
    """Get user's fasting profile and preferences"""
    profile = await service.get_fasting_profile(current_user.user_id)
    return profile


@router.put("/profile", response_model=FastingProfile)
async def update_profile(
    profile: FastingProfile,
    current_user: User = Depends(get_current_user),
    service: FastingService = Depends(get_fasting_service)
):
    """Create or update fasting profile"""
    profile = await service.create_or_update_profile(current_user.user_id, profile)
    return profile


# ============================================================================
# AI COACHING ENDPOINTS
# ============================================================================

@router.get("/coaching/context")
async def get_coaching_context(
    current_user: User = Depends(get_current_user),
    service: FastingService = Depends(get_fasting_service)
):
    """
    Get comprehensive context for AI coaching
    
    Returns all data needed for personalized coaching:
    - Active session
    - Profile
    - Analytics
    - Recent history
    """
    context = await service.get_coaching_context(current_user.user_id)
    return context


@router.post("/coaching/recommend-window")
async def recommend_window(
    user_schedule: dict,
    current_user: User = Depends(get_current_user),
    service: FastingService = Depends(get_fasting_service)
):
    """
    Get AI-powered fasting window recommendation
    
    Analyzes user's schedule and recommends optimal protocol
    """
    recommendation = await service.recommend_fasting_window(
        current_user.user_id,
        user_schedule
    )
    return recommendation

