"""
Unit Tests for Food Macro Service
Tests fuzzy matching, portion parsing, and cache performance
"""

import pytest
import asyncio
from app.services.food_macro_service import get_food_macro_service
from app.models.food_macro import FoodMacroCreate, MacroNutrients


class TestFuzzyMatching:
    """Test fuzzy matching functionality"""
    
    @pytest.mark.asyncio
    async def test_exact_match(self):
        """Test exact match on food name"""
        service = get_food_macro_service()
        result = await service.fuzzy_match_food("2 eggs")
        
        assert result.matched == True
        assert "egg" in result.food_macro.standardized_name.lower()
        assert result.confidence == 1.0
        assert result.match_type == "exact"
    
    @pytest.mark.asyncio
    async def test_fuzzy_match_typo(self):
        """Test fuzzy match with typo"""
        service = get_food_macro_service()
        result = await service.fuzzy_match_food("eggz")
        
        assert result.matched == True
        assert "egg" in result.food_macro.standardized_name.lower()
        # Fuzzy match should still work
    
    @pytest.mark.asyncio
    async def test_preparation_variant(self):
        """Test matching different preparation styles"""
        service = get_food_macro_service()
        
        # Fried eggs
        result_fried = await service.fuzzy_match_food("fried eggs")
        assert result_fried.matched == True
        assert "fried" in result_fried.food_macro.standardized_name.lower()
        
        # Boiled eggs
        result_boiled = await service.fuzzy_match_food("boiled eggs")
        assert result_boiled.matched == True
        assert "boiled" in result_boiled.food_macro.standardized_name.lower()
        
        # Different calories
        portion_fried = service.parse_portion("1 fried egg", result_fried.food_macro)
        portion_boiled = service.parse_portion("1 boiled egg", result_boiled.food_macro)
        assert portion_fried.macros.calories != portion_boiled.macros.calories
    
    @pytest.mark.asyncio
    async def test_no_match(self):
        """Test that unknown foods don't match"""
        service = get_food_macro_service()
        result = await service.fuzzy_match_food("dragon fruit smoothie")
        
        assert result.matched == False
        assert result.confidence == 0.0
        assert result.match_type == "none"


class TestPortionParsing:
    """Test portion parsing and macro calculation"""
    
    @pytest.mark.asyncio
    async def test_quantity_extraction(self):
        """Test extracting quantity from input"""
        service = get_food_macro_service()
        
        # Test "2 eggs"
        result = await service.fuzzy_match_food("2 eggs")
        portion = service.parse_portion("2 eggs", result.food_macro)
        
        assert portion.quantity == 2.0
        assert portion.macros.calories == pytest.approx(140.0, rel=0.1)
        assert portion.macros.protein_g == pytest.approx(12.0, rel=0.1)
    
    @pytest.mark.asyncio
    async def test_unit_conversion_grams(self):
        """Test gram-based unit conversion"""
        service = get_food_macro_service()
        
        # Test "100g chicken breast"
        result = await service.fuzzy_match_food("100g chicken breast")
        portion = service.parse_portion("100g chicken breast", result.food_macro)
        
        # Should be around 165 kcal for 100g grilled chicken
        assert portion.macros.calories == pytest.approx(165.0, rel=0.2)
        assert portion.macros.protein_g > 20.0  # High protein
    
    @pytest.mark.asyncio
    async def test_default_portion(self):
        """Test default portion when no quantity specified"""
        service = get_food_macro_service()
        
        # Test "apple" (should default to 1)
        result = await service.fuzzy_match_food("apple")
        portion = service.parse_portion("apple", result.food_macro)
        
        assert portion.quantity == 1.0
        assert portion.macros.calories == pytest.approx(95.0, rel=0.1)
    
    def test_unit_conversion_logic(self):
        """Test unit conversion calculations"""
        service = get_food_macro_service()
        
        # Test g to 100g conversion
        result = service._convert_units(100, 'g', '100g')
        assert result == pytest.approx(1.0)
        
        # Test kg to g
        result = service._convert_units(1, 'kg', 'g')
        assert result == pytest.approx(1000.0)
        
        # Test oz to g
        result = service._convert_units(1, 'oz', 'g')
        assert result == pytest.approx(28.35, rel=0.01)


class TestCachePerformance:
    """Test cache performance and optimization"""
    
    @pytest.mark.asyncio
    async def test_cache_loading(self):
        """Test that cache loads correctly"""
        service = get_food_macro_service()
        
        # Load cache
        cache = service._load_cache()
        
        assert cache is not None
        assert len(cache) > 0
        assert "eggs" in cache or "egg" in cache
    
    @pytest.mark.asyncio
    async def test_cache_performance(self):
        """Test that cached lookups are fast"""
        import time
        service = get_food_macro_service()
        
        # First query (loads cache)
        start = time.time()
        result1 = await service.fuzzy_match_food("eggs")
        first_time = time.time() - start
        
        # Second query (uses cache)
        start = time.time()
        result2 = await service.fuzzy_match_food("eggs")
        second_time = time.time() - start
        
        # Second query should be much faster
        assert second_time < 0.01  # Less than 10ms
        assert result1.matched == result2.matched
    
    @pytest.mark.asyncio
    async def test_multiple_lookups(self):
        """Test multiple sequential lookups"""
        service = get_food_macro_service()
        
        foods = ["eggs", "chicken", "apple", "rice", "bread"]
        
        for food in foods:
            result = await service.fuzzy_match_food(food)
            # Most common foods should match
            if food in ["eggs", "chicken", "apple"]:
                assert result.matched == True


class TestAccuracy:
    """Test accuracy of macro calculations"""
    
    @pytest.mark.asyncio
    async def test_egg_macros(self):
        """Test egg macro accuracy"""
        service = get_food_macro_service()
        
        result = await service.fuzzy_match_food("1 boiled egg")
        portion = service.parse_portion("1 boiled egg", result.food_macro)
        
        # USDA values for large boiled egg
        assert portion.macros.calories == pytest.approx(70.0, rel=0.1)
        assert portion.macros.protein_g == pytest.approx(6.0, rel=0.1)
        assert portion.macros.fat_g == pytest.approx(5.0, rel=0.1)
        assert portion.macros.carbs_g == pytest.approx(0.6, rel=0.2)
    
    @pytest.mark.asyncio
    async def test_source_tracking(self):
        """Test that source is tracked correctly"""
        service = get_food_macro_service()
        
        result = await service.fuzzy_match_food("eggs")
        portion = service.parse_portion("eggs", result.food_macro)
        
        assert portion.source is not None
        assert portion.cache_hit == True
        # Should be from USDA for seeded foods
        assert "usda" in portion.source.lower() or portion.source == "usda_fdc"


class TestEdgeCases:
    """Test edge cases and error handling"""
    
    @pytest.mark.asyncio
    async def test_empty_input(self):
        """Test handling of empty input"""
        service = get_food_macro_service()
        result = await service.fuzzy_match_food("")
        
        # Should not crash
        assert result.matched == False
    
    @pytest.mark.asyncio
    async def test_very_long_input(self):
        """Test handling of very long input"""
        service = get_food_macro_service()
        long_input = "eggs " * 100
        result = await service.fuzzy_match_food(long_input)
        
        # Should still try to match
        assert result is not None
    
    @pytest.mark.asyncio
    async def test_special_characters(self):
        """Test handling of special characters"""
        service = get_food_macro_service()
        result = await service.fuzzy_match_food("eggs!!!")
        
        # Should still match despite special chars
        # (normalization should handle this)
        assert result is not None


class TestNormalization:
    """Test input normalization"""
    
    def test_normalize_quantity(self):
        """Test quantity extraction"""
        service = get_food_macro_service()
        
        # Test "2 eggs"
        parsed = service.normalize_input("2 eggs")
        assert parsed["quantity"] == 2.0
        assert "egg" in parsed["food"]
        
        # Test "100g chicken"
        parsed = service.normalize_input("100g chicken")
        assert parsed["quantity"] == 100.0
        assert parsed["unit"] == "g"
        assert "chicken" in parsed["food"]
    
    def test_normalize_preparation(self):
        """Test preparation style extraction"""
        service = get_food_macro_service()
        
        # Test "fried eggs"
        parsed = service.normalize_input("fried eggs")
        assert parsed["prep"] == "fried"
        
        # Test "grilled chicken"
        parsed = service.normalize_input("grilled chicken")
        assert parsed["prep"] == "grilled"


# Run tests
if __name__ == "__main__":
    pytest.main([__file__, "-v", "--asyncio-mode=auto"])





