"""
Chat Response Generator Service
Generates context-aware, category-specific responses for user actions.

This service ensures users get appropriate feedback based on what they logged:
- Tasks → Task confirmation
- Meals → Nutrition summary
- Workouts → Workout confirmation
- Water → Hydration tracking
- Supplements → Supplement confirmation

Design Principles:
- Modular: Easy to add new categories
- Scalable: Can handle multiple items of different types
- Production-ready: Comprehensive error handling
- UX-first: Friendly, encouraging, contextual responses
"""

from typing import List, Dict, Any, Optional
from datetime import datetime
from pydantic import BaseModel


class ChatResponse(BaseModel):
    """Structured chat response"""
    response: str  # Full message (existing)
    category: str
    items: List[Dict[str, Any]]
    metadata: Optional[Dict[str, Any]] = None
    
    # ✨ NEW FIELDS (Expandable Chat):
    summary: Optional[str] = None          # "🍌 1 banana logged! 105 kcal"
    suggestion: Optional[str] = None       # "Great potassium source!"
    details: Optional[Dict[str, Any]] = None  # Structured breakdown
    expandable: bool = False               # Flag for frontend
    
    # 🧠 PHASE 2 FIELDS (Explainable AI):
    confidence_score: Optional[float] = None          # 0.0 - 1.0
    confidence_level: Optional[str] = None            # "high", "medium", "low"
    confidence_factors: Optional[Dict[str, float]] = None  # Breakdown
    explanation: Optional[Dict[str, Any]] = None      # Why AI made this decision
    alternatives: Optional[List[Dict[str, Any]]] = None  # 2-3 alternative interpretations


class ChatResponseGenerator:
    """Generates context-aware responses based on user actions"""
    
    def generate_response(
        self,
        items: List[Dict[str, Any]],
        user_context: Optional[Dict[str, Any]] = None
    ) -> ChatResponse:
        """
        Generate appropriate response based on items and context
        
        Args:
            items: List of parsed items with category and data
            user_context: User profile, goals, streaks, etc.
        
        Returns:
            ChatResponse with appropriate message
        """
        if not items:
            return ChatResponse(
                response="Got it! I've logged that for you.",
                category="unknown",
                items=[]
            )
        
        # Group items by category
        categories = self._group_by_category(items)
        
        # Determine primary category (for response type)
        primary_category = self._get_primary_category(categories)
        
        # Generate response based on primary category
        if primary_category == "question":
            # 🎯 NEW: Handle conversational/question messages
            response_text = self._generate_question_response(categories["question"], user_context)
        elif primary_category == "task":
            response_text = self._generate_task_response(categories["task"], user_context)
        elif primary_category == "meal":
            response_text = self._generate_meal_response(categories, user_context)
        elif primary_category == "workout":
            response_text = self._generate_workout_response(categories["workout"], user_context)
        elif primary_category == "water":
            response_text = self._generate_water_response(categories["water"], user_context)
        elif primary_category == "supplement":
            response_text = self._generate_supplement_response(categories["supplement"], user_context)
        else:
            response_text = "Got it! I've logged that for you. 👍"
        
        # ✨ NEW: Post-process to create expandable format (< 1ms)
        # Only meals need expandable cards (nutrition details)
        # Water, supplements, tasks, events, workouts should be simple one-liners
        expandable_categories = ['meal', 'snack']
        
        if items and primary_category in expandable_categories:
            # Full expandable format for meals only
            summary = self._extract_summary(response_text, items)
            suggestion = self._generate_suggestion(items, user_context or {})
            details = self._structure_details(items, user_context or {})
            expandable = True
        else:
            # Simple one-liner for water, supplements, tasks, events, workouts
            summary = None
            suggestion = None
            details = None
            expandable = False
        
        return ChatResponse(
            response=response_text,
            category=primary_category,
            items=items,
            metadata={"categories": list(categories.keys())},
            # ✨ NEW FIELDS:
            summary=summary,
            suggestion=suggestion,
            details=details,
            expandable=expandable
        )
    
    def _group_by_category(self, items: List[Dict[str, Any]]) -> Dict[str, List[Dict[str, Any]]]:
        """Group items by category"""
        grouped = {}
        for item in items:
            category = item.get("category", "unknown")
            if category not in grouped:
                grouped[category] = []
            grouped[category].append(item)
        return grouped
    
    def _get_primary_category(self, categories: Dict[str, List[Dict[str, Any]]]) -> str:
        """
        Determine primary category for response
        Priority: question > task > workout > meal > water > supplement
        """
        priority = ["question", "task", "reminder", "workout", "meal", "snack", "water", "supplement"]
        for cat in priority:
            if cat in categories:
                return cat
        return list(categories.keys())[0] if categories else "unknown"
    
    # ==================== QUESTION/CONVERSATIONAL RESPONSES ====================
    
    def _generate_question_response(
        self,
        questions: List[Dict[str, Any]],
        user_context: Optional[Dict[str, Any]]
    ) -> str:
        """Generate conversational response to user questions/emotions"""
        if not questions:
            return "I'm here to help! How can I assist you today?"
        
        question = questions[0]
        data = question.get("data", {})
        summary = question.get("summary", "")
        
        # Detect type of conversational message
        question_type = data.get("type", "general")
        
        if question_type == "emotion":
            # User expressing emotion (e.g., "I am frustrated")
            if any(word in summary.lower() for word in ["frustrated", "stress", "overwhelm"]):
                return "I understand you're feeling frustrated. 😌 I'm here to help make tracking easier! Would you like to:\n\n• Log something specific? (e.g., 'apple', '2 eggs')\n• Ask a question about your progress?\n• Get help with how this works?\n\nJust let me know!"
            elif any(word in summary.lower() for word in ["happy", "great", "excited"]):
                return "That's wonderful to hear! 🎉 Keep up the positive energy! How can I help you today?"
            else:
                return "I hear you! 💙 I'm here to support your fitness journey. How can I assist?"
        
        elif question_type == "help":
            # User asking for help
            return "I'd be happy to help! 🤗\n\nYou can ask me to:\n• Log meals: 'apple', '2 eggs for breakfast'\n• Log workouts: 'ran 5k', '30min yoga'\n• Log water: '1 glass of water'\n• Track supplements: 'vitamin D'\n• Create reminders: 'call mom at 3pm'\n\nWhat would you like to do?"
        
        else:
            # General question/conversation
            return "I'm your AI fitness assistant! 💪 I can help you track meals, workouts, water, supplements, and set reminders.\n\nTo log something, just tell me what you had (e.g., 'apple', '2 eggs', 'ran 5k').\n\nWhat would you like to log today?"
    
    # ==================== TASK RESPONSES ====================
    
    def _generate_task_response(
        self,
        tasks: List[Dict[str, Any]],
        user_context: Optional[Dict[str, Any]]
    ) -> str:
        """Generate task confirmation response"""
        if not tasks:
            return "Task created successfully!"
        
        task = tasks[0]  # Focus on first task
        data = task.get("data", {})
        
        title = data.get("title", task.get("summary", "Task"))
        due_date = data.get("due_date")
        priority = data.get("priority", "medium")
        
        # Build response
        response_parts = []
        
        # Confirmation header
        response_parts.append("✅ Got it! I've added a reminder:\n")
        
        # Task details
        icon = self._get_task_icon(title)
        response_parts.append(f"{icon} {title}")
        
        # Due date info
        if due_date:
            time_str = self._format_time(due_date)
            response_parts.append(f"⏰ Due: {time_str}")
        
        # Priority indicator
        if priority == "high":
            response_parts.append("🔴 High Priority")
        
        # Encouraging message
        response_parts.append("\nI'll make sure you don't forget! 🔔")
        
        # Multiple tasks
        if len(tasks) > 1:
            response_parts.append(f"\n📋 +{len(tasks) - 1} more task(s) added")
        
        return "\n".join(response_parts)
    
    def _get_task_icon(self, title: str) -> str:
        """Get appropriate icon for task based on title"""
        title_lower = title.lower()
        if "call" in title_lower or "phone" in title_lower:
            return "📞"
        elif "email" in title_lower or "message" in title_lower:
            return "✉️"
        elif "meet" in title_lower or "meeting" in title_lower:
            return "🤝"
        elif "buy" in title_lower or "shop" in title_lower:
            return "🛒"
        elif "read" in title_lower or "book" in title_lower:
            return "📚"
        elif "workout" in title_lower or "exercise" in title_lower:
            return "💪"
        else:
            return "📋"
    
    def _format_time(self, due_date: Any) -> str:
        """Format due date for display"""
        if isinstance(due_date, str):
            try:
                dt = datetime.fromisoformat(due_date.replace("Z", "+00:00"))
                return dt.strftime("%I:%M %p")
            except:
                return due_date
        return "Later"
    
    # ==================== MEAL RESPONSES ====================
    
    def _generate_meal_response(
        self,
        categories: Dict[str, List[Dict[str, Any]]],
        user_context: Optional[Dict[str, Any]]
    ) -> str:
        """Generate nutrition summary response (existing logic)"""
        # Import existing formatter for meals
        from app.services.response_formatter import get_response_formatter
        
        # Flatten all items
        all_items = []
        for items in categories.values():
            all_items.extend(items)
        
        # Use existing formatter
        formatter = get_response_formatter()
        formatted = formatter.format_response(
            items=all_items,
            user_goal=user_context.get("fitness_goal") if user_context else None,
            daily_calorie_goal=user_context.get("daily_calorie_goal") if user_context else None
        )
        
        return formatted.summary_text
    
    # ==================== WORKOUT RESPONSES ====================
    
    def _generate_workout_response(
        self,
        workouts: List[Dict[str, Any]],
        user_context: Optional[Dict[str, Any]]
    ) -> str:
        """Generate workout confirmation response"""
        if not workouts:
            return "Workout logged! 💪"
        
        workout = workouts[0]
        data = workout.get("data", {})
        
        workout_type = data.get("item", "workout").title()
        duration = data.get("duration_minutes", 0)
        calories_burned = data.get("calories_burned", 0)
        intensity = data.get("intensity", "")
        
        # Build response
        response_parts = []
        
        # Congratulations header
        response_parts.append("💪 Great job!")
        
        # Workout details
        if duration:
            response_parts.append(f"\n🏋️ {workout_type} - {duration} min")
        else:
            response_parts.append(f"\n🏋️ {workout_type}")
        
        # Calories burned
        if calories_burned:
            response_parts.append(f"🔥 Burned ~{calories_burned} kcal")
        
        # Intensity
        if intensity:
            response_parts.append(f"⚡ {intensity.capitalize()} intensity")
        
        # Encouraging message
        response_parts.append("\nKeep up the great work! 🎯")
        
        # Multiple workouts
        if len(workouts) > 1:
            response_parts.append(f"\n+{len(workouts) - 1} more workout(s) logged")
        
        return "\n".join(response_parts)
    
    # ==================== WATER RESPONSES ====================
    
    def _generate_water_response(
        self,
        water_logs: List[Dict[str, Any]],
        user_context: Optional[Dict[str, Any]]
    ) -> str:
        """Generate hydration tracking response"""
        if not water_logs:
            return "Water logged! 💧"
        
        # Calculate total water
        total_ml = sum(
            log.get("data", {}).get("quantity_ml", 250)
            for log in water_logs
        )
        
        # Convert to glasses (250ml = 1 glass)
        glasses = total_ml / 250
        
        # Build response
        response_parts = []
        
        response_parts.append("💧 Hydration logged!")
        response_parts.append(f"\n🥤 {int(glasses)} glass{'es' if glasses != 1 else ''} ({total_ml}ml)")
        
        # Daily goal progress (if available)
        if user_context and user_context.get("daily_water_goal"):
            goal_ml = user_context["daily_water_goal"]
            progress = min(100, int((total_ml / goal_ml) * 100))
            response_parts.append(f"📊 {progress}% of daily goal")
        
        # Encouraging message
        if total_ml >= 2000:
            response_parts.append("\n✨ Excellent hydration! Keep it up!")
        else:
            response_parts.append("\n💪 Stay hydrated throughout the day!")
        
        return "\n".join(response_parts)
    
    # ==================== SUPPLEMENT RESPONSES ====================
    
    def _generate_supplement_response(
        self,
        supplements: List[Dict[str, Any]],
        user_context: Optional[Dict[str, Any]]
    ) -> str:
        """Generate supplement confirmation response"""
        if not supplements:
            return "Supplement logged! 💊"
        
        supplement = supplements[0]
        data = supplement.get("data", {})
        
        name = data.get("supplement_name", data.get("item", "Supplement"))
        dosage = data.get("dosage", "")
        
        # Build response
        response_parts = []
        
        response_parts.append("💊 Supplement logged!")
        response_parts.append(f"\n✅ {name}")
        
        if dosage:
            response_parts.append(f"📏 Dosage: {dosage}")
        
        # Encouraging message
        response_parts.append("\n🌟 Taking care of your health!")
        
        # Multiple supplements
        if len(supplements) > 1:
            response_parts.append(f"\n+{len(supplements) - 1} more supplement(s) logged")
        
        return "\n".join(response_parts)
    
    # ==================== EXPANDABLE CHAT HELPERS ====================
    
    def _extract_summary(self, full_message: str, items: List[Dict]) -> str:
        """
        Extract brief one-liner summary from full message (< 0.1ms)
        
        Strategy:
        1. Always build from items data (more accurate and specific)
        2. Use category-specific emoji and formatting
        3. Keep it scannable and concise
        """
        # Build from items (most accurate)
        if not items:
            return "Logged successfully!"
        
        primary_item = items[0]
        category = primary_item.get('category', 'item')
        data = primary_item.get('data', {})
        
        # Check if it's a meal/food item (has nutrition data)
        has_nutrition = 'calories' in data or 'item' in data
        
        if category == 'meal' or (has_nutrition and category == 'other'):
            item_name = primary_item.get('summary', primary_item.get('data', {}).get('item', 'meal'))
            calories = primary_item.get('data', {}).get('calories', 0)
            
            # Strip existing calorie info from item_name (e.g., "(450kcal)" or "(200 kcal)")
            import re
            item_name_clean = re.sub(r'\s*\(\d+\s*k?cal\)', '', item_name, flags=re.IGNORECASE).strip()
            
            # Get emoji based on food type
            emoji = self._get_food_emoji(item_name_clean)
            return f"{emoji} {item_name_clean.capitalize()} logged! {int(calories)} kcal"
        
        elif category == 'workout':
            activity = primary_item.get('data', {}).get('item', 'workout')
            calories = primary_item.get('data', {}).get('calories_burned', 0)
            return f"💪 {activity.capitalize()} logged! {int(calories)} kcal burned"
        
        elif category == 'water':
            quantity = primary_item.get('data', {}).get('quantity_ml', 0)
            glasses = int(quantity / 250)
            return f"💧 Water logged! {glasses} glass{'es' if glasses != 1 else ''} ({int(quantity)}ml)"
        
        elif category == 'supplement':
            name = primary_item.get('data', {}).get('supplement_name', 'supplement')
            return f"💊 {name.capitalize()} logged!"
        
        elif category in ('task', 'reminder'):
            title = primary_item.get('data', {}).get('title', 'task')
            return f"📝 Task created: {title}"
        
        return "✅ Logged successfully!"
    
    def _get_food_emoji(self, food_name: str) -> str:
        """Get appropriate emoji for food item"""
        food_lower = food_name.lower()
        
        # Fruits
        if any(fruit in food_lower for fruit in ['apple', 'apples']):
            return '🍎'
        elif any(fruit in food_lower for fruit in ['banana', 'bananas']):
            return '🍌'
        elif any(fruit in food_lower for fruit in ['orange', 'oranges']):
            return '🍊'
        elif any(fruit in food_lower for fruit in ['grape', 'grapes']):
            return '🍇'
        elif any(fruit in food_lower for fruit in ['strawberry', 'strawberries', 'berry', 'berries']):
            return '🍓'
        elif any(fruit in food_lower for fruit in ['watermelon']):
            return '🍉'
        
        # Proteins
        elif any(protein in food_lower for protein in ['chicken', 'turkey', 'meat', 'beef', 'pork']):
            return '🍗'
        elif any(protein in food_lower for protein in ['egg', 'eggs']):
            return '🥚'
        elif any(protein in food_lower for protein in ['fish', 'salmon', 'tuna']):
            return '🐟'
        
        # Vegetables
        elif any(veg in food_lower for veg in ['salad', 'lettuce', 'greens']):
            return '🥗'
        elif any(veg in food_lower for veg in ['carrot', 'carrots']):
            return '🥕'
        elif any(veg in food_lower for veg in ['broccoli']):
            return '🥦'
        
        # Carbs
        elif any(carb in food_lower for carb in ['bread', 'toast', 'sandwich']):
            return '🍞'
        elif any(carb in food_lower for carb in ['rice', 'fried rice']):
            return '🍚'
        elif any(carb in food_lower for carb in ['pasta', 'spaghetti']):
            return '🍝'
        elif any(carb in food_lower for carb in ['pizza']):
            return '🍕'
        
        # Snacks
        elif any(snack in food_lower for snack in ['cookie', 'cookies']):
            return '🍪'
        elif any(snack in food_lower for snack in ['cake']):
            return '🍰'
        elif any(snack in food_lower for snack in ['ice cream']):
            return '🍦'
        
        # Default
        return '🍽️'
    
    def _generate_suggestion(self, items: List[Dict], user_context: Dict[str, Any]) -> str:
        """
        Generate brief, actionable suggestion based on context (< 0.1ms)
        
        Uses smart logic (not LLM!) to provide helpful tips
        """
        if not items:
            return "Keep up the great work!"
        
        primary_category = items[0].get('category', 'other')
        
        # Get user context values
        daily_goal = user_context.get('daily_calorie_goal', 2000)
        calories_today = user_context.get('calories_consumed_today', 0)
        protein_today = user_context.get('protein_today', 0)
        meals_today = user_context.get('meals_logged_today', 0)
        
        # Calculate progress
        progress_pct = (calories_today / daily_goal * 100) if daily_goal > 0 else 0
        calories_remaining = daily_goal - calories_today
        
        if primary_category == 'meal':
            # Meal-specific suggestions
            if progress_pct >= 90:
                return "Almost at goal! Stay strong! 💪"
            elif progress_pct >= 80:
                return f"Great! Only {int(calories_remaining)} kcal remaining today!"
            elif protein_today < 50 and meals_today < 3:
                return "Add protein for satiety! 🍗"
            elif meals_today == 1:
                return "Good start! Stay balanced throughout the day."
            else:
                return "Great choice! Keep it balanced. ✨"
        
        elif primary_category == 'workout':
            if calories_today < daily_goal * 0.5:
                return "Nice work! Refuel with protein for recovery. 🍗"
            else:
                return "Excellent workout! Remember to hydrate. 💧"
        
        elif primary_category == 'water':
            return "Excellent hydration! Keep it up! 💧"
        
        elif primary_category == 'supplement':
            return "Great! Stay consistent for best results. 💊"
        
        elif primary_category in ('task', 'reminder'):
            return "Task saved! You've got this! 📝"
        
        return "Keep up the great work! ✨"
    
    def _structure_details(self, items: List[Dict], user_context: Dict[str, Any]) -> Dict[str, Any]:
        """
        Structure detailed breakdown for expandable view (< 0.5ms)
        
        Returns organized data for frontend to display
        """
        # Calculate totals from current items
        total_calories = sum(item.get('data', {}).get('calories', 0) for item in items)
        total_protein = sum(item.get('data', {}).get('protein_g', 0) for item in items)
        total_carbs = sum(item.get('data', {}).get('carbs_g', 0) for item in items)
        total_fat = sum(item.get('data', {}).get('fat_g', 0) for item in items)
        
        # Get user context (AFTER current items were logged - realtime data)
        daily_goal = user_context.get('daily_calorie_goal', 2000)
        calories_today = user_context.get('calories_consumed_today', 0)
        protein_today = user_context.get('protein_today', 0)
        
        # ✨ NOTE: calories_today ALREADY INCLUDES current items!
        # (because we fetch realtime data AFTER saving to DB)
        # So we DON'T add total_calories again (would be double counting!)
        
        details = {
            "nutrition": {
                "calories": round(total_calories, 1),
                "protein_g": round(total_protein, 1),
                "carbs_g": round(total_carbs, 1),
                "fat_g": round(total_fat, 1),
            },
            "progress": {
                "daily_calories": round(calories_today, 0),
                "daily_goal": daily_goal,
                "remaining": round(daily_goal - calories_today, 0),
                "protein_today": round(protein_today, 1),
                "progress_percent": round((calories_today / daily_goal * 100) if daily_goal > 0 else 0, 1)
            },
            "items": items,  # Include raw items for reference
        }
        
        # Add insights (optional, can be generated separately)
        insights = self._generate_insights(items, user_context)
        if insights:
            details["insights"] = insights
        
        return details
    
    def _generate_insights(self, items: List[Dict], user_context: Dict[str, Any]) -> str:
        """
        Generate brief insights/encouragement (< 0.1ms)
        """
        if not items:
            return ""
        
        primary_category = items[0].get('category', 'other')
        
        if primary_category == 'meal':
            protein = sum(item.get('data', {}).get('protein_g', 0) for item in items)
            
            if protein >= 20:
                return "Great protein content! Helps with muscle recovery and satiety."
            elif protein < 5:
                return "Consider adding protein for a more balanced meal."
            else:
                return "Good nutritional balance for sustained energy."
        
        elif primary_category == 'workout':
            return "Regular exercise improves both physical and mental health. Keep it up!"
        
        return ""


# Singleton instance
_generator = None


def get_chat_response_generator() -> ChatResponseGenerator:
    """Get singleton instance of ChatResponseGenerator"""
    global _generator
    if _generator is None:
        _generator = ChatResponseGenerator()
    return _generator

