"""
Cloud Function: Cleanup Expired Chat Sessions
Runs daily to delete expired chat sessions and their messages
"""

from google.cloud import firestore
from datetime import datetime, timezone
import functions_framework

@functions_framework.cloud_event
def cleanup_expired_sessions(cloud_event):
    """
    Scheduled function to cleanup expired chat sessions
    Trigger: Cloud Scheduler (daily at 2 AM UTC)
    """
    db = firestore.Client()
    now = datetime.now(timezone.utc)
    
    deleted_sessions = 0
    deleted_messages = 0
    
    try:
        # Get all users
        users_ref = db.collection('users')
        
        for user_doc in users_ref.stream():
            user_id = user_doc.id
            
            # Get expired sessions for this user
            sessions_ref = user_doc.reference.collection('chat_sessions')
            
            for session in sessions_ref.stream():
                session_data = session.to_dict()
                expires_at = session_data.get('expiresAt')
                
                if expires_at and expires_at < now:
                    # Delete all messages in this session
                    messages_ref = session.reference.collection('messages')
                    for msg in messages_ref.stream():
                        msg.reference.delete()
                        deleted_messages += 1
                    
                    # Delete the session
                    session.reference.delete()
                    deleted_sessions += 1
                    
                    print(f"Deleted expired session {session.id} for user {user_id}")
        
        print(f"Cleanup complete: {deleted_sessions} sessions, {deleted_messages} messages deleted")
        
        return {
            'status': 'success',
            'deleted_sessions': deleted_sessions,
            'deleted_messages': deleted_messages
        }
        
    except Exception as e:
        print(f"Error during cleanup: {e}")
        return {
            'status': 'error',
            'error': str(e)
        }

