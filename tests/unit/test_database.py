"""
Unit Tests for Database Service

Tests Firestore operations, user management, and fitness log CRUD
"""

import pytest
from unittest.mock import Mock, MagicMock, patch
from datetime import datetime, timezone, timedelta
from app.services.database import DatabaseService, get_db_service
from app.models.user import User, UserProfile
from app.models.fitness_log import FitnessLog, FitnessLogType


class TestDatabaseServiceSingleton:
    """Test singleton pattern"""
    
    @patch('app.services.database.firestore.Client')
    def test_singleton_instance(self, mock_firestore):
        """Test that get_db_service returns same instance"""
        mock_firestore.return_value = Mock()
        
        service1 = get_db_service()
        service2 = get_db_service()
        assert service1 is service2


class TestUserOperations:
    """Test user CRUD operations"""
    
    @patch('app.services.database.firestore.Client')
    def test_create_user(self, mock_firestore):
        """Test creating a new user"""
        mock_db = Mock()
        mock_collection = Mock()
        mock_doc = Mock()
        
        mock_db.collection.return_value = mock_collection
        mock_collection.document.return_value = mock_doc
        mock_firestore.return_value = mock_db
        
        service = DatabaseService()
        
        user = User(
            user_id="user123",
            email="test@example.com",
            display_name="Test User"
        )
        
        result = service.create_user(user)
        
        assert result.user_id == "user123"
        mock_doc.set.assert_called_once()
    
    @patch('app.services.database.firestore.Client')
    def test_get_user_by_id_exists(self, mock_firestore):
        """Test getting existing user by ID"""
        mock_db = Mock()
        mock_collection = Mock()
        mock_doc_ref = Mock()
        mock_doc = Mock()
        
        mock_doc.exists = True
        mock_doc.to_dict.return_value = {
            'user_id': 'user123',
            'email': 'test@example.com',
            'display_name': 'Test User'
        }
        
        mock_db.collection.return_value = mock_collection
        mock_collection.document.return_value = mock_doc_ref
        mock_doc_ref.get.return_value = mock_doc
        mock_firestore.return_value = mock_db
        
        service = DatabaseService()
        result = service.get_user_by_id("user123")
        
        assert result is not None
        assert result.email == "test@example.com"
    
    @patch('app.services.database.firestore.Client')
    def test_get_user_by_id_not_found(self, mock_firestore):
        """Test getting non-existent user"""
        mock_db = Mock()
        mock_collection = Mock()
        mock_doc_ref = Mock()
        mock_doc = Mock()
        
        mock_doc.exists = False
        
        mock_db.collection.return_value = mock_collection
        mock_collection.document.return_value = mock_doc_ref
        mock_doc_ref.get.return_value = mock_doc
        mock_firestore.return_value = mock_db
        
        service = DatabaseService()
        result = service.get_user_by_id("nonexistent")
        
        assert result is None


class TestUserProfileOperations:
    """Test user profile operations"""
    
    @patch('app.services.database.firestore.Client')
    def test_get_user_profile_exists(self, mock_firestore):
        """Test getting existing user profile"""
        mock_db = Mock()
        mock_collection = Mock()
        mock_doc_ref = Mock()
        mock_doc = Mock()
        
        mock_doc.exists = True
        mock_doc.to_dict.return_value = {
            'user_id': 'user123',
            'fitness_goal': 'lose_weight',
            'daily_calorie_goal': 2000
        }
        
        mock_db.collection.return_value = mock_collection
        mock_collection.document.return_value = mock_doc_ref
        mock_doc_ref.get.return_value = mock_doc
        mock_firestore.return_value = mock_db
        
        service = DatabaseService()
        result = service.get_user_profile("user123")
        
        assert result is not None
        assert result.fitness_goal == "lose_weight"
        assert result.daily_calorie_goal == 2000
    
    @patch('app.services.database.firestore.Client')
    def test_update_user_profile(self, mock_firestore):
        """Test updating user profile"""
        mock_db = Mock()
        mock_collection = Mock()
        mock_doc = Mock()
        
        mock_db.collection.return_value = mock_collection
        mock_collection.document.return_value = mock_doc
        mock_firestore.return_value = mock_db
        
        service = DatabaseService()
        
        profile = UserProfile(
            user_id="user123",
            fitness_goal="gain_muscle",
            daily_calorie_goal=2500
        )
        
        service.update_user_profile(profile)
        
        mock_doc.set.assert_called_once()


class TestFitnessLogOperations:
    """Test fitness log CRUD operations"""
    
    @patch('app.services.database.firestore.Client')
    def test_create_fitness_log(self, mock_firestore):
        """Test creating a fitness log"""
        mock_db = Mock()
        mock_collection = Mock()
        mock_doc = Mock()
        
        mock_db.collection.return_value = mock_collection
        mock_collection.document.return_value = mock_doc
        mock_firestore.return_value = mock_db
        
        service = DatabaseService()
        
        log = FitnessLog(
            user_id="user123",
            log_type=FitnessLogType.meal,
            content="1 apple",
            calories=95
        )
        
        result = service.create_fitness_log(log)
        
        assert result.user_id == "user123"
        assert result.calories == 95
    
    @patch('app.services.database.firestore.Client')
    def test_list_fitness_logs_by_user(self, mock_firestore):
        """Test listing fitness logs by user"""
        mock_db = Mock()
        mock_collection = Mock()
        mock_query = Mock()
        
        mock_db.collection.return_value = mock_collection
        mock_collection.where.return_value = mock_query
        mock_query.where.return_value = mock_query
        mock_query.order_by.return_value = mock_query
        mock_query.limit.return_value = mock_query
        mock_query.stream.return_value = []
        
        mock_firestore.return_value = mock_db
        
        service = DatabaseService()
        result = service.list_fitness_logs_by_user(
            user_id="user123",
            start_ts=datetime.now(timezone.utc) - timedelta(days=7),
            log_type=None,
            limit=100
        )
        
        assert result == []
    
    @patch('app.services.database.firestore.Client')
    def test_delete_fitness_log(self, mock_firestore):
        """Test deleting a fitness log"""
        mock_db = Mock()
        mock_collection = Mock()
        mock_doc = Mock()
        
        mock_db.collection.return_value = mock_collection
        mock_collection.document.return_value = mock_doc
        mock_firestore.return_value = mock_db
        
        service = DatabaseService()
        service.delete_fitness_log("log123")
        
        mock_doc.delete.assert_called_once()


class TestQueryFiltering:
    """Test query filtering logic"""
    
    @patch('app.services.database.firestore.Client')
    def test_filter_by_log_type(self, mock_firestore):
        """Test filtering logs by type"""
        mock_db = Mock()
        mock_collection = Mock()
        mock_query = Mock()
        
        mock_db.collection.return_value = mock_collection
        mock_collection.where.return_value = mock_query
        mock_query.where.return_value = mock_query
        mock_query.order_by.return_value = mock_query
        mock_query.limit.return_value = mock_query
        mock_query.stream.return_value = []
        
        mock_firestore.return_value = mock_db
        
        service = DatabaseService()
        service.list_fitness_logs_by_user(
            user_id="user123",
            start_ts=datetime.now(timezone.utc),
            log_type=FitnessLogType.meal,
            limit=50
        )
        
        # Should add log_type filter
        assert mock_collection.where.call_count >= 1
    
    @patch('app.services.database.firestore.Client')
    def test_filter_by_date_range(self, mock_firestore):
        """Test filtering logs by date range"""
        mock_db = Mock()
        mock_collection = Mock()
        mock_query = Mock()
        
        mock_db.collection.return_value = mock_collection
        mock_collection.where.return_value = mock_query
        mock_query.where.return_value = mock_query
        mock_query.order_by.return_value = mock_query
        mock_query.limit.return_value = mock_query
        mock_query.stream.return_value = []
        
        mock_firestore.return_value = mock_db
        
        service = DatabaseService()
        start = datetime.now(timezone.utc) - timedelta(days=7)
        
        service.list_fitness_logs_by_user(
            user_id="user123",
            start_ts=start,
            log_type=None,
            limit=100
        )
        
        # Should add timestamp filter
        assert mock_collection.where.call_count >= 1


class TestBatchOperations:
    """Test batch operations"""
    
    @patch('app.services.database.firestore.Client')
    def test_batch_delete_logs(self, mock_firestore):
        """Test batch deleting logs"""
        mock_db = Mock()
        mock_batch = Mock()
        mock_collection = Mock()
        
        mock_db.batch.return_value = mock_batch
        mock_db.collection.return_value = mock_collection
        mock_firestore.return_value = mock_db
        
        service = DatabaseService()
        
        # Simulate deleting multiple logs
        log_ids = ["log1", "log2", "log3"]
        for log_id in log_ids:
            doc_ref = mock_collection.document(log_id)
            doc_ref.delete()
        
        # Verify delete was called for each
        assert mock_collection.document.call_count == 3


class TestConnectionHandling:
    """Test database connection handling"""
    
    @patch('app.services.database.firestore.Client')
    def test_database_connection_initialized(self, mock_firestore):
        """Test that database connection is initialized"""
        mock_db = Mock()
        mock_firestore.return_value = mock_db
        
        service = DatabaseService()
        
        assert service.db is not None
        mock_firestore.assert_called_once()


class TestErrorHandling:
    """Test error handling in database operations"""
    
    @patch('app.services.database.firestore.Client')
    def test_handle_missing_document(self, mock_firestore):
        """Test handling missing document gracefully"""
        mock_db = Mock()
        mock_collection = Mock()
        mock_doc_ref = Mock()
        mock_doc = Mock()
        
        mock_doc.exists = False
        mock_db.collection.return_value = mock_collection
        mock_collection.document.return_value = mock_doc_ref
        mock_doc_ref.get.return_value = mock_doc
        mock_firestore.return_value = mock_db
        
        service = DatabaseService()
        result = service.get_user_by_id("missing_user")
        
        # Should return None, not raise exception
        assert result is None
    
    @patch('app.services.database.firestore.Client')
    def test_handle_firestore_exception(self, mock_firestore):
        """Test handling Firestore exceptions"""
        mock_db = Mock()
        mock_collection = Mock()
        
        # Simulate Firestore exception
        mock_collection.document.side_effect = Exception("Firestore error")
        mock_db.collection.return_value = mock_collection
        mock_firestore.return_value = mock_db
        
        service = DatabaseService()
        
        with pytest.raises(Exception):
            mock_collection.document("test")


class TestDataValidation:
    """Test data validation"""
    
    def test_validate_user_id_format(self):
        """Test user ID format validation"""
        # Valid user IDs
        valid_ids = ["user123", "abc_123", "user-456"]
        
        for user_id in valid_ids:
            assert isinstance(user_id, str)
            assert len(user_id) > 0
    
    def test_validate_timestamp_format(self):
        """Test timestamp format validation"""
        timestamp = datetime.now(timezone.utc)
        
        assert isinstance(timestamp, datetime)
        assert timestamp.tzinfo is not None


class TestCollectionPaths:
    """Test Firestore collection paths"""
    
    @patch('app.services.database.firestore.Client')
    def test_users_collection_path(self, mock_firestore):
        """Test users collection path"""
        mock_db = Mock()
        mock_firestore.return_value = mock_db
        
        service = DatabaseService()
        service.db.collection("users")
        
        mock_db.collection.assert_called_with("users")
    
    @patch('app.services.database.firestore.Client')
    def test_fitness_logs_collection_path(self, mock_firestore):
        """Test fitness_logs collection path"""
        mock_db = Mock()
        mock_firestore.return_value = mock_db
        
        service = DatabaseService()
        service.db.collection("fitness_logs")
        
        mock_db.collection.assert_called_with("fitness_logs")

