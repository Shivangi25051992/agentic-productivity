"""
Unit tests for water quantity parsing (Bug #15 fix)
Tests the fallback parsing logic for water units
"""

import re


def parse_water_quantity(text: str) -> int:
    """
    Parse water quantity from text and return ml
    This is the same logic as in app/main.py lines 1080-1110
    """
    text_lower = text.lower()
    quantity_ml = None
    
    # Check for litres/liters
    if "litre" in text_lower or "liter" in text_lower or re.search(r'\d+\.?\d*\s*l\b', text_lower):
        match = re.search(r'(\d+\.?\d*)\s*(litres?|liters?|l)\b', text_lower)
        if match:
            quantity_ml = float(match.group(1)) * 1000
        else:
            quantity_ml = 1000  # Default to 1 litre
    
    # Check for glasses
    elif "glass" in text_lower:
        match = re.search(r'(\d+\.?\d*)\s*glass', text_lower)
        if match:
            quantity_ml = float(match.group(1)) * 250
        else:
            quantity_ml = 250  # Default to 1 glass
    
    # Check for ml
    elif "ml" in text_lower:
        match = re.search(r'(\d+\.?\d*)\s*ml', text_lower)
        if match:
            quantity_ml = float(match.group(1))
        else:
            quantity_ml = 250  # Default
    
    else:
        # No unit specified, default to 1 glass
        quantity_ml = 250
    
    return int(quantity_ml)


class TestWaterQuantityParsing:
    """Test water quantity parsing for various units"""
    
    # ==================== LITRE TESTS ====================
    
    def test_one_litre(self):
        """Test: 1 litre = 1000ml"""
        assert parse_water_quantity("1 litre of water") == 1000
    
    def test_two_litres(self):
        """Test: 2 litres = 2000ml"""
        assert parse_water_quantity("2 litres of water") == 2000
    
    def test_one_liter_american_spelling(self):
        """Test: 1 liter (American spelling) = 1000ml"""
        assert parse_water_quantity("1 liter of water") == 1000
    
    def test_one_point_five_litres(self):
        """Test: 1.5 litres = 1500ml"""
        assert parse_water_quantity("1.5 litres") == 1500
    
    def test_one_l_abbreviation(self):
        """Test: 1l = 1000ml"""
        assert parse_water_quantity("1l water") == 1000
    
    def test_litre_without_number(self):
        """Test: 'litre' without number defaults to 1000ml"""
        assert parse_water_quantity("litre of water") == 1000
    
    # ==================== GLASS TESTS ====================
    
    def test_one_glass(self):
        """Test: 1 glass = 250ml"""
        assert parse_water_quantity("1 glass of water") == 250
    
    def test_two_glasses(self):
        """Test: 2 glasses = 500ml"""
        assert parse_water_quantity("2 glasses of water") == 500
    
    def test_three_glasses(self):
        """Test: 3 glasses = 750ml"""
        assert parse_water_quantity("3 glasses") == 750
    
    def test_glass_without_number(self):
        """Test: 'glass' without number defaults to 250ml"""
        assert parse_water_quantity("glass of water") == 250
    
    # ==================== ML TESTS ====================
    
    def test_500_ml(self):
        """Test: 500 ml = 500ml"""
        assert parse_water_quantity("500 ml of water") == 500
    
    def test_750_ml(self):
        """Test: 750ml = 750ml"""
        assert parse_water_quantity("750ml water") == 750
    
    def test_1000_ml(self):
        """Test: 1000 ml = 1000ml"""
        assert parse_water_quantity("1000 ml") == 1000
    
    def test_ml_without_number(self):
        """Test: 'ml' without number defaults to 250ml"""
        assert parse_water_quantity("ml of water") == 250
    
    # ==================== DEFAULT TESTS ====================
    
    def test_water_without_unit(self):
        """Test: 'water' without unit defaults to 250ml (1 glass)"""
        assert parse_water_quantity("water") == 250
    
    def test_drank_water(self):
        """Test: 'drank water' defaults to 250ml"""
        assert parse_water_quantity("drank water") == 250
    
    # ==================== EDGE CASES ====================
    
    def test_decimal_litres(self):
        """Test: 0.5 litres = 500ml"""
        assert parse_water_quantity("0.5 litres") == 500
    
    def test_decimal_glasses(self):
        """Test: 1.5 glasses = 375ml"""
        assert parse_water_quantity("1.5 glasses") == 375
    
    def test_case_insensitive_litre(self):
        """Test: Case insensitive - 'LITRE' works"""
        assert parse_water_quantity("1 LITRE") == 1000
    
    def test_case_insensitive_glass(self):
        """Test: Case insensitive - 'GLASS' works"""
        assert parse_water_quantity("2 GLASSES") == 500
    
    # ==================== REGRESSION TESTS ====================
    
    def test_original_bug_case(self):
        """Test: Original bug - '1 litre of water' should be 1000ml not 250ml"""
        result = parse_water_quantity("1 litre of water")
        assert result == 1000, f"Expected 1000ml, got {result}ml"
    
    def test_glass_still_works(self):
        """Test: Regression - '1 glass' should still work as 250ml"""
        result = parse_water_quantity("1 glass of water")
        assert result == 250, f"Expected 250ml, got {result}ml"


if __name__ == "__main__":
    # Run tests manually
    test_class = TestWaterQuantityParsing()
    test_methods = [method for method in dir(test_class) if method.startswith('test_')]
    
    passed = 0
    failed = 0
    
    print("=" * 70)
    print("Running Water Quantity Parsing Tests")
    print("=" * 70)
    
    for method_name in test_methods:
        try:
            method = getattr(test_class, method_name)
            method()
            print(f"✅ PASS: {method_name}")
            passed += 1
        except AssertionError as e:
            print(f"❌ FAIL: {method_name} - {e}")
            failed += 1
        except Exception as e:
            print(f"❌ ERROR: {method_name} - {e}")
            failed += 1
    
    print("=" * 70)
    print(f"Results: {passed} passed, {failed} failed out of {passed + failed} tests")
    print("=" * 70)
    
    if failed == 0:
        print("✅ ALL TESTS PASSED!")
        exit(0)
    else:
        print(f"❌ {failed} TEST(S) FAILED!")
        exit(1)

