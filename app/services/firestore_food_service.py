"""
Firestore-based Food Service
Replaces hardcoded Python dict with scalable Firestore database
"""

from typing import Optional, List, Dict, Tuple
from google.cloud import firestore
from rapidfuzz import fuzz, process
import re
import os
from dotenv import load_dotenv

load_dotenv()
load_dotenv('.env.local', override=True)

class FirestoreFoodService:
    """Production-grade food service using Firestore"""
    
    def __init__(self):
        project = os.getenv("GOOGLE_CLOUD_PROJECT")
        self.db = firestore.Client(project=project) if project else firestore.Client()
        self.collection = self.db.collection('food_database')
        self._cache = None
        self._cache_timestamp = None
    
    def search_food(self, query: str) -> Optional[Dict]:
        """
        Search for food in database
        Returns: Food document if found, None otherwise
        """
        query_lower = query.lower().strip()
        
        # 1. Try exact name match
        docs = self.collection.where('name', '==', query).limit(1).get()
        if docs:
            return self._format_food_doc(docs[0])
        
        # 2. Try alias match
        docs = self.collection.where('aliases', 'array_contains', query_lower).limit(1).get()
        if docs:
            return self._format_food_doc(docs[0])
        
        # 3. Try fuzzy matching
        result = self._fuzzy_search(query_lower)
        if result:
            return result
        
        return None
    
    def _fuzzy_search(self, query: str, threshold: int = 80) -> Optional[Dict]:
        """Fuzzy search using rapidfuzz"""
        
        # Load cache if needed
        if not self._cache:
            self._load_cache()
        
        # Get all food names
        food_names = list(self._cache.keys())
        
        # Fuzzy match
        matches = process.extract(query, food_names, scorer=fuzz.ratio, limit=5)
        
        if matches and matches[0][1] >= threshold:
            best_match_name = matches[0][0]
            return self._cache[best_match_name]
        
        return None
    
    def _load_cache(self):
        """Load all foods into memory cache for fast fuzzy matching"""
        import time
        
        # Check if cache is recent (< 5 minutes old)
        if self._cache and self._cache_timestamp:
            if time.time() - self._cache_timestamp < 300:
                return
        
        print("🔄 Loading food database cache...")
        
        self._cache = {}
        docs = self.collection.limit(1000).get()
        
        for doc in docs:
            data = doc.to_dict()
            food_data = self._format_food_doc(doc)
            
            # Index by name
            self._cache[data['name'].lower()] = food_data
            
            # Index by aliases
            for alias in data.get('aliases', []):
                if alias.lower() not in self._cache:
                    self._cache[alias.lower()] = food_data
        
        self._cache_timestamp = time.time()
        print(f"✅ Loaded {len(self._cache)} food entries into cache")
    
    def _format_food_doc(self, doc) -> Dict:
        """Format Firestore document to food data"""
        data = doc.to_dict()
        
        # Convert to format expected by multi_food_parser
        macros = data.get('macros', {})
        
        formatted = {
            'food_id': doc.id,
            'name': data.get('name'),
            'aliases': data.get('aliases', []),
            'category': data.get('category'),
            'unit_type': macros.get('unit_type', 'per_100g'),
            'verified': data.get('verified', False),
            'source': data.get('source', 'unknown')
        }
        
        # Add macros based on unit type
        if macros.get('unit_type') == 'per_piece':
            formatted['per_piece'] = {
                'calories': macros.get('calories', 0),
                'protein': macros.get('protein_g', 0),
                'carbs': macros.get('carbs_g', 0),
                'fat': macros.get('fat_g', 0),
                'fiber': macros.get('fiber_g', 0)
            }
        else:
            formatted['per_100g'] = {
                'calories': macros.get('calories', 0),
                'protein': macros.get('protein_g', 0),
                'carbs': macros.get('carbs_g', 0),
                'fat': macros.get('fat_g', 0),
                'fiber': macros.get('fiber_g', 0)
            }
        
        # Add portions
        formatted['portions'] = data.get('portions', {})
        
        # Add preparations
        formatted['preparations'] = data.get('preparations', {})
        
        return formatted
    
    def add_food(self, food_data: Dict) -> str:
        """Add a new food to database"""
        doc_ref = self.collection.document()
        doc_ref.set(food_data)
        
        # Invalidate cache
        self._cache = None
        
        return doc_ref.id
    
    def update_food(self, food_id: str, updates: Dict):
        """Update existing food"""
        self.collection.document(food_id).update(updates)
        
        # Invalidate cache
        self._cache = None
    
    def get_all_foods(self, limit: int = 100) -> List[Dict]:
        """Get all foods (for admin/testing)"""
        docs = self.collection.limit(limit).get()
        return [self._format_food_doc(doc) for doc in docs]
    
    def search_by_category(self, category: str, limit: int = 50) -> List[Dict]:
        """Search foods by category"""
        docs = self.collection.where('category', '==', category).limit(limit).get()
        return [self._format_food_doc(doc) for doc in docs]


# Singleton instance
_food_service = None

def get_food_service() -> FirestoreFoodService:
    """Get singleton food service instance"""
    global _food_service
    if _food_service is None:
        _food_service = FirestoreFoodService()
    return _food_service


# Compatibility functions for existing code
def get_food_info(food_name: str) -> Optional[Dict]:
    """Get food info - compatible with old indian_foods.py"""
    service = get_food_service()
    return service.search_food(food_name)


def search_foods(query: str) -> List[Tuple[str, Dict]]:
    """Search foods - compatible with old indian_foods.py"""
    service = get_food_service()
    result = service.search_food(query)
    
    if result:
        return [(result['name'], result)]
    return []

