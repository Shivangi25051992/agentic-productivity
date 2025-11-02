"""
Admin Feedback Management Router
Allows admins to view, filter, and manage user feedback
"""
from __future__ import annotations

from typing import Dict, List, Optional, Any
from datetime import datetime, timezone

from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel

from app.services.admin_auth import verify_admin_token
from app.services.admin_audit import audit_log
from google.cloud import firestore
import os

router = APIRouter(prefix="/admin/feedback", tags=["admin"], include_in_schema=False)


class FeedbackItem(BaseModel):
    id: str
    type: str
    comment: str
    user_email: str
    screen: str
    timestamp: str
    has_screenshot: bool
    screenshot_size: Optional[int] = None
    status: Optional[str] = "new"


class FeedbackStats(BaseModel):
    total: int
    bugs: int
    suggestions: int
    questions: int
    praise: int
    resolved: int
    pending: int


@router.get("/list")
def list_feedback(
    admin_subject: str = Depends(verify_admin_token),
    filter_type: Optional[str] = None,
    filter_status: Optional[str] = None,
    limit: int = 50
) -> Dict[str, Any]:
    """
    List all feedback with optional filters
    """
    try:
        project = os.getenv("GOOGLE_CLOUD_PROJECT", "productivityai-mvp")
        db = firestore.Client(project=project)
        
        # Build query
        query = db.collection("feedback").order_by("timestamp", direction=firestore.Query.DESCENDING)
        
        # Apply filters
        if filter_type:
            query = query.where("type", "==", filter_type)
        if filter_status:
            query = query.where("status", "==", filter_status)
        
        # Execute query
        docs = query.limit(limit).stream()
        
        feedback_list = []
        for doc in docs:
            data = doc.to_dict()
            feedback_list.append({
                "id": doc.id,
                "type": data.get("type", "unknown"),
                "comment": data.get("comment", ""),
                "user_email": data.get("user_email", "anonymous"),
                "screen": data.get("screen", "unknown"),
                "timestamp": data.get("timestamp").isoformat() if hasattr(data.get("timestamp"), 'isoformat') else str(data.get("timestamp", "")),
                "has_screenshot": data.get("has_screenshot", False),
                "screenshot_size": data.get("screenshot_size"),
                "status": data.get("status", "new")
            })
        
        # Log admin action
        audit_log("admin_feedback_list", actor=admin_subject, extra={"count": len(feedback_list)})
        
        return {
            "status": "success",
            "feedback": feedback_list,
            "count": len(feedback_list)
        }
    
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to fetch feedback: {str(e)}"
        )


@router.get("/stats")
def get_feedback_stats(
    admin_subject: str = Depends(verify_admin_token)
) -> FeedbackStats:
    """
    Get feedback statistics
    """
    try:
        project = os.getenv("GOOGLE_CLOUD_PROJECT", "productivityai-mvp")
        db = firestore.Client(project=project)
        
        # Get all feedback
        docs = db.collection("feedback").stream()
        
        total = 0
        bugs = 0
        suggestions = 0
        questions = 0
        praise = 0
        resolved = 0
        pending = 0
        
        for doc in docs:
            data = doc.to_dict()
            total += 1
            
            # Count by type
            ftype = data.get("type", "unknown")
            if ftype == "bug":
                bugs += 1
            elif ftype == "suggestion":
                suggestions += 1
            elif ftype == "question":
                questions += 1
            elif ftype == "praise":
                praise += 1
            
            # Count by status
            fstatus = data.get("status", "new")
            if fstatus == "resolved":
                resolved += 1
            else:
                pending += 1
        
        return FeedbackStats(
            total=total,
            bugs=bugs,
            suggestions=suggestions,
            questions=questions,
            praise=praise,
            resolved=resolved,
            pending=pending
        )
    
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to fetch stats: {str(e)}"
        )


@router.post("/{feedback_id}/resolve")
def resolve_feedback(
    feedback_id: str,
    admin_subject: str = Depends(verify_admin_token)
) -> Dict[str, str]:
    """
    Mark feedback as resolved
    """
    try:
        project = os.getenv("GOOGLE_CLOUD_PROJECT", "productivityai-mvp")
        db = firestore.Client(project=project)
        
        # Update feedback status
        db.collection("feedback").document(feedback_id).update({
            "status": "resolved",
            "resolved_at": firestore.SERVER_TIMESTAMP,
            "resolved_by": admin_subject
        })
        
        # Log admin action
        audit_log("admin_feedback_resolved", actor=admin_subject, extra={"feedback_id": feedback_id})
        
        return {
            "status": "success",
            "message": "Feedback marked as resolved"
        }
    
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to resolve feedback: {str(e)}"
        )


@router.delete("/{feedback_id}")
def delete_feedback(
    feedback_id: str,
    admin_subject: str = Depends(verify_admin_token)
) -> Dict[str, str]:
    """
    Delete feedback (use with caution)
    """
    try:
        project = os.getenv("GOOGLE_CLOUD_PROJECT", "productivityai-mvp")
        db = firestore.Client(project=project)
        
        # Delete feedback
        db.collection("feedback").document(feedback_id).delete()
        
        # Log admin action
        audit_log("admin_feedback_deleted", actor=admin_subject, extra={"feedback_id": feedback_id})
        
        return {
            "status": "success",
            "message": "Feedback deleted"
        }
    
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to delete feedback: {str(e)}"
        )

