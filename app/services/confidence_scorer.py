"""
Confidence Scoring Service

Calculates confidence scores for AI responses based on multiple factors
Part of Phase 2: Explainable AI & Context Management
"""

from typing import Dict, Any, List, Optional
import re
from app.models.explainable_response import (
    ConfidenceFactors,
    ConfidenceLevel,
    ConfidenceScoreRequest
)


class ConfidenceScorer:
    """
    Service for calculating confidence scores for AI responses
    
    Confidence is based on:
    1. Input clarity (how clear was the user's request)
    2. Data completeness (how much nutrition data is available)
    3. Model certainty (explicit confidence from LLM if available)
    4. Historical accuracy (how accurate has AI been for similar requests)
    """
    
    def __init__(self):
        self.ambiguous_keywords = ['maybe', 'probably', 'around', 'about', 'roughly', 'approximately']
        self.vague_quantities = ['some', 'a few', 'a bit', 'little', 'lot']
    
    def calculate_confidence(
        self,
        user_input: str,
        parsed_items: List[Dict[str, Any]],
        llm_response: Optional[Dict[str, Any]] = None,
        user_history: Optional[Dict[str, Any]] = None
    ) -> tuple[float, ConfidenceFactors]:
        """
        Calculate overall confidence score and contributing factors
        
        Args:
            user_input: User's original input text
            parsed_items: Items parsed by AI
            llm_response: Raw LLM response (optional)
            user_history: User's historical accuracy data (optional)
        
        Returns:
            (confidence_score, confidence_factors)
        """
        
        # Calculate individual factors
        input_clarity = self._calculate_input_clarity(user_input)
        data_completeness = self._calculate_data_completeness(parsed_items)
        model_certainty = self._calculate_model_certainty(llm_response)
        historical_accuracy = self._calculate_historical_accuracy(user_history, parsed_items)
        
        # Weighted average of factors
        weights = {
            'input_clarity': 0.3,
            'data_completeness': 0.3,
            'model_certainty': 0.2,
            'historical_accuracy': 0.2
        }
        
        confidence_score = (
            input_clarity * weights['input_clarity'] +
            data_completeness * weights['data_completeness'] +
            model_certainty * weights['model_certainty'] +
            historical_accuracy * weights['historical_accuracy']
        )
        
        # Clamp to 0.0 - 1.0
        confidence_score = max(0.0, min(1.0, confidence_score))
        
        factors = ConfidenceFactors(
            input_clarity=input_clarity,
            data_completeness=data_completeness,
            model_certainty=model_certainty,
            historical_accuracy=historical_accuracy if user_history else None
        )
        
        return confidence_score, factors
    
    def _calculate_input_clarity(self, user_input: str) -> float:
        """
        Calculate how clear and specific the user's input is
        
        High clarity (0.9-1.0): "2 large eggs, scrambled" 
        Medium clarity (0.7-0.8): "eggs for breakfast"
        Low clarity (0.4-0.6): "some food"
        """
        clarity_score = 1.0
        input_lower = user_input.lower()
        
        # Penalty for ambiguous keywords
        for keyword in self.ambiguous_keywords:
            if keyword in input_lower:
                clarity_score -= 0.15
        
        # Penalty for vague quantities
        for vague in self.vague_quantities:
            if vague in input_lower:
                clarity_score -= 0.2
        
        # Bonus for specific quantities
        if re.search(r'\d+', user_input):
            clarity_score += 0.1
        
        # Bonus for units
        if re.search(r'\d+\s*(g|kg|oz|cup|tbsp|ml|l)\b', input_lower):
            clarity_score += 0.1
        
        # Penalty for very short inputs (< 5 chars)
        if len(user_input.strip()) < 5:
            clarity_score -= 0.3
        
        # Penalty for very vague inputs
        vague_patterns = ['something', 'stuff', 'things', 'food', 'ate']
        if any(pattern in input_lower for pattern in vague_patterns) and len(user_input.split()) < 3:
            clarity_score -= 0.3
        
        return max(0.0, min(1.0, clarity_score))
    
    def _calculate_data_completeness(self, parsed_items: List[Dict[str, Any]]) -> float:
        """
        Calculate how complete the nutrition data is
        
        High completeness (0.9-1.0): All macros present
        Medium completeness (0.6-0.8): Calories + some macros
        Low completeness (0.3-0.5): Only calories or estimates
        """
        if not parsed_items:
            return 0.3  # No data = low completeness
        
        completeness_scores = []
        
        for item in parsed_items:
            data = item.get('data', {})
            score = 0.5  # Base score
            
            # Check for key fields
            if 'calories' in data and data['calories']:
                score += 0.2
            
            if 'protein_g' in data and data['protein_g']:
                score += 0.1
            
            if 'carbs_g' in data and data['carbs_g']:
                score += 0.1
            
            if 'fat_g' in data and data['fat_g']:
                score += 0.1
            
            # Check for specificity
            if 'quantity' in data and data['quantity']:
                score += 0.1
            
            if 'preparation' in data and data['preparation']:
                score += 0.05
            
            # Penalty for estimates
            if item.get('summary', '').lower().find('estimated') >= 0:
                score -= 0.2
            
            completeness_scores.append(min(1.0, score))
        
        # Average across all items
        return sum(completeness_scores) / len(completeness_scores) if completeness_scores else 0.3
    
    def _calculate_model_certainty(self, llm_response: Optional[Dict[str, Any]]) -> float:
        """
        Calculate model's internal certainty from LLM response
        
        Uses explicit confidence if provided, otherwise heuristics
        """
        if not llm_response:
            return 0.75  # Default: Assume reasonably certain
        
        # Check if LLM provided explicit confidence
        if 'confidence' in llm_response:
            return float(llm_response['confidence'])
        
        # Check for uncertainty indicators in response
        response_text = str(llm_response).lower()
        
        uncertainty_indicators = [
            'not sure', 'unclear', 'might be', 'could be',
            'possibly', 'maybe', 'uncertain', 'ambiguous'
        ]
        
        certainty = 0.8  # Default certainty
        
        for indicator in uncertainty_indicators:
            if indicator in response_text:
                certainty -= 0.15
        
        return max(0.3, min(1.0, certainty))
    
    def _calculate_historical_accuracy(
        self,
        user_history: Optional[Dict[str, Any]],
        current_items: List[Dict[str, Any]]
    ) -> float:
        """
        Calculate confidence based on historical accuracy for similar requests
        
        If user frequently corrects certain types of items, lower confidence
        """
        if not user_history:
            return 0.7  # Default: No history available
        
        # Extract correction rate from history
        feedback_summary = user_history.get('feedback_summary', {})
        total_interactions = feedback_summary.get('total_interactions', 0)
        corrections = feedback_summary.get('corrections', 0)
        
        if total_interactions == 0:
            return 0.7  # No history yet
        
        # Calculate accuracy rate
        accuracy_rate = 1.0 - (corrections / total_interactions)
        
        # Check if current item category has been problematic
        current_categories = {item.get('category') for item in current_items}
        correction_history = user_history.get('correction_history', [])
        
        # Find corrections for similar categories
        similar_corrections = [
            c for c in correction_history
            if c.get('category') in current_categories
        ]
        
        # If this category has many corrections, lower confidence
        if len(similar_corrections) > 3:
            accuracy_rate -= 0.15
        
        return max(0.3, min(1.0, accuracy_rate))
    
    def should_request_clarification(self, confidence_score: float) -> bool:
        """
        Determine if AI should ask for clarification
        
        Returns True if confidence < 0.7
        """
        return confidence_score < 0.7
    
    def generate_clarification_question(
        self,
        user_input: str,
        parsed_items: List[Dict[str, Any]],
        confidence_factors: ConfidenceFactors
    ) -> str:
        """
        Generate a clarification question based on low confidence factors
        """
        
        # Identify the weakest factor
        factors_dict = {
            'input_clarity': confidence_factors.input_clarity,
            'data_completeness': confidence_factors.data_completeness,
            'model_certainty': confidence_factors.model_certainty
        }
        
        weakest_factor = min(factors_dict, key=factors_dict.get)
        
        # Generate appropriate question
        if weakest_factor == 'input_clarity':
            return self._clarify_input(user_input, parsed_items)
        elif weakest_factor == 'data_completeness':
            return self._clarify_data(parsed_items)
        else:
            return self._clarify_general(user_input, parsed_items)
    
    def _clarify_input(self, user_input: str, parsed_items: List[Dict[str, Any]]) -> str:
        """Generate clarification for unclear input"""
        if not parsed_items:
            return f"I'm not sure I understood '{user_input}' correctly. Can you be more specific? For example, '2 eggs for breakfast' or '1 cup of rice'."
        
        item = parsed_items[0]
        food_name = item.get('data', {}).get('item', 'that')
        
        return f"Did you mean {food_name}? If so, how much did you have? (e.g., '2 eggs' or '150g')"
    
    def _clarify_data(self, parsed_items: List[Dict[str, Any]]) -> str:
        """Generate clarification for incomplete data"""
        if not parsed_items:
            return "Can you tell me more about what you ate? Include quantity if possible."
        
        item = parsed_items[0]
        food_name = item.get('data', {}).get('item', 'that item')
        
        return f"I found {food_name}, but I'm not sure about the exact amount. Was it a standard serving, or can you specify the quantity?"
    
    def _clarify_general(self, user_input: str, parsed_items: List[Dict[str, Any]]) -> str:
        """Generate general clarification"""
        return f"I logged what I understood from '{user_input}', but I'm not entirely certain. Does this look correct?"


# Singleton instance
_confidence_scorer = None

def get_confidence_scorer() -> ConfidenceScorer:
    """Get singleton instance of ConfidenceScorer"""
    global _confidence_scorer
    if _confidence_scorer is None:
        _confidence_scorer = ConfidenceScorer()
    return _confidence_scorer

