"""
Unit Tests for Response Explainer Service

Tests for Phase 2: Explainable AI response explanations
"""

import pytest
from app.services.response_explainer import ResponseExplainer, get_response_explainer
from app.models.explainable_response import ResponseExplanation


class TestResponseExplainer:
    """Test suite for ResponseExplainer"""
    
    def setup_method(self):
        """Setup test explainer"""
        self.explainer = ResponseExplainer()
    
    # ==================== REASONING STEPS TESTS ====================
    
    def test_build_reasoning_simple_meal(self):
        """Test reasoning for simple meal input"""
        user_input = "2 eggs for breakfast"
        parsed_items = [{
            'category': 'meal',
            'data': {
                'item': 'eggs',
                'quantity': 2,
                'calories': 140
            }
        }]
        
        reasoning = self.explainer._build_reasoning_steps(
            user_input, parsed_items, 'meal', None
        )
        
        assert "You said: '2 eggs for breakfast'" in reasoning
        assert "2 eggs" in reasoning
        assert "140" in reasoning
    
    def test_build_reasoning_with_context(self):
        """Test reasoning includes user context"""
        user_input = "chicken breast"
        parsed_items = [{
            'category': 'meal',
            'data': {'item': 'chicken breast', 'calories': 165}
        }]
        user_context = {
            'daily_calorie_goal': 2000,
            'calories_consumed_today': 1500
        }
        
        reasoning = self.explainer._build_reasoning_steps(
            user_input, parsed_items, 'meal', user_context
        )
        
        assert "500 calories remaining" in reasoning
        assert "progress" in reasoning.lower()
    
    def test_build_reasoning_no_items(self):
        """Test reasoning when no items parsed"""
        user_input = "something vague"
        parsed_items = []
        
        reasoning = self.explainer._build_reasoning_steps(
            user_input, parsed_items, 'other', None
        )
        
        assert "You said" in reasoning
        assert "Parsed your input" in reasoning
    
    # ==================== DATA SOURCES TESTS ====================
    
    def test_identify_data_sources_with_calories(self):
        """Test data source identification when calories present"""
        parsed_items = [{
            'data': {'calories': 140}
        }]
        
        sources = self.explainer._identify_data_sources(parsed_items, None)
        
        assert any('USDA' in source for source in sources)
    
    def test_identify_data_sources_with_history(self):
        """Test including user history as source"""
        parsed_items = [{'data': {'calories': 100}}]
        user_context = {
            'recent_meals': ['eggs', 'chicken']
        }
        
        sources = self.explainer._identify_data_sources(parsed_items, user_context)
        
        assert any('previous logs' in source for source in sources)
    
    def test_identify_data_sources_with_preferences(self):
        """Test including user preferences as source"""
        user_context = {
            'preferences': {'protein_preference': 'high'}
        }
        
        sources = self.explainer._identify_data_sources([], user_context)
        
        assert any('preferences' in source for source in sources)
    
    def test_identify_data_sources_default_llm(self):
        """Test default to LLM knowledge when no data"""
        sources = self.explainer._identify_data_sources([], None)
        
        assert any('AI' in source or 'knowledge' in source for source in sources)
    
    def test_identify_data_sources_typical_portions(self):
        """Test including typical portions when no quantity"""
        parsed_items = [{
            'data': {'item': 'apple'}  # No quantity specified
        }]
        
        sources = self.explainer._identify_data_sources(parsed_items, None)
        
        assert any('serving sizes' in source for source in sources)
    
    # ==================== ASSUMPTIONS TESTS ====================
    
    def test_assumptions_egg_size(self):
        """Test assumption about egg size"""
        parsed_items = [{
            'data': {'item': 'eggs', 'calories': 70}
        }]
        user_input = "eggs"
        
        assumptions = self.explainer._identify_assumptions(parsed_items, user_input)
        
        assert any('medium-sized eggs' in assumption for assumption in assumptions)
    
    def test_assumptions_meat_preparation(self):
        """Test assumption about meat preparation"""
        parsed_items = [{
            'data': {'item': 'chicken breast', 'calories': 165}
        }]
        user_input = "chicken breast"
        
        assumptions = self.explainer._identify_assumptions(parsed_items, user_input)
        
        assert any('grilled' in assumption.lower() or 'baked' in assumption.lower() for assumption in assumptions)
    
    def test_assumptions_no_quantity(self):
        """Test assumption when no quantity specified"""
        parsed_items = [{
            'data': {'item': 'apple'}
        }]
        user_input = "apple"
        
        assumptions = self.explainer._identify_assumptions(parsed_items, user_input)
        
        assert any('standard serving' in assumption for assumption in assumptions)
    
    def test_assumptions_cooked_grain(self):
        """Test assumption for rice/pasta as cooked"""
        parsed_items = [{
            'data': {'item': 'rice', 'calories': 200}
        }]
        user_input = "rice"
        
        assumptions = self.explainer._identify_assumptions(parsed_items, user_input)
        
        assert any('cooked' in assumption.lower() for assumption in assumptions)
    
    def test_assumptions_no_items(self):
        """Test assumptions when no items parsed"""
        assumptions = self.explainer._identify_assumptions([], "something")
        
        assert len(assumptions) > 0
        assert any('awaiting' in assumption.lower() for assumption in assumptions)
    
    # ==================== CLASSIFICATION EXPLANATION TESTS ====================
    
    def test_explain_classification_meal_keyword(self):
        """Test meal classification explanation with keywords"""
        explanation = self.explainer._explain_classification_choice(
            "I had eggs for breakfast",
            "meal",
            None
        )
        
        assert "meal-related keywords" in explanation.lower() or "breakfast" in explanation.lower()
    
    def test_explain_classification_workout(self):
        """Test workout classification explanation"""
        explanation = self.explainer._explain_classification_choice(
            "I ran 5k",
            "workout",
            None
        )
        
        assert "workout" in explanation.lower() or "activity" in explanation.lower()
    
    def test_explain_classification_water(self):
        """Test water classification explanation"""
        explanation = self.explainer._explain_classification_choice(
            "drank water",
            "water",
            None
        )
        
        assert "water" in explanation.lower() or "hydration" in explanation.lower()
    
    def test_explain_classification_supplement(self):
        """Test supplement classification explanation"""
        explanation = self.explainer._explain_classification_choice(
            "took vitamin D",
            "supplement",
            None
        )
        
        assert "supplement" in explanation.lower() or "vitamin" in explanation.lower()
    
    # ==================== CONFIDENCE BREAKDOWN TESTS ====================
    
    def test_confidence_breakdown_structure(self):
        """Test confidence breakdown has required fields"""
        breakdown = self.explainer._build_confidence_breakdown(
            "2 eggs",
            [{'data': {'calories': 140}}],
            0.85
        )
        
        assert 'input_clarity' in breakdown
        assert 'data_quality' in breakdown
        assert 'context_match' in breakdown
        assert 'overall' in breakdown
        assert breakdown['overall'] == 0.85
    
    def test_confidence_breakdown_high_quality_input(self):
        """Test high input clarity for detailed input"""
        breakdown = self.explainer._build_confidence_breakdown(
            "2 large eggs scrambled",
            [{'data': {'calories': 140, 'protein_g': 12}}],
            0.9
        )
        
        assert breakdown['input_clarity'] >= 0.8
        assert breakdown['data_quality'] >= 0.8
    
    def test_confidence_breakdown_low_quality_input(self):
        """Test low scores for vague input"""
        breakdown = self.explainer._build_confidence_breakdown(
            "food",
            [],
            0.4
        )
        
        assert breakdown['input_clarity'] < 0.7
        assert breakdown['data_quality'] < 0.7
    
    def test_confidence_breakdown_complete_data(self):
        """Test high data quality for complete nutrition"""
        parsed_items = [{
            'data': {
                'calories': 200,
                'protein_g': 15,
                'carbs_g': 5,
                'fat_g': 12
            }
        }]
        
        breakdown = self.explainer._build_confidence_breakdown(
            "chicken breast",
            parsed_items,
            0.9
        )
        
        assert breakdown['data_quality'] >= 0.9
    
    # ==================== FULL EXPLANATION TESTS ====================
    
    def test_explain_classification_complete(self):
        """Test complete explanation generation"""
        user_input = "2 eggs for breakfast"
        parsed_items = [{
            'category': 'meal',
            'data': {
                'item': 'eggs',
                'quantity': 2,
                'calories': 140,
                'protein_g': 12
            }
        }]
        
        explanation = self.explainer.explain_classification(
            user_input=user_input,
            parsed_items=parsed_items,
            classification='meal',
            confidence_score=0.85,
            user_context=None
        )
        
        assert isinstance(explanation, ResponseExplanation)
        assert len(explanation.reasoning) > 0
        assert len(explanation.data_sources) > 0
        assert len(explanation.assumptions) > 0
        assert explanation.why_this_classification is not None
        assert explanation.confidence_breakdown is not None
    
    def test_explain_classification_with_context(self):
        """Test explanation includes user context"""
        user_input = "chicken"
        parsed_items = [{'category': 'meal', 'data': {'item': 'chicken', 'calories': 165}}]
        user_context = {
            'daily_calorie_goal': 2000,
            'calories_consumed_today': 1500,
            'recent_meals': ['eggs', 'rice']
        }
        
        explanation = self.explainer.explain_classification(
            user_input=user_input,
            parsed_items=parsed_items,
            classification='meal',
            confidence_score=0.8,
            user_context=user_context
        )
        
        assert any('previous logs' in source for source in explanation.data_sources)
        assert '500 calories remaining' in explanation.reasoning
    
    def test_explain_classification_vague_input(self):
        """Test explanation for vague/unclear input"""
        user_input = "food"
        parsed_items = []
        
        explanation = self.explainer.explain_classification(
            user_input=user_input,
            parsed_items=parsed_items,
            classification='other',
            confidence_score=0.5,
            user_context=None
        )
        
        assert isinstance(explanation, ResponseExplanation)
        assert len(explanation.reasoning) > 0
        # Should have some assumptions about needing more info
        assert len(explanation.assumptions) > 0
    
    # ==================== SINGLETON TESTS ====================
    
    def test_get_response_explainer_singleton(self):
        """Test singleton pattern"""
        explainer1 = get_response_explainer()
        explainer2 = get_response_explainer()
        
        assert explainer1 is explainer2
        assert isinstance(explainer1, ResponseExplainer)
    
    # ==================== EDGE CASES ====================
    
    def test_empty_input_handling(self):
        """Test handling of empty input"""
        explanation = self.explainer.explain_classification(
            user_input="",
            parsed_items=[],
            classification='other',
            confidence_score=0.3,
            user_context=None
        )
        
        assert isinstance(explanation, ResponseExplanation)
        assert len(explanation.reasoning) > 0
    
    def test_multiple_items_explanation(self):
        """Test explanation for multiple parsed items"""
        parsed_items = [
            {'category': 'meal', 'data': {'item': 'eggs', 'calories': 140}},
            {'category': 'meal', 'data': {'item': 'toast', 'calories': 80}}
        ]
        
        explanation = self.explainer.explain_classification(
            user_input="eggs and toast",
            parsed_items=parsed_items,
            classification='meal',
            confidence_score=0.85,
            user_context=None
        )
        
        assert isinstance(explanation, ResponseExplanation)
        # Should still generate valid explanation (focuses on first item)
        assert len(explanation.reasoning) > 0

