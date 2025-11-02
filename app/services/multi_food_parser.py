"""
Multi-Food Parser - Parse complex inputs into separate meals
Example: "2 eggs morning, rice lunch, pistachios afternoon" → 3 separate meals
"""

import re
from typing import List, Dict, Optional, Tuple
from datetime import datetime, time
from app.data.indian_foods import INDIAN_FOODS
from app.data.supplements_and_misc import SUPPLEMENTS_AND_MISC
from app.services.nutrition_db import find_food, get_nutrition_info

class MealEntry:
    """Represents a single meal entry"""
    def __init__(self, food: str, quantity: Optional[str], meal_type: str, meal_time: Optional[str]):
        self.food = food
        self.quantity = quantity
        self.meal_type = meal_type
        self.meal_time = meal_time
        self.macros = None
    
    def to_dict(self):
        return {
            "food": self.food,
            "quantity": self.quantity,
            "meal_type": self.meal_type,
            "meal_time": self.meal_time,
            "macros": self.macros
        }

class MultiFoodParser:
    """Parse complex multi-food inputs"""
    
    # Time markers that indicate meal boundaries
    TIME_MARKERS = {
        "morning": "breakfast",
        "breakfast": "breakfast",
        "day time": "lunch",
        "daytime": "lunch",
        "lunch": "lunch",
        "afternoon": "snack",
        "evening": "dinner",
        "dinner": "dinner",
        "night": "late_night_snack"
    }
    
    # Conjunctions that separate foods within same meal
    FOOD_SEPARATORS = [" and ", " with ", ", "]
    
    def __init__(self, user_id: Optional[str] = None):
        self.user_id = user_id
        self.current_time = self._get_current_time()
    
    def _get_current_time(self) -> datetime:
        """Get current time in user's timezone if available"""
        if self.user_id:
            try:
                from app.services.timezone_service import get_user_local_time
                return get_user_local_time(self.user_id)
            except Exception as e:
                print(f"Error getting user local time: {e}")
                return datetime.now()
        return datetime.now()
    
    def parse(self, text: str) -> List[MealEntry]:
        """
        Parse complex input into separate meal entries
        
        Example inputs:
        1. "2 eggs in the morning, 1 bowl of rice and 1 bowl of curd during day time"
        2. "breakfast: 2 eggs, lunch: rice and dal, dinner: chicken"
        3. "morning had oats, lunch was biryani, evening snack was almonds"
        """
        text = text.lower().strip()
        meals = []
        
        # Strategy 1: Split by time markers
        meals_by_time = self._split_by_time_markers(text)
        
        if len(meals_by_time) > 1:
            # Multiple time periods detected
            for time_period, foods_text in meals_by_time:
                meal_type = self._classify_meal_type(time_period)
                foods = self._extract_foods(foods_text)
                
                for food, quantity in foods:
                    meals.append(MealEntry(
                        food=food,
                        quantity=quantity,
                        meal_type=meal_type,
                        meal_time=time_period
                    ))
        else:
            # Single time period or no time markers
            # Try to detect meal type from context or current time
            meal_type = self._infer_meal_type()
            foods = self._extract_foods(text)
            
            for food, quantity in foods:
                meals.append(MealEntry(
                    food=food,
                    quantity=quantity,
                    meal_type=meal_type,
                    meal_time=None
                ))
        
        return meals
    
    def _split_by_time_markers(self, text: str) -> List[Tuple[str, str]]:
        """
        Split text by time markers
        Returns: [(time_marker, food_text), ...]
        """
        results = []
        
        # Pattern: "in the morning", "during day time", "for breakfast", etc.
        time_patterns = [
            r"in the (morning|afternoon|evening|night)",
            r"during (day time|daytime|lunch|dinner)",
            r"for (breakfast|lunch|dinner)",
            r"(breakfast|lunch|dinner):",
        ]
        
        # Find all time markers and their positions
        markers = []
        for pattern in time_patterns:
            for match in re.finditer(pattern, text):
                time_marker = match.group(1) if match.lastindex else match.group(0)
                time_marker = time_marker.replace(":", "").strip()
                markers.append((match.start(), match.end(), time_marker))
        
        if not markers:
            return [(None, text)]
        
        # Sort by position
        markers.sort(key=lambda x: x[0])
        
        # Extract text between markers (including text BEFORE first marker)
        for i, (start, end, marker) in enumerate(markers):
            # Get text BEFORE this marker (for first marker only)
            if i == 0 and start > 0:
                before_text = text[0:start].strip()
                # Remove common prefixes
                before_text = re.sub(r'^(i ate|i had|ate|had)\s+', '', before_text, flags=re.IGNORECASE)
                if before_text:
                    results.append((marker, before_text))
            
            # Get text after this marker until next marker (or end)
            text_start = end
            text_end = markers[i+1][0] if i+1 < len(markers) else len(text)
            food_text = text[text_start:text_end].strip()
            
            # Clean up
            food_text = food_text.lstrip(",").strip()
            
            # Don't add if it's just the time marker text again
            if food_text and food_text not in self.TIME_MARKERS:
                results.append((marker, food_text))
        
        return results if results else [(None, text)]
    
    def _extract_foods(self, text: str) -> List[Tuple[str, Optional[str]]]:
        """
        Extract individual foods from text
        Returns: [(food_name, quantity), ...]
        """
        foods = []
        
        # Split by common separators: newlines, comma, 'and', or '+'
        parts = re.split(r'[\n,+]|\band\b', text)
        
        for part in parts:
            part = part.strip()
            if not part or len(part) < 3:
                continue
            
            # Extract quantity and food name
            # Pattern: "2 eggs", "1 bowl of rice", "200g chicken", "1.5 litres of water"
            quantity_match = re.match(r'^(\d+\.?\d*\s*(?:g|gm|kg|ml|l|litre|litres|liter|liters|bowl|cup|glass|piece|roti|egg)?)\s+(.+)$', part)
            
            if quantity_match:
                quantity = quantity_match.group(1).strip()
                food = quantity_match.group(2).strip()
            else:
                quantity = None
                food = part.strip()
            
            # Clean up food name
            food = self._clean_food_name(food)
            
            if food:
                foods.append((food, quantity))
        
        return foods
    
    def _clean_food_name(self, food: str) -> str:
        """Clean up food name"""
        # Remove common words and time markers
        remove_words = ["of", "the", "a", "an", "some", "i ate", "i had", "ate", "had", 
                       "during", "afternoon", "morning", "evening", "night", "daytime", "day time",
                       "for", "breakfast", "lunch", "dinner", "snack"]
        words = food.split()
        words = [w for w in words if w not in remove_words]
        return " ".join(words).strip()
    
    def _classify_meal_type(self, time_marker: Optional[str]) -> str:
        """Classify meal type from time marker"""
        if not time_marker:
            return self._infer_meal_type()
        
        time_marker = time_marker.lower().strip()
        
        # Direct mapping
        if time_marker in self.TIME_MARKERS:
            return self.TIME_MARKERS[time_marker]
        
        # Fuzzy matching
        for marker, meal_type in self.TIME_MARKERS.items():
            if marker in time_marker or time_marker in marker:
                return meal_type
        
        return self._infer_meal_type()
    
    def _infer_meal_type(self) -> str:
        """Infer meal type from current time"""
        current_hour = self.current_time.hour
        
        if 5 <= current_hour < 11:
            return "breakfast"
        elif 11 <= current_hour < 15:
            return "lunch"
        elif 15 <= current_hour < 18:
            return "snack"
        elif 18 <= current_hour < 23:
            return "dinner"
        else:
            return "late_night_snack"
    
    def calculate_macros(self, meal: MealEntry) -> Dict:
        """Calculate macros for a meal entry"""
        # Clean food name
        food_name = meal.food.lower().strip()
        
        # Search order: Supplements -> Indian Foods -> Nutrition DB
        food_info = None
        
        # 1. Try supplements and misc database first (for vitamins, water, etc.)
        for key, data in SUPPLEMENTS_AND_MISC.items():
            if key.replace("_", " ") in food_name or food_name in key.replace("_", " "):
                food_info = data
                break
            # Check aliases
            if "aliases" in data:
                for alias in data["aliases"]:
                    if alias in food_name or food_name in alias:
                        food_info = data
                        break
                if food_info:
                    break
        
        # 2. Try Indian foods database
        if not food_info:
            for key, data in INDIAN_FOODS.items():
                if key in food_name or food_name in key:
                    food_info = data
                    break
                # Check aliases
                if "aliases" in data:
                    for alias in data["aliases"]:
                        if alias in food_name or food_name in alias:
                            food_info = data
                            break
                    if food_info:
                        break
        
        # 3. Try nutrition_db
        if not food_info:
            nutrition_data = find_food(food_name)
            if nutrition_data:
                # Convert NutritionData to dict format
                food_info = {
                    "name": nutrition_data.name,
                    "per_100g": {
                        "calories": nutrition_data.calories,
                        "protein": nutrition_data.protein_g,
                        "carbs": nutrition_data.carbs_g,
                        "fat": nutrition_data.fat_g,
                        "fiber": nutrition_data.fiber_g
                    }
                }
        
        if not food_info:
            # Fallback: Use LLM or return clarification
            return {
                "calories": 0,
                "protein": 0,
                "carbs": 0,
                "fat": 0,
                "fiber": 0,
                "estimated": True,
                "needs_clarification": True,
                "clarification_question": f"I couldn't find '{meal.food}' in my database. Could you provide more details?"
            }
        
        # Calculate based on quantity
        if meal.quantity:
            # Parse quantity
            quantity_match = re.match(r'(\d+\.?\d*)\s*(\w+)?', meal.quantity)
            if quantity_match:
                amount = float(quantity_match.group(1))
                unit = quantity_match.group(2) or "piece"
                
                # Get macros
                if "per_piece" in food_info:
                    # Per-piece foods (eggs, rotis, etc.)
                    macros = food_info["per_piece"]
                    multiplier = amount
                elif "per_100g" in food_info:
                    # Per-100g foods (rice, dal, etc.)
                    macros = food_info["per_100g"]
                    
                    # Check if unit is in portions
                    portion_key = f"{int(amount)} {unit}" if unit != "piece" else None
                    if portion_key and portion_key in food_info.get("portions", {}):
                        # Use predefined portion size
                        grams = food_info["portions"][portion_key]
                        multiplier = grams / 100.0
                    elif unit == "bowl":
                        # Default bowl size
                        grams = 200 * amount
                        multiplier = grams / 100.0
                    elif unit == "cup":
                        grams = 150 * amount
                        multiplier = grams / 100.0
                    elif unit in ["g", "gm", "gram", "grams"]:
                        multiplier = amount / 100.0
                    elif unit == "kg":
                        multiplier = (amount * 1000) / 100.0
                    else:
                        # Default to 100g per unit
                        multiplier = amount
                elif "per_100ml" in food_info:
                    # Liquids
                    macros = food_info["per_100ml"]
                    if unit in ["glass", "cup"]:
                        ml = 240 * amount
                        multiplier = ml / 100.0
                    elif unit in ["l", "litre", "litres", "liter", "liters"]:
                        ml = 1000 * amount
                        multiplier = ml / 100.0
                    elif unit in ["ml"]:
                        multiplier = amount / 100.0
                    else:
                        multiplier = amount / 100.0
                else:
                    macros = food_info.get("per_cup", {"calories": 200, "protein": 10, "carbs": 25, "fat": 5})
                    multiplier = amount
                
                return {
                    "calories": round(macros["calories"] * multiplier, 1),
                    "protein": round(macros["protein"] * multiplier, 1),
                    "carbs": round(macros["carbs"] * multiplier, 1),
                    "fat": round(macros["fat"] * multiplier, 1),
                    "fiber": round(macros.get("fiber", 0) * multiplier, 1),
                    "estimated": False
                }
        
        # Default portion (no quantity specified)
        if "per_piece" in food_info:
            # For countable items, ask for clarification
            food_name = food_info["name"]
            portions = food_info.get("portions", {})
            portion_options = ", ".join([f"'{p}'" for p in list(portions.keys())[:3]]) if portions else "1, 2, or 3"
            
            return {
                "calories": food_info["per_piece"]["calories"],
                "protein": food_info["per_piece"]["protein"],
                "carbs": food_info["per_piece"]["carbs"],
                "fat": food_info["per_piece"]["fat"],
                "fiber": food_info["per_piece"].get("fiber", 0),
                "estimated": False,
                "needs_clarification": True,
                "clarification_question": f"How many {food_name.lower()}? (e.g., {portion_options})",
                "assumed_quantity": "1 piece"
            }
        elif "per_100g" in food_info:
            # Default to 1 bowl (200g)
            macros = food_info["per_100g"]
            multiplier = 2.0  # 200g
            return {
                "calories": round(macros["calories"] * multiplier, 1),
                "protein": round(macros["protein"] * multiplier, 1),
                "carbs": round(macros["carbs"] * multiplier, 1),
                "fat": round(macros["fat"] * multiplier, 1),
                "fiber": round(macros.get("fiber", 0) * multiplier, 1),
                "estimated": False
            }
        elif "per_100ml" in food_info:
            # Default to 1 glass (250ml)
            macros = food_info["per_100ml"]
            multiplier = 2.5  # 250ml
            return {
                "calories": round(macros["calories"] * multiplier, 1),
                "protein": round(macros["protein"] * multiplier, 1),
                "carbs": round(macros["carbs"] * multiplier, 1),
                "fat": round(macros["fat"] * multiplier, 1),
                "fiber": round(macros.get("fiber", 0) * multiplier, 1),
                "estimated": False
            }
        else:
            # Should not reach here, but if it does, return clarification
            return {
                "calories": 0,
                "protein": 0,
                "carbs": 0,
                "fat": 0,
                "fiber": 0,
                "estimated": True,
                "needs_clarification": True,
                "clarification_question": f"I need more information about '{meal.food}'. Could you specify the quantity or preparation method?"
            }

# Singleton instance
_parser = None

def get_parser() -> MultiFoodParser:
    """Get singleton parser instance"""
    global _parser
    if _parser is None:
        _parser = MultiFoodParser()
    return _parser

# Export
__all__ = ['MultiFoodParser', 'MealEntry', 'get_parser']

