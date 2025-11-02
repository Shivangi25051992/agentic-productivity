"""
Context Service - Provides user context for intelligent chat responses
Makes the AI aware of user's history, patterns, and progress
"""

from typing import Dict, Any, List, Optional
from datetime import datetime, timedelta, timezone
from pydantic import BaseModel


class UserContext(BaseModel):
    """User context for intelligent responses"""
    user_id: str
    
    # Today's stats
    calories_consumed_today: int = 0
    calories_burned_today: int = 0
    protein_today: float = 0.0
    meals_logged_today: int = 0
    workouts_today: int = 0
    
    # Weekly stats
    calories_consumed_week: int = 0
    workouts_this_week: int = 0
    logging_streak_days: int = 0
    
    # Patterns
    most_logged_foods: List[str] = []
    favorite_workout: Optional[str] = None
    typical_meal_times: Dict[str, str] = {}
    
    # Goals
    daily_calorie_goal: int = 1592
    fitness_goal: str = "lose_weight"
    
    # Recent activity
    last_meal_time: Optional[datetime] = None
    last_workout_time: Optional[datetime] = None
    hours_since_last_meal: Optional[float] = None


class ContextService:
    """Builds user context from historical data"""
    
    def __init__(self, db_service):
        self.db = db_service
    
    def get_user_context(self, user_id: str) -> UserContext:
        """
        Build comprehensive user context from database
        
        Args:
            user_id: User ID
        
        Returns:
            UserContext with all relevant user data
        """
        context = UserContext(user_id=user_id)
        
        # Get today's logs
        today_start = datetime.now(timezone.utc).replace(hour=0, minute=0, second=0, microsecond=0)
        today_logs = self.db.list_fitness_logs_by_user(
            user_id=user_id,
            start_ts=today_start,
            log_type=None,
            limit=100
        )
        
        # Calculate today's stats
        for log in today_logs:
            if log.log_type.value == "meal":
                context.calories_consumed_today += log.calories or 0
                context.meals_logged_today += 1
                
                if log.ai_parsed_data:
                    context.protein_today += log.ai_parsed_data.get("protein_g", 0)
                
                # Track last meal time
                if log.timestamp:
                    if context.last_meal_time is None or log.timestamp > context.last_meal_time:
                        context.last_meal_time = log.timestamp
            
            elif log.log_type.value == "workout":
                context.calories_burned_today += log.calories or 0
                context.workouts_today += 1
                
                # Track last workout time
                if log.timestamp:
                    if context.last_workout_time is None or log.timestamp > context.last_workout_time:
                        context.last_workout_time = log.timestamp
        
        # Calculate hours since last meal
        if context.last_meal_time:
            now = datetime.now(timezone.utc)
            delta = now - context.last_meal_time
            context.hours_since_last_meal = delta.total_seconds() / 3600
        
        # Get weekly stats
        week_start = today_start - timedelta(days=7)
        week_logs = self.db.list_fitness_logs_by_user(
            user_id=user_id,
            start_ts=week_start,
            log_type=None,
            limit=500
        )
        
        for log in week_logs:
            if log.log_type.value == "meal":
                context.calories_consumed_week += log.calories or 0
            elif log.log_type.value == "workout":
                context.workouts_this_week += 1
        
        # Calculate logging streak
        context.logging_streak_days = self._calculate_streak(user_id)
        
        # Find patterns
        context.most_logged_foods = self._find_most_logged_foods(week_logs)
        context.favorite_workout = self._find_favorite_workout(week_logs)
        
        return context
    
    def _calculate_streak(self, user_id: str) -> int:
        """Calculate consecutive days with at least one log"""
        streak = 0
        current_date = datetime.now(timezone.utc).date()
        
        for i in range(30):  # Check last 30 days
            check_date = current_date - timedelta(days=i)
            day_start = datetime.combine(check_date, datetime.min.time()).replace(tzinfo=timezone.utc)
            day_end = day_start + timedelta(days=1)
            
            logs = self.db.list_fitness_logs_by_user(
                user_id=user_id,
                start_ts=day_start,
                log_type=None,
                limit=1
            )
            
            if logs:
                streak += 1
            else:
                break  # Streak broken
        
        return streak
    
    def _find_most_logged_foods(self, logs: List) -> List[str]:
        """Find most frequently logged foods"""
        food_counts = {}
        
        for log in logs:
            if log.log_type.value == "meal" and log.ai_parsed_data:
                food = log.ai_parsed_data.get("item") or log.ai_parsed_data.get("meal")
                if food:
                    food_counts[food] = food_counts.get(food, 0) + 1
        
        # Sort by count and return top 3
        sorted_foods = sorted(food_counts.items(), key=lambda x: x[1], reverse=True)
        return [food for food, count in sorted_foods[:3]]
    
    def _find_favorite_workout(self, logs: List) -> Optional[str]:
        """Find most frequent workout type"""
        workout_counts = {}
        
        for log in logs:
            if log.log_type.value == "workout" and log.ai_parsed_data:
                workout = log.ai_parsed_data.get("activity_type") or log.ai_parsed_data.get("item")
                if workout:
                    workout_counts[workout] = workout_counts.get(workout, 0) + 1
        
        if not workout_counts:
            return None
        
        # Return most common
        return max(workout_counts, key=workout_counts.get)
    
    def generate_context_aware_message(self, context: UserContext, items: List[Dict]) -> str:
        """
        Generate intelligent, context-aware feedback messages
        
        Args:
            context: User context
            items: Items just logged
        
        Returns:
            Personalized message with kudos, recommendations, insights
        """
        messages = []
        
        # Streak kudos
        if context.logging_streak_days >= 7:
            messages.append(f"🔥 Amazing! {context.logging_streak_days}-day logging streak! Keep it up!")
        elif context.logging_streak_days >= 3:
            messages.append(f"💪 {context.logging_streak_days} days in a row! Consistency is key!")
        
        # Meal timing feedback
        if context.hours_since_last_meal and context.hours_since_last_meal > 5:
            messages.append(f"⏰ It's been {context.hours_since_last_meal:.1f} hours since your last meal. Good timing to refuel!")
        
        # Workout kudos
        if context.workouts_today > 0 and any(item.get('category') == 'workout' for item in items):
            if context.workouts_today == 1:
                messages.append("🏃 First workout of the day! Great start!")
            else:
                messages.append(f"💪 Workout #{context.workouts_today} today! You're crushing it!")
        
        # Weekly workout milestone
        if context.workouts_this_week >= 5:
            messages.append(f"🎯 {context.workouts_this_week} workouts this week! You're a fitness champion!")
        
        # Protein tracking
        if context.protein_today >= 100:
            messages.append(f"💪 {context.protein_today:.0f}g protein today! Excellent for muscle recovery!")
        elif context.protein_today < 30 and context.meals_logged_today >= 2:
            messages.append(f"🥩 Protein is a bit low ({context.protein_today:.0f}g). Consider adding eggs, chicken, or legumes!")
        
        # Calorie progress
        net_calories = context.calories_consumed_today - context.calories_burned_today
        remaining = context.daily_calorie_goal - net_calories
        
        if remaining > 0:
            messages.append(f"📊 {remaining} kcal remaining for today. You're on track!")
        elif remaining < -200:
            messages.append(f"⚠️ You're {abs(remaining)} kcal over your goal. Consider lighter meals for the rest of the day.")
        
        # Pattern recognition
        if context.most_logged_foods:
            favorite = context.most_logged_foods[0]
            messages.append(f"📝 I notice you love {favorite}! Great choice!")
        
        return " ".join(messages) if messages else None


# Singleton instance
_context_service = None


def get_context_service(db_service):
    """Get singleton instance of ContextService"""
    global _context_service
    if _context_service is None:
        _context_service = ContextService(db_service)
    return _context_service


