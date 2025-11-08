"""
Unit Tests for ResponseFormatter

Tests the ChatGPT-style response formatting service
"""

import pytest
from app.services.response_formatter import (
    ResponseFormatter,
    FormattedResponse,
    get_response_formatter
)


class TestResponseFormatterSingleton:
    """Test singleton pattern"""
    
    def test_singleton_instance(self):
        """Test that get_response_formatter returns same instance"""
        formatter1 = get_response_formatter()
        formatter2 = get_response_formatter()
        assert formatter1 is formatter2


class TestFormatResponse:
    """Test format_response() main method"""
    
    def setup_method(self):
        self.formatter = ResponseFormatter()
    
    def test_format_single_meal(self):
        """Test formatting a single meal"""
        items = [{
            'category': 'meal',
            'data': {
                'item': 'chicken breast',
                'quantity': '150g',
                'calories': 165,
                'protein_g': 31,
                'carbs_g': 0,
                'fat_g': 3.6,
                'meal_type': 'lunch'
            }
        }]
        
        result = self.formatter.format_response(items)
        
        assert isinstance(result, FormattedResponse)
        assert result.net_calories == 165
        assert 'chicken breast' in result.summary_text.lower()
        assert '165 kcal' in result.summary_text
        assert '31g protein' in result.summary_text
    
    def test_format_multiple_meals(self):
        """Test formatting multiple meals"""
        items = [
            {
                'category': 'meal',
                'data': {
                    'item': 'apple',
                    'calories': 95,
                    'protein_g': 0.5,
                    'carbs_g': 25,
                    'fat_g': 0.3,
                    'meal_type': 'snack'
                }
            },
            {
                'category': 'meal',
                'data': {
                    'item': 'banana',
                    'calories': 105,
                    'protein_g': 1.3,
                    'carbs_g': 27,
                    'fat_g': 0.4,
                    'meal_type': 'snack'
                }
            }
        ]
        
        result = self.formatter.format_response(items)
        
        assert result.net_calories == 200  # 95 + 105
        assert 'apple' in result.summary_text.lower()
        assert 'banana' in result.summary_text.lower()
        assert '~200 kcal' in result.summary_text  # Total
    
    def test_format_meal_with_workout(self):
        """Test formatting meal with workout (net calories)"""
        items = [
            {
                'category': 'meal',
                'data': {
                    'item': 'pasta',
                    'calories': 400,
                    'protein_g': 15,
                    'carbs_g': 75,
                    'fat_g': 5,
                    'meal_type': 'dinner'
                }
            },
            {
                'category': 'workout',
                'data': {
                    'item': 'running',
                    'quantity': '30 minutes',
                    'calories_burned': 300,
                    'intensity': 'moderate'
                }
            }
        ]
        
        result = self.formatter.format_response(items)
        
        assert result.net_calories == 100  # 400 - 300
        assert 'pasta' in result.summary_text.lower()
        assert 'running' in result.summary_text.lower()
        assert 'Calories consumed: ~400 kcal' in result.summary_text
        assert 'Calories burned: ~300 kcal' in result.summary_text
        assert 'Net: ≈ +100 kcal' in result.summary_text
    
    def test_format_net_deficit(self):
        """Test formatting with calorie deficit"""
        items = [
            {
                'category': 'meal',
                'data': {
                    'item': 'salad',
                    'calories': 150,
                    'protein_g': 10,
                    'carbs_g': 20,
                    'fat_g': 3
                }
            },
            {
                'category': 'workout',
                'data': {
                    'item': 'cycling',
                    'quantity': '1 hour',
                    'calories_burned': 400
                }
            }
        ]
        
        result = self.formatter.format_response(items)
        
        assert result.net_calories == -250  # 150 - 400
        assert 'Net: ≈ -250 kcal' in result.summary_text
        assert 'deficit' in result.summary_text
    
    def test_format_net_maintenance(self):
        """Test formatting with exact maintenance"""
        items = [
            {
                'category': 'meal',
                'data': {
                    'item': 'meal',
                    'calories': 300,
                    'protein_g': 20,
                    'carbs_g': 30,
                    'fat_g': 10
                }
            },
            {
                'category': 'workout',
                'data': {
                    'item': 'walking',
                    'quantity': '1 hour',
                    'calories_burned': 300
                }
            }
        ]
        
        result = self.formatter.format_response(items)
        
        assert result.net_calories == 0
        assert 'maintenance' in result.summary_text
    
    def test_format_with_supplements(self):
        """Test formatting with supplements"""
        items = [
            {
                'category': 'meal',
                'data': {
                    'item': 'oatmeal',
                    'calories': 150,
                    'protein_g': 5,
                    'carbs_g': 27,
                    'fat_g': 3
                }
            },
            {
                'category': 'supplement',
                'data': {
                    'item': 'protein powder',
                    'calories': 120,
                    'protein_g': 25,
                    'carbs_g': 3,
                    'fat_g': 2
                }
            }
        ]
        
        result = self.formatter.format_response(items)
        
        assert result.net_calories == 270  # 150 + 120
        assert 'oatmeal' in result.summary_text.lower()
        assert 'protein powder' in result.summary_text.lower()
    
    def test_format_empty_items(self):
        """Test formatting with no items"""
        result = self.formatter.format_response([])
        
        assert result.net_calories == 0
        assert "Here's a quick nutrition" in result.summary_text
    
    def test_format_with_preparation(self):
        """Test formatting with preparation method"""
        items = [{
            'category': 'meal',
            'data': {
                'item': 'chicken',
                'quantity': '200g',
                'preparation': 'grilled',
                'calories': 220,
                'protein_g': 40,
                'carbs_g': 0,
                'fat_g': 6
            }
        }]
        
        result = self.formatter.format_response(items)
        
        assert 'grilled' in result.summary_text.lower()
        assert '200g' in result.summary_text
    
    def test_format_capitalizes_item_names(self):
        """Test that item names are properly capitalized"""
        items = [{
            'category': 'meal',
            'data': {
                'item': 'CHICKEN BREAST',  # All caps
                'calories': 165,
                'protein_g': 31,
                'carbs_g': 0,
                'fat_g': 3.6
            }
        }]
        
        result = self.formatter.format_response(items)
        
        # Should be title case
        assert 'Chicken Breast' in result.summary_text


class TestGenerateSuggestions:
    """Test _generate_suggestions() method"""
    
    def setup_method(self):
        self.formatter = ResponseFormatter()
    
    def test_suggestion_low_protein(self):
        """Test suggestion for low protein intake"""
        suggestions = self.formatter._generate_suggestions(
            net_calories=1500,
            total_protein=30,  # Low
            total_carbs=200,
            total_fat=50,
            user_goal='lose_weight',
            daily_calorie_goal=2000
        )
        
        assert suggestions is not None
        assert 'protein' in suggestions.lower()
        assert 'eggs' in suggestions.lower() or 'chicken' in suggestions.lower()
    
    def test_suggestion_lose_weight_over_goal(self):
        """Test suggestion for weight loss when over calorie goal"""
        suggestions = self.formatter._generate_suggestions(
            net_calories=2200,  # Over goal
            total_protein=100,
            total_carbs=250,
            total_fat=70,
            user_goal='lose_weight',
            daily_calorie_goal=2000
        )
        
        assert suggestions is not None
        assert '200 kcal over' in suggestions
        assert 'lighter dinner' in suggestions.lower() or 'skip snacks' in suggestions.lower()
    
    def test_suggestion_lose_weight_under_goal(self):
        """Test suggestion for weight loss when under calorie goal"""
        suggestions = self.formatter._generate_suggestions(
            net_calories=1300,  # Well under goal
            total_protein=100,
            total_carbs=150,
            total_fat=40,
            user_goal='lose_weight',
            daily_calorie_goal=2000
        )
        
        assert suggestions is not None
        assert '700 kcal remaining' in suggestions
        assert 'protein' in suggestions.lower()
    
    def test_suggestion_gain_muscle(self):
        """Test suggestion for muscle gain goal"""
        suggestions = self.formatter._generate_suggestions(
            net_calories=2200,  # Under goal
            total_protein=120,
            total_carbs=300,
            total_fat=60,
            user_goal='gain_muscle',
            daily_calorie_goal=2600
        )
        
        assert suggestions is not None
        assert '400 kcal remaining' in suggestions
        assert 'protein' in suggestions.lower()
        assert 'muscle growth' in suggestions.lower()
    
    def test_suggestion_high_carbs_relative_to_protein(self):
        """Test suggestion for high carb-to-protein ratio"""
        suggestions = self.formatter._generate_suggestions(
            net_calories=1800,
            total_protein=40,  # Low
            total_carbs=200,  # High (5x protein)
            total_fat=50,
            user_goal='lose_weight',
            daily_calorie_goal=2000
        )
        
        assert suggestions is not None
        assert 'carbs are high' in suggestions.lower()
        assert 'protein' in suggestions.lower()
    
    def test_suggestion_no_suggestions(self):
        """Test no suggestions when everything is balanced"""
        suggestions = self.formatter._generate_suggestions(
            net_calories=1900,
            total_protein=150,  # Good
            total_carbs=200,
            total_fat=60,
            user_goal='maintain',
            daily_calorie_goal=2000
        )
        
        # Might be None or empty
        assert suggestions is None or len(suggestions) == 0
    
    def test_suggestion_without_user_goal(self):
        """Test suggestions without user goal"""
        suggestions = self.formatter._generate_suggestions(
            net_calories=1500,
            total_protein=30,  # Low
            total_carbs=200,
            total_fat=50,
            user_goal=None,  # No goal
            daily_calorie_goal=None
        )
        
        # Should still suggest increasing protein
        assert suggestions is not None
        assert 'protein' in suggestions.lower()


class TestCalculations:
    """Test calorie and macro calculations"""
    
    def setup_method(self):
        self.formatter = ResponseFormatter()
    
    def test_total_calories_consumed(self):
        """Test total calories calculation"""
        items = [
            {'category': 'meal', 'data': {'calories': 100}},
            {'category': 'meal', 'data': {'calories': 200}},
            {'category': 'snack', 'data': {'calories': 50}}
        ]
        
        result = self.formatter.format_response(items)
        assert result.net_calories == 350
    
    def test_total_macros(self):
        """Test macro totals calculation"""
        items = [
            {'category': 'meal', 'data': {'calories': 100, 'protein_g': 10, 'carbs_g': 15, 'fat_g': 3}},
            {'category': 'meal', 'data': {'calories': 200, 'protein_g': 20, 'carbs_g': 25, 'fat_g': 8}}
        ]
        
        result = self.formatter.format_response(items)
        
        # Check totals in summary
        assert '~30g protein' in result.summary_text  # 10 + 20
        assert '~40g carbs' in result.summary_text  # 15 + 25
        assert '~11g fat' in result.summary_text  # 3 + 8
    
    def test_net_calories_with_workout(self):
        """Test net calories calculation with workout"""
        items = [
            {'category': 'meal', 'data': {'calories': 500}},
            {'category': 'workout', 'data': {'calories_burned': 300}}
        ]
        
        result = self.formatter.format_response(items)
        assert result.net_calories == 200  # 500 - 300
    
    def test_missing_macro_data(self):
        """Test handling missing macro data"""
        items = [{
            'category': 'meal',
            'data': {
                'item': 'food',
                'calories': 100
                # No protein, carbs, fat
            }
        }]
        
        result = self.formatter.format_response(items)
        
        # Should default to 0
        assert '0g protein' in result.summary_text
        assert '0g fat' in result.summary_text
        assert '0g carbs' in result.summary_text


class TestFormattedResponseModel:
    """Test FormattedResponse data model"""
    
    def test_model_creation(self):
        """Test creating FormattedResponse"""
        response = FormattedResponse(
            summary_text="Test summary",
            items=[{'category': 'meal'}],
            net_calories=500,
            suggestions="Test suggestion"
        )
        
        assert response.summary_text == "Test summary"
        assert response.net_calories == 500
        assert response.suggestions == "Test suggestion"
        assert len(response.items) == 1
    
    def test_model_without_suggestions(self):
        """Test FormattedResponse without suggestions"""
        response = FormattedResponse(
            summary_text="Test",
            items=[],
            net_calories=0
        )
        
        assert response.suggestions is None

