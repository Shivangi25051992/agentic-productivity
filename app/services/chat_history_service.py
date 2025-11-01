"""
Chat History Service - Persist chat conversations for 7 days
"""

from google.cloud import firestore
from datetime import datetime, timedelta
from typing import List, Dict, Optional
import os
from dotenv import load_dotenv

load_dotenv()
load_dotenv('.env.local', override=True)


class ChatHistoryService:
    """Service to manage chat history persistence"""
    
    def __init__(self):
        self.db = firestore.Client(project=os.getenv("GOOGLE_CLOUD_PROJECT"))
        self.collection = self.db.collection('chat_history')
        self.retention_days = 7
    
    def save_message(self, user_id: str, role: str, content: str, metadata: Optional[Dict] = None):
        """
        Save a chat message
        
        Args:
            user_id: User identifier
            role: 'user' or 'assistant'
            content: Message content
            metadata: Additional data (calories, items, etc.)
        """
        message = {
            'user_id': user_id,
            'role': role,
            'content': content,
            'metadata': metadata or {},
            'timestamp': firestore.SERVER_TIMESTAMP,
            'expires_at': datetime.utcnow() + timedelta(days=self.retention_days)
        }
        
        self.collection.add(message)
    
    def get_user_history(self, user_id: str, limit: int = 100) -> List[Dict]:
        """
        Get chat history for a user
        
        Args:
            user_id: User identifier
            limit: Max messages to retrieve
        
        Returns:
            List of messages ordered by timestamp
        """
        query = (
            self.collection
            .where('user_id', '==', user_id)
            .where('expires_at', '>', datetime.utcnow())
            .order_by('timestamp', direction=firestore.Query.DESCENDING)
            .limit(limit)
        )
        
        messages = []
        for doc in query.stream():
            data = doc.to_dict()
            data['id'] = doc.id
            messages.append(data)
        
        # Reverse to get chronological order
        return list(reversed(messages))
    
    def get_conversation_context(self, user_id: str, last_n: int = 10) -> str:
        """
        Get recent conversation context for LLM
        
        Args:
            user_id: User identifier
            last_n: Number of recent messages
        
        Returns:
            Formatted conversation string
        """
        messages = self.get_user_history(user_id, limit=last_n)
        
        context = []
        for msg in messages:
            role = msg.get('role', 'user')
            content = msg.get('content', '')
            context.append(f"{role.upper()}: {content}")
        
        return "\n".join(context)
    
    def cleanup_expired(self):
        """Remove expired chat history (run as cron job)"""
        query = self.collection.where('expires_at', '<', datetime.utcnow())
        
        deleted = 0
        for doc in query.stream():
            doc.reference.delete()
            deleted += 1
        
        return deleted
    
    def get_user_stats(self, user_id: str) -> Dict:
        """Get statistics for a user's chat history"""
        messages = self.get_user_history(user_id, limit=1000)
        
        total_messages = len(messages)
        user_messages = sum(1 for m in messages if m.get('role') == 'user')
        assistant_messages = sum(1 for m in messages if m.get('role') == 'assistant')
        
        # Count meals logged
        meals_logged = 0
        total_calories = 0
        for msg in messages:
            metadata = msg.get('metadata', {})
            if metadata.get('category') == 'meal':
                meals_logged += 1
                total_calories += metadata.get('calories', 0)
        
        return {
            'total_messages': total_messages,
            'user_messages': user_messages,
            'assistant_messages': assistant_messages,
            'meals_logged': meals_logged,
            'total_calories': total_calories,
            'oldest_message': messages[0].get('timestamp') if messages else None,
            'newest_message': messages[-1].get('timestamp') if messages else None
        }


# Singleton instance
_chat_history_service = None

def get_chat_history_service() -> ChatHistoryService:
    """Get or create chat history service instance"""
    global _chat_history_service
    if _chat_history_service is None:
        _chat_history_service = ChatHistoryService()
    return _chat_history_service

