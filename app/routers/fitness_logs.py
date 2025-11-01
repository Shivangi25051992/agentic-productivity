from __future__ import annotations

from typing import Any, Dict, List, Optional
from datetime import datetime, timezone

from fastapi import APIRouter, HTTPException, Query
from pydantic import BaseModel

from app.models import FitnessLog, FitnessLogType
from app.services.database import (
    create_fitness_log,
    delete_fitness_log,
    get_fitness_log,
    list_fitness_logs_by_user,
    update_fitness_log,
)


router = APIRouter(prefix="/fitness-logs", tags=["fitness_logs"])


def _now_utc() -> datetime:
    return datetime.now(timezone.utc)


class FitnessLogCreate(BaseModel):
    user_id: str
    log_type: FitnessLogType
    content: str
    calories: Optional[int] = None
    timestamp: Optional[datetime] = None
    ai_parsed_data: Dict[str, Any] = {}


class FitnessLogUpdate(BaseModel):
    log_type: Optional[FitnessLogType] = None
    content: Optional[str] = None
    calories: Optional[int] = None
    timestamp: Optional[datetime] = None
    ai_parsed_data: Optional[Dict[str, Any]] = None


@router.post("/", response_model=FitnessLog)
def create_fitness_log_endpoint(payload: FitnessLogCreate) -> FitnessLog:
    values = payload.model_dump()
    if not values.get("timestamp"):
        values["timestamp"] = _now_utc()
    log = FitnessLog(**values)
    return create_fitness_log(log)


@router.get("/{log_id}", response_model=FitnessLog)
def get_fitness_log_endpoint(log_id: str) -> FitnessLog:
    log = get_fitness_log(log_id)
    if not log:
        raise HTTPException(status_code=404, detail="Fitness log not found")
    return log


@router.patch("/{log_id}", response_model=FitnessLog)
def update_fitness_log_endpoint(log_id: str, updates: FitnessLogUpdate) -> FitnessLog:
    updated = update_fitness_log(log_id, {k: v for k, v in updates.model_dump(exclude_none=True).items()})
    if not updated:
        raise HTTPException(status_code=404, detail="Fitness log not found")
    return updated


@router.delete("/{log_id}")
def delete_fitness_log_endpoint(log_id: str) -> Dict[str, bool]:
    deleted = delete_fitness_log(log_id)
    if not deleted:
        raise HTTPException(status_code=404, detail="Fitness log not found")
    return {"deleted": True}


@router.get("/", response_model=List[FitnessLog])
def list_fitness_logs_endpoint(user_id: Optional[str] = Query(None), limit: int = Query(100, ge=1, le=500)) -> List[FitnessLog]:
    if not user_id:
        raise HTTPException(status_code=400, detail="user_id query parameter is required")
    return list_fitness_logs_by_user(user_id=user_id, limit=limit)






