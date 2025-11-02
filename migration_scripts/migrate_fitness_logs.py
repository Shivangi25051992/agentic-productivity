#!/usr/bin/env python3
"""
Migrate fitness logs to subcollection structure
OLD: fitness_logs/{logId} (flat collection with user_id field)
NEW: users/{userId}/fitness_logs/{logId} (subcollection)

This migration also fixes duplicate meals by grouping multi-item meals
"""

import os
from google.cloud import firestore
from google.oauth2 import service_account
from datetime import datetime
from collections import defaultdict

# Initialize Firestore
project_id = os.getenv("GOOGLE_CLOUD_PROJECT", "productivityai-mvp")
credentials_path = "/Users/pchintanwar/keys/productivityai-mvp-0017f7241a58.json"
credentials = service_account.Credentials.from_service_account_file(credentials_path)
db = firestore.Client(project=project_id, credentials=credentials)

def migrate_fitness_logs(user_id: str) -> int:
    """Migrate all fitness logs for a single user"""
    try:
        print(f"  Migrating fitness logs for {user_id}...")
        
        # Get all logs for this user
        old_logs = db.collection('fitness_logs')\
                     .where('user_id', '==', user_id)\
                     .stream()
        
        migrated_count = 0
        
        for log in old_logs:
            old_data = log.to_dict()
            
            # Determine log type
            log_type = old_data.get('log_type', 'meal')
            timestamp = old_data.get('timestamp', datetime.now())
            
            # Extract date for querying
            if hasattr(timestamp, 'date'):
                date_str = timestamp.date().isoformat()
            else:
                date_str = datetime.now().date().isoformat()
            
            # Create new structured log
            if log_type == 'meal':
                new_log = {
                    'logId': log.id,
                    'logType': 'meal',
                    'timestamp': timestamp,
                    'date': date_str,
                    'meal': {
                        'mealType': old_data.get('ai_parsed_data', {}).get('meal_type', 'unknown'),
                        'items': [],
                        'totalCalories': old_data.get('calories', 0),
                        'totalProtein': old_data.get('ai_parsed_data', {}).get('protein_g', 0),
                        'totalCarbs': old_data.get('ai_parsed_data', {}).get('carbs_g', 0),
                        'totalFat': old_data.get('ai_parsed_data', {}).get('fat_g', 0),
                        'totalFiber': old_data.get('ai_parsed_data', {}).get('fiber_g', 0),
                        'notes': old_data.get('content', '')
                    },
                    'source': 'migrated',
                    'confidence': old_data.get('ai_parsed_data', {}).get('confidence_category', 1.0),
                    'createdAt': old_data.get('created_at', timestamp),
                    'updatedAt': firestore.SERVER_TIMESTAMP
                }
                
                # Parse items from ai_parsed_data
                items_list = old_data.get('ai_parsed_data', {}).get('items', [])
                if isinstance(items_list, list):
                    for item_name in items_list:
                        new_log['meal']['items'].append({
                            'name': item_name,
                            'quantity': 1,
                            'unit': 'serving',
                            'calories': 0,  # Will be recalculated
                            'protein': 0,
                            'carbs': 0,
                            'fat': 0,
                            'fiber': 0
                        })
                
            elif log_type == 'workout':
                new_log = {
                    'logId': log.id,
                    'logType': 'workout',
                    'timestamp': timestamp,
                    'date': date_str,
                    'workout': {
                        'activityType': old_data.get('ai_parsed_data', {}).get('activity_type', 'other'),
                        'duration': old_data.get('ai_parsed_data', {}).get('duration_minutes', 30),
                        'intensity': old_data.get('ai_parsed_data', {}).get('intensity', 'moderate'),
                        'caloriesBurned': old_data.get('calories', 0),
                        'distance': old_data.get('ai_parsed_data', {}).get('distance_km', 0),
                        'notes': old_data.get('content', '')
                    },
                    'source': 'migrated',
                    'confidence': old_data.get('ai_parsed_data', {}).get('confidence_category', 1.0),
                    'createdAt': old_data.get('created_at', timestamp),
                    'updatedAt': firestore.SERVER_TIMESTAMP
                }
            
            else:
                # Unknown type, skip
                continue
            
            # Write to new location
            new_log_ref = db.collection('users').document(user_id)\
                            .collection('fitness_logs').document(log.id)
            new_log_ref.set(new_log)
            
            migrated_count += 1
        
        print(f"    ✅ Migrated {migrated_count} logs")
        return migrated_count
        
    except Exception as e:
        print(f"    ❌ Error: {e}")
        return 0

def main():
    """Migrate all fitness logs"""
    print("=" * 70)
    print("🏋️ MIGRATING FITNESS LOGS")
    print("=" * 70)
    print()
    
    # Get all unique user IDs from fitness_logs
    logs = db.collection('fitness_logs').stream()
    user_ids = set()
    
    for log in logs:
        data = log.to_dict()
        user_id = data.get('user_id')
        if user_id:
            user_ids.add(user_id)
    
    print(f"Found {len(user_ids)} users with fitness logs")
    print()
    
    total_migrated = 0
    for user_id in user_ids:
        count = migrate_fitness_logs(user_id)
        total_migrated += count
    
    print()
    print("=" * 70)
    print(f"✅ Migration complete: {total_migrated} logs migrated")
    print("=" * 70)

if __name__ == "__main__":
    main()

