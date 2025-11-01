"""
Global Feedback and Error Capture Service
Comprehensive system for user feedback, error reporting, and issue tracking
"""

from google.cloud import firestore
from datetime import datetime, timedelta
from typing import Optional, List, Dict, Any
import os
import traceback
import json
from enum import Enum
from pydantic import BaseModel
from dotenv import load_dotenv

load_dotenv()
load_dotenv('.env.local', override=True)


class FeedbackType(str, Enum):
    """Types of feedback"""
    BUG = "bug"
    UX = "ux"
    FEATURE = "feature"
    CRASH = "crash"
    PERFORMANCE = "performance"
    CONTENT = "content"
    OTHER = "other"


class FeedbackSeverity(str, Enum):
    """Severity levels"""
    CRITICAL = "critical"  # App crashes, data loss
    HIGH = "high"  # Major feature broken
    MEDIUM = "medium"  # Minor issues
    LOW = "low"  # Cosmetic, suggestions


class FeedbackStatus(str, Enum):
    """Feedback status"""
    NEW = "new"
    ACKNOWLEDGED = "acknowledged"
    IN_PROGRESS = "in_progress"
    RESOLVED = "resolved"
    WONT_FIX = "wont_fix"
    DUPLICATE = "duplicate"


class FeedbackSubmission(BaseModel):
    """User feedback submission"""
    user_id: Optional[str] = None
    email: Optional[str] = None
    screen_name: str
    message: str
    feedback_type: Optional[FeedbackType] = None
    
    # Auto-captured context
    device_os: Optional[str] = None
    device_version: Optional[str] = None
    app_version: Optional[str] = None
    timestamp: datetime = datetime.utcnow()
    
    # User actions breadcrumb
    last_actions: List[Dict[str, Any]] = []
    
    # Error context (if applicable)
    error_message: Optional[str] = None
    stack_trace: Optional[str] = None
    error_code: Optional[str] = None
    
    # Attachments
    screenshot_url: Optional[str] = None
    log_file_url: Optional[str] = None
    
    # User preferences
    wants_followup: bool = False
    contact_email: Optional[str] = None


class FeedbackRecord(BaseModel):
    """Internal feedback record with metadata"""
    id: str
    submission: FeedbackSubmission
    
    # AI/Rule-based classification
    auto_type: Optional[FeedbackType] = None
    auto_severity: Optional[FeedbackSeverity] = None
    auto_tags: List[str] = []
    
    # Status tracking
    status: FeedbackStatus = FeedbackStatus.NEW
    assigned_to: Optional[str] = None
    resolution_notes: Optional[str] = None
    
    # Deduplication
    similar_feedback_ids: List[str] = []
    duplicate_of: Optional[str] = None
    occurrence_count: int = 1
    
    # Timestamps
    created_at: datetime
    updated_at: datetime
    resolved_at: Optional[datetime] = None
    
    # User notification
    user_notified: bool = False
    notification_sent_at: Optional[datetime] = None


class FeedbackService:
    """Service for managing feedback and error reports"""
    
    def __init__(self):
        self.db = firestore.Client(project=os.getenv("GOOGLE_CLOUD_PROJECT"))
        self.feedback_collection = self.db.collection('feedback')
        self.actions_collection = self.db.collection('user_actions')
        self.errors_collection = self.db.collection('app_errors')
    
    def submit_feedback(self, submission: FeedbackSubmission) -> Dict[str, Any]:
        """
        Submit user feedback
        
        Returns:
            Dict with feedback_id and confirmation message
        """
        # Auto-classify feedback
        auto_type, auto_severity, auto_tags = self._classify_feedback(submission)
        
        # Check for duplicates
        similar_ids = self._find_similar_feedback(submission)
        
        # Create feedback record
        feedback_ref = self.feedback_collection.document()
        feedback_id = feedback_ref.id
        
        record = {
            'id': feedback_id,
            'submission': submission.dict(),
            'auto_type': auto_type,
            'auto_severity': auto_severity,
            'auto_tags': auto_tags,
            'status': FeedbackStatus.NEW.value,
            'similar_feedback_ids': similar_ids,
            'occurrence_count': 1,
            'created_at': firestore.SERVER_TIMESTAMP,
            'updated_at': firestore.SERVER_TIMESTAMP,
            'user_notified': False
        }
        
        # If duplicate found, increment count
        if similar_ids:
            original_id = similar_ids[0]
            original_ref = self.feedback_collection.document(original_id)
            original_ref.update({
                'occurrence_count': firestore.Increment(1),
                'updated_at': firestore.SERVER_TIMESTAMP
            })
            record['duplicate_of'] = original_id
        
        # Save feedback
        feedback_ref.set(record)
        
        # Send confirmation to user
        confirmation = self._send_user_confirmation(submission, feedback_id)
        
        # Trigger alerts for critical issues
        if auto_severity == FeedbackSeverity.CRITICAL:
            self._send_critical_alert(feedback_id, submission)
        
        return {
            'feedback_id': feedback_id,
            'message': confirmation,
            'status': 'received',
            'estimated_response_time': self._estimate_response_time(auto_severity)
        }
    
    def log_error(
        self,
        error: Exception,
        context: Dict[str, Any],
        user_id: Optional[str] = None
    ) -> str:
        """
        Log application error with full context
        
        Args:
            error: The exception that occurred
            context: Additional context (screen, action, etc.)
            user_id: Optional user ID
        
        Returns:
            Error ID for tracking
        """
        error_ref = self.errors_collection.document()
        error_id = error_ref.id
        
        error_record = {
            'id': error_id,
            'error_type': type(error).__name__,
            'error_message': str(error),
            'stack_trace': traceback.format_exc(),
            'context': context,
            'user_id': user_id,
            'timestamp': firestore.SERVER_TIMESTAMP,
            'resolved': False
        }
        
        error_ref.set(error_record)
        
        # Try to link to user feedback if exists
        if user_id:
            self._link_error_to_feedback(error_id, user_id, context)
        
        return error_id
    
    def track_user_action(
        self,
        user_id: str,
        action: str,
        screen: str,
        metadata: Optional[Dict] = None
    ):
        """
        Track user actions for breadcrumb trail
        
        Args:
            user_id: User identifier
            action: Action name (e.g., "button_tap", "screen_view")
            screen: Screen name
            metadata: Additional data
        """
        action_ref = self.actions_collection.document()
        
        action_record = {
            'user_id': user_id,
            'action': action,
            'screen': screen,
            'metadata': metadata or {},
            'timestamp': firestore.SERVER_TIMESTAMP
        }
        
        action_ref.set(action_record)
        
        # Clean up old actions (keep last 100 per user)
        self._cleanup_old_actions(user_id, keep_last=100)
    
    def get_last_user_actions(
        self,
        user_id: str,
        limit: int = 5
    ) -> List[Dict[str, Any]]:
        """Get last N user actions for breadcrumb"""
        query = (
            self.actions_collection
            .where('user_id', '==', user_id)
            .order_by('timestamp', direction=firestore.Query.DESCENDING)
            .limit(limit)
        )
        
        actions = []
        for doc in query.stream():
            data = doc.to_dict()
            actions.append({
                'action': data['action'],
                'screen': data['screen'],
                'timestamp': data['timestamp'].isoformat() if data.get('timestamp') else None,
                'metadata': data.get('metadata', {})
            })
        
        return list(reversed(actions))  # Chronological order
    
    def get_feedback_dashboard(
        self,
        days: int = 7
    ) -> Dict[str, Any]:
        """
        Get feedback dashboard metrics
        
        Returns:
            Dashboard data with trends and statistics
        """
        cutoff = datetime.utcnow() - timedelta(days=days)
        
        # Query feedback
        query = self.feedback_collection.where('created_at', '>', cutoff)
        
        feedback_list = []
        for doc in query.stream():
            feedback_list.append(doc.to_dict())
        
        # Calculate metrics
        total = len(feedback_list)
        by_type = {}
        by_severity = {}
        by_status = {}
        critical_unresolved = []
        trending_issues = {}
        
        for fb in feedback_list:
            # Count by type
            fb_type = fb.get('auto_type', 'other')
            by_type[fb_type] = by_type.get(fb_type, 0) + 1
            
            # Count by severity
            severity = fb.get('auto_severity', 'low')
            by_severity[severity] = by_severity.get(severity, 0) + 1
            
            # Count by status
            status = fb.get('status', 'new')
            by_status[status] = by_status.get(status, 0) + 1
            
            # Track critical unresolved
            if severity == 'critical' and status in ['new', 'acknowledged']:
                critical_unresolved.append({
                    'id': fb['id'],
                    'message': fb['submission']['message'][:100],
                    'created_at': fb['created_at']
                })
            
            # Track trending issues (by occurrence count)
            if fb.get('occurrence_count', 1) > 1:
                issue_key = fb['submission']['message'][:50]
                trending_issues[issue_key] = fb.get('occurrence_count', 1)
        
        # Calculate response metrics
        avg_response_time = self._calculate_avg_response_time(feedback_list)
        resolution_rate = (
            by_status.get('resolved', 0) / total * 100 if total > 0 else 0
        )
        
        return {
            'period_days': days,
            'total_feedback': total,
            'by_type': by_type,
            'by_severity': by_severity,
            'by_status': by_status,
            'critical_unresolved': critical_unresolved,
            'trending_issues': sorted(
                trending_issues.items(),
                key=lambda x: x[1],
                reverse=True
            )[:10],
            'avg_response_time_hours': avg_response_time,
            'resolution_rate_percent': round(resolution_rate, 1),
            'needs_attention': len(critical_unresolved) + by_status.get('new', 0)
        }
    
    def update_feedback_status(
        self,
        feedback_id: str,
        status: FeedbackStatus,
        notes: Optional[str] = None,
        assigned_to: Optional[str] = None
    ):
        """Update feedback status"""
        feedback_ref = self.feedback_collection.document(feedback_id)
        
        update_data = {
            'status': status.value,
            'updated_at': firestore.SERVER_TIMESTAMP
        }
        
        if notes:
            update_data['resolution_notes'] = notes
        
        if assigned_to:
            update_data['assigned_to'] = assigned_to
        
        if status == FeedbackStatus.RESOLVED:
            update_data['resolved_at'] = firestore.SERVER_TIMESTAMP
        
        feedback_ref.update(update_data)
        
        # Notify user if they requested followup
        feedback_doc = feedback_ref.get()
        if feedback_doc.exists:
            data = feedback_doc.to_dict()
            if data['submission'].get('wants_followup'):
                self._notify_user_of_resolution(feedback_id, data, notes)
    
    def export_feedback(
        self,
        filters: Optional[Dict] = None,
        format: str = "json"
    ) -> str:
        """
        Export feedback to external issue tracker
        
        Args:
            filters: Optional filters (status, type, severity)
            format: Export format (json, csv, github, jira)
        
        Returns:
            Export data or URL
        """
        query = self.feedback_collection
        
        if filters:
            if 'status' in filters:
                query = query.where('status', '==', filters['status'])
            if 'type' in filters:
                query = query.where('auto_type', '==', filters['type'])
            if 'severity' in filters:
                query = query.where('auto_severity', '==', filters['severity'])
        
        feedback_list = []
        for doc in query.stream():
            feedback_list.append(doc.to_dict())
        
        if format == "json":
            return json.dumps(feedback_list, indent=2, default=str)
        elif format == "csv":
            return self._export_to_csv(feedback_list)
        elif format == "github":
            return self._export_to_github(feedback_list)
        elif format == "jira":
            return self._export_to_jira(feedback_list)
        
        return json.dumps(feedback_list, default=str)
    
    # ========================================================================
    # PRIVATE HELPER METHODS
    # ========================================================================
    
    def _classify_feedback(
        self,
        submission: FeedbackSubmission
    ) -> tuple[FeedbackType, FeedbackSeverity, List[str]]:
        """
        AI/Rule-based classification of feedback
        
        Returns:
            (type, severity, tags)
        """
        message = submission.message.lower()
        
        # Determine type
        if submission.error_message or submission.stack_trace:
            fb_type = FeedbackType.CRASH
        elif any(word in message for word in ['crash', 'error', 'broken', 'bug', 'not working']):
            fb_type = FeedbackType.BUG
        elif any(word in message for word in ['slow', 'lag', 'freeze', 'performance']):
            fb_type = FeedbackType.PERFORMANCE
        elif any(word in message for word in ['confusing', 'hard to', 'difficult', 'ux', 'design']):
            fb_type = FeedbackType.UX
        elif any(word in message for word in ['feature', 'add', 'want', 'wish', 'could']):
            fb_type = FeedbackType.FEATURE
        else:
            fb_type = submission.feedback_type or FeedbackType.OTHER
        
        # Determine severity
        if fb_type == FeedbackType.CRASH:
            severity = FeedbackSeverity.CRITICAL
        elif any(word in message for word in ['critical', 'urgent', 'important', 'data loss']):
            severity = FeedbackSeverity.HIGH
        elif any(word in message for word in ['minor', 'small', 'cosmetic']):
            severity = FeedbackSeverity.LOW
        else:
            severity = FeedbackSeverity.MEDIUM
        
        # Extract tags
        tags = []
        if 'login' in message or 'auth' in message:
            tags.append('authentication')
        if 'chat' in message or 'ai' in message:
            tags.append('ai_chat')
        if 'dashboard' in message or 'home' in message:
            tags.append('dashboard')
        if 'onboarding' in message:
            tags.append('onboarding')
        if submission.screen_name:
            tags.append(f"screen:{submission.screen_name}")
        
        return fb_type, severity, tags
    
    def _find_similar_feedback(
        self,
        submission: FeedbackSubmission,
        threshold: float = 0.8
    ) -> List[str]:
        """Find similar feedback using simple text matching"""
        # Query recent feedback from same screen
        query = (
            self.feedback_collection
            .where('submission.screen_name', '==', submission.screen_name)
            .where('created_at', '>', datetime.utcnow() - timedelta(days=7))
            .limit(50)
        )
        
        similar_ids = []
        for doc in query.stream():
            data = doc.to_dict()
            existing_message = data['submission']['message'].lower()
            new_message = submission.message.lower()
            
            # Simple similarity check (can be improved with ML)
            common_words = set(existing_message.split()) & set(new_message.split())
            if len(common_words) >= 3:  # At least 3 common words
                similar_ids.append(data['id'])
        
        return similar_ids
    
    def _send_user_confirmation(
        self,
        submission: FeedbackSubmission,
        feedback_id: str
    ) -> str:
        """Generate user confirmation message"""
        if submission.feedback_type == FeedbackType.CRASH:
            return (
                f"We're so sorry you experienced a crash! "
                f"Our team has been notified (ID: {feedback_id[:8]}) and we're "
                f"working on a fix. We'll update you within 24 hours."
            )
        elif submission.feedback_type == FeedbackType.BUG:
            return (
                f"Thanks for reporting this bug! We've logged it (ID: {feedback_id[:8]}) "
                f"and our team will investigate. You're helping make the app better! 🙏"
            )
        else:
            return (
                f"Thank you for your feedback! We've received it (ID: {feedback_id[:8]}) "
                f"and we'll review it carefully. Your input helps us improve! ✨"
            )
    
    def _estimate_response_time(self, severity: FeedbackSeverity) -> str:
        """Estimate response time based on severity"""
        if severity == FeedbackSeverity.CRITICAL:
            return "within 4 hours"
        elif severity == FeedbackSeverity.HIGH:
            return "within 24 hours"
        elif severity == FeedbackSeverity.MEDIUM:
            return "within 3 days"
        else:
            return "within 1 week"
    
    def _send_critical_alert(self, feedback_id: str, submission: FeedbackSubmission):
        """Send alert for critical issues"""
        # TODO: Integrate with Slack/PagerDuty/Email
        print(f"🚨 CRITICAL FEEDBACK: {feedback_id}")
        print(f"   User: {submission.user_id}")
        print(f"   Screen: {submission.screen_name}")
        print(f"   Message: {submission.message}")
    
    def _link_error_to_feedback(
        self,
        error_id: str,
        user_id: str,
        context: Dict
    ):
        """Link backend error to user feedback if exists"""
        # Query recent feedback from this user
        query = (
            self.feedback_collection
            .where('submission.user_id', '==', user_id)
            .where('created_at', '>', datetime.utcnow() - timedelta(minutes=5))
            .limit(1)
        )
        
        for doc in query.stream():
            # Link error to feedback
            doc.reference.update({
                'linked_error_id': error_id,
                'updated_at': firestore.SERVER_TIMESTAMP
            })
    
    def _cleanup_old_actions(self, user_id: str, keep_last: int = 100):
        """Clean up old user actions to prevent bloat"""
        query = (
            self.actions_collection
            .where('user_id', '==', user_id)
            .order_by('timestamp', direction=firestore.Query.DESCENDING)
            .offset(keep_last)
        )
        
        for doc in query.stream():
            doc.reference.delete()
    
    def _calculate_avg_response_time(self, feedback_list: List[Dict]) -> float:
        """Calculate average response time in hours"""
        response_times = []
        
        for fb in feedback_list:
            if fb.get('resolved_at') and fb.get('created_at'):
                created = fb['created_at']
                resolved = fb['resolved_at']
                if isinstance(created, datetime) and isinstance(resolved, datetime):
                    delta = resolved - created
                    response_times.append(delta.total_seconds() / 3600)
        
        return sum(response_times) / len(response_times) if response_times else 0
    
    def _notify_user_of_resolution(
        self,
        feedback_id: str,
        feedback_data: Dict,
        notes: Optional[str]
    ):
        """Notify user that their feedback was resolved"""
        # TODO: Send email/push notification
        print(f"📧 Notifying user about resolution: {feedback_id}")
    
    def _export_to_csv(self, feedback_list: List[Dict]) -> str:
        """Export to CSV format"""
        import csv
        import io
        
        output = io.StringIO()
        writer = csv.DictWriter(output, fieldnames=[
            'id', 'type', 'severity', 'status', 'message', 'screen', 'created_at'
        ])
        writer.writeheader()
        
        for fb in feedback_list:
            writer.writerow({
                'id': fb['id'],
                'type': fb.get('auto_type', ''),
                'severity': fb.get('auto_severity', ''),
                'status': fb.get('status', ''),
                'message': fb['submission']['message'][:100],
                'screen': fb['submission']['screen_name'],
                'created_at': str(fb.get('created_at', ''))
            })
        
        return output.getvalue()
    
    def _export_to_github(self, feedback_list: List[Dict]) -> str:
        """Export as GitHub issues format"""
        # TODO: Integrate with GitHub API
        return "GitHub export not implemented yet"
    
    def _export_to_jira(self, feedback_list: List[Dict]) -> str:
        """Export as JIRA issues format"""
        # TODO: Integrate with JIRA API
        return "JIRA export not implemented yet"


# Singleton instance
_feedback_service = None

def get_feedback_service() -> FeedbackService:
    """Get or create feedback service instance"""
    global _feedback_service
    if _feedback_service is None:
        _feedback_service = FeedbackService()
    return _feedback_service

