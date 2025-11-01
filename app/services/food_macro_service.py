"""
Food Macro Service
Handles CRUD operations and fuzzy matching for food macro reference table
"""

from typing import Optional, List, Tuple
from datetime import datetime
from google.cloud import firestore
from rapidfuzz import fuzz, process
import re

from app.services.database import get_firestore_client
from app.models.food_macro import (
    FoodMacro,
    FoodMacroCreate,
    FoodMacroUpdate,
    FoodMacroHistory,
    FoodMatchResult,
    PortionParseResult,
    MacroNutrients
)


class FoodMacroService:
    """Service for managing food macro reference data"""
    
    def __init__(self):
        self.db = get_firestore_client()
        self.collection = self.db.collection('food_macros')
        self.history_collection = self.db.collection('food_macro_history')
        self._cache = None  # In-memory cache for fast lookups
        self._cache_time = None
    
    # ==================== CRUD Operations ====================
    
    async def create_food_macro(
        self, 
        food_data: FoodMacroCreate, 
        created_by: str
    ) -> FoodMacro:
        """Create a new food macro entry"""
        
        # Check if standardized_name already exists
        existing = self.collection.where(
            'standardized_name', '==', food_data.standardized_name
        ).limit(1).get()
        
        if existing:
            raise ValueError(f"Food macro with name '{food_data.standardized_name}' already exists")
        
        # Create document
        doc_ref = self.collection.document()
        
        food_macro = FoodMacro(
            food_id=doc_ref.id,
            **food_data.dict(),
            created_by=created_by,
            created_at=datetime.now(),
            updated_at=datetime.now()
        )
        
        # Save to Firestore
        doc_ref.set(food_macro.dict(exclude={'food_id'}))
        
        # Log to history
        await self._log_history(
            food_macro_id=doc_ref.id,
            action="created",
            new_values=food_macro.dict(),
            changed_by=created_by
        )
        
        return food_macro
    
    async def get_food_macro(self, food_id: str) -> Optional[FoodMacro]:
        """Get food macro by ID"""
        doc = self.collection.document(food_id).get()
        
        if not doc.exists:
            return None
        
        data = doc.to_dict()
        data['food_id'] = doc.id
        return FoodMacro(**data)
    
    async def update_food_macro(
        self,
        food_id: str,
        updates: FoodMacroUpdate,
        updated_by: str
    ) -> FoodMacro:
        """Update food macro entry"""
        
        # Get existing
        existing = await self.get_food_macro(food_id)
        if not existing:
            raise ValueError(f"Food macro {food_id} not found")
        
        # Log to history
        await self._log_history(
            food_macro_id=food_id,
            action="updated",
            old_values=existing.dict(),
            new_values=updates.dict(exclude_unset=True),
            changed_by=updated_by
        )
        
        # Update
        update_data = updates.dict(exclude_unset=True)
        update_data['updated_at'] = datetime.now()
        
        self.collection.document(food_id).update(update_data)
        
        # Return updated
        return await self.get_food_macro(food_id)
    
    async def delete_food_macro(self, food_id: str, deleted_by: str):
        """Soft delete food macro (mark as inactive)"""
        
        existing = await self.get_food_macro(food_id)
        if not existing:
            raise ValueError(f"Food macro {food_id} not found")
        
        # Log to history
        await self._log_history(
            food_macro_id=food_id,
            action="deleted",
            old_values=existing.dict(),
            changed_by=deleted_by
        )
        
        # Mark as deleted (don't actually delete for audit trail)
        self.collection.document(food_id).update({
            'deleted': True,
            'deleted_at': datetime.now(),
            'deleted_by': deleted_by
        })
    
    async def list_food_macros(
        self,
        category: Optional[str] = None,
        verified_only: bool = False,
        limit: int = 100
    ) -> List[FoodMacro]:
        """List food macros with optional filters"""
        
        query = self.collection
        
        # Filter by category
        if category:
            query = query.where('category', '==', category)
        
        # Filter verified only
        if verified_only:
            query = query.where('verification_flag', '==', True)
        
        # Order by access count (most popular first)
        query = query.order_by('access_count', direction=firestore.Query.DESCENDING)
        query = query.limit(limit)
        
        docs = query.get()
        
        results = []
        for doc in docs:
            data = doc.to_dict()
            data['food_id'] = doc.id
            results.append(FoodMacro(**data))
        
        return results
    
    # ==================== Fuzzy Matching ====================
    
    def _load_cache(self):
        """Load all foods into memory cache for fast lookups"""
        import time
        
        # Cache for 5 minutes
        if self._cache is not None and self._cache_time is not None:
            if time.time() - self._cache_time < 300:
                return self._cache
        
        # Load all foods
        all_foods = self.collection.limit(1000).get()
        
        self._cache = {}
        for doc in all_foods:
            data = doc.to_dict()
            data['food_id'] = doc.id
            food = FoodMacro(**data)
            
            # Index by standardized_name
            self._cache[food.standardized_name] = food
            
            # Index by all aliases
            for alias in food.aliases:
                if alias not in self._cache:
                    self._cache[alias] = food
        
        self._cache_time = time.time()
        return self._cache
    
    def normalize_input(self, user_input: str) -> dict:
        """
        Normalize user input and extract quantity, food, preparation
        
        Examples:
        - "2 eggs" → {"quantity": 2, "food": "eggs", "prep": None}
        - "100g chicken breast" → {"quantity": 100, "unit": "g", "food": "chicken breast"}
        - "fried eggs" → {"quantity": None, "food": "eggs", "prep": "fried"}
        """
        
        user_input = user_input.lower().strip()
        
        # Extract quantity and unit
        quantity_pattern = r'^(\d+\.?\d*)\s*(piece|pieces|g|kg|cup|cups|oz|lb|lbs|serving|servings)?\s*'
        quantity_match = re.match(quantity_pattern, user_input)
        
        quantity = None
        unit = None
        
        if quantity_match:
            quantity = float(quantity_match.group(1))
            unit = quantity_match.group(2)
            # Remove quantity from input
            user_input = re.sub(quantity_pattern, '', user_input).strip()
        
        # Extract preparation style
        prep_keywords = ['boiled', 'fried', 'grilled', 'baked', 'raw', 'scrambled', 'poached', 'steamed']
        prep = None
        
        for keyword in prep_keywords:
            if keyword in user_input:
                prep = keyword
                break
        
        return {
            "quantity": quantity,
            "unit": unit,
            "food": user_input,
            "prep": prep
        }
    
    async def fuzzy_match_food(self, user_input: str) -> FoodMatchResult:
        """
        Multi-stage fuzzy matching (OPTIMIZED with in-memory cache):
        1. Exact match on standardized_name (from cache)
        2. Exact match on aliases (from cache)
        3. Fuzzy match with Levenshtein distance
        """
        
        # Load cache
        cache = self._load_cache()
        
        # Normalize input
        parsed = self.normalize_input(user_input)
        search_term = parsed['food']
        
        # Stage 1 & 2: Exact match (cache lookup - O(1))
        if search_term in cache:
            return FoodMatchResult(
                matched=True,
                food_macro=cache[search_term],
                confidence=1.0,
                match_type="exact"
            )
        
        # Stage 3: Fuzzy match (Levenshtein distance)
        food_names = list(cache.keys())
        
        # Find best matches
        matches = process.extract(
            search_term,
            food_names,
            scorer=fuzz.ratio,
            limit=5
        )
        
        if matches and matches[0][1] >= 80:  # 80% similarity threshold
            best_match_name = matches[0][0]
            food_macro = cache[best_match_name]
            
            # Get suggestions (other good matches)
            suggestions = []
            for match_name, score, _ in matches[1:4]:
                if score >= 70:
                    suggestions.append(cache[match_name])
            
            return FoodMatchResult(
                matched=True,
                food_macro=food_macro,
                confidence=matches[0][1] / 100.0,
                match_type="fuzzy",
                suggestions=suggestions
            )
        
        # No match found
        return FoodMatchResult(
            matched=False,
            confidence=0.0,
            match_type="none",
            suggestions=[]
        )
    
    # ==================== Portion Parsing ====================
    
    def parse_portion(
        self,
        user_input: str,
        food_macro: FoodMacro
    ) -> PortionParseResult:
        """
        Parse portion from user input and calculate macros
        
        Examples:
        - "2 eggs" → 2 pieces → 140 kcal
        - "100g chicken" → 100g → calculated macros
        """
        
        parsed = self.normalize_input(user_input)
        
        # Get quantity - if not specified, use 1 (not default_portion)
        # User can always say "2 eggs" if they want 2
        quantity = parsed['quantity'] if parsed['quantity'] is not None else 1.0
        unit = parsed['unit'] or food_macro.unit_type
        
        # Convert units if needed
        quantity_in_standard_units = self._convert_units(
            quantity,
            unit,
            food_macro.unit_type
        )
        
        # Calculate macros
        base_macros = food_macro.macros_per_unit
        
        calculated_macros = MacroNutrients(
            calories=base_macros.calories * quantity_in_standard_units,
            protein_g=base_macros.protein_g * quantity_in_standard_units,
            carbs_g=base_macros.carbs_g * quantity_in_standard_units,
            fat_g=base_macros.fat_g * quantity_in_standard_units,
            fiber_g=base_macros.fiber_g * quantity_in_standard_units,
            sugar_g=base_macros.sugar_g * quantity_in_standard_units,
            sodium_mg=base_macros.sodium_mg * quantity_in_standard_units,
            cholesterol_mg=base_macros.cholesterol_mg * quantity_in_standard_units if base_macros.cholesterol_mg else None,
            saturated_fat_g=base_macros.saturated_fat_g * quantity_in_standard_units if base_macros.saturated_fat_g else None,
            trans_fat_g=base_macros.trans_fat_g * quantity_in_standard_units if base_macros.trans_fat_g else None
        )
        
        # Update access tracking
        self.collection.document(food_macro.food_id).update({
            'access_count': firestore.Increment(1),
            'last_accessed': datetime.now()
        })
        
        return PortionParseResult(
            quantity=quantity,
            unit=unit,
            macros=calculated_macros,
            source=food_macro.source,
            source_id=food_macro.source_id,
            cache_hit=True
        )
    
    def _convert_units(self, quantity: float, from_unit: str, to_unit: str) -> float:
        """Convert between different units"""
        
        # Normalize unit names
        from_unit = from_unit.lower() if from_unit else 'piece'
        to_unit = to_unit.lower() if to_unit else 'piece'
        
        # If units are the same, no conversion needed
        if from_unit == to_unit:
            return quantity
        
        # Special handling for "100g" unit type (common in database)
        if to_unit == '100g':
            if from_unit == 'g':
                return quantity / 100.0  # 100g input = 1 unit of "100g"
            elif from_unit == 'kg':
                return (quantity * 1000) / 100.0
            elif from_unit == 'oz':
                return (quantity * 28.35) / 100.0
        
        # Unit conversion table (to grams)
        to_grams = {
            'g': 1.0,
            '100g': 100.0,
            'kg': 1000.0,
            'oz': 28.35,
            'lb': 453.59,
            'lbs': 453.59,
            'cup': 240.0,  # Approximate for liquids
            'cups': 240.0,
            'piece': 1.0,  # No conversion for pieces
            'pieces': 1.0,
            'medium': 1.0,  # For fruits/vegetables
            'serving': 1.0,
            'servings': 1.0,
            'slice': 1.0,
        }
        
        # Convert from_unit to grams
        quantity_in_grams = quantity * to_grams.get(from_unit, 1.0)
        
        # Convert from grams to to_unit
        quantity_in_target = quantity_in_grams / to_grams.get(to_unit, 1.0)
        
        return quantity_in_target
    
    # ==================== History & Audit ====================
    
    async def _log_history(
        self,
        food_macro_id: str,
        action: str,
        changed_by: str,
        old_values: Optional[dict] = None,
        new_values: Optional[dict] = None,
        reason: Optional[str] = None
    ):
        """Log changes to food macro history"""
        
        history = FoodMacroHistory(
            food_macro_id=food_macro_id,
            action=action,
            old_values=old_values,
            new_values=new_values,
            changed_by=changed_by,
            reason=reason
        )
        
        doc_ref = self.history_collection.document()
        doc_ref.set(history.dict(exclude={'history_id'}))
    
    async def get_food_macro_history(
        self,
        food_macro_id: str,
        limit: int = 50
    ) -> List[FoodMacroHistory]:
        """Get history of changes for a food macro"""
        
        docs = self.history_collection.where(
            'food_macro_id', '==', food_macro_id
        ).order_by(
            'changed_at', direction=firestore.Query.DESCENDING
        ).limit(limit).get()
        
        results = []
        for doc in docs:
            data = doc.to_dict()
            data['history_id'] = doc.id
            results.append(FoodMacroHistory(**data))
        
        return results
    
    # ==================== Admin Review Queue ====================
    
    async def get_review_queue(self, limit: int = 100) -> List[FoodMacro]:
        """
        Get food macros needing admin review:
        - New AI entries
        - Low confidence (<0.8)
        - High access count but unverified
        """
        
        # Query for unverified entries
        unverified = self.collection.where(
            'verification_flag', '==', False
        ).order_by(
            'access_count', direction=firestore.Query.DESCENDING
        ).limit(limit).get()
        
        results = []
        for doc in unverified:
            data = doc.to_dict()
            data['food_id'] = doc.id
            
            # Include if:
            # 1. AI generated
            # 2. Low confidence
            # 3. High access count (>100)
            if (data.get('entry_origin') == 'ai' or 
                data.get('confidence_score', 1.0) < 0.8 or
                data.get('access_count', 0) > 100):
                results.append(FoodMacro(**data))
        
        return results
    
    async def verify_food_macro(
        self,
        food_id: str,
        verified_by: str,
        updates: Optional[FoodMacroUpdate] = None
    ) -> FoodMacro:
        """Admin verify and optionally update food macro"""
        
        # Get existing
        existing = await self.get_food_macro(food_id)
        if not existing:
            raise ValueError(f"Food macro {food_id} not found")
        
        # Apply updates if provided
        if updates:
            await self.update_food_macro(food_id, updates, verified_by)
        
        # Mark as verified
        self.collection.document(food_id).update({
            'verification_flag': True,
            'confidence_score': 1.0,
            'updated_at': datetime.now()
        })
        
        # Log to history
        await self._log_history(
            food_macro_id=food_id,
            action="verified",
            changed_by=verified_by,
            reason="Admin verification"
        )
        
        return await self.get_food_macro(food_id)


# Singleton instance
_food_macro_service = None

def get_food_macro_service() -> FoodMacroService:
    """Get singleton instance of FoodMacroService"""
    global _food_macro_service
    if _food_macro_service is None:
        _food_macro_service = FoodMacroService()
    return _food_macro_service

