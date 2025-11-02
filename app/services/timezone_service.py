"""
Timezone Service - Handle user timezone conversions
"""
from datetime import datetime
from typing import Optional
import pytz
from google.cloud import firestore
import os


def _get_firestore_db():
    """Get Firestore client"""
    project = os.getenv("GOOGLE_CLOUD_PROJECT", "productivityai-mvp")
    return firestore.Client(project=project)


def get_user_timezone(user_id: str) -> str:
    """
    Get user's timezone from their profile.
    Returns 'UTC' if not found or on error.
    """
    try:
        db = _get_firestore_db()
        doc = db.collection("user_profiles").document(user_id).get()
        
        if doc.exists:
            profile_data = doc.to_dict()
            return profile_data.get("timezone", "UTC")
        
        return "UTC"
    except Exception as e:
        print(f"Error fetching user timezone: {e}")
        return "UTC"


def get_user_local_time(user_id: str) -> datetime:
    """
    Get current time in user's timezone.
    Returns datetime object in user's local timezone.
    """
    user_tz_str = get_user_timezone(user_id)
    
    try:
        user_tz = pytz.timezone(user_tz_str)
        utc_now = datetime.now(pytz.UTC)
        local_time = utc_now.astimezone(user_tz)
        return local_time
    except Exception as e:
        print(f"Error converting to user timezone {user_tz_str}: {e}")
        # Fallback to UTC
        return datetime.now(pytz.UTC)


def convert_to_user_timezone(utc_time: datetime, user_id: str) -> datetime:
    """
    Convert a UTC datetime to user's timezone.
    """
    user_tz_str = get_user_timezone(user_id)
    
    try:
        user_tz = pytz.timezone(user_tz_str)
        
        # Ensure utc_time is timezone-aware
        if utc_time.tzinfo is None:
            utc_time = pytz.UTC.localize(utc_time)
        
        local_time = utc_time.astimezone(user_tz)
        return local_time
    except Exception as e:
        print(f"Error converting to user timezone {user_tz_str}: {e}")
        return utc_time


def classify_meal_type_by_time(user_id: str, timestamp: Optional[datetime] = None) -> tuple[str, float]:
    """
    Classify meal type based on time in user's timezone.
    
    Returns:
        tuple: (meal_type, confidence)
    """
    if timestamp:
        # Convert provided timestamp to user's timezone
        local_time = convert_to_user_timezone(timestamp, user_id)
    else:
        # Get current time in user's timezone
        local_time = get_user_local_time(user_id)
    
    hour = local_time.hour
    
    # Time-based classification
    if 5 <= hour < 11:
        return "breakfast", 0.9
    elif 11 <= hour < 15:
        return "lunch", 0.9
    elif 15 <= hour < 18:
        return "snack", 0.8
    elif 18 <= hour < 23:
        return "dinner", 0.9
    else:
        return "late_night_snack", 0.7

