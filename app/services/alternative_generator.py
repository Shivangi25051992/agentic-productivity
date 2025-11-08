"""
Alternative Suggestion Generator

Generates alternative interpretations when AI is uncertain
Part of Phase 2: Explainable AI & Context Management
"""

from typing import List, Dict, Any, Optional
from datetime import datetime, timezone
from app.models.explainable_response import AlternativeInterpretation


class AlternativeGenerator:
    """
    Service for generating alternative interpretations of ambiguous input
    
    When confidence is low, provide 2-3 alternative interpretations
    for user to select the correct one
    """
    
    def __init__(self):
        # Common food portion variations
        self.portion_variations = {
            'small': 0.7,
            'medium': 1.0,
            'large': 1.3,
            'extra_large': 1.6
        }
        
        # Meal timing variations
        self.meal_time_map = {
            'breakfast': (6, 11),
            'lunch': (11, 16),
            'dinner': (16, 22),
            'snack': (0, 24)
        }
    
    def generate_alternatives(
        self,
        user_input: str,
        primary_interpretation: Dict[str, Any],
        primary_confidence: float,
        user_context: Optional[Dict[str, Any]] = None
    ) -> List[AlternativeInterpretation]:
        """
        Generate alternative interpretations for ambiguous input
        
        Args:
            user_input: User's original input
            primary_interpretation: AI's best guess
            primary_confidence: Confidence in primary
            user_context: User's historical data
        
        Returns:
            List of 2-3 alternative interpretations, sorted by confidence
        """
        alternatives = []
        
        # Only generate alternatives if confidence is low-medium (< 0.85)
        if primary_confidence >= 0.85:
            return alternatives
        
        # Check what kind of ambiguity exists
        has_quantity_ambiguity = self._has_quantity_ambiguity(user_input)
        has_timing_ambiguity = self._has_timing_ambiguity(user_input)
        has_preparation_ambiguity = self._has_preparation_ambiguity(user_input)
        
        # Generate quantity alternatives
        if has_quantity_ambiguity:
            quantity_alts = self._generate_quantity_alternatives(
                user_input, primary_interpretation
            )
            alternatives.extend(quantity_alts)
        
        # Generate timing alternatives
        if has_timing_ambiguity:
            timing_alts = self._generate_timing_alternatives(
                user_input, primary_interpretation
            )
            alternatives.extend(timing_alts)
        
        # Generate preparation alternatives
        if has_preparation_ambiguity:
            prep_alts = self._generate_preparation_alternatives(
                user_input, primary_interpretation
            )
            alternatives.extend(prep_alts)
        
        # Sort by confidence (highest first) and limit to top 3
        alternatives.sort(key=lambda x: x.confidence, reverse=True)
        return alternatives[:3]
    
    def _has_quantity_ambiguity(self, user_input: str) -> bool:
        """Check if input has ambiguous quantity"""
        vague_quantities = ['some', 'a few', 'a bit', 'little', 'lot', 'bunch']
        input_lower = user_input.lower()
        
        # Vague quantity words
        if any(vague in input_lower for vague in vague_quantities):
            return True
        
        # No quantity specified at all (no numbers)
        if not any(char.isdigit() for char in user_input):
            return True
        
        return False
    
    def _has_timing_ambiguity(self, user_input: str) -> bool:
        """Check if meal timing is ambiguous"""
        meal_keywords = ['breakfast', 'lunch', 'dinner', 'snack']
        input_lower = user_input.lower()
        
        # No explicit meal timing mentioned
        if not any(meal in input_lower for meal in meal_keywords):
            return True
        
        return False
    
    def _has_preparation_ambiguity(self, user_input: str) -> bool:
        """Check if preparation method is ambiguous"""
        prep_keywords = ['fried', 'grilled', 'baked', 'boiled', 'raw', 'cooked', 'steamed']
        input_lower = user_input.lower()
        
        # Food mentioned but no preparation method
        food_items = ['chicken', 'beef', 'fish', 'eggs', 'vegetables']
        has_food = any(food in input_lower for food in food_items)
        has_prep = any(prep in input_lower for prep in prep_keywords)
        
        return has_food and not has_prep
    
    def _generate_quantity_alternatives(
        self,
        user_input: str,
        primary_interpretation: Dict[str, Any]
    ) -> List[AlternativeInterpretation]:
        """Generate alternatives with different quantities"""
        alternatives = []
        primary_data = primary_interpretation.get('data', {})
        base_calories = primary_data.get('calories', 100)
        food_item = primary_data.get('item', 'item')
        
        # Alternative 1: Smaller portion
        small_calories = int(base_calories * self.portion_variations['small'])
        alternatives.append(AlternativeInterpretation(
            interpretation=f"Small portion of {food_item}",
            confidence=0.65,
            explanation=f"If you meant a small serving (70% of standard)",
            data={
                **primary_data,
                'calories': small_calories,
                'protein_g': primary_data.get('protein_g', 0) * 0.7,
                'carbs_g': primary_data.get('carbs_g', 0) * 0.7,
                'fat_g': primary_data.get('fat_g', 0) * 0.7,
                'portion_size': 'small'
            }
        ))
        
        # Alternative 2: Larger portion
        large_calories = int(base_calories * self.portion_variations['large'])
        alternatives.append(AlternativeInterpretation(
            interpretation=f"Large portion of {food_item}",
            confidence=0.6,
            explanation=f"If you meant a large serving (130% of standard)",
            data={
                **primary_data,
                'calories': large_calories,
                'protein_g': primary_data.get('protein_g', 0) * 1.3,
                'carbs_g': primary_data.get('carbs_g', 0) * 1.3,
                'fat_g': primary_data.get('fat_g', 0) * 1.3,
                'portion_size': 'large'
            }
        ))
        
        return alternatives
    
    def _generate_timing_alternatives(
        self,
        user_input: str,
        primary_interpretation: Dict[str, Any]
    ) -> List[AlternativeInterpretation]:
        """Generate alternatives with different meal timings"""
        alternatives = []
        primary_data = primary_interpretation.get('data', {})
        food_item = primary_data.get('item', 'item')
        current_hour = datetime.now(timezone.utc).hour
        
        # Get primary meal type (or infer from time)
        primary_meal_type = primary_data.get('meal_type')
        if not primary_meal_type:
            if 6 <= current_hour < 11:
                primary_meal_type = 'breakfast'
            elif 11 <= current_hour < 16:
                primary_meal_type = 'lunch'
            elif 16 <= current_hour < 22:
                primary_meal_type = 'dinner'
            else:
                primary_meal_type = 'snack'
        
        # Generate alternative meal timings
        meal_options = ['breakfast', 'lunch', 'dinner', 'snack']
        meal_options.remove(primary_meal_type)
        
        for idx, meal_type in enumerate(meal_options[:2]):  # Max 2 alternatives
            confidence = 0.7 - (idx * 0.1)  # Descending confidence
            alternatives.append(AlternativeInterpretation(
                interpretation=f"{food_item.capitalize()} as {meal_type}",
                confidence=confidence,
                explanation=f"If you had this for {meal_type} instead",
                data={
                    **primary_data,
                    'meal_type': meal_type
                }
            ))
        
        return alternatives
    
    def _generate_preparation_alternatives(
        self,
        user_input: str,
        primary_interpretation: Dict[str, Any]
    ) -> List[AlternativeInterpretation]:
        """Generate alternatives with different preparation methods"""
        alternatives = []
        primary_data = primary_interpretation.get('data', {})
        food_item = primary_data.get('item', '').lower()
        base_calories = primary_data.get('calories', 100)
        
        # Only for protein/meat items
        if not any(meat in food_item for meat in ['chicken', 'beef', 'fish', 'eggs']):
            return alternatives
        
        # Preparation method variations
        prep_methods = {
            'fried': {
                'multiplier': 1.4,
                'explanation': 'If fried in oil (adds ~40% calories from fat)'
            },
            'grilled': {
                'multiplier': 1.0,
                'explanation': 'If grilled without added fat (standard)'
            },
            'steamed': {
                'multiplier': 0.95,
                'explanation': 'If steamed (minimal calories added)'
            }
        }
        
        # Assume primary is "grilled" (standard)
        for prep_method, details in list(prep_methods.items())[:2]:
            if prep_method == 'grilled':
                continue
            
            alt_calories = int(base_calories * details['multiplier'])
            alternatives.append(AlternativeInterpretation(
                interpretation=f"{prep_method.capitalize()} {food_item}",
                confidence=0.65,
                explanation=details['explanation'],
                data={
                    **primary_data,
                    'calories': alt_calories,
                    'fat_g': primary_data.get('fat_g', 0) * details['multiplier'],
                    'preparation': prep_method
                }
            ))
        
        return alternatives[:1]  # Only return 1 prep alternative
    
    def select_alternative(
        self,
        selected_index: int,
        alternatives: List[AlternativeInterpretation],
        user_id: str
    ) -> Dict[str, Any]:
        """
        Record user's selection of an alternative
        
        This will be used for learning user preferences
        
        Args:
            selected_index: Index of selected alternative
            alternatives: List of alternatives shown
            user_id: User who made selection
        
        Returns:
            Selected alternative data
        """
        if selected_index < 0 or selected_index >= len(alternatives):
            raise ValueError(f"Invalid alternative index: {selected_index}")
        
        selected = alternatives[selected_index]
        
        # TODO: Store selection for learning
        # This will feed into Context Management (Step 4)
        selection_record = {
            'user_id': user_id,
            'selected_interpretation': selected.interpretation,
            'selected_data': selected.data,
            'alternatives_shown': len(alternatives),
            'timestamp': datetime.now(timezone.utc).isoformat()
        }
        
        return selection_record


# Singleton instance
_alternative_generator = None

def get_alternative_generator() -> AlternativeGenerator:
    """Get singleton instance of AlternativeGenerator"""
    global _alternative_generator
    if _alternative_generator is None:
        _alternative_generator = AlternativeGenerator()
    return _alternative_generator

