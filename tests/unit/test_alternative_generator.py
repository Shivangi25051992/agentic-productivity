"""
Unit Tests for Alternative Generator Service

Tests for Phase 2: Explainable AI alternative suggestions
"""

import pytest
from app.services.alternative_generator import AlternativeGenerator, get_alternative_generator
from app.models.explainable_response import AlternativeInterpretation


class TestAlternativeGenerator:
    """Test suite for AlternativeGenerator"""
    
    def setup_method(self):
        """Setup test generator"""
        self.generator = AlternativeGenerator()
    
    # ==================== AMBIGUITY DETECTION TESTS ====================
    
    def test_has_quantity_ambiguity_vague_words(self):
        """Test detection of vague quantity words"""
        assert self.generator._has_quantity_ambiguity("some chicken") is True
        assert self.generator._has_quantity_ambiguity("a few eggs") is True
        assert self.generator._has_quantity_ambiguity("a bit of rice") is True
    
    def test_has_quantity_ambiguity_no_numbers(self):
        """Test detection of missing quantity numbers"""
        assert self.generator._has_quantity_ambiguity("chicken breast") is True
        assert self.generator._has_quantity_ambiguity("eggs") is True
    
    def test_has_quantity_ambiguity_clear_quantity(self):
        """Test no ambiguity for clear quantities"""
        assert self.generator._has_quantity_ambiguity("2 eggs") is False
        assert self.generator._has_quantity_ambiguity("150g chicken") is False
    
    def test_has_timing_ambiguity_no_meal_keyword(self):
        """Test detection of missing meal timing"""
        assert self.generator._has_timing_ambiguity("eggs and toast") is True
        assert self.generator._has_timing_ambiguity("chicken") is True
    
    def test_has_timing_ambiguity_explicit_timing(self):
        """Test no ambiguity when meal timing is explicit"""
        assert self.generator._has_timing_ambiguity("eggs for breakfast") is False
        assert self.generator._has_timing_ambiguity("lunch salad") is False
    
    def test_has_preparation_ambiguity_no_method(self):
        """Test detection of missing preparation method"""
        assert self.generator._has_preparation_ambiguity("chicken breast") is True
        assert self.generator._has_preparation_ambiguity("fish") is True
    
    def test_has_preparation_ambiguity_explicit_method(self):
        """Test no ambiguity when prep method is explicit"""
        assert self.generator._has_preparation_ambiguity("grilled chicken") is False
        assert self.generator._has_preparation_ambiguity("fried eggs") is False
    
    def test_has_preparation_ambiguity_non_food(self):
        """Test no ambiguity for non-protein foods"""
        assert self.generator._has_preparation_ambiguity("rice") is False
        assert self.generator._has_preparation_ambiguity("banana") is False
    
    # ==================== QUANTITY ALTERNATIVES TESTS ====================
    
    def test_generate_quantity_alternatives_structure(self):
        """Test structure of quantity alternatives"""
        primary = {
            'data': {
                'item': 'chicken',
                'calories': 165,
                'protein_g': 31
            }
        }
        
        alternatives = self.generator._generate_quantity_alternatives("chicken", primary)
        
        assert len(alternatives) == 2  # Small and large
        assert all(isinstance(alt, AlternativeInterpretation) for alt in alternatives)
    
    def test_generate_quantity_alternatives_small_portion(self):
        """Test small portion alternative"""
        primary = {
            'data': {
                'item': 'chicken',
                'calories': 165,
                'protein_g': 31
            }
        }
        
        alternatives = self.generator._generate_quantity_alternatives("chicken", primary)
        small_alt = alternatives[0]  # First is small
        
        assert "small" in small_alt.interpretation.lower()
        assert small_alt.data['calories'] == int(165 * 0.7)
        assert small_alt.data['portion_size'] == 'small'
        assert 0.6 <= small_alt.confidence <= 0.7
    
    def test_generate_quantity_alternatives_large_portion(self):
        """Test large portion alternative"""
        primary = {
            'data': {
                'item': 'chicken',
                'calories': 165,
                'protein_g': 31
            }
        }
        
        alternatives = self.generator._generate_quantity_alternatives("chicken", primary)
        large_alt = alternatives[1]  # Second is large
        
        assert "large" in large_alt.interpretation.lower()
        assert large_alt.data['calories'] == int(165 * 1.3)
        assert large_alt.data['portion_size'] == 'large'
        assert 0.5 <= large_alt.confidence <= 0.7
    
    def test_generate_quantity_alternatives_preserves_macros(self):
        """Test that macros are scaled proportionally"""
        primary = {
            'data': {
                'item': 'chicken',
                'calories': 165,
                'protein_g': 31,
                'carbs_g': 0,
                'fat_g': 3.6
            }
        }
        
        alternatives = self.generator._generate_quantity_alternatives("chicken", primary)
        small_alt = alternatives[0]
        
        # Check macros are scaled
        assert small_alt.data['protein_g'] == pytest.approx(31 * 0.7, rel=0.01)
        assert small_alt.data['fat_g'] == pytest.approx(3.6 * 0.7, rel=0.01)
    
    # ==================== TIMING ALTERNATIVES TESTS ====================
    
    def test_generate_timing_alternatives_structure(self):
        """Test structure of timing alternatives"""
        primary = {
            'data': {
                'item': 'eggs',
                'meal_type': 'breakfast',
                'calories': 140
            }
        }
        
        alternatives = self.generator._generate_timing_alternatives("eggs", primary)
        
        assert len(alternatives) <= 2  # Max 2 timing alternatives
        assert all(isinstance(alt, AlternativeInterpretation) for alt in alternatives)
    
    def test_generate_timing_alternatives_excludes_primary(self):
        """Test that primary meal type is excluded"""
        primary = {
            'data': {
                'item': 'eggs',
                'meal_type': 'breakfast',
                'calories': 140
            }
        }
        
        alternatives = self.generator._generate_timing_alternatives("eggs", primary)
        
        # Should not suggest breakfast (it's the primary)
        assert not any('breakfast' in alt.data.get('meal_type', '') for alt in alternatives)
    
    def test_generate_timing_alternatives_confidence_descending(self):
        """Test that confidence decreases for later alternatives"""
        primary = {
            'data': {
                'item': 'eggs',
                'meal_type': 'breakfast',
                'calories': 140
            }
        }
        
        alternatives = self.generator._generate_timing_alternatives("eggs", primary)
        
        if len(alternatives) > 1:
            assert alternatives[0].confidence > alternatives[1].confidence
    
    # ==================== PREPARATION ALTERNATIVES TESTS ====================
    
    def test_generate_preparation_alternatives_protein_only(self):
        """Test prep alternatives only for protein foods"""
        protein_primary = {
            'data': {
                'item': 'chicken',
                'calories': 165
            }
        }
        non_protein_primary = {
            'data': {
                'item': 'apple',
                'calories': 95
            }
        }
        
        protein_alts = self.generator._generate_preparation_alternatives("chicken", protein_primary)
        non_protein_alts = self.generator._generate_preparation_alternatives("apple", non_protein_primary)
        
        assert len(protein_alts) > 0
        assert len(non_protein_alts) == 0
    
    def test_generate_preparation_alternatives_fried_variation(self):
        """Test fried variation has higher calories"""
        primary = {
            'data': {
                'item': 'chicken',
                'calories': 165,
                'fat_g': 3.6
            }
        }
        
        alternatives = self.generator._generate_preparation_alternatives("chicken", primary)
        
        # Should have fried alternative with ~40% more calories
        fried_alt = next((alt for alt in alternatives if 'fried' in alt.interpretation.lower()), None)
        if fried_alt:
            assert fried_alt.data['calories'] > 165
            assert fried_alt.data['fat_g'] > 3.6
    
    # ==================== MAIN GENERATE ALTERNATIVES TESTS ====================
    
    def test_generate_alternatives_high_confidence_no_alternatives(self):
        """Test no alternatives generated when confidence is high"""
        user_input = "2 large eggs, scrambled"
        primary = {
            'data': {
                'item': 'eggs',
                'calories': 140
            }
        }
        
        alternatives = self.generator.generate_alternatives(
            user_input=user_input,
            primary_interpretation=primary,
            primary_confidence=0.9  # High confidence
        )
        
        assert len(alternatives) == 0
    
    def test_generate_alternatives_low_confidence_generates(self):
        """Test alternatives generated when confidence is low"""
        user_input = "chicken"  # Ambiguous
        primary = {
            'data': {
                'item': 'chicken',
                'calories': 165,
                'meal_type': 'lunch'
            }
        }
        
        alternatives = self.generator.generate_alternatives(
            user_input=user_input,
            primary_interpretation=primary,
            primary_confidence=0.7  # Low confidence
        )
        
        assert len(alternatives) > 0
        assert len(alternatives) <= 3  # Max 3
    
    def test_generate_alternatives_sorted_by_confidence(self):
        """Test alternatives are sorted by confidence (highest first)"""
        user_input = "some chicken"
        primary = {
            'data': {
                'item': 'chicken',
                'calories': 165,
                'meal_type': 'lunch'
            }
        }
        
        alternatives = self.generator.generate_alternatives(
            user_input=user_input,
            primary_interpretation=primary,
            primary_confidence=0.6
        )
        
        if len(alternatives) > 1:
            for i in range(len(alternatives) - 1):
                assert alternatives[i].confidence >= alternatives[i + 1].confidence
    
    def test_generate_alternatives_mixed_ambiguity(self):
        """Test alternatives for input with multiple ambiguities"""
        user_input = "chicken"  # No quantity, no timing, no prep
        primary = {
            'data': {
                'item': 'chicken',
                'calories': 165,
                'meal_type': 'lunch'
            }
        }
        
        alternatives = self.generator.generate_alternatives(
            user_input=user_input,
            primary_interpretation=primary,
            primary_confidence=0.65
        )
        
        # Should have alternatives from different categories
        assert len(alternatives) > 0
        assert len(alternatives) <= 3
    
    # ==================== ALTERNATIVE SELECTION TESTS ====================
    
    def test_select_alternative_valid_index(self):
        """Test selecting a valid alternative"""
        alternatives = [
            AlternativeInterpretation(
                interpretation="Small chicken",
                confidence=0.7,
                explanation="Small portion",
                data={'calories': 115}
            ),
            AlternativeInterpretation(
                interpretation="Large chicken",
                confidence=0.6,
                explanation="Large portion",
                data={'calories': 215}
            )
        ]
        
        selection = self.generator.select_alternative(0, alternatives, "user123")
        
        assert selection['selected_interpretation'] == "Small chicken"
        assert selection['selected_data']['calories'] == 115
        assert selection['user_id'] == "user123"
        assert 'timestamp' in selection
    
    def test_select_alternative_invalid_index(self):
        """Test error on invalid alternative index"""
        alternatives = [
            AlternativeInterpretation(
                interpretation="Test",
                confidence=0.7,
                explanation="Test",
                data={}
            )
        ]
        
        with pytest.raises(ValueError, match="Invalid alternative index"):
            self.generator.select_alternative(5, alternatives, "user123")
    
    def test_select_alternative_negative_index(self):
        """Test error on negative index"""
        alternatives = [
            AlternativeInterpretation(
                interpretation="Test",
                confidence=0.7,
                explanation="Test",
                data={}
            )
        ]
        
        with pytest.raises(ValueError, match="Invalid alternative index"):
            self.generator.select_alternative(-1, alternatives, "user123")
    
    # ==================== SINGLETON TESTS ====================
    
    def test_get_alternative_generator_singleton(self):
        """Test singleton pattern"""
        gen1 = get_alternative_generator()
        gen2 = get_alternative_generator()
        
        assert gen1 is gen2
        assert isinstance(gen1, AlternativeGenerator)
    
    # ==================== EDGE CASES ====================
    
    def test_empty_primary_interpretation(self):
        """Test handling of empty primary interpretation"""
        alternatives = self.generator.generate_alternatives(
            user_input="test",
            primary_interpretation={'data': {}},
            primary_confidence=0.5
        )
        
        # Should handle gracefully
        assert isinstance(alternatives, list)
    
    def test_missing_data_field(self):
        """Test handling of missing data field"""
        alternatives = self.generator.generate_alternatives(
            user_input="test",
            primary_interpretation={},  # No 'data' field
            primary_confidence=0.5
        )
        
        # Should handle gracefully
        assert isinstance(alternatives, list)

