"""
Unit Tests for FoodMacroService

Tests CRUD operations, fuzzy matching, portion parsing, and caching
"""

import pytest
from unittest.mock import Mock, MagicMock, patch, AsyncMock
from datetime import datetime
from app.services.food_macro_service import FoodMacroService, get_food_macro_service
from app.models.food_macro import (
    FoodMacro,
    FoodMacroCreate,
    FoodMacroUpdate,
    MacroNutrients,
    FoodMatchResult,
    PortionParseResult
)


class TestFoodMacroServiceSingleton:
    """Test singleton pattern"""
    
    @patch('app.services.food_macro_service.get_firestore_client')
    def test_singleton_instance(self, mock_firestore):
        """Test that get_food_macro_service returns same instance"""
        mock_firestore.return_value = Mock()
        
        service1 = get_food_macro_service()
        service2 = get_food_macro_service()
        assert service1 is service2


class TestInputNormalization:
    """Test normalize_input() method"""
    
    @patch('app.services.food_macro_service.get_firestore_client')
    def setup_method(self, mock_firestore):
        mock_firestore.return_value = Mock()
        self.service = FoodMacroService()
    
    def test_normalize_quantity_and_food(self):
        """Test normalizing '2 eggs'"""
        result = self.service.normalize_input("2 eggs")
        
        assert result['quantity'] == 2.0
        assert result['unit'] is None
        assert result['food'] == 'eggs'
        assert result['prep'] is None
    
    def test_normalize_with_unit_grams(self):
        """Test normalizing '100g chicken breast'"""
        result = self.service.normalize_input("100g chicken breast")
        
        assert result['quantity'] == 100.0
        assert result['unit'] == 'g'
        assert 'chicken breast' in result['food']
    
    def test_normalize_with_preparation(self):
        """Test normalizing 'fried eggs'"""
        result = self.service.normalize_input("fried eggs")
        
        assert result['quantity'] is None
        assert result['prep'] == 'fried'
        assert 'eggs' in result['food']
    
    def test_normalize_decimal_quantity(self):
        """Test normalizing '1.5 cups rice'"""
        result = self.service.normalize_input("1.5 cups rice")
        
        assert result['quantity'] == 1.5
        assert result['unit'] == 'cups'
        assert result['food'] == 'rice'
    
    def test_normalize_multiple_prep_keywords(self):
        """Test extracting first prep keyword"""
        result = self.service.normalize_input("grilled baked chicken")
        
        # Should find first keyword
        assert result['prep'] in ['grilled', 'baked']
    
    def test_normalize_case_insensitive(self):
        """Test case insensitivity"""
        result = self.service.normalize_input("2 EGGS")
        
        assert result['food'] == '2 eggs'
    
    def test_normalize_units_oz(self):
        """Test ounces unit"""
        result = self.service.normalize_input("4oz salmon")
        
        assert result['quantity'] == 4.0
        assert result['unit'] == 'oz'
        assert 'salmon' in result['food']
    
    def test_normalize_units_lb(self):
        """Test pounds unit"""
        result = self.service.normalize_input("1.5 lbs ground beef")
        
        assert result['quantity'] == 1.5
        assert result['unit'] == 'lbs'
        assert 'ground beef' in result['food']


class TestUnitConversion:
    """Test _convert_units() method"""
    
    @patch('app.services.food_macro_service.get_firestore_client')
    def setup_method(self, mock_firestore):
        mock_firestore.return_value = Mock()
        self.service = FoodMacroService()
    
    def test_convert_same_unit(self):
        """Test no conversion when units are the same"""
        result = self.service._convert_units(100, 'g', 'g')
        assert result == 100.0
    
    def test_convert_g_to_100g(self):
        """Test converting grams to 100g units"""
        result = self.service._convert_units(100, 'g', '100g')
        assert result == 1.0  # 100g input = 1 unit of "100g"
        
        result = self.service._convert_units(200, 'g', '100g')
        assert result == 2.0
    
    def test_convert_kg_to_100g(self):
        """Test converting kg to 100g"""
        result = self.service._convert_units(1, 'kg', '100g')
        assert result == 10.0  # 1kg = 10 units of 100g
    
    def test_convert_oz_to_100g(self):
        """Test converting ounces to 100g"""
        result = self.service._convert_units(1, 'oz', '100g')
        assert abs(result - 0.2835) < 0.01  # 1oz ≈ 28.35g ≈ 0.2835 units of 100g
    
    def test_convert_kg_to_g(self):
        """Test converting kg to g"""
        result = self.service._convert_units(1, 'kg', 'g')
        assert result == 1000.0
    
    def test_convert_lb_to_g(self):
        """Test converting pounds to grams"""
        result = self.service._convert_units(1, 'lb', 'g')
        assert abs(result - 453.59) < 0.1
    
    def test_convert_pieces_no_conversion(self):
        """Test pieces don't convert"""
        result = self.service._convert_units(2, 'piece', 'piece')
        assert result == 2.0


class TestPortionParsing:
    """Test parse_portion() method"""
    
    @patch('app.services.food_macro_service.get_firestore_client')
    def setup_method(self, mock_firestore):
        # Mock Firestore
        mock_db = Mock()
        mock_collection = Mock()
        mock_doc = Mock()
        mock_doc.update = Mock()
        
        mock_collection.document.return_value = mock_doc
        mock_db.collection.return_value = mock_collection
        mock_firestore.return_value = mock_db
        
        self.service = FoodMacroService()
    
    def test_parse_portion_default_quantity(self):
        """Test parsing '1 egg' (default quantity)"""
        food = FoodMacro(
            food_id="egg123",
            standardized_name="egg",
            aliases=[],
            category="protein",
            unit_type="piece",
            default_portion=1.0,
            macros_per_unit=MacroNutrients(
                calories=70,
                protein_g=6,
                carbs_g=0.5,
                fat_g=5,
                fiber_g=0,
                sugar_g=0,
                sodium_mg=70
            ),
            source="usda",
            source_id="egg_usda",
            entry_origin="manual",
            verification_flag=True,
            confidence_score=1.0,
            access_count=0,
            created_by="admin",
            created_at=datetime.now(),
            updated_at=datetime.now()
        )
        
        result = self.service.parse_portion("egg", food)
        
        assert result.quantity == 1.0  # Default to 1 (not default_portion)
        assert result.macros.calories == 70
        assert result.macros.protein_g == 6
    
    def test_parse_portion_with_quantity(self):
        """Test parsing '2 eggs'"""
        food = FoodMacro(
            food_id="egg123",
            standardized_name="egg",
            aliases=[],
            category="protein",
            unit_type="piece",
            default_portion=1.0,
            macros_per_unit=MacroNutrients(
                calories=70,
                protein_g=6,
                carbs_g=0.5,
                fat_g=5,
                fiber_g=0,
                sugar_g=0,
                sodium_mg=70
            ),
            source="usda",
            source_id="egg_usda",
            entry_origin="manual",
            verification_flag=True,
            confidence_score=1.0,
            access_count=0,
            created_by="admin",
            created_at=datetime.now(),
            updated_at=datetime.now()
        )
        
        result = self.service.parse_portion("2 eggs", food)
        
        assert result.quantity == 2.0
        assert result.macros.calories == 140  # 70 * 2
        assert result.macros.protein_g == 12  # 6 * 2
    
    def test_parse_portion_with_unit_conversion(self):
        """Test parsing '100g chicken' when DB uses '100g' units"""
        food = FoodMacro(
            food_id="chicken123",
            standardized_name="chicken breast",
            aliases=[],
            category="protein",
            unit_type="100g",
            default_portion=1.0,
            macros_per_unit=MacroNutrients(
                calories=165,
                protein_g=31,
                carbs_g=0,
                fat_g=3.6,
                fiber_g=0,
                sugar_g=0,
                sodium_mg=74
            ),
            source="usda",
            source_id="chicken_usda",
            entry_origin="manual",
            verification_flag=True,
            confidence_score=1.0,
            access_count=0,
            created_by="admin",
            created_at=datetime.now(),
            updated_at=datetime.now()
        )
        
        result = self.service.parse_portion("100g chicken breast", food)
        
        # 100g input = 1 unit of "100g" in DB
        assert result.quantity == 100.0
        assert result.unit == 'g'
        assert result.macros.calories == 165
        assert result.macros.protein_g == 31
    
    def test_parse_portion_fractional(self):
        """Test parsing '1.5 servings'"""
        food = FoodMacro(
            food_id="rice123",
            standardized_name="rice",
            aliases=[],
            category="carbs",
            unit_type="serving",
            default_portion=1.0,
            macros_per_unit=MacroNutrients(
                calories=200,
                protein_g=4,
                carbs_g=45,
                fat_g=0.5,
                fiber_g=1,
                sugar_g=0,
                sodium_mg=0
            ),
            source="usda",
            source_id="rice_usda",
            entry_origin="manual",
            verification_flag=True,
            confidence_score=1.0,
            access_count=0,
            created_by="admin",
            created_at=datetime.now(),
            updated_at=datetime.now()
        )
        
        result = self.service.parse_portion("1.5 servings rice", food)
        
        assert result.quantity == 1.5
        assert result.macros.calories == 300  # 200 * 1.5
        assert result.macros.carbs_g == 67.5  # 45 * 1.5


class TestCacheManagement:
    """Test _load_cache() method"""
    
    @patch('app.services.food_macro_service.time')
    @patch('app.services.food_macro_service.get_firestore_client')
    def test_cache_loads_from_firestore(self, mock_firestore, mock_time):
        """Test cache loads data from Firestore"""
        # Mock Firestore docs
        mock_doc = Mock()
        mock_doc.id = "egg123"
        mock_doc.to_dict.return_value = {
            'standardized_name': 'egg',
            'aliases': ['eggs', 'hen egg'],
            'category': 'protein',
            'unit_type': 'piece',
            'default_portion': 1.0,
            'macros_per_unit': {
                'calories': 70,
                'protein_g': 6,
                'carbs_g': 0.5,
                'fat_g': 5,
                'fiber_g': 0,
                'sugar_g': 0,
                'sodium_mg': 70
            },
            'source': 'usda',
            'source_id': 'egg_usda',
            'entry_origin': 'manual',
            'verification_flag': True,
            'confidence_score': 1.0,
            'access_count': 0,
            'created_by': 'admin',
            'created_at': datetime.now(),
            'updated_at': datetime.now()
        }
        
        mock_query = Mock()
        mock_query.get.return_value = [mock_doc]
        mock_query.limit.return_value = mock_query
        
        mock_collection = Mock()
        mock_collection.limit.return_value = mock_query
        
        mock_db = Mock()
        mock_db.collection.return_value = mock_collection
        mock_firestore.return_value = mock_db
        
        mock_time.time.return_value = 1000
        
        service = FoodMacroService()
        cache = service._load_cache()
        
        # Should index by standardized_name and aliases
        assert 'egg' in cache
        assert 'eggs' in cache
        assert 'hen egg' in cache
    
    @patch('app.services.food_macro_service.time')
    @patch('app.services.food_macro_service.get_firestore_client')
    def test_cache_ttl(self, mock_firestore, mock_time):
        """Test cache TTL (5 minutes)"""
        mock_db = Mock()
        mock_collection = Mock()
        mock_query = Mock()
        mock_query.get.return_value = []
        mock_query.limit.return_value = mock_query
        mock_collection.limit.return_value = mock_query
        mock_db.collection.return_value = mock_collection
        mock_firestore.return_value = mock_db
        
        service = FoodMacroService()
        
        # First load
        mock_time.time.return_value = 1000
        service._load_cache()
        
        # Second load within TTL (< 300 seconds)
        mock_time.time.return_value = 1200
        service._load_cache()
        
        # Should only call Firestore once (cache hit)
        assert mock_collection.limit.call_count == 1
        
        # Third load after TTL (> 300 seconds)
        mock_time.time.return_value = 1400
        service._load_cache()
        
        # Should call Firestore again (cache miss)
        assert mock_collection.limit.call_count == 2


class TestFuzzyMatching:
    """Test fuzzy_match_food() method"""
    
    @patch('app.services.food_macro_service.get_firestore_client')
    async def setup_method(self, mock_firestore):
        # Create mock food for cache
        self.mock_food = FoodMacro(
            food_id="egg123",
            standardized_name="egg",
            aliases=["eggs", "hen egg"],
            category="protein",
            unit_type="piece",
            default_portion=1.0,
            macros_per_unit=MacroNutrients(
                calories=70,
                protein_g=6,
                carbs_g=0.5,
                fat_g=5,
                fiber_g=0,
                sugar_g=0,
                sodium_mg=70
            ),
            source="usda",
            source_id="egg_usda",
            entry_origin="manual",
            verification_flag=True,
            confidence_score=1.0,
            access_count=0,
            created_by="admin",
            created_at=datetime.now(),
            updated_at=datetime.now()
        )
        
        mock_db = Mock()
        mock_collection = Mock()
        mock_query = Mock()
        mock_query.get.return_value = []
        mock_query.limit.return_value = mock_query
        mock_collection.limit.return_value = mock_query
        mock_db.collection.return_value = mock_collection
        mock_firestore.return_value = mock_db
        
        self.service = FoodMacroService()
        
        # Manually populate cache for testing
        self.service._cache = {
            'egg': self.mock_food,
            'eggs': self.mock_food,
            'hen egg': self.mock_food
        }
        self.service._cache_time = 1000
    
    @pytest.mark.asyncio
    async def test_exact_match_standardized_name(self):
        """Test exact match on standardized name"""
        result = await self.service.fuzzy_match_food("egg")
        
        assert result.matched is True
        assert result.match_type == "exact"
        assert result.confidence == 1.0
        assert result.food_macro.standardized_name == "egg"
    
    @pytest.mark.asyncio
    async def test_exact_match_alias(self):
        """Test exact match on alias"""
        result = await self.service.fuzzy_match_food("eggs")
        
        assert result.matched is True
        assert result.match_type == "exact"
        assert result.confidence == 1.0
        assert result.food_macro.standardized_name == "egg"
    
    @pytest.mark.asyncio
    @patch('app.services.food_macro_service.process')
    async def test_fuzzy_match_typo(self, mock_process):
        """Test fuzzy match with typo"""
        # Mock fuzzy matching library
        mock_process.extract.return_value = [
            ('egg', 85, 0),  # 85% match
            ('eggs', 80, 1),
            ('hen egg', 75, 2)
        ]
        
        result = await self.service.fuzzy_match_food("eg")
        
        assert result.matched is True
        assert result.match_type == "fuzzy"
        assert result.confidence == 0.85  # 85 / 100
        assert result.food_macro.standardized_name == "egg"
    
    @pytest.mark.asyncio
    @patch('app.services.food_macro_service.process')
    async def test_fuzzy_match_no_match(self, mock_process):
        """Test fuzzy match with no good match"""
        # Mock poor matches
        mock_process.extract.return_value = [
            ('egg', 50, 0),  # < 80% threshold
            ('eggs', 45, 1)
        ]
        
        result = await self.service.fuzzy_match_food("xyzabc")
        
        assert result.matched is False
        assert result.match_type == "none"
        assert result.confidence == 0.0


class TestCRUDOperations:
    """Test CRUD operations"""
    
    @patch('app.services.food_macro_service.get_firestore_client')
    def setup_method(self, mock_firestore):
        self.mock_db = Mock()
        self.mock_collection = Mock()
        self.mock_db.collection.return_value = self.mock_collection
        mock_firestore.return_value = self.mock_db
        
        self.service = FoodMacroService()
    
    @pytest.mark.asyncio
    async def test_create_food_macro(self):
        """Test creating a new food macro"""
        # Mock no existing food
        mock_query = Mock()
        mock_query.get.return_value = []
        self.mock_collection.where.return_value.limit.return_value = mock_query
        
        # Mock document creation
        mock_doc = Mock()
        mock_doc.id = "new_food_id"
        mock_doc.set = Mock()
        self.mock_collection.document.return_value = mock_doc
        
        # Mock history collection
        self.service.history_collection = Mock()
        mock_history_doc = Mock()
        self.service.history_collection.document.return_value = mock_history_doc
        
        food_data = FoodMacroCreate(
            standardized_name="test_food",
            aliases=["test"],
            category="protein",
            unit_type="piece",
            default_portion=1.0,
            macros_per_unit=MacroNutrients(
                calories=100,
                protein_g=10,
                carbs_g=5,
                fat_g=2,
                fiber_g=1,
                sugar_g=0,
                sodium_mg=50
            ),
            source="manual",
            source_id="test_001",
            entry_origin="manual"
        )
        
        result = await self.service.create_food_macro(food_data, "admin")
        
        assert result.food_id == "new_food_id"
        assert result.standardized_name == "test_food"
        assert result.created_by == "admin"
        mock_doc.set.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_create_duplicate_raises_error(self):
        """Test creating duplicate food raises error"""
        # Mock existing food
        mock_existing = Mock()
        self.mock_collection.where.return_value.limit.return_value.get.return_value = [mock_existing]
        
        food_data = FoodMacroCreate(
            standardized_name="existing_food",
            aliases=[],
            category="protein",
            unit_type="piece",
            default_portion=1.0,
            macros_per_unit=MacroNutrients(
                calories=100,
                protein_g=10,
                carbs_g=5,
                fat_g=2,
                fiber_g=1,
                sugar_g=0,
                sodium_mg=50
            ),
            source="manual",
            source_id="test_001",
            entry_origin="manual"
        )
        
        with pytest.raises(ValueError, match="already exists"):
            await self.service.create_food_macro(food_data, "admin")
    
    @pytest.mark.asyncio
    async def test_get_food_macro(self):
        """Test getting food macro by ID"""
        mock_doc = Mock()
        mock_doc.exists = True
        mock_doc.id = "food123"
        mock_doc.to_dict.return_value = {
            'standardized_name': 'test_food',
            'aliases': [],
            'category': 'protein',
            'unit_type': 'piece',
            'default_portion': 1.0,
            'macros_per_unit': {
                'calories': 100,
                'protein_g': 10,
                'carbs_g': 5,
                'fat_g': 2,
                'fiber_g': 1,
                'sugar_g': 0,
                'sodium_mg': 50
            },
            'source': 'manual',
            'source_id': 'test_001',
            'entry_origin': 'manual',
            'verification_flag': True,
            'confidence_score': 1.0,
            'access_count': 0,
            'created_by': 'admin',
            'created_at': datetime.now(),
            'updated_at': datetime.now()
        }
        
        self.mock_collection.document.return_value.get.return_value = mock_doc
        
        result = await self.service.get_food_macro("food123")
        
        assert result is not None
        assert result.food_id == "food123"
        assert result.standardized_name == "test_food"
    
    @pytest.mark.asyncio
    async def test_get_food_macro_not_found(self):
        """Test getting non-existent food macro"""
        mock_doc = Mock()
        mock_doc.exists = False
        self.mock_collection.document.return_value.get.return_value = mock_doc
        
        result = await self.service.get_food_macro("nonexistent")
        
        assert result is None

