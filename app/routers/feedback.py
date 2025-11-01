"""
Feedback API Endpoints
Handles user feedback submission, error reporting, and admin dashboard
"""

from fastapi import APIRouter, Depends, HTTPException, status, Request
from typing import Optional, List
from pydantic import BaseModel
from app.services.auth import get_current_user
from app.models.user import User
from app.services.feedback_service import (
    get_feedback_service,
    FeedbackSubmission,
    FeedbackType,
    FeedbackSeverity,
    FeedbackStatus
)

router = APIRouter(prefix="/feedback", tags=["feedback"])


# ============================================================================
# REQUEST/RESPONSE MODELS
# ============================================================================

class SubmitFeedbackRequest(BaseModel):
    """Request model for submitting feedback"""
    screen_name: str
    message: str
    feedback_type: Optional[FeedbackType] = None
    
    # Optional context
    device_os: Optional[str] = None
    device_version: Optional[str] = None
    app_version: Optional[str] = None
    
    # Error details (if applicable)
    error_message: Optional[str] = None
    error_code: Optional[str] = None
    
    # Attachments
    screenshot_url: Optional[str] = None
    
    # User preferences
    wants_followup: bool = False
    contact_email: Optional[str] = None


class FeedbackResponse(BaseModel):
    """Response after submitting feedback"""
    feedback_id: str
    message: str
    status: str
    estimated_response_time: str


class TrackActionRequest(BaseModel):
    """Request model for tracking user actions"""
    action: str
    screen: str
    metadata: Optional[dict] = None


class UpdateFeedbackStatusRequest(BaseModel):
    """Request model for updating feedback status"""
    status: FeedbackStatus
    notes: Optional[str] = None
    assigned_to: Optional[str] = None


# ============================================================================
# PUBLIC ENDPOINTS (User-facing)
# ============================================================================

@router.post("/submit", response_model=FeedbackResponse)
async def submit_feedback(
    request: SubmitFeedbackRequest,
    current_user: Optional[User] = Depends(get_current_user)
):
    """
    Submit user feedback or bug report
    
    - **screen_name**: Current screen where feedback originated
    - **message**: User's feedback message
    - **feedback_type**: Optional type (bug, feature, etc.)
    - **wants_followup**: Whether user wants to be contacted
    """
    feedback_service = get_feedback_service()
    
    # Get last user actions for context
    last_actions = []
    if current_user:
        last_actions = feedback_service.get_last_user_actions(current_user.user_id, limit=5)
    
    # Create submission
    submission = FeedbackSubmission(
        user_id=current_user.user_id if current_user else None,
        email=current_user.email if current_user else None,
        screen_name=request.screen_name,
        message=request.message,
        feedback_type=request.feedback_type,
        device_os=request.device_os,
        device_version=request.device_version,
        app_version=request.app_version,
        last_actions=last_actions,
        error_message=request.error_message,
        error_code=request.error_code,
        screenshot_url=request.screenshot_url,
        wants_followup=request.wants_followup,
        contact_email=request.contact_email or (current_user.email if current_user else None)
    )
    
    # Submit feedback
    result = feedback_service.submit_feedback(submission)
    
    return FeedbackResponse(**result)


@router.post("/track-action")
async def track_action(
    request: TrackActionRequest,
    current_user: User = Depends(get_current_user)
):
    """
    Track user action for breadcrumb trail
    
    - **action**: Action name (e.g., "button_tap", "screen_view")
    - **screen**: Screen name
    - **metadata**: Additional context
    """
    feedback_service = get_feedback_service()
    
    feedback_service.track_user_action(
        user_id=current_user.user_id,
        action=request.action,
        screen=request.screen,
        metadata=request.metadata
    )
    
    return {"status": "tracked"}


@router.get("/my-feedback")
async def get_my_feedback(
    current_user: User = Depends(get_current_user),
    limit: int = 20
):
    """Get user's own feedback submissions"""
    feedback_service = get_feedback_service()
    
    # Query user's feedback
    query = (
        feedback_service.feedback_collection
        .where('submission.user_id', '==', current_user.user_id)
        .order_by('created_at', direction='DESCENDING')
        .limit(limit)
    )
    
    feedback_list = []
    for doc in query.stream():
        data = doc.to_dict()
        feedback_list.append({
            'id': data['id'],
            'message': data['submission']['message'],
            'type': data.get('auto_type'),
            'status': data.get('status'),
            'created_at': data.get('created_at'),
            'resolution_notes': data.get('resolution_notes')
        })
    
    return {
        'feedback': feedback_list,
        'count': len(feedback_list)
    }


# ============================================================================
# ADMIN ENDPOINTS (Protected)
# ============================================================================

@router.get("/dashboard")
async def get_feedback_dashboard(
    days: int = 7,
    current_user: User = Depends(get_current_user)
):
    """
    Get feedback dashboard metrics
    
    - **days**: Number of days to analyze (default: 7)
    
    **Admin only**
    """
    # TODO: Add admin role check
    # if not current_user.is_admin:
    #     raise HTTPException(status_code=403, detail="Admin access required")
    
    feedback_service = get_feedback_service()
    dashboard = feedback_service.get_feedback_dashboard(days=days)
    
    return dashboard


@router.get("/list")
async def list_feedback(
    status: Optional[FeedbackStatus] = None,
    feedback_type: Optional[FeedbackType] = None,
    severity: Optional[FeedbackSeverity] = None,
    limit: int = 50,
    current_user: User = Depends(get_current_user)
):
    """
    List all feedback with optional filters
    
    **Admin only**
    """
    # TODO: Add admin role check
    
    feedback_service = get_feedback_service()
    query = feedback_service.feedback_collection
    
    if status:
        query = query.where('status', '==', status.value)
    if feedback_type:
        query = query.where('auto_type', '==', feedback_type.value)
    if severity:
        query = query.where('auto_severity', '==', severity.value)
    
    query = query.order_by('created_at', direction='DESCENDING').limit(limit)
    
    feedback_list = []
    for doc in query.stream():
        data = doc.to_dict()
        feedback_list.append({
            'id': data['id'],
            'user_id': data['submission'].get('user_id'),
            'screen': data['submission']['screen_name'],
            'message': data['submission']['message'],
            'type': data.get('auto_type'),
            'severity': data.get('auto_severity'),
            'status': data.get('status'),
            'occurrence_count': data.get('occurrence_count', 1),
            'created_at': data.get('created_at'),
            'last_actions': data['submission'].get('last_actions', [])
        })
    
    return {
        'feedback': feedback_list,
        'count': len(feedback_list)
    }


@router.put("/{feedback_id}/status")
async def update_feedback_status(
    feedback_id: str,
    request: UpdateFeedbackStatusRequest,
    current_user: User = Depends(get_current_user)
):
    """
    Update feedback status
    
    **Admin only**
    """
    # TODO: Add admin role check
    
    feedback_service = get_feedback_service()
    
    feedback_service.update_feedback_status(
        feedback_id=feedback_id,
        status=request.status,
        notes=request.notes,
        assigned_to=request.assigned_to
    )
    
    return {"status": "updated"}


@router.get("/export")
async def export_feedback(
    format: str = "json",
    status: Optional[FeedbackStatus] = None,
    feedback_type: Optional[FeedbackType] = None,
    severity: Optional[FeedbackSeverity] = None,
    current_user: User = Depends(get_current_user)
):
    """
    Export feedback to external format
    
    - **format**: Export format (json, csv, github, jira)
    
    **Admin only**
    """
    # TODO: Add admin role check
    
    feedback_service = get_feedback_service()
    
    filters = {}
    if status:
        filters['status'] = status.value
    if feedback_type:
        filters['type'] = feedback_type.value
    if severity:
        filters['severity'] = severity.value
    
    export_data = feedback_service.export_feedback(filters=filters, format=format)
    
    return {
        'format': format,
        'data': export_data
    }


@router.get("/trending")
async def get_trending_issues(
    days: int = 7,
    limit: int = 10,
    current_user: User = Depends(get_current_user)
):
    """
    Get trending/repeated issues
    
    **Admin only**
    """
    # TODO: Add admin role check
    
    feedback_service = get_feedback_service()
    
    # Query feedback with high occurrence count
    query = (
        feedback_service.feedback_collection
        .where('occurrence_count', '>', 1)
        .order_by('occurrence_count', direction='DESCENDING')
        .limit(limit)
    )
    
    trending = []
    for doc in query.stream():
        data = doc.to_dict()
        trending.append({
            'id': data['id'],
            'message': data['submission']['message'],
            'type': data.get('auto_type'),
            'severity': data.get('auto_severity'),
            'occurrence_count': data.get('occurrence_count', 1),
            'status': data.get('status'),
            'created_at': data.get('created_at')
        })
    
    return {
        'trending': trending,
        'count': len(trending)
    }


# ============================================================================
# ERROR LOGGING ENDPOINT (Internal)
# ============================================================================

@router.post("/log-error")
async def log_error(
    request: Request,
    error_type: str,
    error_message: str,
    stack_trace: Optional[str] = None,
    context: Optional[dict] = None,
    current_user: Optional[User] = Depends(get_current_user)
):
    """
    Log application error
    
    Internal endpoint for error tracking
    """
    feedback_service = get_feedback_service()
    
    # Create exception object for logging
    class LoggedException(Exception):
        pass
    
    error = LoggedException(error_message)
    
    error_id = feedback_service.log_error(
        error=error,
        context=context or {},
        user_id=current_user.user_id if current_user else None
    )
    
    return {
        'error_id': error_id,
        'status': 'logged'
    }

