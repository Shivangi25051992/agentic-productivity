"""
Unit Tests for ChatResponseGenerator

Tests the expandable chat response generation logic including:
- Summary extraction
- Suggestion generation  
- Details structuring
- Food emoji matching
- Response formatting
"""

import pytest
from app.services.chat_response_generator import (
    ChatResponseGenerator,
    ChatResponse,
    get_chat_response_generator
)


class TestChatResponseGeneratorSingleton:
    """Test singleton pattern"""
    
    def test_singleton_instance(self):
        """Test that get_chat_response_generator returns same instance"""
        gen1 = get_chat_response_generator()
        gen2 = get_chat_response_generator()
        assert gen1 is gen2


class TestExtractSummary:
    """Test _extract_summary() method"""
    
    def setup_method(self):
        self.generator = ChatResponseGenerator()
    
    def test_summary_for_apple(self):
        """Test summary for apple"""
        items = [{
            'category': 'meal',
            'summary': '1 apple',
            'data': {'item': 'apple', 'calories': 95}
        }]
        summary = self.generator._extract_summary("Full message", items)
        assert summary == "🍎 1 apple logged! 95 kcal"
    
    def test_summary_for_banana(self):
        """Test summary for banana"""
        items = [{
            'category': 'meal',
            'summary': 'Banana, Raw (1.0 medium)',
            'data': {'item': 'banana', 'calories': 105}
        }]
        summary = self.generator._extract_summary("", items)
        assert summary == "🍌 Banana, raw (1.0 medium) logged! 105 kcal"
    
    def test_summary_strips_existing_calories(self):
        """Test that summary strips (XXXkcal) from item name"""
        items = [{
            'category': 'meal',
            'summary': '1 bowl of rice (450kcal)',
            'data': {'item': 'rice', 'calories': 200}
        }]
        summary = self.generator._extract_summary("", items)
        assert "(450kcal)" not in summary
        assert "200 kcal" in summary
    
    def test_summary_for_orange(self):
        """Test summary for orange"""
        items = [{
            'category': 'meal',
            'summary': '1 orange (62kcal)',
            'data': {'item': 'orange', 'calories': 62}
        }]
        summary = self.generator._extract_summary("", items)
        assert summary == "🍊 1 orange logged! 62 kcal"
    
    def test_summary_for_chicken(self):
        """Test summary for chicken"""
        items = [{
            'category': 'meal',
            'summary': 'chicken breast',
            'data': {'item': 'chicken', 'calories': 165}
        }]
        summary = self.generator._extract_summary("", items)
        assert summary == "🍗 Chicken breast logged! 165 kcal"
    
    def test_summary_for_eggs(self):
        """Test summary for eggs"""
        items = [{
            'category': 'meal',
            'summary': '2 eggs',
            'data': {'item': 'eggs', 'calories': 140}
        }]
        summary = self.generator._extract_summary("", items)
        assert summary == "🥚 2 eggs logged! 140 kcal"
    
    def test_summary_for_workout(self):
        """Test summary for workout"""
        items = [{
            'category': 'workout',
            'summary': 'running',
            'data': {'item': 'running', 'calories_burned': 300}
        }]
        summary = self.generator._extract_summary("", items)
        assert summary == "💪 Running logged! 300 kcal burned"
    
    def test_summary_for_water(self):
        """Test summary for water"""
        items = [{
            'category': 'water',
            'summary': '1 glass',
            'data': {'quantity_ml': 250}
        }]
        summary = self.generator._extract_summary("", items)
        assert summary == "💧 Water logged! 1 glass (250ml)"
    
    def test_summary_for_water_multiple_glasses(self):
        """Test summary for multiple glasses of water"""
        items = [{
            'category': 'water',
            'summary': '3 glasses',
            'data': {'quantity_ml': 750}
        }]
        summary = self.generator._extract_summary("", items)
        assert summary == "💧 Water logged! 3 glasses (750ml)"
    
    def test_summary_for_supplement(self):
        """Test summary for supplement"""
        items = [{
            'category': 'supplement',
            'summary': 'vitamin D',
            'data': {'supplement_name': 'vitamin D'}
        }]
        summary = self.generator._extract_summary("", items)
        assert summary == "💊 Vitamin d logged!"
    
    def test_summary_for_task(self):
        """Test summary for task"""
        items = [{
            'category': 'task',
            'summary': 'Call doctor',
            'data': {'title': 'Call doctor'}
        }]
        summary = self.generator._extract_summary("", items)
        assert summary == "📝 Task created: Call doctor"
    
    def test_summary_empty_items(self):
        """Test summary with empty items"""
        summary = self.generator._extract_summary("", [])
        assert summary == "Logged successfully!"
    
    def test_summary_category_other_with_nutrition(self):
        """Test summary for category 'other' with nutrition data"""
        items = [{
            'category': 'other',
            'summary': 'orange',
            'data': {'item': 'orange', 'calories': 62}
        }]
        summary = self.generator._extract_summary("", items)
        assert "🍊" in summary
        assert "62 kcal" in summary


class TestGetFoodEmoji:
    """Test _get_food_emoji() method"""
    
    def setup_method(self):
        self.generator = ChatResponseGenerator()
    
    def test_emoji_for_fruits(self):
        """Test emoji for various fruits"""
        assert self.generator._get_food_emoji("apple") == "🍎"
        assert self.generator._get_food_emoji("banana") == "🍌"
        assert self.generator._get_food_emoji("orange") == "🍊"
        assert self.generator._get_food_emoji("grapes") == "🍇"
        assert self.generator._get_food_emoji("strawberry") == "🍓"
        assert self.generator._get_food_emoji("watermelon") == "🍉"
    
    def test_emoji_for_proteins(self):
        """Test emoji for protein foods"""
        assert self.generator._get_food_emoji("chicken") == "🍗"
        assert self.generator._get_food_emoji("eggs") == "🥚"
        assert self.generator._get_food_emoji("fish") == "🐟"
        assert self.generator._get_food_emoji("salmon") == "🐟"
    
    def test_emoji_for_vegetables(self):
        """Test emoji for vegetables"""
        assert self.generator._get_food_emoji("salad") == "🥗"
        assert self.generator._get_food_emoji("carrot") == "🥕"
        assert self.generator._get_food_emoji("broccoli") == "🥦"
    
    def test_emoji_for_carbs(self):
        """Test emoji for carbohydrates"""
        assert self.generator._get_food_emoji("bread") == "🍞"
        assert self.generator._get_food_emoji("rice") == "🍚"
        assert self.generator._get_food_emoji("pasta") == "🍝"
        assert self.generator._get_food_emoji("pizza") == "🍕"
    
    def test_emoji_for_snacks(self):
        """Test emoji for snacks"""
        assert self.generator._get_food_emoji("cookie") == "🍪"
        assert self.generator._get_food_emoji("cake") == "🍰"
        assert self.generator._get_food_emoji("ice cream") == "🍦"
    
    def test_emoji_case_insensitive(self):
        """Test emoji matching is case insensitive"""
        assert self.generator._get_food_emoji("APPLE") == "🍎"
        assert self.generator._get_food_emoji("Banana") == "🍌"
        assert self.generator._get_food_emoji("ChIcKeN") == "🍗"
    
    def test_emoji_default_for_unknown_food(self):
        """Test default emoji for unknown food"""
        assert self.generator._get_food_emoji("unknown food") == "🍽️"
        assert self.generator._get_food_emoji("xyz123") == "🍽️"


class TestGenerateSuggestion:
    """Test _generate_suggestion() method"""
    
    def setup_method(self):
        self.generator = ChatResponseGenerator()
    
    def test_suggestion_almost_at_goal(self):
        """Test suggestion when 90%+ of daily goal"""
        items = [{'category': 'meal', 'data': {}}]
        context = {
            'daily_calorie_goal': 2000,
            'calories_consumed_today': 1850,  # 92.5%
            'protein_today': 100,
            'meals_logged_today': 3
        }
        suggestion = self.generator._generate_suggestion(items, context)
        assert "Almost at goal" in suggestion or "Stay strong" in suggestion
    
    def test_suggestion_80_percent(self):
        """Test suggestion when 80-90% of daily goal"""
        items = [{'category': 'meal', 'data': {}}]
        context = {
            'daily_calorie_goal': 2000,
            'calories_consumed_today': 1700,  # 85%
            'protein_today': 100,
            'meals_logged_today': 3
        }
        suggestion = self.generator._generate_suggestion(items, context)
        assert "remaining" in suggestion.lower()
    
    def test_suggestion_low_protein(self):
        """Test suggestion for low protein"""
        items = [{'category': 'meal', 'data': {}}]
        context = {
            'daily_calorie_goal': 2000,
            'calories_consumed_today': 800,
            'protein_today': 20,  # Low protein
            'meals_logged_today': 1
        }
        suggestion = self.generator._generate_suggestion(items, context)
        assert "protein" in suggestion.lower()
    
    def test_suggestion_for_workout(self):
        """Test suggestion for workout"""
        items = [{'category': 'workout', 'data': {}}]
        context = {
            'daily_calorie_goal': 2000,
            'calories_consumed_today': 800,
            'protein_today': 50,
            'meals_logged_today': 2
        }
        suggestion = self.generator._generate_suggestion(items, context)
        assert "work" in suggestion.lower() or "protein" in suggestion.lower() or "recovery" in suggestion.lower()
    
    def test_suggestion_for_water(self):
        """Test suggestion for water"""
        items = [{'category': 'water', 'data': {}}]
        context = {}
        suggestion = self.generator._generate_suggestion(items, context)
        assert "hydration" in suggestion.lower() or "water" in suggestion.lower()
    
    def test_suggestion_for_supplement(self):
        """Test suggestion for supplement"""
        items = [{'category': 'supplement', 'data': {}}]
        context = {}
        suggestion = self.generator._generate_suggestion(items, context)
        assert "consistent" in suggestion.lower() or "results" in suggestion.lower()
    
    def test_suggestion_empty_items(self):
        """Test suggestion with empty items"""
        suggestion = self.generator._generate_suggestion([], {})
        assert "Keep up the great work" in suggestion


class TestStructureDetails:
    """Test _structure_details() method"""
    
    def setup_method(self):
        self.generator = ChatResponseGenerator()
    
    def test_details_structure_meal(self):
        """Test details structure for meal"""
        items = [{
            'category': 'meal',
            'data': {
                'calories': 100,
                'protein_g': 20,
                'carbs_g': 10,
                'fat_g': 5
            }
        }]
        context = {
            'daily_calorie_goal': 2000,
            'calories_consumed_today': 500,
            'protein_today': 50
        }
        
        details = self.generator._structure_details(items, context)
        
        assert 'nutrition' in details
        assert 'progress' in details
        assert 'items' in details
        
        # Check nutrition
        assert details['nutrition']['calories'] == 100
        assert details['nutrition']['protein_g'] == 20
        assert details['nutrition']['carbs_g'] == 10
        assert details['nutrition']['fat_g'] == 5
        
        # Check progress (uses realtime data directly - no double counting)
        assert details['progress']['daily_calories'] == 500  # From context (realtime)
        assert details['progress']['daily_goal'] == 2000
        assert details['progress']['remaining'] == 1500
        assert details['progress']['protein_today'] == 50  # From context (realtime)
    
    def test_details_no_double_counting(self):
        """Test that details don't double-count current items"""
        items = [{
            'category': 'meal',
            'data': {
                'calories': 100,
                'protein_g': 10,
                'carbs_g': 20,
                'fat_g': 5
            }
        }]
        context = {
            'daily_calorie_goal': 2000,
            'calories_consumed_today': 900,  # Already includes current item
            'protein_today': 60
        }
        
        details = self.generator._structure_details(items, context)
        
        # Should use context values as-is (realtime data already includes current item)
        assert details['progress']['daily_calories'] == 900  # Use context directly
        assert details['progress']['protein_today'] == 60  # Use context directly
    
    def test_details_multiple_items(self):
        """Test details with multiple items"""
        items = [
            {'category': 'meal', 'data': {'calories': 100, 'protein_g': 10, 'carbs_g': 20, 'fat_g': 5}},
            {'category': 'meal', 'data': {'calories': 200, 'protein_g': 15, 'carbs_g': 30, 'fat_g': 10}}
        ]
        context = {
            'daily_calorie_goal': 2000,
            'calories_consumed_today': 500,
            'protein_today': 50
        }
        
        details = self.generator._structure_details(items, context)
        
        # Should sum all items
        assert details['nutrition']['calories'] == 300  # 100 + 200
        assert details['nutrition']['protein_g'] == 25  # 10 + 15
        assert details['nutrition']['carbs_g'] == 50  # 20 + 30
        assert details['nutrition']['fat_g'] == 15  # 5 + 10
    
    def test_details_progress_percentage(self):
        """Test progress percentage calculation"""
        items = [{'category': 'meal', 'data': {'calories': 100, 'protein_g': 10, 'carbs_g': 0, 'fat_g': 0}}]
        context = {
            'daily_calorie_goal': 2000,
            'calories_consumed_today': 900,  # 45% (realtime - already includes current item)
            'protein_today': 50
        }
        
        details = self.generator._structure_details(items, context)
        
        # 900 / 2000 = 45%
        assert details['progress']['progress_percent'] == 45.0


class TestGenerateInsights:
    """Test _generate_insights() method"""
    
    def setup_method(self):
        self.generator = ChatResponseGenerator()
    
    def test_insights_high_protein(self):
        """Test insights for high protein meal"""
        items = [{'category': 'meal', 'data': {'protein_g': 25}}]
        context = {}
        
        insight = self.generator._generate_insights(items, context)
        assert "protein" in insight.lower()
        assert "muscle" in insight.lower() or "satiety" in insight.lower()
    
    def test_insights_low_protein(self):
        """Test insights for low protein meal"""
        items = [{'category': 'meal', 'data': {'protein_g': 2}}]
        context = {}
        
        insight = self.generator._generate_insights(items, context)
        assert "protein" in insight.lower()
    
    def test_insights_medium_protein(self):
        """Test insights for medium protein meal"""
        items = [{'category': 'meal', 'data': {'protein_g': 10}}]
        context = {}
        
        insight = self.generator._generate_insights(items, context)
        assert "balance" in insight.lower() or "energy" in insight.lower()
    
    def test_insights_for_workout(self):
        """Test insights for workout"""
        items = [{'category': 'workout', 'data': {}}]
        context = {}
        
        insight = self.generator._generate_insights(items, context)
        assert "exercise" in insight.lower() or "health" in insight.lower()
    
    def test_insights_empty(self):
        """Test insights with empty items"""
        insight = self.generator._generate_insights([], {})
        assert insight == ""


class TestGenerateResponse:
    """Test generate_response() main method"""
    
    def setup_method(self):
        self.generator = ChatResponseGenerator()
    
    def test_response_for_meal(self):
        """Test complete response for meal"""
        items = [{
            'category': 'meal',
            'summary': '1 apple',
            'data': {
                'item': 'apple',
                'calories': 95,
                'protein_g': 0.5,
                'carbs_g': 25,
                'fat_g': 0.3
            }
        }]
        context = {
            'fitness_goal': 'lose_weight',
            'daily_calorie_goal': 2000,
            'calories_consumed_today': 500,
            'protein_today': 20,
            'meals_logged_today': 2
        }
        
        response = self.generator.generate_response(items, context)
        
        # Check response structure
        assert isinstance(response, ChatResponse)
        assert response.category == 'meal'
        assert response.expandable is True
        
        # Check expandable fields
        assert response.summary is not None
        assert "apple" in response.summary.lower()
        assert "95 kcal" in response.summary
        
        assert response.suggestion is not None
        assert len(response.suggestion) > 0
        
        assert response.details is not None
        assert 'nutrition' in response.details
        assert 'progress' in response.details
    
    def test_response_without_items(self):
        """Test response with no items"""
        response = self.generator.generate_response([], {})
        
        assert response.expandable is False
        assert response.summary is None
        assert response.suggestion is None
        assert response.details is None
    
    def test_response_metadata(self):
        """Test response metadata"""
        items = [
            {'category': 'meal', 'data': {}},
            {'category': 'workout', 'data': {}}
        ]
        
        response = self.generator.generate_response(items, {})
        
        assert response.metadata is not None
        assert 'categories' in response.metadata
        assert 'meal' in response.metadata['categories']

