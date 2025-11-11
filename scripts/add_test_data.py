#!/usr/bin/env python3
"""
Add test data to Firestore for realistic benchmarking

This script adds 100+ fitness logs to test index performance
with a realistic dataset size.

Usage:
    python scripts/add_test_data.py [--count 100]
"""

import sys
import os
import argparse
from datetime import datetime, timedelta, timezone
import random

# Add parent directory to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from google.cloud import firestore
import uuid

# Initialize Firestore
db = firestore.Client()

# Sample data
FOODS = [
    ("eggs", 2, "meal", 140, 12, 10, 1),
    ("chicken breast", 150, "meal", 165, 31, 0, 3.6),
    ("brown rice", 100, "meal", 111, 2.6, 23, 0.9),
    ("almonds", 20, "meal", 115, 4.3, 4.3, 10),
    ("banana", 1, "meal", 105, 1.3, 27, 0.4),
    ("protein shake", 1, "meal", 120, 24, 3, 1.5),
    ("salmon", 150, "meal", 280, 39, 0, 13),
    ("broccoli", 100, "meal", 34, 2.8, 7, 0.4),
    ("sweet potato", 150, "meal", 129, 2, 30, 0.2),
    ("greek yogurt", 200, "meal", 130, 20, 9, 0),
]

MEAL_TYPES = ["breakfast", "lunch", "dinner", "snack"]
WORKOUT_TYPES = ["cardio", "strength", "yoga", "hiit"]

def add_fitness_logs(user_id: str, count: int = 100):
    """
    Add test fitness logs to Firestore
    
    Args:
        user_id: User ID to add logs for
        count: Number of logs to add
    """
    
    print(f"\n{'='*60}")
    print(f"ADDING {count} TEST FITNESS LOGS")
    print(f"{'='*60}")
    print(f"User ID: {user_id}")
    print(f"Target count: {count}")
    print(f"{'='*60}\n")
    
    logs_ref = db.collection('users').document(user_id).collection('fitness_logs')
    
    # Get current count
    existing = len(list(logs_ref.limit(500).stream()))
    print(f"Existing logs: {existing}")
    
    if existing >= count:
        print(f"✅ Already have {existing} logs (target: {count})")
        return
    
    to_add = count - existing
    print(f"Adding {to_add} new logs...\n")
    
    # Generate logs over the past 30 days
    end_date = datetime.now(timezone.utc)
    start_date = end_date - timedelta(days=30)
    
    batch = db.batch()
    batch_count = 0
    total_added = 0
    
    for i in range(to_add):
        # Random timestamp in the past 30 days
        random_days = random.uniform(0, 30)
        timestamp = end_date - timedelta(days=random_days)
        
        # 70% meals, 20% workouts, 10% water
        log_type_rand = random.random()
        
        if log_type_rand < 0.7:
            # Meal log
            food_name, quantity, _, calories, protein, carbs, fat = random.choice(FOODS)
            meal_type = random.choice(MEAL_TYPES)
            
            log_data = {
                'log_id': str(uuid.uuid4()),
                'user_id': user_id,
                'log_type': 'meal',
                'content': f"{food_name} x{quantity}",
                'timestamp': timestamp,
                'calories': calories,
                'ai_parsed_data': {
                    'meal_type': meal_type,
                    'food_name': food_name,
                    'quantity': quantity,
                    'protein_g': protein,
                    'carbs_g': carbs,
                    'fat_g': fat,
                },
                'created_at': timestamp,
            }
        elif log_type_rand < 0.9:
            # Workout log
            workout_type = random.choice(WORKOUT_TYPES)
            duration = random.randint(20, 60)
            calories_burned = random.randint(150, 500)
            
            log_data = {
                'log_id': str(uuid.uuid4()),
                'user_id': user_id,
                'log_type': 'workout',
                'content': f"{workout_type} for {duration} minutes",
                'timestamp': timestamp,
                'calories': -calories_burned,  # Negative for burned
                'ai_parsed_data': {
                    'workout_type': workout_type,
                    'duration_minutes': duration,
                    'calories_burned': calories_burned,
                },
                'created_at': timestamp,
            }
        else:
            # Water log
            glasses = random.randint(1, 3)
            ml = glasses * 250
            
            log_data = {
                'log_id': str(uuid.uuid4()),
                'user_id': user_id,
                'log_type': 'water',
                'content': f"{glasses} glasses of water",
                'timestamp': timestamp,
                'calories': 0,
                'ai_parsed_data': {
                    'glasses': glasses,
                    'ml': ml,
                },
                'created_at': timestamp,
            }
        
        # Add to batch
        doc_ref = logs_ref.document(log_data['log_id'])
        batch.set(doc_ref, log_data)
        batch_count += 1
        total_added += 1
        
        # Commit batch every 500 operations (Firestore limit)
        if batch_count >= 500:
            batch.commit()
            print(f"  ✅ Committed batch: {total_added}/{to_add} logs added")
            batch = db.batch()
            batch_count = 0
    
    # Commit remaining
    if batch_count > 0:
        batch.commit()
        print(f"  ✅ Committed final batch: {total_added}/{to_add} logs added")
    
    print(f"\n{'='*60}")
    print(f"✅ SUCCESSFULLY ADDED {total_added} LOGS")
    print(f"{'='*60}")
    print(f"Total logs now: {existing + total_added}")
    print(f"{'='*60}\n")

def main():
    parser = argparse.ArgumentParser(description='Add test data to Firestore')
    parser.add_argument('--count', type=int, default=100,
                        help='Number of logs to add (default: 100)')
    parser.add_argument('--user-id', type=str, 
                        default='mLNCSrl01vhubtZXJYj7R4kEQ8g2',
                        help='User ID to add logs for')
    
    args = parser.parse_args()
    
    try:
        add_fitness_logs(args.user_id, args.count)
        print("✅ Test data added successfully!")
        print("\nNext steps:")
        print("  1. Run benchmark: python scripts/benchmark_timeline.py")
        print("  2. Compare results to see index impact with larger dataset")
        
    except Exception as e:
        print(f"\n❌ Error adding test data: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

if __name__ == "__main__":
    main()

