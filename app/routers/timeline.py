"""
Timeline Router - Unified activity feed
Combines meals, workouts, tasks, events into single chronological timeline
"""
from datetime import datetime, timezone, timedelta
from typing import List, Optional, Set
from fastapi import APIRouter, Depends, Query
import logging

from app.models import User
from app.services import auth as auth_service
from app.services import database as dbsvc
from app.services.cache_service import cache_service  # 🚀 REDIS CACHE
from app.models.fitness_log import FitnessLogType
from app.models.task import TaskStatus
from pydantic import BaseModel

logger = logging.getLogger(__name__)


router = APIRouter(prefix="/timeline", tags=["timeline"])


class TimelineActivity(BaseModel):
    """Unified activity model for timeline"""
    id: str
    type: str  # meal, workout, task, event, water, supplement
    title: str
    timestamp: datetime
    icon: str
    color: str
    status: str
    details: dict
    due_date: Optional[datetime] = None
    priority: Optional[str] = None
    client_generated_id: Optional[str] = None  # 🔑 For optimistic UI matching


class TimelineResponse(BaseModel):
    """Timeline API response"""
    activities: List[TimelineActivity]
    total_count: int
    has_more: bool
    next_offset: int


def _fitness_log_to_activity(log) -> TimelineActivity:
    """Convert FitnessLog to TimelineActivity"""
    
    # Determine icon and color based on log type
    type_config = {
        "meal": {"icon": "restaurant", "color": "green"},
        "workout": {"icon": "fitness_center", "color": "blue"},
        "water": {"icon": "water_drop", "color": "lightblue"},
        "supplement": {"icon": "medication", "color": "purple"},
    }
    
    config = type_config.get(log.log_type.value, {"icon": "circle", "color": "grey"})
    
    # Build title based on type
    if log.log_type == FitnessLogType.meal:
        meal_type = log.ai_parsed_data.get("meal_type", "snack") if log.ai_parsed_data else "snack"
        title = f"{meal_type.capitalize()} - {log.content[:50]}"
    elif log.log_type == FitnessLogType.workout:
        activity = log.ai_parsed_data.get("activity_type", "workout") if log.ai_parsed_data else "workout"
        title = f"{activity.capitalize()} - {log.content[:50]}"
    else:
        title = log.content[:50]
    
    # Build details
    details = {
        "content": log.content,
        "calories": log.calories,
    }
    
    if log.ai_parsed_data:
        details.update(log.ai_parsed_data)
    
    return TimelineActivity(
        id=log.log_id,
        type=log.log_type.value,
        title=title,
        timestamp=log.timestamp,
        icon=config["icon"],
        color=config["color"],
        status="completed",
        details=details,
        client_generated_id=getattr(log, 'client_generated_id', None),  # 🔑 Include if present
    )


def _task_to_activity(task) -> TimelineActivity:
    """Convert Task to TimelineActivity"""
    
    # Determine status display
    status_map = {
        "pending": "pending",
        "in_progress": "in_progress",
        "completed": "completed",
        "cancelled": "cancelled",
    }
    
    # Determine color based on priority
    priority_colors = {
        "low": "grey",
        "medium": "orange",
        "high": "red",
    }
    
    return TimelineActivity(
        id=task.task_id,
        type="task",
        title=task.title,
        timestamp=task.due_date or task.created_at,  # Use due_date if available, else created_at
        icon="check_circle",
        color=priority_colors.get(task.priority.value, "orange"),
        status=status_map.get(task.status.value, "pending"),
        details={
            "description": task.description,
            "priority": task.priority.value,
            "status": task.status.value,
            "created_at": task.created_at.isoformat(),
        },
        due_date=task.due_date,
        priority=task.priority.value,
    )


@router.get("", response_model=TimelineResponse)
async def get_timeline(
    start_date: Optional[str] = Query(None, description="Start date (YYYY-MM-DD)"),
    end_date: Optional[str] = Query(None, description="End date (YYYY-MM-DD)"),
    types: Optional[str] = Query(
        None, 
        description="Comma-separated activity types (meal,workout,task,event,water,supplement)"
    ),
    limit: int = Query(50, ge=1, le=200),
    offset: int = Query(0, ge=0),
    current_user: User = Depends(auth_service.get_current_user),
):
    """
    Get unified timeline of all activities
    
    Returns meals, workouts, tasks, events in chronological order
    with optional filtering by type and date range.
    
    🚀 REDIS CACHE: Caches timeline data for 5 minutes (configurable)
    """
    
    # Parse date range
    start_ts = None
    end_ts = None
    
    if start_date:
        try:
            start_ts = datetime.fromisoformat(start_date).replace(tzinfo=timezone.utc)
        except ValueError:
            pass
    
    if end_date:
        try:
            end_ts = datetime.fromisoformat(end_date).replace(tzinfo=timezone.utc)
        except ValueError:
            pass
    
    # Default to last 30 days if no date range specified
    if not start_ts and not end_ts:
        end_ts = datetime.now(timezone.utc)
        start_ts = end_ts - timedelta(days=30)
    
    # 🔍 DEBUG: Log date range
    logger.info(f"🔍 [TIMELINE] Date range: {start_ts} to {end_ts}")
    logger.info(f"🔍 [TIMELINE] Params: start_date={start_date}, end_date={end_date}")
    
    # Parse activity types filter
    selected_types: Set[str] = set()
    if types:
        selected_types = set(types.split(","))
    else:
        # Default: show all types
        selected_types = {"meal", "workout", "task", "event", "water", "supplement"}
    
    # 🚫 CACHE DISABLED: Always fetch fresh data (no Redis cache for timeline)
    # This ensures logs appear immediately after saving
    types_str = ",".join(sorted(selected_types))
    cached_data = None  # Force cache miss
    if False and offset == 0:  # Cache disabled
        cached_data = cache_service.get_timeline(
            user_id=current_user.user_id,
            types=types_str,
            start_date=start_date,
            end_date=end_date,
        )
        
        if cached_data:
            logger.info(f"⚡ Timeline cache HIT for user {current_user.user_id}")
            # Apply pagination to cached data
            cached_activities = [TimelineActivity(**act) for act in cached_data.get("activities", [])]
            total_count = len(cached_activities)
            paginated_activities = cached_activities[offset:offset + limit]
            has_more = (offset + limit) < total_count
            next_offset = offset + limit if has_more else offset
            
            return TimelineResponse(
                activities=paginated_activities,
                total_count=total_count,
                has_more=has_more,
                next_offset=next_offset,
            )
    
    # Fetch activities from different sources
    all_activities: List[TimelineActivity] = []
    
    # 1. Fetch fitness logs (meals, workouts, water, supplements)
    if any(t in selected_types for t in ["meal", "workout", "water", "supplement"]):
        try:
            fitness_logs = dbsvc.list_fitness_logs_by_user(
                user_id=current_user.user_id,
                start_ts=start_ts,
                end_ts=end_ts,
                limit=500,  # Fetch more, we'll paginate later
            )
            
            logger.info(f"📊 [TIMELINE] Fetched {len(fitness_logs)} fitness logs from DB")
            
            for log in fitness_logs:
                if log.log_type.value in selected_types:
                    activity = _fitness_log_to_activity(log)
                    all_activities.append(activity)
                    logger.info(f"  ✅ Added {log.log_type.value}: {log.content[:50]}")
            
            logger.info(f"📊 [TIMELINE] Total activities after fitness logs: {len(all_activities)}")
        except Exception as e:
            print(f"Error fetching fitness logs: {e}")
    
    # 2. Fetch tasks
    if "task" in selected_types:
        try:
            # Fetch all tasks (not just those with due dates)
            tasks = dbsvc.list_tasks_by_user(
                user_id=current_user.user_id,
                limit=500,
            )
            
            for task in tasks:
                # Filter by date range if specified
                task_timestamp = task.due_date or task.created_at
                if start_ts and task_timestamp < start_ts:
                    continue
                if end_ts and task_timestamp > end_ts:
                    continue
                
                all_activities.append(_task_to_activity(task))
        except Exception as e:
            print(f"Error fetching tasks: {e}")
    
    # 3. TODO: Fetch events (when implemented)
    # if "event" in selected_types:
    #     events = fetch_events(...)
    #     all_activities.extend(events)
    
    # Sort by timestamp (most recent first)
    all_activities.sort(key=lambda x: x.timestamp, reverse=True)
    
    # 🚫 REDIS CACHE DISABLED: Don't cache Timeline (ensures fresh data)
    # Caching causes stale data issues - logs don't appear immediately after saving
    if False and offset == 0:  # Cache disabled
        cache_data = {
            "activities": [act.model_dump() for act in all_activities],
            "cached_at": datetime.now(timezone.utc).isoformat(),
        }
        cache_service.set_timeline(
            user_id=current_user.user_id,
            data=cache_data,
            types=types_str,
            start_date=start_date,
            end_date=end_date,
        )
        logger.info(f"✅ Timeline cached for user {current_user.user_id}")
    
    # Apply pagination
    total_count = len(all_activities)
    paginated_activities = all_activities[offset:offset + limit]
    has_more = (offset + limit) < total_count
    next_offset = offset + limit if has_more else offset
    
    return TimelineResponse(
        activities=paginated_activities,
        total_count=total_count,
        has_more=has_more,
        next_offset=next_offset,
    )


@router.get("/stats")
async def get_timeline_stats(
    start_date: Optional[str] = Query(None),
    end_date: Optional[str] = Query(None),
    current_user: User = Depends(auth_service.get_current_user),
):
    """
    Get timeline statistics (counts by type)
    """
    
    # Parse dates
    start_ts = None
    end_ts = None
    
    if start_date:
        try:
            start_ts = datetime.fromisoformat(start_date).replace(tzinfo=timezone.utc)
        except ValueError:
            pass
    
    if end_date:
        try:
            end_ts = datetime.fromisoformat(end_date).replace(tzinfo=timezone.utc)
        except ValueError:
            pass
    
    # Default to last 30 days
    if not start_ts and not end_ts:
        end_ts = datetime.now(timezone.utc)
        start_ts = end_ts - timedelta(days=30)
    
    # Count activities by type
    stats = {
        "meal": 0,
        "workout": 0,
        "task": 0,
        "event": 0,
        "water": 0,
        "supplement": 0,
    }
    
    # Count fitness logs
    try:
        fitness_logs = dbsvc.list_fitness_logs_by_user(
            user_id=current_user.user_id,
            start_ts=start_ts,
            end_ts=end_ts,
            limit=1000,
        )
        
        for log in fitness_logs:
            log_type = log.log_type.value
            if log_type in stats:
                stats[log_type] += 1
    except Exception as e:
        print(f"Error counting fitness logs: {e}")
    
    # Count tasks
    try:
        tasks = dbsvc.list_tasks_by_user(
            user_id=current_user.user_id,
            limit=1000,
        )
        
        for task in tasks:
            task_timestamp = task.due_date or task.created_at
            if start_ts and task_timestamp < start_ts:
                continue
            if end_ts and task_timestamp > end_ts:
                continue
            stats["task"] += 1
    except Exception as e:
        print(f"Error counting tasks: {e}")
    
    return {
        "stats": stats,
        "total": sum(stats.values()),
        "start_date": start_ts.isoformat() if start_ts else None,
        "end_date": end_ts.isoformat() if end_ts else None,
    }

