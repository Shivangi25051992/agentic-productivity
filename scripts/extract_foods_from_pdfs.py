#!/usr/bin/env python3
"""
Extract food data from diet chart PDFs and create comprehensive food database
"""

import pdfplumber
import re
import json
from pathlib import Path
from typing import List, Dict, Set
import pandas as pd

class FoodExtractor:
    def __init__(self):
        self.all_foods = {}
        self.unique_foods = set()
        
    def extract_from_pdf(self, pdf_path: str) -> List[Dict]:
        """Extract all food items from a PDF"""
        foods = []
        
        print(f"\n📄 Processing: {Path(pdf_path).name}")
        
        with pdfplumber.open(pdf_path) as pdf:
            for page_num, page in enumerate(pdf.pages, 1):
                # Extract tables
                tables = page.extract_tables()
                
                for table in tables:
                    if not table or len(table) < 2:
                        continue
                    
                    # Check if this is a macronutrients table
                    header = table[0] if table else []
                    if not header:
                        continue
                    
                    # Look for macro columns
                    has_energy = any('Energy' in str(cell) or 'Kcal' in str(cell) for cell in header if cell)
                    has_prot = any('Prot' in str(cell) for cell in header if cell)
                    
                    if has_energy and has_prot:
                        # This is a macronutrients table!
                        foods.extend(self._parse_macro_table(table))
        
        print(f"  ✅ Extracted {len(foods)} food items")
        return foods
    
    def _parse_macro_table(self, table: List[List]) -> List[Dict]:
        """Parse a macronutrients table"""
        foods = []
        
        # Find column indexes
        header = table[0]
        food_col = 0
        energy_col = None
        prot_col = None
        fat_col = None
        carb_col = None
        
        for i, cell in enumerate(header):
            if not cell:
                continue
            cell_str = str(cell).lower()
            if 'energy' in cell_str or 'kcal' in cell_str:
                energy_col = i
            elif 'prot' in cell_str:
                prot_col = i
            elif 'fat' in cell_str:
                fat_col = i
            elif 'carb' in cell_str:
                carb_col = i
        
        # Parse rows
        current_meal_type = None
        
        for row in table[1:]:
            if not row or len(row) < 2:
                continue
            
            food_name = str(row[food_col]) if row[food_col] else ""
            
            # Skip empty rows
            if not food_name or food_name == 'None':
                continue
            
            # Check if this is a meal type header
            if food_name in ['Empty Stomach', 'Breakfast', 'Morning Tea', 'Lunch', 'Evening Tea', 'Dinner', 'Before Bed']:
                current_meal_type = food_name.lower().replace(' ', '_')
                continue
            
            # Skip total rows
            if 'Total for' in food_name or 'Total' == food_name:
                continue
            
            # Extract macros
            try:
                energy = float(row[energy_col]) if energy_col and row[energy_col] and row[energy_col] != 'None' else None
                protein = float(row[prot_col]) if prot_col and row[prot_col] and row[prot_col] != 'None' else None
                fat = float(row[fat_col]) if fat_col and row[fat_col] and row[fat_col] != 'None' else None
                carbs = float(row[carb_col]) if carb_col and row[carb_col] and row[carb_col] != 'None' else None
                
                # Skip if no macros
                if energy is None:
                    continue
                
                # Parse food name and portion
                food_info = self._parse_food_name(food_name)
                
                if food_info:
                    food_data = {
                        **food_info,
                        'meal_type': current_meal_type,
                        'macros': {
                            'calories': energy,
                            'protein_g': protein,
                            'fat_g': fat,
                            'carbs_g': carbs
                        }
                    }
                    
                    foods.append(food_data)
                    
            except (ValueError, IndexError, TypeError) as e:
                # Skip rows with invalid data
                continue
        
        return foods
    
    def _parse_food_name(self, food_text: str) -> Dict:
        """Parse food name and extract portion info"""
        
        # Pattern: "Food Name, quantity (weight g)"
        # Examples:
        # - "Lemon, 1 fruit (2-1/8" dia) (58 g)"
        # - "Boiled Eggs, 1 1 (65 g)"
        # - "Lamb Mince, 1 serving (115 g)"
        # - "Vegetable (Refer Nutritional guide), 1 cup (235 g)"
        
        # Extract weight in grams
        weight_match = re.search(r'\((\d+(?:\.\d+)?)\s*g\)', food_text)
        weight_g = float(weight_match.group(1)) if weight_match else None
        
        # Extract quantity/portion
        portion_patterns = [
            r',\s*(\d+(?:\.\d+)?)\s+(fruit|egg|eggs|serving|servings|cup|cups|tsp|tbsp|teaspoon|tablespoon|portion|portions|half|halves|bunch)',
            r',\s*(\d+(?:\.\d+)?)\s+(\d+)',  # "1 1" means 1 egg
        ]
        
        quantity = None
        unit = None
        
        for pattern in portion_patterns:
            match = re.search(pattern, food_text, re.IGNORECASE)
            if match:
                quantity = match.group(1)
                unit = match.group(2) if len(match.groups()) > 1 else 'piece'
                break
        
        # Clean food name (remove portion info)
        clean_name = re.split(r',\s*\d+', food_text)[0]
        clean_name = re.sub(r'\([^)]*\)', '', clean_name)  # Remove parentheses
        clean_name = clean_name.strip()
        
        # Skip generic vegetables
        if 'Refer Nutritional guide' in clean_name:
            return None
        
        return {
            'name': clean_name,
            'quantity': quantity,
            'unit': unit,
            'weight_g': weight_g
        }
    
    def process_all_pdfs(self, pdf_dir: str) -> Dict:
        """Process all PDFs in directory"""
        pdf_files = list(Path(pdf_dir).glob("*.pdf"))
        
        print(f"\n{'='*80}")
        print(f"🚀 Processing {len(pdf_files)} PDF files")
        print(f"{'='*80}")
        
        all_foods = []
        
        for pdf_file in pdf_files:
            try:
                foods = self.extract_from_pdf(str(pdf_file))
                all_foods.extend(foods)
            except Exception as e:
                print(f"  ❌ Error: {e}")
        
        # Deduplicate and aggregate
        food_database = self._aggregate_foods(all_foods)
        
        print(f"\n{'='*80}")
        print(f"✅ Extraction Complete!")
        print(f"{'='*80}")
        print(f"  Total food entries: {len(all_foods)}")
        print(f"  Unique foods: {len(food_database)}")
        
        return food_database
    
    def _aggregate_foods(self, foods: List[Dict]) -> Dict:
        """Aggregate multiple entries of same food"""
        food_db = {}
        
        for food in foods:
            name = food['name'].lower().strip()
            
            if name not in food_db:
                food_db[name] = {
                    'name': food['name'],
                    'entries': [],
                    'avg_macros': {}
                }
            
            food_db[name]['entries'].append(food)
        
        # Calculate averages
        for name, data in food_db.items():
            entries = data['entries']
            
            # Average macros
            total_cal = sum(e['macros']['calories'] for e in entries if e['macros']['calories'])
            total_prot = sum(e['macros']['protein_g'] for e in entries if e['macros']['protein_g'])
            total_fat = sum(e['macros']['fat_g'] for e in entries if e['macros']['fat_g'])
            total_carbs = sum(e['macros']['carbs_g'] for e in entries if e['macros']['carbs_g'])
            
            count = len(entries)
            
            data['avg_macros'] = {
                'calories': round(total_cal / count, 1),
                'protein_g': round(total_prot / count, 1),
                'fat_g': round(total_fat / count, 1),
                'carbs_g': round(total_carbs / count, 1)
            }
            
            # Get most common portion
            portions = [e for e in entries if e.get('weight_g')]
            if portions:
                avg_weight = sum(p['weight_g'] for p in portions) / len(portions)
                data['avg_weight_g'] = round(avg_weight, 1)
        
        return food_db


if __name__ == "__main__":
    extractor = FoodExtractor()
    
    pdf_dir = "/Users/pchintanwar/Documents/DietCharts/"
    
    food_database = extractor.process_all_pdfs(pdf_dir)
    
    # Save to JSON
    output_file = "/Users/pchintanwar/Documents/Projects-AIProductivity/agentic-productivity/data/extracted_foods.json"
    
    with open(output_file, 'w') as f:
        json.dump(food_database, f, indent=2)
    
    print(f"\n💾 Saved to: {output_file}")
    
    # Print sample
    print(f"\n📊 Sample foods:")
    print(f"{'='*80}")
    for i, (name, data) in enumerate(list(food_database.items())[:10], 1):
        macros = data['avg_macros']
        print(f"{i}. {data['name']}")
        print(f"   Calories: {macros['calories']} kcal")
        print(f"   Protein: {macros['protein_g']}g | Fat: {macros['fat_g']}g | Carbs: {macros['carbs_g']}g")
        print(f"   Entries: {len(data['entries'])}")
        print()

