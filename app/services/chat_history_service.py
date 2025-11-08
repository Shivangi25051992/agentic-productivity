"""
Chat History Service - Persist chat conversations for 7 days
NEW: Uses subcollection structure with sessions
"""

from google.cloud import firestore
from datetime import datetime, timedelta, timezone
from typing import List, Dict, Optional, Any
import os
import asyncio
from dotenv import load_dotenv

load_dotenv()
load_dotenv('.env.local', override=True)


class ChatHistoryService:
    """Service to manage chat history persistence with session support"""
    
    def __init__(self):
        self.db = firestore.Client(project=os.getenv("GOOGLE_CLOUD_PROJECT"))
        self.retention_days = 7
        self.use_new_structure = True  # Feature flag for migration
    
    def _get_or_create_session(self, user_id: str) -> str:
        """Get or create today's chat session"""
        today = datetime.utcnow().date().isoformat()
        session_id = today
        
        session_ref = self.db.collection('users').document(user_id)\
                             .collection('chat_sessions').document(session_id)
        
        session = session_ref.get()
        
        if not session.exists:
            # Create new session
            session_data = {
                'sessionId': session_id,
                'title': f"Chat - {today}",
                'startedAt': firestore.SERVER_TIMESTAMP,
                'lastMessageAt': firestore.SERVER_TIMESTAMP,
                'messageCount': 0,
                'expiresAt': datetime.utcnow() + timedelta(days=self.retention_days),
                'archived': False
            }
            session_ref.set(session_data)
        
        return session_id
    
    async def save_message(
        self, 
        user_id: str, 
        role: str, 
        content: str, 
        metadata: Optional[Dict] = None,
        # ✨ NEW: Accept expandable fields
        summary: Optional[str] = None,
        suggestion: Optional[str] = None,
        details: Optional[Dict] = None,
        expandable: bool = False,
        # 🧠 PHASE 2: Accept explainable AI fields
        confidence_score: Optional[float] = None,
        confidence_level: Optional[str] = None,
        confidence_factors: Optional[Dict[str, float]] = None,
        explanation: Optional[Dict[str, Any]] = None,
        alternatives: Optional[List[Dict[str, Any]]] = None,
        # 🎨 UX FIX: Accept messageId for consistency
        message_id: Optional[str] = None
    ):
        """
        Save a chat message to user's current session (ASYNC - non-blocking)
        
        Args:
            user_id: User identifier
            role: 'user' or 'assistant'
            content: Message content
            metadata: Additional data (calories, items, etc.)
            summary: Brief one-liner summary (expandable chat)
            suggestion: Actionable tip (expandable chat)
            details: Structured breakdown (expandable chat)
            expandable: Whether message supports expandable UI
        """
        if self.use_new_structure:
            # NEW: Save to subcollection with session
            session_id = self._get_or_create_session(user_id)
            
            # 🎨 UX FIX: Generate consistent messageId (milliseconds since epoch)
            if not message_id:
                message_id = str(int(datetime.now(timezone.utc).timestamp() * 1000))
            
            message = {
                'messageId': message_id,  # 🎨 UX FIX: Store consistent ID for feedback matching
                'role': role,
                'content': content,
                'metadata': metadata or {},
                'timestamp': firestore.SERVER_TIMESTAMP,
                # ✨ NEW: Add expandable fields at top level (for easy retrieval)
                'summary': summary,
                'suggestion': suggestion,
                'details': details,
                'expandable': expandable,
                # 🧠 PHASE 2: Add explainable AI fields
                'confidence_score': confidence_score,
                'confidence_level': confidence_level,
                'confidence_factors': confidence_factors,
                'explanation': explanation,
                'alternatives': alternatives
            }
            
            # Add message to session (ASYNC - non-blocking)
            session_ref = self.db.collection('users').document(user_id)\
                                 .collection('chat_sessions').document(session_id)
            message_ref = session_ref.collection('messages').document()
            await asyncio.to_thread(message_ref.set, message)
            
            # Update session metadata (ASYNC - non-blocking)
            await asyncio.to_thread(session_ref.update, {
                'lastMessageAt': firestore.SERVER_TIMESTAMP,
                'messageCount': firestore.Increment(1)
            })
        else:
            # OLD: Save to flat collection (backward compatibility)
            message = {
                'user_id': user_id,
                'role': role,
                'content': content,
                'metadata': metadata or {},
                'timestamp': firestore.SERVER_TIMESTAMP,
                'expires_at': datetime.utcnow() + timedelta(days=self.retention_days),
                # ✨ NEW: Add expandable fields for backward compatibility
                'summary': summary,
                'suggestion': suggestion,
                'details': details,
                'expandable': expandable,
                # 🧠 PHASE 2: Add explainable AI fields
                'confidence_score': confidence_score,
                'confidence_level': confidence_level,
                'confidence_factors': confidence_factors,
                'explanation': explanation,
                'alternatives': alternatives
            }
            self.db.collection('chat_history').add(message)
    
    def get_user_history(self, user_id: str, limit: int = 100) -> List[Dict]:
        """
        Get chat history for a user
        
        Args:
            user_id: User identifier
            limit: Max messages to retrieve
        
        Returns:
            List of messages ordered by timestamp
        """
        messages = []
        seen_message_ids = set()  # Track unique message IDs to prevent duplicates
        
        if self.use_new_structure:
            # NEW: Load from subcollections
            try:
                # Filter for last 24 hours only
                cutoff_time = datetime.now(timezone.utc) - timedelta(hours=24)
                
                # Get ONLY today's session (session_id is date-based)
                today = datetime.utcnow().date().isoformat()
                
                # Try to get today's session first
                try:
                    session_ref = self.db.collection('users').document(user_id)\
                                         .collection('chat_sessions').document(today)
                    session = session_ref.get()
                    
                    if session.exists:
                        # Get messages from today's session (ASCENDING = oldest first, so newest appear at bottom)
                        session_messages = session_ref.collection('messages')\
                                                  .order_by('timestamp', direction=firestore.Query.ASCENDING)\
                                                  .limit(limit)\
                                                  .stream()
                        
                        for msg in session_messages:
                            msg_data = msg.to_dict()
                            msg_id = msg.id
                            
                            # Skip duplicates
                            if msg_id in seen_message_ids:
                                continue
                            seen_message_ids.add(msg_id)
                            
                            msg_data['id'] = msg_id
                            # 🎨 UX FIX: Ensure messageId is present (fallback to doc ID if not stored)
                            if 'messageId' not in msg_data or not msg_data['messageId']:
                                msg_data['messageId'] = msg_id
                            
                            # Convert timestamp
                            timestamp_obj = msg_data.get('timestamp')
                            if timestamp_obj:
                                try:
                                    # Check if message is within last 24 hours
                                    if timestamp_obj < cutoff_time:
                                        continue  # Skip old messages
                                    msg_data['timestamp'] = timestamp_obj.isoformat()
                                except:
                                    msg_data['timestamp'] = datetime.utcnow().isoformat()
                            else:
                                msg_data['timestamp'] = datetime.utcnow().isoformat()
                            
                            messages.append(msg_data)
                            
                            if len(messages) >= limit:
                                break
                except Exception as e:
                    print(f"Error loading today's session: {e}")
                
                return messages[:limit]
                
            except Exception as e:
                print(f"Error loading from new structure: {e}")
                # Fall back to old structure
                return self._get_history_old_structure(user_id, limit)
        else:
            # OLD: Load from flat collection
            return self._get_history_old_structure(user_id, limit)
    
    def _get_history_old_structure(self, user_id: str, limit: int) -> List[Dict]:
        """Backward compatibility: Load from old flat structure"""
        query = self.db.collection('chat_history').where('user_id', '==', user_id)
        
        messages = []
        now = datetime.utcnow()
        
        for doc in query.stream():
            data = doc.to_dict()
            data['id'] = doc.id
            
            # Filter out expired messages
            expires_at = data.get('expires_at')
            if expires_at and expires_at < now:
                continue
            
            # Convert timestamp
            timestamp_obj = data.get('timestamp')
            if timestamp_obj:
                try:
                    data['timestamp'] = timestamp_obj.isoformat()
                except:
                    data['timestamp'] = datetime.utcnow().isoformat()
            else:
                data['timestamp'] = datetime.utcnow().isoformat()
            
            # Convert expires_at
            if expires_at:
                try:
                    data['expires_at'] = expires_at.isoformat()
                except:
                    pass
            
            messages.append(data)
        
        # Sort and limit
        messages.sort(key=lambda x: x.get('timestamp', ''), reverse=True)
        return list(reversed(messages[:limit]))
    
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
        """Remove expired chat sessions (run as cron job)"""
        # This will be handled by Cloud Function
        # For now, just return 0
        return 0
    
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
