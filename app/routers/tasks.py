from __future__ import annotations

from datetime import datetime, timezone
from typing import Any, Dict, List, Optional

from fastapi import APIRouter, Depends, HTTPException, Query, status
from pydantic import BaseModel, Field

from app.models import Task, TaskPriority, TaskStatus, User
from app.services.ai import parse_natural_language_task
from app.services.auth import get_current_user
from app.services.database import create_task, delete_task, get_task, list_tasks_by_user, update_task


router = APIRouter(prefix="/tasks", tags=["tasks"])


def _now_utc() -> datetime:
    return datetime.now(timezone.utc)


class TaskCreate(BaseModel):
    title: str = Field(min_length=1, max_length=200)
    description: Optional[str] = None
    due_date: Optional[datetime] = None
    priority: TaskPriority = TaskPriority.medium
    status: TaskStatus = TaskStatus.pending


class TaskUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    due_date: Optional[datetime] = None
    priority: Optional[TaskPriority] = None
    status: Optional[TaskStatus] = None


@router.post("/", response_model=Task)
def create_task_endpoint(payload: TaskCreate, current_user: User = Depends(get_current_user)) -> Task:
    task = Task(user_id=current_user.user_id, **payload.model_dump())
    return create_task(task)


@router.get("/{task_id}", response_model=Task)
def get_task_endpoint(task_id: str, current_user: User = Depends(get_current_user)) -> Task:
    task = get_task(task_id)
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    if task.user_id != current_user.user_id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Forbidden")
    return task


@router.patch("/{task_id}", response_model=Task)
def update_task_endpoint(task_id: str, updates: TaskUpdate, current_user: User = Depends(get_current_user)) -> Task:
    existing = get_task(task_id)
    if not existing:
        raise HTTPException(status_code=404, detail="Task not found")
    if existing.user_id != current_user.user_id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Forbidden")
    update_dict: Dict[str, Any] = updates.model_dump(exclude_none=True)
    update_dict["updated_at"] = _now_utc()
    updated = update_task(task_id, update_dict)
    if not updated:
        raise HTTPException(status_code=404, detail="Task not found")
    return updated


@router.delete("/{task_id}")
def delete_task_endpoint(task_id: str, current_user: User = Depends(get_current_user)) -> Dict[str, bool]:
    existing = get_task(task_id)
    if not existing:
        raise HTTPException(status_code=404, detail="Task not found")
    if existing.user_id != current_user.user_id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Forbidden")
    deleted = delete_task(task_id)
    if not deleted:
        raise HTTPException(status_code=404, detail="Task not found")
    return {"deleted": True}


@router.get("/", response_model=List[Task])
def list_tasks_endpoint(
    status_filter: Optional[TaskStatus] = Query(None, alias="status"),
    priority_filter: Optional[TaskPriority] = Query(None, alias="priority"),
    start_due: Optional[datetime] = Query(None),
    end_due: Optional[datetime] = Query(None),
    limit: int = Query(100, ge=1, le=500),
    current_user: User = Depends(get_current_user),
) -> List[Task]:
    date_range = (start_due, end_due) if (start_due or end_due) else None
    return list_tasks_by_user(
        user_id=current_user.user_id,
        limit=limit,
        status=status_filter,
        priority=priority_filter,
        date_range=date_range,
    )


class TaskNLCreate(BaseModel):
    text: str = Field(min_length=1, max_length=500)


@router.post("/create", response_model=Task, status_code=status.HTTP_201_CREATED)
def create_task_nl_endpoint(payload: TaskNLCreate, current_user: User = Depends(get_current_user)) -> Task:
    parsed = parse_natural_language_task(payload.text)
    task = Task(
        user_id=current_user.user_id,
        title=parsed.title,
        description=parsed.description,
        due_date=parsed.due_date,
        priority=parsed.priority,
    )
    return create_task(task)


