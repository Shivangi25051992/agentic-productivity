"""
Unit Tests for ContextService

Tests user context retrieval, caching, and realtime data fetching
"""

import pytest
from unittest.mock import Mock, MagicMock, patch
from datetime import datetime, timezone, timedelta
from app.services.context_service import ContextService, UserContext
from app.models.fitness_log import FitnessLog, FitnessLogType


class TestUserContextModel:
    """Test UserContext data model"""
    
    def test_user_context_creation(self):
        """Test creating UserContext"""
        context = UserContext(
            user_id="user123",
            fitness_goal="lose_weight",
            daily_calorie_goal=2000,
            calories_consumed_today=800,
            protein_today=50.0,
            logging_streak_days=5
        )
        
        assert context.user_id == "user123"
        assert context.fitness_goal == "lose_weight"
        assert context.daily_calorie_goal == 2000
        assert context.calories_consumed_today == 800
        assert context.protein_today == 50.0
        assert context.logging_streak_days == 5


class TestContextServiceInit:
    """Test ContextService initialization"""
    
    def test_init_with_database_service(self):
        """Test initialization with database service"""
        db = Mock()
        service = ContextService(db)
        
        assert service.db == db
        assert service._cache_ttl_seconds == 30
    
    def test_init_sets_cache_ttl(self):
        """Test that cache TTL is configurable"""
        db = Mock()
        service = ContextService(db)
        
        # Default is 30 seconds
        assert service._cache_ttl_seconds == 30


class TestGetTodayCaloriesRealtime:
    """Test get_today_calories_realtime() method"""
    
    def test_realtime_empty_logs(self):
        """Test realtime calories with no logs"""
        db = Mock()
        db.list_fitness_logs_by_user.return_value = []
        
        service = ContextService(db)
        calories, protein, meals = service.get_today_calories_realtime("user123")
        
        assert calories == 0
        assert protein == 0.0
        assert meals == 0
        
        # Verify DB was called with correct params
        db.list_fitness_logs_by_user.assert_called_once()
        call_args = db.list_fitness_logs_by_user.call_args
        assert call_args[1]['user_id'] == "user123"
        assert call_args[1]['log_type'] is None
        assert call_args[1]['limit'] == 100
    
    def test_realtime_single_meal(self):
        """Test realtime calories with single meal"""
        db = Mock()
        
        log = FitnessLog(
            user_id="user123",
            log_type=FitnessLogType.meal,
            content="1 apple",
            calories=100,
            ai_parsed_data={"protein_g": 10.0},
            timestamp=datetime.now(timezone.utc)
        )
        db.list_fitness_logs_by_user.return_value = [log]
        
        service = ContextService(db)
        calories, protein, meals = service.get_today_calories_realtime("user123")
        
        assert calories == 100
        assert protein == 10.0
        assert meals == 1
    
    def test_realtime_multiple_meals(self):
        """Test realtime calories with multiple meals"""
        db = Mock()
        
        logs = [
            FitnessLog(
                user_id="user123",
                log_type=FitnessLogType.meal,
                content="meal 1",
                calories=100,
                ai_parsed_data={"protein_g": 10.0},
                timestamp=datetime.now(timezone.utc)
            ),
            FitnessLog(
                user_id="user123",
                log_type=FitnessLogType.meal,
                content="meal 2",
                calories=200,
                ai_parsed_data={"protein_g": 15.0},
                timestamp=datetime.now(timezone.utc)
            ),
            FitnessLog(
                user_id="user123",
                log_type=FitnessLogType.meal,
                content="meal 3",
                calories=150,
                ai_parsed_data={"protein_g": 12.0},
                timestamp=datetime.now(timezone.utc)
            )
        ]
        db.list_fitness_logs_by_user.return_value = logs
        
        service = ContextService(db)
        calories, protein, meals = service.get_today_calories_realtime("user123")
        
        assert calories == 450  # 100 + 200 + 150
        assert protein == 37.0  # 10 + 15 + 12
        assert meals == 3
    
    def test_realtime_ignores_non_meals(self):
        """Test realtime calories ignores non-meal logs"""
        db = Mock()
        
        logs = [
            FitnessLog(
                user_id="user123",
                log_type=FitnessLogType.meal,
                content="meal",
                calories=100,
                ai_parsed_data={"protein_g": 10.0},
                timestamp=datetime.now(timezone.utc)
            ),
            FitnessLog(
                user_id="user123",
                log_type=FitnessLogType.workout,
                content="workout",
                calories=0,
                ai_parsed_data={},
                timestamp=datetime.now(timezone.utc)
            ),
            FitnessLog(
                user_id="user123",
                log_type=FitnessLogType.water,
                content="water",
                calories=0,
                ai_parsed_data={},
                timestamp=datetime.now(timezone.utc)
            )
        ]
        db.list_fitness_logs_by_user.return_value = logs
        
        service = ContextService(db)
        calories, protein, meals = service.get_today_calories_realtime("user123")
        
        assert calories == 100
        assert protein == 10.0
        assert meals == 1  # Only meal logs counted
    
    def test_realtime_meal_without_protein(self):
        """Test realtime calories with meal missing protein data"""
        db = Mock()
        
        log = FitnessLog(
            user_id="user123",
            log_type=FitnessLogType.meal,
            content="meal without protein",
            calories=100,
            ai_parsed_data={},  # No protein_g
            timestamp=datetime.now(timezone.utc)
        )
        db.list_fitness_logs_by_user.return_value = [log]
        
        service = ContextService(db)
        calories, protein, meals = service.get_today_calories_realtime("user123")
        
        assert calories == 100
        assert protein == 0.0  # No protein
        assert meals == 1
    
    def test_realtime_no_cache(self):
        """Test that realtime method bypasses cache"""
        db = Mock()
        db.list_fitness_logs_by_user.return_value = []
        
        service = ContextService(db)
        
        # Call twice
        service.get_today_calories_realtime("user123")
        service.get_today_calories_realtime("user123")
        
        # Should call DB both times (no cache)
        assert db.list_fitness_logs_by_user.call_count == 2


class TestGetUserContext:
    """Test get_user_context() method with caching"""
    
    @patch('app.services.context_service.time')
    def test_context_caching_within_ttl(self, mock_time):
        """Test that context is cached within TTL"""
        # Mock time to return consistent time bucket
        mock_time.time.return_value = 1000  # Will create bucket 33 (1000 / 30)
        
        db = Mock()
        db.get_user_profile.return_value = Mock(
            fitness_goal="lose_weight",
            daily_calorie_goal=2000
        )
        db.list_fitness_logs_by_user.return_value = []
        
        service = ContextService(db)
        
        # First call - should hit DB
        context1 = service.get_user_context("user123")
        
        # Second call - should use cache (same time bucket)
        context2 = service.get_user_context("user123")
        
        # DB should only be called once
        assert db.get_user_profile.call_count == 1
        
        # Contexts should be identical
        assert context1.user_id == context2.user_id
        assert context1.daily_calorie_goal == context2.daily_calorie_goal
    
    @patch('app.services.context_service.time')
    def test_context_cache_expires_after_ttl(self, mock_time):
        """Test that cache expires after TTL"""
        db = Mock()
        db.get_user_profile.return_value = Mock(
            fitness_goal="lose_weight",
            daily_calorie_goal=2000
        )
        db.list_fitness_logs_by_user.return_value = []
        
        service = ContextService(db)
        
        # First call at time bucket 33
        mock_time.time.return_value = 1000
        context1 = service.get_user_context("user123")
        
        # Second call at time bucket 34 (different bucket = expired)
        mock_time.time.return_value = 1050
        context2 = service.get_user_context("user123")
        
        # DB should be called twice (cache expired)
        assert db.get_user_profile.call_count == 2
    
    def test_context_with_profile_data(self):
        """Test context includes profile data"""
        db = Mock()
        profile = Mock(
            fitness_goal="build_muscle",
            daily_calorie_goal=2500,
            daily_water_goal=3000
        )
        db.get_user_profile.return_value = profile
        db.list_fitness_logs_by_user.return_value = []
        
        service = ContextService(db)
        context = service.get_user_context("user123")
        
        assert context.user_id == "user123"
        assert context.fitness_goal == "build_muscle"
        assert context.daily_calorie_goal == 2500
    
    def test_context_with_no_profile(self):
        """Test context when profile is missing"""
        db = Mock()
        db.get_user_profile.return_value = None
        db.list_fitness_logs_by_user.return_value = []
        
        service = ContextService(db)
        context = service.get_user_context("user123")
        
        assert context.user_id == "user123"
        assert context.fitness_goal is None
        assert context.daily_calorie_goal == 2000  # Default
    
    def test_context_calculates_today_calories(self):
        """Test context calculates today's calories"""
        db = Mock()
        db.get_user_profile.return_value = Mock(
            fitness_goal="lose_weight",
            daily_calorie_goal=2000
        )
        
        logs = [
            FitnessLog(
                user_id="user123",
                log_type=FitnessLogType.meal,
                content="breakfast",
                calories=100,
                ai_parsed_data={"protein_g": 10.0},
                timestamp=datetime.now(timezone.utc)
            ),
            FitnessLog(
                user_id="user123",
                log_type=FitnessLogType.meal,
                content="lunch",
                calories=200,
                ai_parsed_data={"protein_g": 15.0},
                timestamp=datetime.now(timezone.utc)
            )
        ]
        db.list_fitness_logs_by_user.return_value = logs
        
        service = ContextService(db)
        context = service.get_user_context("user123")
        
        assert context.calories_consumed_today == 300
        assert context.protein_today == 25.0
    
    def test_context_streak_disabled(self):
        """Test that streak calculation is disabled"""
        db = Mock()
        db.get_user_profile.return_value = Mock(
            fitness_goal="lose_weight",
            daily_calorie_goal=2000
        )
        db.list_fitness_logs_by_user.return_value = []
        
        service = ContextService(db)
        context = service.get_user_context("user123")
        
        # Streak should be 0 (disabled for performance)
        assert context.logging_streak_days == 0


class TestCacheKeyGeneration:
    """Test cache key and time bucket logic"""
    
    @patch('app.services.context_service.time')
    def test_time_bucket_calculation(self, mock_time):
        """Test time bucket calculation (30-second buckets)"""
        db = Mock()
        db.get_user_profile.return_value = Mock(
            fitness_goal="lose_weight",
            daily_calorie_goal=2000
        )
        db.list_fitness_logs_by_user.return_value = []
        
        service = ContextService(db)
        
        # Time 0-29 seconds -> bucket 0
        mock_time.time.return_value = 15
        service.get_user_context("user123")
        
        # Time 30-59 seconds -> bucket 1
        mock_time.time.return_value = 45
        service.get_user_context("user123")
        
        # Should hit DB twice (different buckets)
        assert db.get_user_profile.call_count == 2
    
    @patch('app.services.context_service.time')
    def test_same_bucket_uses_cache(self, mock_time):
        """Test calls within same 30s bucket use cache"""
        db = Mock()
        db.get_user_profile.return_value = Mock(
            fitness_goal="lose_weight",
            daily_calorie_goal=2000
        )
        db.list_fitness_logs_by_user.return_value = []
        
        service = ContextService(db)
        
        # Multiple calls within same bucket (0-30s)
        mock_time.time.return_value = 5
        service.get_user_context("user123")
        
        mock_time.time.return_value = 10
        service.get_user_context("user123")
        
        mock_time.time.return_value = 29
        service.get_user_context("user123")
        
        # Should only hit DB once
        assert db.get_user_profile.call_count == 1


# Note: recent_activity_summary tests removed as this field doesn't exist in UserContext model

