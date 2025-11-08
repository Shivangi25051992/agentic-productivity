"""
Fasting Service - Business Logic Layer
Implements use cases and orchestrates domain operations
Follows Clean Architecture principles
"""

from datetime import datetime, timedelta
from typing import List, Optional, Dict, Any
from google.cloud import firestore
import os
from dotenv import load_dotenv

from app.models.fasting import (
    FastingSession,
    FastingProfile,
    FastingProtocol,
    BreakReason,
    StartFastingRequest,
    EndFastingRequest,
    FastingAnalytics,
    FastingSessionResponse,
    FastingStage,
)

load_dotenv()
load_dotenv('.env.local', override=True)


class FastingService:
    """
    Service for managing fasting sessions and profiles
    
    Responsibilities:
    - Orchestrate fasting session lifecycle
    - Calculate analytics and insights
    - Manage user fasting preferences
    - Provide AI coaching recommendations
    """
    
    def __init__(self):
        self.db = firestore.Client(project=os.getenv("GOOGLE_CLOUD_PROJECT"))
        self.collection = "fasting_sessions"
        self.profiles_collection = "fasting_profiles"
    
    # ========================================================================
    # FASTING SESSION OPERATIONS
    # ========================================================================
    
    async def start_fasting_session(
        self, 
        user_id: str, 
        request: StartFastingRequest
    ) -> FastingSession:
        """
        Start a new fasting session
        
        Business Rules:
        - Only one active session per user
        - Validate protocol and duration
        - Auto-end previous session if exists
        """
        # Check for active session
        active_session = await self.get_active_session(user_id)
        if active_session:
            # Auto-complete previous session
            await self.end_fasting_session(
                user_id=user_id,
                session_id=active_session.id,
                request=EndFastingRequest(
                    break_reason=BreakReason.PLANNED,
                    energy_level=3,
                    hunger_level=3,
                    notes="Auto-ended when starting new session"
                )
            )
        
        # Create new session
        session = FastingSession(
            user_id=user_id,
            start_time=datetime.utcnow(),
            target_duration_hours=request.target_duration_hours,
            protocol=request.protocol,
            notes=request.notes,
            is_active=True,
        )
        
        # Save to Firestore
        doc_ref = self.db.collection('users').document(user_id)\
                         .collection(self.collection).document(session.id)
        doc_ref.set(session.to_dict())
        
        print(f"✅ Started fasting session: {session.id} for user {user_id}")
        return session
    
    async def end_fasting_session(
        self,
        user_id: str,
        session_id: str,
        request: EndFastingRequest
    ) -> FastingSession:
        """
        End an active fasting session
        
        Business Rules:
        - Session must be active
        - Record completion metrics
        - Update analytics
        """
        # Get session
        session = await self.get_session_by_id(user_id, session_id)
        if not session:
            raise ValueError(f"Session {session_id} not found")
        
        if not session.is_active:
            raise ValueError(f"Session {session_id} is already ended")
        
        # Complete session
        session.complete(
            reason=request.break_reason,
            energy=request.energy_level,
            hunger=request.hunger_level,
            notes=request.notes
        )
        
        # Update in Firestore
        doc_ref = self.db.collection('users').document(user_id)\
                         .collection(self.collection).document(session_id)
        doc_ref.update(session.to_dict())
        
        print(f"✅ Ended fasting session: {session_id} - Reason: {request.break_reason.value}")
        return session
    
    async def get_active_session(self, user_id: str) -> Optional[FastingSession]:
        """Get user's currently active fasting session"""
        docs = self.db.collection('users').document(user_id)\
                      .collection(self.collection)\
                      .where('is_active', '==', True)\
                      .limit(1)\
                      .stream()
        
        for doc in docs:
            return FastingSession.from_dict(doc.to_dict())
        
        return None
    
    async def get_session_by_id(self, user_id: str, session_id: str) -> Optional[FastingSession]:
        """Get a specific fasting session"""
        doc = self.db.collection('users').document(user_id)\
                     .collection(self.collection).document(session_id).get()
        
        if doc.exists:
            return FastingSession.from_dict(doc.to_dict())
        return None
    
    async def get_session_with_details(self, user_id: str, session_id: str) -> Optional[FastingSessionResponse]:
        """
        Get session with calculated details
        
        Includes:
        - Current stage
        - Progress percentage
        - Time remaining
        - Next stage prediction
        """
        session = await self.get_session_by_id(user_id, session_id)
        if not session:
            return None
        
        current_stage = session.current_stage
        progress = session.progress_percentage
        
        # Calculate time remaining
        time_remaining = None
        if session.is_active:
            time_remaining = max(0, session.target_duration_hours - session.current_duration_hours)
        
        # Calculate next stage
        next_stage = None
        next_stage_in_hours = None
        
        stage_thresholds = {
            FastingStage.ANABOLIC: (4, FastingStage.CATABOLIC),
            FastingStage.CATABOLIC: (16, FastingStage.AUTOPHAGY_LIGHT),
            FastingStage.AUTOPHAGY_LIGHT: (24, FastingStage.AUTOPHAGY_DEEP),
            FastingStage.AUTOPHAGY_DEEP: (48, FastingStage.GROWTH_HORMONE),
        }
        
        if current_stage in stage_thresholds:
            threshold, next_stage_enum = stage_thresholds[current_stage]
            next_stage = next_stage_enum
            next_stage_in_hours = max(0, threshold - session.current_duration_hours)
        
        return FastingSessionResponse(
            session=session,
            current_stage=current_stage,
            progress_percentage=progress,
            time_remaining_hours=time_remaining,
            next_stage=next_stage,
            next_stage_in_hours=next_stage_in_hours,
        )
    
    async def get_fasting_history(
        self,
        user_id: str,
        limit: int = 30,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None
    ) -> List[FastingSession]:
        """
        Get user's fasting history
        
        Returns sessions in reverse chronological order (newest first)
        """
        query = self.db.collection('users').document(user_id)\
                       .collection(self.collection)\
                       .order_by('start_time', direction=firestore.Query.DESCENDING)
        
        if start_date:
            query = query.where('start_time', '>=', start_date)
        if end_date:
            query = query.where('start_time', '<=', end_date)
        
        query = query.limit(limit)
        
        sessions = []
        for doc in query.stream():
            sessions.append(FastingSession.from_dict(doc.to_dict()))
        
        return sessions
    
    # ========================================================================
    # ANALYTICS & INSIGHTS
    # ========================================================================
    
    async def get_fasting_analytics(
        self,
        user_id: str,
        period_days: int = 30
    ) -> FastingAnalytics:
        """
        Calculate comprehensive fasting analytics
        
        Metrics:
        - Completion rate
        - Average duration
        - Longest fast
        - Current streak
        - Break reason distribution
        - Energy/hunger patterns
        """
        cutoff_date = datetime.utcnow() - timedelta(days=period_days)
        sessions = await self.get_fasting_history(
            user_id=user_id,
            limit=1000,
            start_date=cutoff_date
        )
        
        if not sessions:
            return FastingAnalytics(
                user_id=user_id,
                period_days=period_days,
                total_fasts=0,
                completed_fasts=0,
                completion_rate=0.0,
                average_duration_hours=0.0,
                longest_fast_hours=0.0,
                current_streak_days=0,
                total_fasting_hours=0.0,
                break_reasons={},
            )
        
        # Calculate metrics
        total_fasts = len(sessions)
        completed_fasts = sum(1 for s in sessions if s.is_completed)
        completion_rate = (completed_fasts / total_fasts) * 100 if total_fasts > 0 else 0.0
        
        durations = [s.actual_duration_hours for s in sessions if s.actual_duration_hours]
        average_duration = sum(durations) / len(durations) if durations else 0.0
        longest_fast = max(durations) if durations else 0.0
        total_fasting_hours = sum(durations)
        
        # Calculate current streak
        current_streak = self._calculate_streak(sessions)
        
        # Break reason distribution
        break_reasons = {}
        for session in sessions:
            if session.break_reason:
                reason = session.break_reason.value
                break_reasons[reason] = break_reasons.get(reason, 0) + 1
        
        # Average energy and hunger levels
        energy_levels = [s.energy_level for s in sessions if s.energy_level]
        hunger_levels = [s.hunger_level for s in sessions if s.hunger_level]
        
        avg_energy = sum(energy_levels) / len(energy_levels) if energy_levels else None
        avg_hunger = sum(hunger_levels) / len(hunger_levels) if hunger_levels else None
        
        # Best time of day (when most fasts are completed)
        best_time = self._calculate_best_time_of_day(sessions)
        
        return FastingAnalytics(
            user_id=user_id,
            period_days=period_days,
            total_fasts=total_fasts,
            completed_fasts=completed_fasts,
            completion_rate=round(completion_rate, 1),
            average_duration_hours=round(average_duration, 1),
            longest_fast_hours=round(longest_fast, 1),
            current_streak_days=current_streak,
            total_fasting_hours=round(total_fasting_hours, 1),
            break_reasons=break_reasons,
            average_energy_level=round(avg_energy, 1) if avg_energy else None,
            average_hunger_level=round(avg_hunger, 1) if avg_hunger else None,
            best_time_of_day=best_time,
        )
    
    def _calculate_streak(self, sessions: List[FastingSession]) -> int:
        """Calculate current consecutive days with completed fasts"""
        if not sessions:
            return 0
        
        # Sort by date (newest first)
        sorted_sessions = sorted(sessions, key=lambda s: s.start_time, reverse=True)
        
        streak = 0
        current_date = datetime.utcnow().date()
        
        for session in sorted_sessions:
            session_date = session.start_time.date()
            
            # Check if session is from current_date or previous consecutive day
            if session_date == current_date and session.is_completed:
                streak += 1
                current_date -= timedelta(days=1)
            elif session_date < current_date:
                break
        
        return streak
    
    def _calculate_best_time_of_day(self, sessions: List[FastingSession]) -> Optional[str]:
        """Determine the time of day when user completes most fasts"""
        if not sessions:
            return None
        
        completed_sessions = [s for s in sessions if s.is_completed and s.end_time]
        if not completed_sessions:
            return None
        
        # Group by hour of day
        hour_counts = {}
        for session in completed_sessions:
            hour = session.end_time.hour
            hour_counts[hour] = hour_counts.get(hour, 0) + 1
        
        # Find most common hour
        best_hour = max(hour_counts, key=hour_counts.get)
        
        # Convert to readable format
        if 5 <= best_hour < 12:
            return "morning"
        elif 12 <= best_hour < 17:
            return "afternoon"
        elif 17 <= best_hour < 21:
            return "evening"
        else:
            return "night"
    
    # ========================================================================
    # PROFILE MANAGEMENT
    # ========================================================================
    
    async def get_fasting_profile(self, user_id: str) -> Optional[FastingProfile]:
        """Get user's fasting profile"""
        doc = self.db.collection('users').document(user_id)\
                     .collection(self.profiles_collection).document('profile').get()
        
        if doc.exists:
            return FastingProfile.from_dict(doc.to_dict())
        return None
    
    async def create_or_update_profile(
        self,
        user_id: str,
        profile: FastingProfile
    ) -> FastingProfile:
        """Create or update fasting profile"""
        profile.user_id = user_id
        profile.updated_at = datetime.utcnow()
        
        doc_ref = self.db.collection('users').document(user_id)\
                         .collection(self.profiles_collection).document('profile')
        doc_ref.set(profile.to_dict())
        
        print(f"✅ Updated fasting profile for user {user_id}")
        return profile
    
    # ========================================================================
    # AI COACHING HELPERS
    # ========================================================================
    
    async def get_coaching_context(self, user_id: str) -> Dict[str, Any]:
        """
        Get context for AI coaching
        
        Returns comprehensive data for AI to provide personalized coaching
        """
        active_session = await self.get_active_session(user_id)
        profile = await self.get_fasting_profile(user_id)
        analytics = await self.get_fasting_analytics(user_id, period_days=30)
        recent_history = await self.get_fasting_history(user_id, limit=10)
        
        return {
            "active_session": active_session.dict() if active_session else None,
            "profile": profile.dict() if profile else None,
            "analytics": analytics.dict(),
            "recent_history": [s.dict() for s in recent_history],
            "current_time": datetime.utcnow().isoformat(),
        }
    
    async def recommend_fasting_window(
        self,
        user_id: str,
        user_schedule: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        AI-powered fasting window recommendation
        
        Analyzes user's schedule and recommends optimal fasting protocol
        """
        # This will be enhanced with AI in later phase
        # For now, return basic recommendation based on schedule
        
        profile = await self.get_fasting_profile(user_id)
        
        # Default recommendation for beginners
        if not profile or profile.experience_level.value == "beginner":
            return {
                "protocol": FastingProtocol.SIXTEEN_EIGHT.value,
                "eating_window_start": "12:00",
                "eating_window_end": "20:00",
                "reasoning": [
                    "16:8 is beginner-friendly and sustainable",
                    "Eating window allows for lunch and dinner",
                    "Fasting during sleep and morning is easier"
                ],
                "tips": [
                    "Drink plenty of water during fasting",
                    "Black coffee/tea is allowed",
                    "Break fast with protein and healthy fats"
                ]
            }
        
        # For experienced users, suggest based on their history
        analytics = await self.get_fasting_analytics(user_id)
        
        if analytics.completion_rate > 80:
            # User is doing well, can try longer fasts
            return {
                "protocol": FastingProtocol.EIGHTEEN_SIX.value,
                "eating_window_start": "14:00",
                "eating_window_end": "20:00",
                "reasoning": [
                    f"Your completion rate is {analytics.completion_rate}% - excellent!",
                    "You're ready for 18:6 protocol",
                    "This will enhance autophagy benefits"
                ],
                "tips": [
                    "Your best time is {analytics.best_time_of_day}",
                    "Consider breaking fast with high-fat meal",
                    "Monitor energy levels carefully"
                ]
            }
        
        # Struggling user, suggest easier protocol
        return {
            "protocol": FastingProtocol.SIXTEEN_EIGHT.value,
            "eating_window_start": "11:00",
            "eating_window_end": "19:00",
            "reasoning": [
                f"Your completion rate is {analytics.completion_rate}%",
                "Let's focus on consistency with 16:8",
                "Earlier eating window may help"
            ],
            "tips": [
                "Focus on high-protein, high-fat meals",
                "Avoid high-carb meals that spike insulin",
                "Stay hydrated throughout the day"
            ]
        }


# Singleton instance
_fasting_service = None

def get_fasting_service() -> FastingService:
    """Get singleton instance of FastingService"""
    global _fasting_service
    if _fasting_service is None:
        _fasting_service = FastingService()
    return _fasting_service

