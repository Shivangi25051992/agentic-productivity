# 🗄️ Food Database Architecture & Best Practices

## 📊 Current Architecture

### Where is the Food Database Stored?

**Current Implementation:** ❌ **Hardcoded Python Dictionary**

**File:** `app/data/indian_foods.py`

```python
INDIAN_FOODS = {
    "egg": {
        "name": "Egg",
        "per_piece": {"calories": 70, "protein": 6, ...},
        "aliases": ["anda", "eggs"]
    },
    "rice": {
        "name": "Rice, White, Cooked",
        "per_100g": {"calories": 130, "protein": 2.7, ...},
        "aliases": ["chawal", "steamed rice"]
    },
    # ... only ~50 foods
}
```

**Problems:**
- ❌ Limited to ~50 foods
- ❌ Hardcoded in Python (not scalable)
- ❌ No dynamic updates
- ❌ Can't add new foods without code deployment
- ❌ No fallback when food not found

---

## 🎯 Best Practice Architecture (What We SHOULD Have)

### Recommended: **Multi-Tier Fallback System**

```
User Input: "cooked white basmati rice"
    ↓
┌─────────────────────────────────────────────────────────────┐
│ TIER 1: Local Database (Firestore)                         │
│ - Fast lookup (~10ms)                                       │
│ - 1000+ common foods                                        │
│ - User's custom foods                                       │
│ - Community-contributed foods                               │
└─────────────────────────────────────────────────────────────┘
    ↓ (if not found)
┌─────────────────────────────────────────────────────────────┐
│ TIER 2: Fuzzy Matching + Synonyms                          │
│ - "basmati rice" → "rice, white, cooked"                   │
│ - "anda" → "egg"                                            │
│ - "chawal" → "rice"                                         │
└─────────────────────────────────────────────────────────────┘
    ↓ (if still not found)
┌─────────────────────────────────────────────────────────────┐
│ TIER 3: External APIs (USDA, Nutritionix, Edamam)          │
│ - Query external nutrition databases                        │
│ - Cache result in Firestore for future                     │
│ - ~500ms latency                                            │
└─────────────────────────────────────────────────────────────┘
    ↓ (if still not found)
┌─────────────────────────────────────────────────────────────┐
│ TIER 4: OpenAI/LLM Estimation                              │
│ - Use GPT-4 to estimate macros                             │
│ - Based on similar foods                                    │
│ - Mark as "AI Estimated"                                    │
│ - Ask user to confirm                                       │
└─────────────────────────────────────────────────────────────┘
    ↓ (if all fail)
┌─────────────────────────────────────────────────────────────┐
│ TIER 5: Ask User for Details                               │
│ - "I couldn't find this food. Can you describe it?"        │
│ - "Is it similar to rice/bread/meat?"                       │
│ - Learn from user input                                     │
└─────────────────────────────────────────────────────────────┘
```

---

## 🏗️ Recommended Database Architecture

### **Option 1: Firestore (NoSQL) - RECOMMENDED ✅**

**Why Firestore?**
- ✅ Already using it for user data
- ✅ Fast queries (~10-50ms)
- ✅ Scalable (millions of foods)
- ✅ Real-time sync
- ✅ Easy to update
- ✅ Built-in search with Algolia integration

**Schema:**

```javascript
// Collection: food_database
{
  "food_id": "egg_001",
  "name": "Egg, Large, Boiled",
  "aliases": ["egg", "eggs", "anda", "boiled egg"],
  "category": "protein",
  "cuisine": "universal",
  "macros": {
    "per_piece": {
      "calories": 70,
      "protein": 6,
      "carbs": 0.5,
      "fat": 5,
      "fiber": 0
    }
  },
  "portions": {
    "1 egg": 1,
    "2 eggs": 2
  },
  "preparations": {
    "boiled": 1.0,
    "fried": 1.3,
    "scrambled": 1.2
  },
  "source": "USDA",
  "verified": true,
  "created_at": "2025-01-15",
  "updated_at": "2025-01-15",
  "search_keywords": ["egg", "anda", "protein", "breakfast"]
}
```

**Indexes:**
```javascript
// Composite indexes for fast search
- name (ASC)
- aliases (ARRAY)
- search_keywords (ARRAY)
- category + cuisine
```

---

### **Option 2: PostgreSQL (SQL) - Alternative**

**Why PostgreSQL?**
- ✅ Better for complex queries
- ✅ Full-text search
- ✅ Relational data (food → recipes → ingredients)
- ✅ ACID compliance

**Schema:**

```sql
-- Foods table
CREATE TABLE foods (
  food_id UUID PRIMARY KEY,
  name VARCHAR(255) NOT NULL,
  category VARCHAR(50),
  cuisine VARCHAR(50),
  source VARCHAR(50),
  verified BOOLEAN DEFAULT false,
  created_at TIMESTAMP,
  updated_at TIMESTAMP
);

-- Macros table
CREATE TABLE food_macros (
  macro_id UUID PRIMARY KEY,
  food_id UUID REFERENCES foods(food_id),
  unit_type VARCHAR(20), -- 'per_piece', 'per_100g', 'per_100ml'
  calories DECIMAL(8,2),
  protein DECIMAL(8,2),
  carbs DECIMAL(8,2),
  fat DECIMAL(8,2),
  fiber DECIMAL(8,2)
);

-- Aliases table
CREATE TABLE food_aliases (
  alias_id UUID PRIMARY KEY,
  food_id UUID REFERENCES foods(food_id),
  alias VARCHAR(255) NOT NULL,
  language VARCHAR(10) -- 'en', 'hi', 'ta'
);

-- Preparations table
CREATE TABLE food_preparations (
  prep_id UUID PRIMARY KEY,
  food_id UUID REFERENCES foods(food_id),
  preparation VARCHAR(50), -- 'boiled', 'fried', 'grilled'
  multiplier DECIMAL(3,2) -- 1.0, 1.3, 1.5
);

-- Full-text search index
CREATE INDEX idx_food_search ON foods USING GIN(to_tsvector('english', name));
CREATE INDEX idx_alias_search ON food_aliases USING GIN(to_tsvector('english', alias));
```

---

## 🔄 Improved Fallback System (What We Need to Build)

### Current Code (Limited):

```python
# app/services/multi_food_parser.py
def calculate_macros(self, meal: MealEntry) -> Dict:
    food_info = get_food_info(meal.food)
    
    if not food_info:
        # ❌ Just return error - BAD UX!
        return {
            "calories": 200,
            "estimated": True,
            "needs_clarification": True,
            "clarification_question": f"I couldn't find '{meal.food}'"
        }
```

### Improved Code (Multi-Tier Fallback):

```python
# app/services/nutrition_service.py (NEW FILE)

class NutritionService:
    def __init__(self):
        self.db = get_firestore_client()
        self.usda_api = USDAClient()
        self.nutritionix_api = NutritionixClient()
        self.openai_client = OpenAIClient()
    
    async def get_nutrition(self, food_name: str, quantity: str = None) -> Dict:
        """
        Multi-tier fallback system for nutrition lookup
        """
        
        # TIER 1: Local Firestore Database
        result = await self._search_local_db(food_name)
        if result:
            return self._format_result(result, quantity, source="local")
        
        # TIER 2: Fuzzy Matching
        result = await self._fuzzy_search(food_name)
        if result:
            return self._format_result(result, quantity, source="fuzzy")
        
        # TIER 3: External APIs (USDA, Nutritionix)
        result = await self._search_external_apis(food_name)
        if result:
            # Cache in Firestore for future
            await self._cache_food(result)
            return self._format_result(result, quantity, source="api")
        
        # TIER 4: OpenAI Estimation
        result = await self._ai_estimate(food_name)
        if result:
            return self._format_result(result, quantity, source="ai_estimated")
        
        # TIER 5: Ask User
        return {
            "found": False,
            "needs_clarification": True,
            "clarification_question": f"I couldn't find '{food_name}'. Can you describe it? (e.g., 'it's like rice', 'it's a type of bread')"
        }
    
    async def _search_local_db(self, food_name: str) -> Optional[Dict]:
        """Search Firestore database"""
        # Direct match
        query = self.db.collection('food_database').where('name', '==', food_name).limit(1)
        docs = query.get()
        if docs:
            return docs[0].to_dict()
        
        # Alias match
        query = self.db.collection('food_database').where('aliases', 'array_contains', food_name).limit(1)
        docs = query.get()
        if docs:
            return docs[0].to_dict()
        
        return None
    
    async def _fuzzy_search(self, food_name: str) -> Optional[Dict]:
        """Fuzzy matching with rapidfuzz"""
        from rapidfuzz import fuzz, process
        
        # Get all food names from cache
        all_foods = await self._get_all_foods()
        
        # Fuzzy match
        matches = process.extract(food_name, all_foods.keys(), scorer=fuzz.ratio, limit=1)
        
        if matches and matches[0][1] >= 80:  # 80% similarity
            return all_foods[matches[0][0]]
        
        return None
    
    async def _search_external_apis(self, food_name: str) -> Optional[Dict]:
        """Search external nutrition APIs"""
        
        # Try USDA first (free, comprehensive)
        try:
            result = await self.usda_api.search(food_name)
            if result:
                return self._convert_usda_format(result)
        except Exception as e:
            print(f"USDA API error: {e}")
        
        # Try Nutritionix (paid, but very accurate)
        try:
            result = await self.nutritionix_api.search(food_name)
            if result:
                return self._convert_nutritionix_format(result)
        except Exception as e:
            print(f"Nutritionix API error: {e}")
        
        return None
    
    async def _ai_estimate(self, food_name: str) -> Optional[Dict]:
        """Use OpenAI to estimate macros"""
        
        prompt = f"""
You are a nutrition expert. Estimate the macronutrients for: "{food_name}"

Provide a realistic estimate based on similar foods. Return JSON:
{{
  "calories": <number>,
  "protein": <number>,
  "carbs": <number>,
  "fat": <number>,
  "fiber": <number>,
  "confidence": <0-100>,
  "reasoning": "<why you estimated this way>",
  "similar_to": "<similar food used as reference>"
}}
"""
        
        try:
            response = await self.openai_client.chat.completions.create(
                model="gpt-4",
                messages=[{"role": "user", "content": prompt}],
                response_format={"type": "json_object"}
            )
            
            result = json.loads(response.choices[0].message.content)
            
            # Only use if confidence > 70%
            if result.get("confidence", 0) > 70:
                return {
                    "name": food_name,
                    "per_100g": {
                        "calories": result["calories"],
                        "protein": result["protein"],
                        "carbs": result["carbs"],
                        "fat": result["fat"],
                        "fiber": result["fiber"]
                    },
                    "source": "ai_estimated",
                    "confidence": result["confidence"],
                    "reasoning": result["reasoning"]
                }
        except Exception as e:
            print(f"OpenAI estimation error: {e}")
        
        return None
    
    async def _cache_food(self, food_data: Dict):
        """Cache food in Firestore for future use"""
        self.db.collection('food_database').add({
            **food_data,
            "created_at": firestore.SERVER_TIMESTAMP,
            "source": "api_cached"
        })
```

---

## 📊 Database Comparison

| Feature | Firestore (NoSQL) | PostgreSQL (SQL) | Python Dict (Current) |
|---------|-------------------|------------------|----------------------|
| **Scalability** | ✅ Excellent | ✅ Good | ❌ Poor |
| **Speed** | ✅ 10-50ms | ✅ 20-100ms | ✅ <1ms |
| **Search** | ⚠️ Limited | ✅ Full-text | ❌ Linear scan |
| **Updates** | ✅ Real-time | ⚠️ Manual | ❌ Code deploy |
| **Cost** | ⚠️ Pay per read | ⚠️ Server cost | ✅ Free |
| **Maintenance** | ✅ Low | ⚠️ Medium | ❌ High |
| **Flexibility** | ✅ Schema-less | ⚠️ Fixed schema | ✅ Any structure |
| **Recommended** | ✅ **YES** | ✅ YES | ❌ **NO** |

---

## 🚀 Migration Plan

### Phase 1: Move to Firestore (Week 1)
1. Create `food_database` collection
2. Migrate 50 existing foods
3. Add 500+ common foods from USDA
4. Update code to query Firestore

### Phase 2: Add External APIs (Week 2)
1. Integrate USDA FoodData Central API
2. Integrate Nutritionix API (optional, paid)
3. Implement caching

### Phase 3: Add AI Fallback (Week 3)
1. Implement OpenAI estimation
2. Add confidence scoring
3. User feedback loop

### Phase 4: Community Features (Week 4)
1. Allow users to add custom foods
2. Community voting on accuracy
3. Admin moderation

---

## 🔑 API Keys Needed

### Free APIs:
- **USDA FoodData Central** - Free, no key needed
  - https://fdc.nal.usda.gov/api-guide.html
  - 1000+ requests/hour

### Paid APIs (Optional):
- **Nutritionix** - $50/month for 5000 requests
  - https://www.nutritionix.com/business/api
  - Very accurate, includes branded foods

- **Edamam** - $0.002 per request
  - https://www.edamam.com/
  - Recipe analysis, meal planning

---

## 📝 Current vs. Recommended

### Current (❌ Limited):
```
User: "cooked white basmati rice"
↓
Search in Python dict (50 foods)
↓
Not found
↓
Return error: "I couldn't find..."
```

### Recommended (✅ Robust):
```
User: "cooked white basmati rice"
↓
1. Search Firestore (1000+ foods) → Not found
↓
2. Fuzzy match "basmati rice" → "rice, white" → Found! ✅
↓
Return: 130 cal per 100g
```

**OR if truly not found:**
```
↓
3. Query USDA API → Found "Rice, white, cooked" ✅
↓
Cache in Firestore
↓
Return: 130 cal per 100g
```

**OR if still not found:**
```
↓
4. Ask OpenAI → Estimate based on similar foods
↓
Return: ~125 cal per 100g (AI estimated, 85% confidence)
```

---

## 🎯 Recommendation

**Immediate (This Week):**
1. ✅ Move food database to Firestore
2. ✅ Add 500+ common foods
3. ✅ Implement fuzzy matching

**Short-term (Next Month):**
1. ✅ Integrate USDA API
2. ✅ Add OpenAI fallback
3. ✅ Implement caching

**Long-term (Next Quarter):**
1. ✅ Community food database
2. ✅ Photo recognition
3. ✅ Recipe breakdown

---

**Want me to implement the Firestore migration now?** 🚀

