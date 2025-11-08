"""
Response Explanation Service

Generates human-readable explanations of AI reasoning
Part of Phase 2: Explainable AI & Context Management
"""

from typing import Dict, Any, List, Optional
from datetime import datetime, timezone
from app.models.explainable_response import ResponseExplanation


class ResponseExplainer:
    """
    Service for generating explanations of AI decisions
    
    Explains:
    - WHY AI classified input a certain way
    - WHAT data sources were used
    - WHAT assumptions were made
    - HOW confidence was determined
    """
    
    def __init__(self):
        self.data_sources = {
            'usda': 'USDA FoodData Central',
            'user_history': 'Your previous logs',
            'typical_portions': 'Standard serving sizes',
            'llm_knowledge': 'AI nutritional knowledge base',
            'user_preferences': 'Your saved preferences'
        }
    
    def explain_classification(
        self,
        user_input: str,
        parsed_items: List[Dict[str, Any]],
        classification: str,
        confidence_score: float,
        user_context: Optional[Dict[str, Any]] = None
    ) -> ResponseExplanation:
        """
        Generate comprehensive explanation for classification decision
        
        Args:
            user_input: Original user input
            parsed_items: What AI parsed from input
            classification: Category assigned (meal, workout, etc.)
            confidence_score: Confidence in this classification
            user_context: User's historical data and preferences
        
        Returns:
            ResponseExplanation with full reasoning breakdown
        """
        
        # Build reasoning steps
        reasoning_steps = self._build_reasoning_steps(
            user_input, 
            parsed_items, 
            classification,
            user_context
        )
        
        # Identify data sources used
        sources = self._identify_data_sources(parsed_items, user_context)
        
        # List assumptions made
        assumptions = self._identify_assumptions(parsed_items, user_input)
        
        # Explain why this specific classification
        why_classification = self._explain_classification_choice(
            user_input,
            classification,
            user_context
        )
        
        # Build confidence breakdown
        confidence_breakdown = self._build_confidence_breakdown(
            user_input,
            parsed_items,
            confidence_score
        )
        
        return ResponseExplanation(
            reasoning=reasoning_steps,
            data_sources=sources,
            assumptions=assumptions,
            why_this_classification=why_classification,
            confidence_breakdown=confidence_breakdown
        )
    
    def _build_reasoning_steps(
        self,
        user_input: str,
        parsed_items: List[Dict[str, Any]],
        classification: str,
        user_context: Optional[Dict[str, Any]]
    ) -> str:
        """
        Build step-by-step reasoning explanation
        
        Example:
        "1. You said '2 eggs for breakfast'
         2. Identified '2 eggs' as food item
         3. Recognized 'breakfast' as meal timing
         4. Looked up nutrition data for eggs
         5. Calculated 140 calories total"
        """
        steps = []
        
        # Step 1: Input recognition
        steps.append(f"1. You said: '{user_input}'")
        
        # Step 2: Parsing
        if parsed_items:
            item = parsed_items[0]
            food_name = item.get('data', {}).get('item', 'item')
            quantity = item.get('data', {}).get('quantity')
            
            if quantity:
                steps.append(f"2. Identified '{quantity} {food_name}' as food item")
            else:
                steps.append(f"2. Identified '{food_name}' as food item")
        else:
            steps.append("2. Parsed your input to understand intent")
        
        # Step 3: Classification
        steps.append(f"3. Classified as '{classification}' based on context")
        
        # Step 4: Data lookup
        if parsed_items:
            calories = parsed_items[0].get('data', {}).get('calories')
            if calories:
                steps.append(f"4. Looked up nutritional data")
                steps.append(f"5. Calculated {int(calories)} total calories")
            else:
                steps.append("4. Estimated nutritional values")
        
        # Step 6: Context check (if available)
        if user_context:
            goal = user_context.get('daily_calorie_goal')
            if goal:
                consumed = user_context.get('calories_consumed_today', 0)
                remaining = goal - consumed
                steps.append(f"6. Checked progress: {int(remaining)} calories remaining today")
        
        return "\n".join(steps)
    
    def _identify_data_sources(
        self,
        parsed_items: List[Dict[str, Any]],
        user_context: Optional[Dict[str, Any]]
    ) -> List[str]:
        """
        Identify which data sources were used
        
        Returns list of human-readable source names
        """
        sources = []
        
        # Check if nutrition data was used
        if parsed_items:
            item = parsed_items[0]
            if item.get('data', {}).get('calories'):
                sources.append(self.data_sources['usda'])
        
        # Check if user history was considered
        if user_context:
            if user_context.get('recent_meals'):
                sources.append(self.data_sources['user_history'])
            if user_context.get('preferences'):
                sources.append(self.data_sources['user_preferences'])
        
        # Default to LLM knowledge
        if not sources:
            sources.append(self.data_sources['llm_knowledge'])
        
        # Always mention typical portions if no specific quantity
        if parsed_items:
            if not parsed_items[0].get('data', {}).get('quantity'):
                sources.append(self.data_sources['typical_portions'])
        
        return sources
    
    def _identify_assumptions(
        self,
        parsed_items: List[Dict[str, Any]],
        user_input: str
    ) -> List[str]:
        """
        Identify assumptions made during classification
        
        Returns list of assumptions (e.g., "Assumed medium-sized eggs")
        """
        assumptions = []
        
        if not parsed_items:
            return ["No specific assumptions - awaiting more information"]
        
        item = parsed_items[0]
        data = item.get('data', {})
        food_name = data.get('item', '').lower()
        
        # Size assumptions
        if 'egg' in food_name and 'large' not in user_input.lower() and 'small' not in user_input.lower():
            assumptions.append("Assumed medium-sized eggs (typical for calculations)")
        
        # Preparation assumptions
        if any(meat in food_name for meat in ['chicken', 'beef', 'fish', 'turkey']):
            if 'fried' not in user_input.lower() and 'oil' not in user_input.lower():
                assumptions.append("Assumed grilled/baked (no added fats)")
        
        # Quantity assumptions
        if not data.get('quantity'):
            assumptions.append("Assumed standard serving size")
        
        # Meal timing assumptions
        current_hour = datetime.now(timezone.utc).hour
        if 'breakfast' not in user_input.lower() and 'lunch' not in user_input.lower() and 'dinner' not in user_input.lower():
            if 6 <= current_hour < 11:
                assumptions.append("Assumed breakfast based on current time")
            elif 11 <= current_hour < 16:
                assumptions.append("Assumed lunch based on current time")
            elif 16 <= current_hour < 22:
                assumptions.append("Assumed dinner based on current time")
        
        # Raw vs cooked
        if any(grain in food_name for grain in ['rice', 'pasta', 'quinoa', 'oats']):
            if 'raw' not in user_input.lower() and 'dry' not in user_input.lower():
                assumptions.append("Assumed cooked weight (not dry/raw)")
        
        return assumptions if assumptions else ["No major assumptions made"]
    
    def _explain_classification_choice(
        self,
        user_input: str,
        classification: str,
        user_context: Optional[Dict[str, Any]]
    ) -> str:
        """
        Explain WHY this specific classification was chosen
        
        Returns human-readable explanation
        """
        input_lower = user_input.lower()
        current_hour = datetime.now(timezone.utc).hour
        
        # Explicit keywords
        if classification == 'meal':
            if any(meal_word in input_lower for meal_word in ['breakfast', 'lunch', 'dinner', 'snack', 'ate', 'had']):
                return f"You used meal-related keywords ('{user_input}')"
            
            # Time-based inference
            if 6 <= current_hour < 11:
                return "It's morning, so I assumed breakfast"
            elif 11 <= current_hour < 16:
                return "It's afternoon, so I assumed lunch"
            elif 16 <= current_hour < 22:
                return "It's evening, so I assumed dinner"
            else:
                return "You mentioned food, classified as late-night snack"
        
        elif classification == 'workout':
            if any(workout_word in input_lower for workout_word in ['ran', 'jogged', 'workout', 'exercise', 'gym', 'lifted']):
                return f"You used workout-related keywords"
            return "Classified as workout based on activity description"
        
        elif classification == 'water':
            if 'water' in input_lower or 'glass' in input_lower or 'ml' in input_lower:
                return "You mentioned water intake"
            return "Classified as hydration based on liquid mention"
        
        elif classification == 'supplement':
            if any(supp in input_lower for supp in ['vitamin', 'protein', 'supplement', 'pill', 'capsule']):
                return "You mentioned supplements or vitamins"
            return "Classified as supplement based on keywords"
        
        return f"Classified as '{classification}' based on context analysis"
    
    def _build_confidence_breakdown(
        self,
        user_input: str,
        parsed_items: List[Dict[str, Any]],
        overall_confidence: float
    ) -> Dict[str, float]:
        """
        Build detailed confidence factor breakdown
        
        Shows contribution of each factor to overall confidence
        """
        # Simple heuristic breakdown
        breakdown = {
            'input_clarity': 0.0,
            'data_quality': 0.0,
            'context_match': 0.0,
            'overall': overall_confidence
        }
        
        # Input clarity
        if len(user_input.split()) > 2 and any(char.isdigit() for char in user_input):
            breakdown['input_clarity'] = 0.9
        elif len(user_input.split()) > 1:
            breakdown['input_clarity'] = 0.7
        else:
            breakdown['input_clarity'] = 0.5
        
        # Data quality
        if parsed_items:
            item = parsed_items[0]
            if item.get('data', {}).get('protein_g') and item.get('data', {}).get('carbs_g'):
                breakdown['data_quality'] = 0.95
            elif item.get('data', {}).get('calories'):
                breakdown['data_quality'] = 0.8
            else:
                breakdown['data_quality'] = 0.6
        else:
            breakdown['data_quality'] = 0.4
        
        # Context match
        meal_keywords = ['breakfast', 'lunch', 'dinner', 'snack', 'ate', 'had']
        if any(keyword in user_input.lower() for keyword in meal_keywords):
            breakdown['context_match'] = 0.9
        else:
            breakdown['context_match'] = 0.7
        
        return breakdown


# Singleton instance
_response_explainer = None

def get_response_explainer() -> ResponseExplainer:
    """Get singleton instance of ResponseExplainer"""
    global _response_explainer
    if _response_explainer is None:
        _response_explainer = ResponseExplainer()
    return _response_explainer

