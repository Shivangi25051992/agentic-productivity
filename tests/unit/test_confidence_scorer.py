"""
Unit Tests for Confidence Scoring Service

Tests for Phase 2: Explainable AI confidence scoring
"""

import pytest
from app.services.confidence_scorer import ConfidenceScorer, get_confidence_scorer
from app.models.explainable_response import ConfidenceFactors, ConfidenceLevel


class TestConfidenceScorer:
    """Test suite for ConfidenceScorer"""
    
    def setup_method(self):
        """Setup test scorer"""
        self.scorer = ConfidenceScorer()
    
    # ==================== INPUT CLARITY TESTS ====================
    
    def test_high_clarity_input(self):
        """Test high clarity input: specific quantities and items"""
        user_input = "2 large eggs, scrambled"
        clarity = self.scorer._calculate_input_clarity(user_input)
        
        assert clarity >= 0.9, f"Expected high clarity (>= 0.9), got {clarity}"
    
    def test_medium_clarity_input(self):
        """Test medium clarity: somewhat specific"""
        user_input = "a bit of rice"
        clarity = self.scorer._calculate_input_clarity(user_input)
        
        assert 0.6 <= clarity < 0.9, f"Expected medium clarity (0.6-0.9), got {clarity}"
    
    def test_low_clarity_input(self):
        """Test low clarity: vague input"""
        user_input = "some food"
        clarity = self.scorer._calculate_input_clarity(user_input)
        
        assert clarity < 0.6, f"Expected low clarity (< 0.6), got {clarity}"
    
    def test_ambiguous_keywords_penalty(self):
        """Test penalty for ambiguous keywords"""
        clear_input = "2 eggs"
        ambiguous_input = "maybe 2 eggs, about"
        
        clear_score = self.scorer._calculate_input_clarity(clear_input)
        ambiguous_score = self.scorer._calculate_input_clarity(ambiguous_input)
        
        assert ambiguous_score < clear_score, "Ambiguous input should have lower clarity"
    
    def test_vague_quantity_penalty(self):
        """Test penalty for vague quantities"""
        specific_input = "2 eggs"
        vague_input = "a few eggs"
        
        specific_score = self.scorer._calculate_input_clarity(specific_input)
        vague_score = self.scorer._calculate_input_clarity(vague_input)
        
        assert vague_score < specific_score, "Vague quantity should have lower clarity"
    
    def test_unit_bonus(self):
        """Test bonus for including units"""
        no_unit = "2 chicken"
        with_unit = "150g chicken"
        
        no_unit_score = self.scorer._calculate_input_clarity(no_unit)
        with_unit_score = self.scorer._calculate_input_clarity(with_unit)
        
        assert with_unit_score >= no_unit_score, "Units should improve clarity"
    
    def test_very_short_input_penalty(self):
        """Test penalty for very short inputs"""
        short_input = "egg"
        clarity = self.scorer._calculate_input_clarity(short_input)
        
        assert clarity < 0.8, f"Very short input should have lower clarity, got {clarity}"
    
    # ==================== DATA COMPLETENESS TESTS ====================
    
    def test_complete_data(self):
        """Test completeness with all nutrition data"""
        items = [{
            'category': 'meal',
            'data': {
                'calories': 200,
                'protein_g': 15,
                'carbs_g': 5,
                'fat_g': 12,
                'quantity': 2,
                'preparation': 'scrambled'
            }
        }]
        
        completeness = self.scorer._calculate_data_completeness(items)
        assert completeness >= 0.9, f"Complete data should score high, got {completeness}"
    
    def test_partial_data(self):
        """Test completeness with only calories"""
        items = [{
            'category': 'meal',
            'data': {
                'calories': 200
            }
        }]
        
        completeness = self.scorer._calculate_data_completeness(items)
        assert 0.5 <= completeness < 0.8, f"Partial data should score medium, got {completeness}"
    
    def test_no_data(self):
        """Test completeness with empty items"""
        items = []
        completeness = self.scorer._calculate_data_completeness(items)
        
        assert completeness < 0.5, f"No data should score low, got {completeness}"
    
    def test_estimate_penalty(self):
        """Test penalty for estimated data"""
        exact_items = [{
            'category': 'meal',
            'summary': 'Chicken breast',
            'data': {'calories': 200}
        }]
        
        estimated_items = [{
            'category': 'meal',
            'summary': 'Estimated chicken breast',
            'data': {'calories': 200}
        }]
        
        exact_score = self.scorer._calculate_data_completeness(exact_items)
        estimated_score = self.scorer._calculate_data_completeness(estimated_items)
        
        assert estimated_score < exact_score, "Estimates should have lower completeness"
    
    def test_multiple_items_average(self):
        """Test averaging across multiple items"""
        items = [
            {'category': 'meal', 'data': {'calories': 200, 'protein_g': 15}},
            {'category': 'meal', 'data': {'calories': 150}}
        ]
        
        completeness = self.scorer._calculate_data_completeness(items)
        assert 0.4 <= completeness <= 0.9, f"Should average across items, got {completeness}"
    
    # ==================== MODEL CERTAINTY TESTS ====================
    
    def test_explicit_confidence(self):
        """Test using explicit confidence from LLM"""
        llm_response = {'confidence': 0.95}
        certainty = self.scorer._calculate_model_certainty(llm_response)
        
        assert certainty == 0.95, f"Should use explicit confidence, got {certainty}"
    
    def test_no_llm_response(self):
        """Test default certainty when no LLM response"""
        certainty = self.scorer._calculate_model_certainty(None)
        
        assert certainty == 0.75, f"Default certainty should be 0.75, got {certainty}"
    
    def test_uncertainty_indicators(self):
        """Test detection of uncertainty in LLM response"""
        uncertain_response = {
            'content': 'I am not sure about this, might be incorrect'
        }
        
        certainty = self.scorer._calculate_model_certainty(uncertain_response)
        assert certainty < 0.75, f"Uncertain response should have lower certainty, got {certainty}"
    
    def test_confident_response(self):
        """Test high certainty for confident LLM response"""
        confident_response = {
            'content': '2 eggs, 140 calories total'
        }
        
        certainty = self.scorer._calculate_model_certainty(confident_response)
        assert certainty >= 0.7, f"Confident response should score well, got {certainty}"
    
    # ==================== HISTORICAL ACCURACY TESTS ====================
    
    def test_no_history_default(self):
        """Test default when no user history"""
        accuracy = self.scorer._calculate_historical_accuracy(None, [])
        
        assert accuracy == 0.7, f"Default accuracy should be 0.7, got {accuracy}"
    
    def test_high_accuracy_history(self):
        """Test high historical accuracy"""
        history = {
            'feedback_summary': {
                'total_interactions': 100,
                'corrections': 5
            }
        }
        
        accuracy = self.scorer._calculate_historical_accuracy(history, [])
        assert accuracy >= 0.9, f"High accuracy history should score high, got {accuracy}"
    
    def test_low_accuracy_history(self):
        """Test low historical accuracy"""
        history = {
            'feedback_summary': {
                'total_interactions': 100,
                'corrections': 40
            }
        }
        
        accuracy = self.scorer._calculate_historical_accuracy(history, [])
        assert accuracy < 0.7, f"Low accuracy history should score low, got {accuracy}"
    
    def test_category_specific_corrections(self):
        """Test lower accuracy for problematic categories"""
        history = {
            'feedback_summary': {
                'total_interactions': 100,
                'corrections': 10
            },
            'correction_history': [
                {'category': 'meal'} for _ in range(5)
            ]
        }
        
        items = [{'category': 'meal', 'data': {}}]
        
        accuracy = self.scorer._calculate_historical_accuracy(history, items)
        # Should be penalized for many meal corrections
        assert accuracy < 0.9, f"Problematic category should have lower accuracy, got {accuracy}"
    
    # ==================== OVERALL CONFIDENCE TESTS ====================
    
    def test_calculate_confidence_high(self):
        """Test overall high confidence scenario"""
        user_input = "2 large eggs, scrambled"
        parsed_items = [{
            'category': 'meal',
            'data': {
                'calories': 140,
                'protein_g': 12,
                'carbs_g': 1,
                'fat_g': 10
            }
        }]
        
        score, factors = self.scorer.calculate_confidence(user_input, parsed_items)
        
        assert score >= 0.8, f"High quality input should have high confidence, got {score}"
        assert isinstance(factors, ConfidenceFactors)
    
    def test_calculate_confidence_low(self):
        """Test overall low confidence scenario"""
        user_input = "some food"
        parsed_items = []
        
        score, factors = self.scorer.calculate_confidence(user_input, parsed_items)
        
        assert score < 0.6, f"Low quality input should have low confidence, got {score}"
        assert isinstance(factors, ConfidenceFactors)
    
    def test_calculate_confidence_medium(self):
        """Test medium confidence scenario"""
        user_input = "eggs for breakfast"
        parsed_items = [{
            'category': 'meal',
            'data': {'calories': 140}
        }]
        
        score, factors = self.scorer.calculate_confidence(user_input, parsed_items)
        
        assert 0.6 <= score < 0.9, f"Medium quality should have medium confidence, got {score}"
    
    def test_confidence_score_clamped(self):
        """Test that confidence score is clamped to 0-1"""
        # Try to trigger edge cases
        user_input = "x"  # Very short
        parsed_items = []  # No data
        
        score, _ = self.scorer.calculate_confidence(user_input, parsed_items)
        
        assert 0.0 <= score <= 1.0, f"Confidence must be 0-1, got {score}"
    
    def test_confidence_factors_all_present(self):
        """Test that all confidence factors are calculated"""
        user_input = "2 eggs"
        parsed_items = [{'category': 'meal', 'data': {'calories': 140}}]
        
        _, factors = self.scorer.calculate_confidence(user_input, parsed_items)
        
        assert hasattr(factors, 'input_clarity')
        assert hasattr(factors, 'data_completeness')
        assert hasattr(factors, 'model_certainty')
        assert 0.0 <= factors.input_clarity <= 1.0
        assert 0.0 <= factors.data_completeness <= 1.0
        assert 0.0 <= factors.model_certainty <= 1.0
    
    # ==================== CLARIFICATION TESTS ====================
    
    def test_should_request_clarification_low_confidence(self):
        """Test clarification request for low confidence"""
        assert self.scorer.should_request_clarification(0.5) is True
        assert self.scorer.should_request_clarification(0.6) is True
    
    def test_should_not_request_clarification_high_confidence(self):
        """Test no clarification for high confidence"""
        assert self.scorer.should_request_clarification(0.8) is False
        assert self.scorer.should_request_clarification(0.9) is False
    
    def test_clarification_boundary(self):
        """Test clarification threshold at 0.7"""
        assert self.scorer.should_request_clarification(0.69) is True
        assert self.scorer.should_request_clarification(0.7) is False
    
    def test_generate_clarification_unclear_input(self):
        """Test clarification question for unclear input"""
        user_input = "food"
        parsed_items = []
        factors = ConfidenceFactors(
            input_clarity=0.3,
            data_completeness=0.7,
            model_certainty=0.8
        )
        
        question = self.scorer.generate_clarification_question(user_input, parsed_items, factors)
        
        assert len(question) > 0, "Should generate a clarification question"
        assert "specific" in question.lower() or "example" in question.lower()
    
    def test_generate_clarification_incomplete_data(self):
        """Test clarification for incomplete data"""
        user_input = "chicken"
        parsed_items = [{'category': 'meal', 'data': {'item': 'chicken'}}]
        factors = ConfidenceFactors(
            input_clarity=0.8,
            data_completeness=0.3,
            model_certainty=0.8
        )
        
        question = self.scorer.generate_clarification_question(user_input, parsed_items, factors)
        
        assert len(question) > 0
        assert "amount" in question.lower() or "quantity" in question.lower() or "serving" in question.lower()
    
    # ==================== SINGLETON TESTS ====================
    
    def test_get_confidence_scorer_singleton(self):
        """Test singleton pattern"""
        scorer1 = get_confidence_scorer()
        scorer2 = get_confidence_scorer()
        
        assert scorer1 is scorer2, "Should return same instance"
        assert isinstance(scorer1, ConfidenceScorer)


class TestConfidenceLevelEnum:
    """Test ConfidenceLevel enum from models"""
    
    def test_determine_confidence_level_very_high(self):
        """Test very high confidence level"""
        from app.models.explainable_response import ExplainableResponse
        
        level = ExplainableResponse.determine_confidence_level(0.95)
        assert level == ConfidenceLevel.very_high
    
    def test_determine_confidence_level_high(self):
        """Test high confidence level"""
        from app.models.explainable_response import ExplainableResponse
        
        level = ExplainableResponse.determine_confidence_level(0.85)
        assert level == ConfidenceLevel.high
    
    def test_determine_confidence_level_medium(self):
        """Test medium confidence level"""
        from app.models.explainable_response import ExplainableResponse
        
        level = ExplainableResponse.determine_confidence_level(0.75)
        assert level == ConfidenceLevel.medium
    
    def test_determine_confidence_level_low(self):
        """Test low confidence level"""
        from app.models.explainable_response import ExplainableResponse
        
        level = ExplainableResponse.determine_confidence_level(0.6)
        assert level == ConfidenceLevel.low
    
    def test_determine_confidence_level_very_low(self):
        """Test very low confidence level"""
        from app.models.explainable_response import ExplainableResponse
        
        level = ExplainableResponse.determine_confidence_level(0.3)
        assert level == ConfidenceLevel.very_low
    
    def test_confidence_level_boundaries(self):
        """Test exact boundary values"""
        from app.models.explainable_response import ExplainableResponse
        
        assert ExplainableResponse.determine_confidence_level(0.9) == ConfidenceLevel.very_high
        assert ExplainableResponse.determine_confidence_level(0.8) == ConfidenceLevel.high
        assert ExplainableResponse.determine_confidence_level(0.7) == ConfidenceLevel.medium
        assert ExplainableResponse.determine_confidence_level(0.5) == ConfidenceLevel.low

