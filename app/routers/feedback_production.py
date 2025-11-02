"""
Production Feedback System
Captures user feedback with screenshots and sends to admin
"""

from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel
from typing import Optional
from datetime import datetime
from google.cloud import firestore
import os

from app.models import User
from app.services.auth import get_current_user
from app.services.invitation_service import get_invitation_service

router = APIRouter(prefix="/feedback", tags=["feedback"])

class FeedbackSubmit(BaseModel):
    type: str  # bug, suggestion, question, praise
    comment: str
    screen: str
    timestamp: str
    has_screenshot: bool = False
    screenshot_size: Optional[int] = None


@router.post("/submit")
async def submit_feedback(
    feedback: FeedbackSubmit,
    current_user: User = Depends(get_current_user)
):
    """
    Submit user feedback
    Stores in Firestore and sends email to admin
    """
    try:
        # Store in Firestore
        db = firestore.Client()
        feedback_ref = db.collection('feedback').document()
        
        feedback_data = {
            'feedback_id': feedback_ref.id,
            'user_id': current_user.user_id,
            'user_email': current_user.email,
            'type': feedback.type,
            'comment': feedback.comment,
            'screen': feedback.screen,
            'timestamp': datetime.fromisoformat(feedback.timestamp.replace('Z', '+00:00')),
            'has_screenshot': feedback.has_screenshot,
            'screenshot_size': feedback.screenshot_size,
            'status': 'new',  # new, reviewing, resolved
            'created_at': firestore.SERVER_TIMESTAMP,
        }
        
        feedback_ref.set(feedback_data)
        
        # Send email to admin
        invitation_service = get_invitation_service()
        _send_feedback_email(
            invitation_service,
            feedback_data,
            current_user.email
        )
        
        return {
            'success': True,
            'feedback_id': feedback_ref.id,
            'message': 'Feedback submitted successfully'
        }
        
    except Exception as e:
        print(f"Error submitting feedback: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to submit feedback: {str(e)}"
        )


def _send_feedback_email(invitation_service, feedback_data, user_email):
    """Send feedback notification to admin"""
    
    emoji_map = {
        'bug': '🐛',
        'suggestion': '💡',
        'question': '❓',
        'praise': '👍'
    }
    
    emoji = emoji_map.get(feedback_data['type'], '📝')
    
    subject = f"{emoji} New Feedback: {feedback_data['type'].title()} from {user_email}"
    
    body = f"""
    <html>
    <body style="font-family: Arial, sans-serif; padding: 20px;">
        <h2 style="color: #FF6B35;">{emoji} New Feedback Received</h2>
        
        <div style="background: #f5f5f5; padding: 15px; border-radius: 5px; margin: 20px 0;">
            <p><strong>Type:</strong> {feedback_data['type'].title()}</p>
            <p><strong>From:</strong> {user_email}</p>
            <p><strong>Screen:</strong> {feedback_data['screen']}</p>
            <p><strong>Time:</strong> {feedback_data['timestamp']}</p>
            <p><strong>Has Screenshot:</strong> {'Yes' if feedback_data['has_screenshot'] else 'No'}</p>
        </div>
        
        <h3>Comment:</h3>
        <div style="background: #fff; padding: 15px; border-left: 4px solid #FF6B35; margin: 20px 0;">
            <p style="white-space: pre-wrap;">{feedback_data['comment']}</p>
        </div>
        
        <h3>Action:</h3>
        <p>View in <a href="https://console.firebase.google.com/project/productivityai-mvp/firestore/data/feedback/{feedback_data['feedback_id']}">Firebase Console</a></p>
        
        <p style="color: #666; font-size: 12px; margin-top: 30px;">
            This is an automated notification from AI Productivity App
        </p>
    </body>
    </html>
    """
    
    try:
        import smtplib
        from email.mime.text import MIMEText
        from email.mime.multipart import MIMEMultipart
        
        msg = MIMEMultipart('alternative')
        msg['Subject'] = subject
        msg['From'] = invitation_service.smtp_user or "noreply@aiproductivity.app"
        msg['To'] = invitation_service.admin_email
        
        html_part = MIMEText(body, 'html')
        msg.attach(html_part)
        
        if invitation_service.smtp_user and invitation_service.smtp_password:
            with smtplib.SMTP(invitation_service.smtp_server, invitation_service.smtp_port) as server:
                server.starttls()
                server.login(invitation_service.smtp_user, invitation_service.smtp_password)
                server.send_message(msg)
            
            print(f"✅ Feedback email sent to {invitation_service.admin_email}")
        else:
            print(f"⚠️  SMTP not configured. Feedback logged to Firestore.")
            print(f"   Type: {feedback_data['type']}")
            print(f"   From: {user_email}")
            print(f"   Comment: {feedback_data['comment'][:100]}...")
    
    except Exception as e:
        print(f"❌ Failed to send feedback email: {e}")
        # Don't fail the request if email fails


@router.get("/list")
async def list_feedback(
    status_filter: Optional[str] = None,
    limit: int = 50
):
    """
    List all feedback (admin only)
    TODO: Add admin authentication
    """
    try:
        db = firestore.Client()
        query = db.collection('feedback').order_by('created_at', direction=firestore.Query.DESCENDING).limit(limit)
        
        if status_filter:
            query = query.where('status', '==', status_filter)
        
        feedback_list = []
        for doc in query.stream():
            data = doc.to_dict()
            data['feedback_id'] = doc.id
            
            # Convert timestamp to ISO string
            if 'created_at' in data and data['created_at']:
                try:
                    data['created_at'] = data['created_at'].isoformat()
                except:
                    pass
            
            if 'timestamp' in data and data['timestamp']:
                try:
                    data['timestamp'] = data['timestamp'].isoformat()
                except:
                    pass
            
            feedback_list.append(data)
        
        return {
            'success': True,
            'count': len(feedback_list),
            'feedback': feedback_list
        }
        
    except Exception as e:
        print(f"Error listing feedback: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to list feedback: {str(e)}"
        )

