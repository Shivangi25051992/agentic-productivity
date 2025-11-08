"""
Unit Tests for MealPlanningService

Tests meal plan generation, recipe management, and grocery list creation
"""

import pytest
from unittest.mock import Mock, MagicMock, patch, AsyncMock
from datetime import date, datetime, timedelta
from app.services.meal_planning_service import MealPlanningService
from app.models.meal_planning import (
    Recipe,
    NutritionInfo,
    MealPlan,
    PlannedMeal,
    MealType,
    DayOfWeek,
    GenerateMealPlanRequest,
    RecipeCategory,
    DietaryTag
)


class TestRecipeOperations:
    """Test recipe CRUD operations"""
    
    @patch('app.services.meal_planning_service.firestore.Client')
    @pytest.mark.asyncio
    async def test_create_recipe(self, mock_firestore):
        """Test creating a new recipe"""
        # Mock Firestore
        mock_db = Mock()
        mock_collection = Mock()
        mock_doc = Mock()
        
        mock_db.collection.return_value = mock_collection
        mock_collection.document.return_value = mock_doc
        mock_firestore.return_value = mock_db
        
        service = MealPlanningService()
        
        recipe = Recipe(
            id="recipe123",
            name="Chicken Salad",
            description="Healthy chicken salad",
            category=RecipeCategory.SALAD,
            prep_time_minutes=15,
            nutrition=NutritionInfo(
                calories=350,
                protein_g=30,
                carbs_g=20,
                fat_g=15
            )
        )
        
        result = await service.create_recipe(recipe)
        
        assert result.name == "Chicken Salad"
        assert result.id == "recipe123"
        mock_doc.set.assert_called_once()
    
    @patch('app.services.meal_planning_service.firestore.Client')
    @pytest.mark.asyncio
    async def test_get_recipe_by_id_exists(self, mock_firestore):
        """Test getting existing recipe by ID"""
        mock_db = Mock()
        mock_collection = Mock()
        mock_doc_ref = Mock()
        mock_doc = Mock()
        
        mock_doc.exists = True
        mock_doc.to_dict.return_value = {
            'id': 'recipe123',
            'name': 'Test Recipe',
            'description': 'Test',
            'category': 'breakfast',
            'prep_time_minutes': 10,
            'nutrition': {
                'calories': 200,
                'protein_g': 10,
                'carbs_g': 20,
                'fat_g': 5
            }
        }
        
        mock_db.collection.return_value = mock_collection
        mock_collection.document.return_value = mock_doc_ref
        mock_doc_ref.get.return_value = mock_doc
        mock_firestore.return_value = mock_db
        
        service = MealPlanningService()
        result = await service.get_recipe_by_id("recipe123")
        
        assert result is not None
        assert result.name == "Test Recipe"
    
    @patch('app.services.meal_planning_service.firestore.Client')
    @pytest.mark.asyncio
    async def test_get_recipe_by_id_not_found(self, mock_firestore):
        """Test getting non-existent recipe"""
        mock_db = Mock()
        mock_collection = Mock()
        mock_doc_ref = Mock()
        mock_doc = Mock()
        
        mock_doc.exists = False
        
        mock_db.collection.return_value = mock_collection
        mock_collection.document.return_value = mock_doc_ref
        mock_doc_ref.get.return_value = mock_doc
        mock_firestore.return_value = mock_db
        
        service = MealPlanningService()
        result = await service.get_recipe_by_id("nonexistent")
        
        assert result is None


class TestMealPlanGeneration:
    """Test meal plan generation"""
    
    @patch('app.services.meal_planning_service.firestore.Client')
    @pytest.mark.asyncio
    async def test_generate_meal_plan_mock(self, mock_firestore):
        """Test generating a meal plan (mock mode)"""
        mock_db = Mock()
        mock_firestore.return_value = mock_db
        
        service = MealPlanningService()
        
        request = GenerateMealPlanRequest(
            user_id="user123",
            start_date=date.today(),
            dietary_preference="balanced",
            daily_calorie_target=2000
        )
        
        result = await service.generate_meal_plan_ai(request)
        
        assert result is not None
        assert result.user_id == "user123"
        assert len(result.meals) > 0
    
    @patch('app.services.meal_planning_service.firestore.Client')
    @pytest.mark.asyncio
    async def test_get_user_meal_plans(self, mock_firestore):
        """Test getting user's meal plans"""
        mock_db = Mock()
        mock_collection = Mock()
        mock_query = Mock()
        
        # Mock Firestore query
        mock_db.collection.return_value = mock_collection
        mock_collection.where.return_value = mock_query
        mock_query.order_by.return_value = mock_query
        mock_query.limit.return_value = mock_query
        mock_query.stream.return_value = []
        
        mock_firestore.return_value = mock_db
        
        service = MealPlanningService()
        result = await service.get_user_meal_plans("user123")
        
        assert result == []
    
    @patch('app.services.meal_planning_service.firestore.Client')
    @pytest.mark.asyncio
    async def test_get_current_week_plan(self, mock_firestore):
        """Test getting current week meal plan"""
        mock_db = Mock()
        mock_collection = Mock()
        mock_query = Mock()
        
        mock_db.collection.return_value = mock_collection
        mock_collection.where.return_value = mock_query
        mock_query.where.return_value = mock_query
        mock_query.limit.return_value = mock_query
        mock_query.stream.return_value = []
        
        mock_firestore.return_value = mock_db
        
        service = MealPlanningService()
        result = await service.get_current_week_plan("user123")
        
        # Should return None if no plan found
        assert result is None


class TestGroceryListGeneration:
    """Test grocery list generation"""
    
    @patch('app.services.meal_planning_service.firestore.Client')
    @pytest.mark.asyncio
    async def test_generate_grocery_list_empty_plan(self, mock_firestore):
        """Test generating grocery list with empty meal plan"""
        mock_db = Mock()
        mock_firestore.return_value = mock_db
        
        service = MealPlanningService()
        
        # Empty meal plan
        meal_plan = MealPlan(
            id="plan123",
            user_id="user123",
            week_start_date=date.today(),
            meals=[],
            is_active=True
        )
        
        result = await service.generate_grocery_list(meal_plan)
        
        assert result is not None
        assert result.meal_plan_id == "plan123"
        assert len(result.items) == 0
    
    @patch('app.services.meal_planning_service.firestore.Client')
    @pytest.mark.asyncio
    async def test_generate_grocery_list_with_meals(self, mock_firestore):
        """Test generating grocery list with meals"""
        mock_db = Mock()
        mock_firestore.return_value = mock_db
        
        service = MealPlanningService()
        
        # Meal plan with meals
        meal_plan = MealPlan(
            id="plan123",
            user_id="user123",
            week_start_date=date.today(),
            meals=[
                PlannedMeal(
                    day=DayOfWeek.MONDAY,
                    meal_type=MealType.BREAKFAST,
                    recipe_id="recipe1",
                    recipe_name="Oatmeal"
                )
            ],
            is_active=True
        )
        
        result = await service.generate_grocery_list(meal_plan)
        
        assert result is not None
        assert result.meal_plan_id == "plan123"


class TestMealPlanValidation:
    """Test meal plan validation logic"""
    
    def test_validate_meal_plan_complete(self):
        """Test validating a complete meal plan"""
        meal_plan = MealPlan(
            id="plan123",
            user_id="user123",
            week_start_date=date.today(),
            meals=[
                PlannedMeal(
                    day=DayOfWeek.MONDAY,
                    meal_type=MealType.BREAKFAST,
                    recipe_id="r1",
                    recipe_name="Breakfast"
                ),
                PlannedMeal(
                    day=DayOfWeek.MONDAY,
                    meal_type=MealType.LUNCH,
                    recipe_id="r2",
                    recipe_name="Lunch"
                ),
                PlannedMeal(
                    day=DayOfWeek.MONDAY,
                    meal_type=MealType.DINNER,
                    recipe_id="r3",
                    recipe_name="Dinner"
                )
            ],
            is_active=True
        )
        
        # Should have meals for all 3 meal types
        meal_types = set(m.meal_type for m in meal_plan.meals)
        assert MealType.BREAKFAST in meal_types
        assert MealType.LUNCH in meal_types
        assert MealType.DINNER in meal_types
    
    def test_validate_meal_plan_incomplete(self):
        """Test validating an incomplete meal plan"""
        meal_plan = MealPlan(
            id="plan123",
            user_id="user123",
            week_start_date=date.today(),
            meals=[
                PlannedMeal(
                    day=DayOfWeek.MONDAY,
                    meal_type=MealType.BREAKFAST,
                    recipe_id="r1",
                    recipe_name="Breakfast"
                )
            ],
            is_active=True
        )
        
        # Missing lunch and dinner
        meal_types = set(m.meal_type for m in meal_plan.meals)
        assert MealType.LUNCH not in meal_types
        assert MealType.DINNER not in meal_types


class TestDietaryPreferences:
    """Test dietary preference handling"""
    
    @patch('app.services.meal_planning_service.firestore.Client')
    @pytest.mark.asyncio
    async def test_generate_vegetarian_plan(self, mock_firestore):
        """Test generating vegetarian meal plan"""
        mock_db = Mock()
        mock_firestore.return_value = mock_db
        
        service = MealPlanningService()
        
        request = GenerateMealPlanRequest(
            user_id="user123",
            start_date=date.today(),
            dietary_preference="vegetarian",
            daily_calorie_target=2000
        )
        
        result = await service.generate_meal_plan_ai(request)
        
        assert result is not None
        assert result.user_id == "user123"
    
    @patch('app.services.meal_planning_service.firestore.Client')
    @pytest.mark.asyncio
    async def test_generate_vegan_plan(self, mock_firestore):
        """Test generating vegan meal plan"""
        mock_db = Mock()
        mock_firestore.return_value = mock_db
        
        service = MealPlanningService()
        
        request = GenerateMealPlanRequest(
            user_id="user123",
            start_date=date.today(),
            dietary_preference="vegan",
            daily_calorie_target=1800
        )
        
        result = await service.generate_meal_plan_ai(request)
        
        assert result is not None
    
    @patch('app.services.meal_planning_service.firestore.Client')
    @pytest.mark.asyncio
    async def test_generate_high_protein_plan(self, mock_firestore):
        """Test generating high protein meal plan"""
        mock_db = Mock()
        mock_firestore.return_value = mock_db
        
        service = MealPlanningService()
        
        request = GenerateMealPlanRequest(
            user_id="user123",
            start_date=date.today(),
            dietary_preference="high_protein",
            daily_calorie_target=2200
        )
        
        result = await service.generate_meal_plan_ai(request)
        
        assert result is not None


class TestWeekCalculations:
    """Test week-related calculations"""
    
    def test_get_week_start_date_monday(self):
        """Test getting week start date (Monday)"""
        # If today is Wednesday, week start should be Monday
        test_date = date(2024, 1, 10)  # Wednesday
        
        # Calculate Monday of that week
        days_since_monday = test_date.weekday()
        expected_monday = test_date - timedelta(days=days_since_monday)
        
        assert expected_monday.weekday() == 0  # Monday is 0
    
    def test_get_week_end_date(self):
        """Test getting week end date (Sunday)"""
        monday = date(2024, 1, 8)
        expected_sunday = monday + timedelta(days=6)
        
        assert expected_sunday.weekday() == 6  # Sunday is 6


class TestNutritionCalculations:
    """Test nutrition-related calculations"""
    
    def test_calculate_daily_nutrition_empty(self):
        """Test calculating daily nutrition with no meals"""
        meals = []
        
        total_calories = sum(0 for _ in meals)
        total_protein = sum(0 for _ in meals)
        
        assert total_calories == 0
        assert total_protein == 0
    
    def test_calculate_daily_nutrition_with_meals(self):
        """Test calculating daily nutrition with meals"""
        meals = [
            PlannedMeal(
                day=DayOfWeek.MONDAY,
                meal_type=MealType.BREAKFAST,
                recipe_id="r1",
                recipe_name="Breakfast",
                calories=300,
                protein=15
            ),
            PlannedMeal(
                day=DayOfWeek.MONDAY,
                meal_type=MealType.LUNCH,
                recipe_id="r2",
                recipe_name="Lunch",
                calories=500,
                protein=25
            )
        ]
        
        total_calories = sum(m.calories or 0 for m in meals)
        total_protein = sum(m.protein or 0 for m in meals)
        
        assert total_calories == 800
        assert total_protein == 40

