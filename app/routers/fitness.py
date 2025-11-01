from __future__ import annotations

from collections import defaultdict
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional

from fastapi import APIRouter, Depends, HTTPException, Query, status
from pydantic import BaseModel, Field

from app.models import FitnessLog, FitnessLogType, User
from app.services.ai import parse_natural_language_fitness
from app.services.auth import get_current_user
from app.services.database import (
    create_fitness_log,
    list_fitness_logs_by_user,
    get_fitness_log,
    update_fitness_log,
    delete_fitness_log,
)


router = APIRouter(prefix="/fitness", tags=["fitness"])


def _ensure_utc(dt: Optional[datetime]) -> Optional[datetime]:
    if dt is None:
        return None
    if dt.tzinfo is None:
        return dt.replace(tzinfo=timezone.utc)
    return dt.astimezone(timezone.utc)


class FitnessNLRequest(BaseModel):
    text: str = Field(min_length=1, max_length=1000)


@router.post("/log", response_model=FitnessLog, status_code=status.HTTP_201_CREATED)
def create_fitness_log_nl(payload: FitnessNLRequest, current_user: User = Depends(get_current_user)) -> FitnessLog:
    parsed = parse_natural_language_fitness(payload.text)
    log = FitnessLog(
        user_id=current_user.user_id,
        log_type=parsed.log_type,
        content=parsed.content,
        calories=parsed.calories,
        timestamp=_ensure_utc(parsed.timestamp) or datetime.now(timezone.utc),
        ai_parsed_data=parsed.ai_parsed_data,
    )
    return create_fitness_log(log)


@router.get("/logs", response_model=List[FitnessLog])
def get_fitness_logs(
    start: Optional[datetime] = Query(None),
    end: Optional[datetime] = Query(None),
    log_type: Optional[FitnessLogType] = Query(None),
    limit: int = Query(200, ge=1, le=1000),
    current_user: User = Depends(get_current_user),
) -> List[FitnessLog]:
    return list_fitness_logs_by_user(
        user_id=current_user.user_id,
        start_ts=_ensure_utc(start) if start else None,
        end_ts=_ensure_utc(end) if end else None,
        log_type=log_type,
        limit=limit,
    )


class StatsResponse(BaseModel):
    daily_calories: Dict[str, int] = Field(default_factory=dict)
    weekly_calories: Dict[str, int] = Field(default_factory=dict)
    workout_summary: Dict[str, int] = Field(default_factory=dict)


@router.get("/stats", response_model=StatsResponse)
def get_stats(
    start: Optional[datetime] = Query(None),
    end: Optional[datetime] = Query(None),
    current_user: User = Depends(get_current_user),
) -> StatsResponse:
    logs = list_fitness_logs_by_user(
        user_id=current_user.user_id,
        start_ts=_ensure_utc(start) if start else None,
        end_ts=_ensure_utc(end) if end else None,
        limit=1000,
    )

    daily_calories: Dict[str, int] = defaultdict(int)
    weekly_calories: Dict[str, int] = defaultdict(int)
    workout_summary: Dict[str, int] = defaultdict(int)

    for log in logs:
        ts = log.timestamp
        if ts.tzinfo is None:
            ts = ts.replace(tzinfo=timezone.utc)
        ts = ts.astimezone(timezone.utc)
        day_key = ts.strftime("%Y-%m-%d")
        week_key = ts.strftime("%Y-W%V")

        if log.log_type == FitnessLogType.meal and isinstance(log.calories, int):
            daily_calories[day_key] += log.calories
            weekly_calories[week_key] += log.calories
        elif log.log_type == FitnessLogType.workout:
            workout_summary[day_key] += 1

    return StatsResponse(
        daily_calories=dict(daily_calories),
        weekly_calories=dict(weekly_calories),
        workout_summary=dict(workout_summary),
    )


class FitnessLogUpdateRequest(BaseModel):
    """Request model for updating a fitness log"""
    content: Optional[str] = None
    calories: Optional[int] = Field(None, ge=0, le=10000)
    ai_parsed_data: Optional[Dict[str, Any]] = None


@router.put("/logs/{log_id}", response_model=FitnessLog)
def update_fitness_log_endpoint(
    log_id: str,
    update_data: FitnessLogUpdateRequest,
    current_user: User = Depends(get_current_user),
) -> FitnessLog:
    """
    Update a fitness log (meal or workout).
    Allows manual adjustment of calories, content, and parsed data.
    """
    # Get existing log
    existing_log = get_fitness_log(log_id)
    if not existing_log:
        raise HTTPException(status_code=404, detail="Fitness log not found")
    
    # Verify ownership
    if existing_log.user_id != current_user.user_id:
        raise HTTPException(status_code=403, detail="Not authorized to update this log")
    
    # Prepare updates
    updates = {}
    if update_data.content is not None:
        updates["content"] = update_data.content
    if update_data.calories is not None:
        updates["calories"] = update_data.calories
    if update_data.ai_parsed_data is not None:
        updates["ai_parsed_data"] = update_data.ai_parsed_data
    
    # Save updated log
    updated_log = update_fitness_log(log_id, updates)
    if not updated_log:
        raise HTTPException(status_code=500, detail="Failed to update log")
    return updated_log


@router.delete("/logs/{log_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_fitness_log_endpoint(
    log_id: str,
    current_user: User = Depends(get_current_user),
) -> None:
    """
    Delete a fitness log.
    """
    # Get existing log
    existing_log = get_fitness_log(log_id)
    if not existing_log:
        raise HTTPException(status_code=404, detail="Fitness log not found")
    
    # Verify ownership
    if existing_log.user_id != current_user.user_id:
        raise HTTPException(status_code=403, detail="Not authorized to delete this log")
    
    # Delete log
    success = delete_fitness_log(log_id)
    if not success:
        raise HTTPException(status_code=500, detail="Failed to delete log")
    return None



