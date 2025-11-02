"""
AI-Powered Insights Service
Generates intelligent, actionable insights for users based on their data
"""

from typing import List, Dict, Optional
from datetime import datetime, timedelta
from enum import Enum

class InsightType(Enum):
    """Types of insights"""
    PROGRESS = "progress"  # Progress towards goals
    WARNING = "warning"  # Over budget or off track
    SUGGESTION = "suggestion"  # Actionable suggestions
    CELEBRATION = "celebration"  # Achievements and streaks
    PATTERN = "pattern"  # Behavioral patterns
    PREDICTION = "prediction"  # Goal achievement predictions

class InsightPriority(Enum):
    """Priority levels for insights"""
    HIGH = "high"  # Critical, show immediately
    MEDIUM = "medium"  # Important, show prominently
    LOW = "low"  # Nice to know, show if space

class Insight:
    """Represents a single insight"""
    def __init__(
        self,
        type: InsightType,
        priority: InsightPriority,
        title: str,
        message: str,
        icon: str,
        color: str,
        action: Optional[str] = None,
        action_label: Optional[str] = None
    ):
        self.type = type
        self.priority = priority
        self.title = title
        self.message = message
        self.icon = icon
        self.color = color
        self.action = action
        self.action_label = action_label
    
    def to_dict(self) -> Dict:
        return {
            "type": self.type.value,
            "priority": self.priority.value,
            "title": self.title,
            "message": self.message,
            "icon": self.icon,
            "color": self.color,
            "action": self.action,
            "action_label": self.action_label
        }

class AIInsightsService:
    """Generate AI-powered insights"""
    
    def generate_insights(
        self,
        calories_consumed: int,
        calories_goal: int,
        calories_burned: int,
        protein_g: float,
        protein_goal: float,
        carbs_g: float,
        carbs_goal: float,
        fat_g: float,
        fat_goal: float,
        streak_days: int = 0,
        user_goal: str = "lose_weight",  # lose_weight, gain_weight, maintain
        historical_data: Optional[List[Dict]] = None
    ) -> List[Insight]:
        """
        Generate personalized insights based on user data
        
        Args:
            calories_consumed: Calories eaten today
            calories_goal: Daily calorie goal
            calories_burned: Calories burned from exercise
            protein_g: Protein consumed (grams)
            protein_goal: Protein goal (grams)
            carbs_g: Carbs consumed (grams)
            carbs_goal: Carbs goal (grams)
            fat_g: Fat consumed (grams)
            fat_goal: Fat goal (grams)
            streak_days: Consecutive days of logging
            user_goal: User's fitness goal
            historical_data: Past days' data for pattern analysis
        
        Returns:
            List of insights ordered by priority
        """
        insights = []
        
        # Calculate key metrics
        net_calories = calories_consumed - calories_burned
        calorie_deficit = net_calories - calories_goal
        is_in_deficit = net_calories < calories_goal
        
        protein_percent = (protein_g / protein_goal * 100) if protein_goal > 0 else 0
        carbs_percent = (carbs_g / carbs_goal * 100) if carbs_goal > 0 else 0
        fat_percent = (fat_g / fat_goal * 100) if fat_goal > 0 else 0
        
        # 1. CELEBRATION INSIGHTS (High Priority)
        if streak_days >= 7:
            insights.append(Insight(
                type=InsightType.CELEBRATION,
                priority=InsightPriority.HIGH,
                title="🎉 Amazing Streak!",
                message=f"You've logged meals for {streak_days} days straight! Consistency is key to success.",
                icon="🔥",
                color="orange"
            ))
        elif streak_days >= 3:
            insights.append(Insight(
                type=InsightType.CELEBRATION,
                priority=InsightPriority.MEDIUM,
                title="💪 Great Consistency!",
                message=f"{streak_days} days in a row! Keep building that habit.",
                icon="📈",
                color="green"
            ))
        
        # 2. PROGRESS INSIGHTS (High Priority)
        if user_goal == "lose_weight":
            if is_in_deficit and abs(calorie_deficit) >= 300:
                insights.append(Insight(
                    type=InsightType.PROGRESS,
                    priority=InsightPriority.HIGH,
                    title="🎯 Perfect Deficit!",
                    message=f"You're {abs(calorie_deficit)} kcal in deficit - ideal for healthy weight loss!",
                    icon="✅",
                    color="green"
                ))
            elif is_in_deficit and abs(calorie_deficit) < 300:
                insights.append(Insight(
                    type=InsightType.PROGRESS,
                    priority=InsightPriority.MEDIUM,
                    title="👍 On Track",
                    message=f"You're {abs(calorie_deficit)} kcal in deficit. Consider a slightly larger deficit for faster results.",
                    icon="📊",
                    color="blue"
                ))
        elif user_goal == "gain_weight":
            if not is_in_deficit and calorie_deficit >= 300:
                insights.append(Insight(
                    type=InsightType.PROGRESS,
                    priority=InsightPriority.HIGH,
                    title="💪 Great Surplus!",
                    message=f"You're {calorie_deficit} kcal in surplus - perfect for muscle gain!",
                    icon="✅",
                    color="green"
                ))
        
        # 3. WARNING INSIGHTS (High Priority)
        if user_goal == "lose_weight" and not is_in_deficit:
            insights.append(Insight(
                type=InsightType.WARNING,
                priority=InsightPriority.HIGH,
                title="⚠️ Over Budget",
                message=f"You're {calorie_deficit} kcal over your goal. Consider a lighter dinner or add some exercise.",
                icon="🚨",
                color="red",
                action="log_workout",
                action_label="Log Workout"
            ))
        
        # 4. MACRO INSIGHTS (Medium Priority)
        if protein_percent < 70:
            protein_needed = protein_goal - protein_g
            insights.append(Insight(
                type=InsightType.SUGGESTION,
                priority=InsightPriority.MEDIUM,
                title="💪 Boost Your Protein",
                message=f"You need {protein_needed:.0f}g more protein. Try adding chicken breast, eggs, or Greek yogurt.",
                icon="🥚",
                color="red",
                action="suggest_protein_foods",
                action_label="See Protein Foods"
            ))
        elif protein_percent >= 90:
            insights.append(Insight(
                type=InsightType.PROGRESS,
                priority=InsightPriority.LOW,
                title="💪 Protein Goal Met!",
                message=f"Excellent! You've hit {protein_percent:.0f}% of your protein goal.",
                icon="✅",
                color="green"
            ))
        
        if carbs_percent > 120:
            insights.append(Insight(
                type=InsightType.WARNING,
                priority=InsightPriority.MEDIUM,
                title="🌾 High Carbs",
                message=f"You're at {carbs_percent:.0f}% of your carb goal. Balance with more protein and veggies.",
                icon="⚠️",
                color="orange"
            ))
        
        # 5. PATTERN INSIGHTS (Low Priority)
        if historical_data and len(historical_data) >= 3:
            # Analyze patterns (simplified for now)
            avg_dinner_percent = self._analyze_meal_timing(historical_data)
            if avg_dinner_percent > 50:
                insights.append(Insight(
                    type=InsightType.PATTERN,
                    priority=InsightPriority.LOW,
                    title="📊 Meal Pattern Detected",
                    message=f"You typically eat {avg_dinner_percent:.0f}% of calories at dinner. Try balancing across the day for better energy.",
                    icon="💡",
                    color="blue"
                ))
        
        # 6. PREDICTION INSIGHTS (Medium Priority)
        if is_in_deficit and abs(calorie_deficit) >= 500:
            # Rough calculation: 3500 kcal = 1 lb
            weekly_deficit = abs(calorie_deficit) * 7
            weekly_loss_lbs = weekly_deficit / 3500
            weeks_to_goal = 10 / weekly_loss_lbs if weekly_loss_lbs > 0 else 0  # Assuming 10 lbs goal
            
            if weeks_to_goal > 0 and weeks_to_goal < 20:
                insights.append(Insight(
                    type=InsightType.PREDICTION,
                    priority=InsightPriority.MEDIUM,
                    title="🎯 Goal Prediction",
                    message=f"At this rate, you'll reach your goal in ~{weeks_to_goal:.0f} weeks! Keep it up!",
                    icon="📈",
                    color="purple"
                ))
        
        # 7. MOTIVATIONAL INSIGHTS (Low Priority)
        if calories_consumed == 0:
            insights.append(Insight(
                type=InsightType.SUGGESTION,
                priority=InsightPriority.HIGH,
                title="🍽️ Start Logging",
                message="Track your first meal today! Consistency is the key to reaching your goals.",
                icon="📝",
                color="blue",
                action="log_meal",
                action_label="Log Meal"
            ))
        
        # Sort by priority (HIGH > MEDIUM > LOW)
        priority_order = {
            InsightPriority.HIGH: 0,
            InsightPriority.MEDIUM: 1,
            InsightPriority.LOW: 2
        }
        insights.sort(key=lambda x: priority_order[x.priority])
        
        # Limit to top 5 insights
        return insights[:5]
    
    def _analyze_meal_timing(self, historical_data: List[Dict]) -> float:
        """Analyze meal timing patterns"""
        # Simplified: Return average dinner percentage
        # In production, this would analyze actual meal times
        return 55.0  # Placeholder
    
    def generate_daily_summary(
        self,
        calories_consumed: int,
        calories_goal: int,
        protein_g: float,
        protein_goal: float,
        user_goal: str = "lose_weight"
    ) -> str:
        """Generate a one-line daily summary"""
        net_calories = calories_consumed
        deficit = calories_goal - net_calories
        
        if user_goal == "lose_weight":
            if deficit >= 500:
                return f"🎯 Crushing it! {deficit} kcal deficit - you're on fire!"
            elif deficit >= 300:
                return f"💪 Great job! {deficit} kcal deficit - keep going!"
            elif deficit > 0:
                return f"👍 On track with {deficit} kcal deficit."
            else:
                return f"⚠️ {abs(deficit)} kcal over - adjust your next meal."
        elif user_goal == "gain_weight":
            surplus = net_calories - calories_goal
            if surplus >= 300:
                return f"💪 Perfect! {surplus} kcal surplus for muscle gain!"
            else:
                return f"📊 Eat more to hit your surplus goal."
        else:
            return f"📊 {calories_consumed}/{calories_goal} kcal consumed today."

# Singleton instance
_service = None

def get_insights_service() -> AIInsightsService:
    """Get singleton insights service"""
    global _service
    if _service is None:
        _service = AIInsightsService()
    return _service


