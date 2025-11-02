"""
Cloud Function: Update Daily Stats
Runs hourly to denormalize daily/weekly stats for fast dashboard loading
"""

from google.cloud import firestore
from datetime import datetime, timedelta, timezone
import functions_framework

@functions_framework.cloud_event
def update_daily_stats(cloud_event):
    """
    Scheduled function to update denormalized daily stats
    Trigger: Cloud Scheduler (hourly)
    """
    db = firestore.Client()
    today = datetime.now(timezone.utc).date()
    
    updated_users = 0
    
    try:
        # Get all users
        users_ref = db.collection('users')
        
        for user_doc in users_ref.stream():
            user_id = user_doc.id
            
            # Calculate today's stats
            stats = calculate_daily_stats(db, user_id, today)
            
            # Save to denormalized collection
            stats_ref = user_doc.reference.collection('daily_stats').document(str(today))
            stats_ref.set(stats, merge=True)
            
            updated_users += 1
            print(f"Updated stats for user {user_id}")
        
        print(f"Stats update complete: {updated_users} users updated")
        
        return {
            'status': 'success',
            'updated_users': updated_users
        }
        
    except Exception as e:
        print(f"Error updating stats: {e}")
        return {
            'status': 'error',
            'error': str(e)
        }


def calculate_daily_stats(db, user_id: str, date) -> dict:
    """Calculate stats for a specific day"""
    start_of_day = datetime.combine(date, datetime.min.time()).replace(tzinfo=timezone.utc)
    end_of_day = datetime.combine(date, datetime.max.time()).replace(tzinfo=timezone.utc)
    
    # Get fitness logs for the day
    logs_ref = db.collection('users').document(user_id).collection('fitness_logs')
    logs_query = logs_ref.where('timestamp', '>=', start_of_day)\
                         .where('timestamp', '<=', end_of_day)
    
    total_calories = 0
    total_protein = 0
    total_carbs = 0
    total_fat = 0
    meal_count = 0
    workout_count = 0
    workout_minutes = 0
    
    for log in logs_query.stream():
        log_data = log.to_dict()
        log_type = log_data.get('log_type', '')
        
        if log_type == 'meal':
            meal_count += 1
            total_calories += log_data.get('calories', 0)
            
            ai_data = log_data.get('ai_parsed_data', {})
            total_protein += ai_data.get('protein_g', 0)
            total_carbs += ai_data.get('carbs_g', 0)
            total_fat += ai_data.get('fat_g', 0)
            
        elif log_type == 'workout':
            workout_count += 1
            ai_data = log_data.get('ai_parsed_data', {})
            workout_minutes += ai_data.get('duration_minutes', 0)
            total_calories -= log_data.get('calories', 0)  # Subtract burned calories
    
    # Get user's goal
    profile_ref = db.collection('users').document(user_id).collection('profile').document('doc')
    profile = profile_ref.get()
    
    daily_calorie_goal = 2000  # Default
    if profile.exists:
        profile_data = profile.to_dict()
        daily_calorie_goal = profile_data.get('dailyCalorieGoal', 2000)
    
    # Calculate deficit/surplus
    calorie_balance = total_calories - daily_calorie_goal
    
    return {
        'date': str(date),
        'totalCalories': total_calories,
        'totalProtein': total_protein,
        'totalCarbs': total_carbs,
        'totalFat': total_fat,
        'mealCount': meal_count,
        'workoutCount': workout_count,
        'workoutMinutes': workout_minutes,
        'dailyCalorieGoal': daily_calorie_goal,
        'calorieBalance': calorie_balance,
        'isInDeficit': calorie_balance < 0,
        'updatedAt': firestore.SERVER_TIMESTAMP
    }

