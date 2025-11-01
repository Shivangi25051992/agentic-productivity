# 🗄️ Production-Grade Food Database - Implementation Plan

## 🎯 Goal

Build a **scalable, elastic, production-ready database** for:
- ✅ Macronutrients (Protein, Carbs, Fat, Fiber, Calories)
- ✅ Micronutrients (Vitamins, Minerals)
- ✅ Food items with accurate portions
- ✅ Indian & International foods
- ✅ Custom foods from user's diet charts

---

## 📊 Architecture Overview

```
┌─────────────────────────────────────────────────────────────┐
│                    USER INPUT                                │
│              "2 eggs for breakfast"                          │
└─────────────────────────────────────────────────────────────┘
                         ↓
┌─────────────────────────────────────────────────────────────┐
│              FIRESTORE FOOD DATABASE                         │
│  - 10,000+ foods (scalable to millions)                     │
│  - Macros + Micros (vitamins, minerals)                     │
│  - User's custom foods from diet PDFs                       │
│  - Community-contributed foods                               │
│  - Fast queries (~10-50ms)                                   │
└─────────────────────────────────────────────────────────────┘
                         ↓
┌─────────────────────────────────────────────────────────────┐
│              FALLBACK LAYERS                                 │
│  1. Fuzzy matching (typos, synonyms)                        │
│  2. USDA API (1M+ foods, free)                              │
│  3. OpenAI estimation (AI-powered)                          │
│  4. User clarification                                       │
└─────────────────────────────────────────────────────────────┘
                         ↓
┌─────────────────────────────────────────────────────────────┐
│              CACHING & LEARNING                              │
│  - Cache API results in Firestore                           │
│  - Learn from user corrections                               │
│  - Improve accuracy over time                                │
└─────────────────────────────────────────────────────────────┘
```

---

## 🏗️ Database Schema (Firestore)

### Collection: `food_database`

```javascript
{
  // Core identification
  "food_id": "egg_boiled_001",
  "name": "Egg, Large, Boiled",
  "name_local": "अंडा (उबला हुआ)",  // Hindi/local name
  "aliases": ["egg", "eggs", "anda", "boiled egg", "hard boiled egg"],
  "search_keywords": ["egg", "anda", "protein", "breakfast", "boiled"],
  
  // Classification
  "category": "protein",  // protein, carbs, fats, vegetables, fruits, dairy, etc.
  "subcategory": "eggs",
  "cuisine": "universal",  // indian, chinese, italian, universal, etc.
  "food_group": "animal_protein",
  
  // Macronutrients (per standard unit)
  "macros": {
    "unit_type": "per_piece",  // per_piece, per_100g, per_100ml, per_serving
    "unit_size": 50,  // grams (for reference)
    "calories": 70,
    "protein_g": 6.0,
    "carbs_g": 0.5,
    "fat_g": 5.0,
    "fiber_g": 0.0,
    "sugar_g": 0.4,
    "saturated_fat_g": 1.6,
    "polyunsaturated_fat_g": 0.7,
    "monounsaturated_fat_g": 2.0,
    "trans_fat_g": 0.0
  },
  
  // Micronutrients (vitamins & minerals)
  "micros": {
    // Vitamins
    "vitamin_a_mcg": 80,
    "vitamin_b1_thiamine_mg": 0.04,
    "vitamin_b2_riboflavin_mg": 0.26,
    "vitamin_b3_niacin_mg": 0.04,
    "vitamin_b5_pantothenic_acid_mg": 0.7,
    "vitamin_b6_mg": 0.06,
    "vitamin_b7_biotin_mcg": 10,
    "vitamin_b9_folate_mcg": 24,
    "vitamin_b12_mcg": 0.6,
    "vitamin_c_mg": 0,
    "vitamin_d_mcg": 1.1,
    "vitamin_e_mg": 0.5,
    "vitamin_k_mcg": 0.3,
    
    // Minerals
    "calcium_mg": 28,
    "iron_mg": 0.9,
    "magnesium_mg": 6,
    "phosphorus_mg": 99,
    "potassium_mg": 69,
    "sodium_mg": 62,
    "zinc_mg": 0.6,
    "copper_mg": 0.04,
    "manganese_mg": 0.01,
    "selenium_mcg": 15.4,
    "iodine_mcg": 24,
    
    // Other
    "cholesterol_mg": 186,
    "omega_3_g": 0.04,
    "omega_6_g": 0.6
  },
  
  // Portion sizes
  "portions": {
    "1 egg": 1,
    "2 eggs": 2,
    "3 eggs": 3,
    "half egg": 0.5
  },
  
  // Preparation methods (multiplier for calories)
  "preparations": {
    "boiled": 1.0,
    "fried": 1.3,  // +30% for oil
    "scrambled": 1.2,  // +20% for butter
    "poached": 1.0,
    "omelette": 1.25  // +25% for oil/butter
  },
  
  // Metadata
  "source": "USDA",  // USDA, NIN, user_diet_chart, community, api_cached
  "source_reference": "FDC ID: 173424",
  "verified": true,
  "verified_by": "expert",  // expert, community, ai
  "accuracy_score": 95,  // 0-100
  "user_ratings": {
    "count": 150,
    "average": 4.8
  },
  
  // User-specific (for custom foods from diet charts)
  "added_by_user_id": null,  // null for public foods
  "is_public": true,
  "is_custom": false,
  
  // Timestamps
  "created_at": "2025-01-15T10:30:00Z",
  "updated_at": "2025-01-15T10:30:00Z",
  "last_verified_at": "2025-01-15T10:30:00Z"
}
```

---

## 📁 Additional Collections

### Collection: `food_categories`
```javascript
{
  "category_id": "protein",
  "name": "Protein",
  "description": "High protein foods",
  "icon": "🥩",
  "color": "#FF6B6B",
  "subcategories": ["eggs", "chicken", "fish", "paneer", "dal", "tofu"]
}
```

### Collection: `user_custom_foods`
```javascript
{
  "custom_food_id": "user123_paneer_tikka",
  "user_id": "user123",
  "name": "Paneer Tikka (Homemade)",
  "based_on_food_id": "paneer_001",  // Reference to base food
  "macros": { /* custom macros */ },
  "notes": "From my nutritionist's diet chart",
  "source_file": "diet_chart_jan_2025.pdf",
  "created_at": "2025-01-15T10:30:00Z"
}
```

### Collection: `food_synonyms`
```javascript
{
  "synonym_id": "anda_001",
  "synonym": "anda",
  "language": "hi",  // Hindi
  "maps_to_food_id": "egg_boiled_001",
  "confidence": 100
}
```

---

## 🔍 Indexes for Fast Queries

```javascript
// Firestore Composite Indexes
1. name (ASC) + category (ASC)
2. aliases (ARRAY) + verified (ASC)
3. search_keywords (ARRAY) + accuracy_score (DESC)
4. category (ASC) + cuisine (ASC) + verified (ASC)
5. user_id (ASC) + is_custom (ASC) + created_at (DESC)
```

---

## 📄 PDF Diet Chart Processing Pipeline

### Step 1: Extract Data from PDFs

```python
# app/services/pdf_processor.py

import PyPDF2
import pdfplumber
import re
from typing import List, Dict

class DietChartProcessor:
    """Extract food data from diet chart PDFs"""
    
    def __init__(self):
        self.openai_client = OpenAIClient()
    
    async def process_pdf(self, pdf_path: str) -> List[Dict]:
        """
        Extract foods from PDF using:
        1. Text extraction
        2. Table detection
        3. OCR (if needed)
        4. AI parsing
        """
        
        # Extract text
        text = self._extract_text(pdf_path)
        
        # Extract tables
        tables = self._extract_tables(pdf_path)
        
        # Parse with AI
        foods = await self._parse_with_ai(text, tables)
        
        return foods
    
    def _extract_text(self, pdf_path: str) -> str:
        """Extract text from PDF"""
        with pdfplumber.open(pdf_path) as pdf:
            text = ""
            for page in pdf.pages:
                text += page.extract_text() + "\n"
        return text
    
    def _extract_tables(self, pdf_path: str) -> List[List[List[str]]]:
        """Extract tables from PDF"""
        tables = []
        with pdfplumber.open(pdf_path) as pdf:
            for page in pdf.pages:
                page_tables = page.extract_tables()
                if page_tables:
                    tables.extend(page_tables)
        return tables
    
    async def _parse_with_ai(self, text: str, tables: List) -> List[Dict]:
        """Use OpenAI to parse food data"""
        
        prompt = f"""
You are a nutrition data extraction expert. Extract all food items from this diet chart.

TEXT:
{text[:5000]}  # Limit to avoid token limits

TABLES:
{str(tables)[:2000]}

For each food item, extract:
- Food name (English & local language if available)
- Quantity/portion
- Macros: calories, protein, carbs, fat, fiber
- Micros: vitamins, minerals (if mentioned)
- Meal type (breakfast, lunch, dinner, snack)
- Any preparation notes

Return as JSON array:
[
  {{
    "name": "Egg, Boiled",
    "name_local": "उबला अंडा",
    "quantity": "2 eggs",
    "meal_type": "breakfast",
    "macros": {{
      "calories": 140,
      "protein_g": 12,
      "carbs_g": 1,
      "fat_g": 10,
      "fiber_g": 0
    }},
    "micros": {{
      "vitamin_a_mcg": 160,
      "calcium_mg": 56,
      "iron_mg": 1.8
    }},
    "preparation": "boiled",
    "notes": "For breakfast"
  }}
]
"""
        
        response = await self.openai_client.chat.completions.create(
            model="gpt-4",
            messages=[{"role": "user", "content": prompt}],
            response_format={"type": "json_object"}
        )
        
        return json.loads(response.choices[0].message.content)
```

---

## 🚀 Implementation Steps

### Phase 1: Database Setup (Today)
1. ✅ Create Firestore collections
2. ✅ Define schema & indexes
3. ✅ Create migration script from current Python dict
4. ✅ Add 500+ common foods from USDA

### Phase 2: PDF Processing (After you provide PDFs)
1. ✅ Install PDF processing libraries
2. ✅ Extract text & tables from your diet PDFs
3. ✅ Use OpenAI to parse food data
4. ✅ Validate & import into Firestore
5. ✅ Create your custom food database

### Phase 3: API Integration (Next)
1. ✅ Integrate USDA FoodData Central API
2. ✅ Add fallback to OpenAI estimation
3. ✅ Implement caching

### Phase 4: Advanced Features (Future)
1. ✅ Community food database
2. ✅ User food ratings
3. ✅ Photo recognition
4. ✅ Barcode scanning

---

## 📦 Required Libraries

```bash
# PDF Processing
pip install PyPDF2
pip install pdfplumber
pip install pytesseract  # OCR (if needed)

# Data Processing
pip install pandas
pip install numpy

# Already installed
# - openai (for AI parsing)
# - google-cloud-firestore (for database)
```

---

## 📊 Database Scalability

### Current Capacity:
- **Firestore Free Tier:**
  - 1 GB storage
  - 50K reads/day
  - 20K writes/day
  - 20K deletes/day

### Scaling Strategy:
- **10,000 foods** = ~50 MB (plenty of room)
- **100,000 foods** = ~500 MB (still within free tier)
- **1M+ foods** = Upgrade to paid tier (~$0.06 per 100K reads)

### Performance:
- **Read latency:** 10-50ms (Firestore)
- **Write latency:** 50-200ms
- **Concurrent users:** 10,000+ (auto-scales)

---

## 🎯 What I Need From You

### 1. PDF Diet Charts
**Please provide:**
- Folder path to your diet chart PDFs
- Any specific format/structure notes
- Which nutrients you want to prioritize

### 2. Preferences
- Focus on Indian foods? International?
- Include micronutrients (vitamins/minerals)?
- Custom portion sizes?

### 3. API Keys (Optional)
- OpenAI API key (for PDF parsing & estimation)
- USDA API (free, no key needed)

---

## ✅ Ready to Start!

**I'm ready when you are!** 

Please provide:
1. **Folder path** to your diet chart PDFs
2. Any **specific requirements** or preferences
3. Confirm you want to proceed with Firestore

Once you provide the folder path, I will:
1. Process all PDFs
2. Extract food data with AI
3. Create comprehensive Firestore database
4. Migrate existing 50 foods
5. Add your custom foods
6. Update code to use Firestore

**This will make your app production-ready with a scalable, elastic database!** 🚀

---

**Ready? Give me the folder path!** 📁

