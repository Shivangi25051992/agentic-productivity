from __future__ import annotations

from datetime import datetime, timezone
from enum import Enum
from typing import Any, Dict, Optional
from uuid import uuid4

from pydantic import BaseModel, Field, field_validator


def _now_utc() -> datetime:
    return datetime.now(timezone.utc)


class TaskPriority(str, Enum):
    low = "low"
    medium = "medium"
    high = "high"


class TaskStatus(str, Enum):
    pending = "pending"
    in_progress = "in_progress"
    completed = "completed"
    cancelled = "cancelled"


class Task(BaseModel):
    task_id: str = Field(default_factory=lambda: str(uuid4()))
    user_id: str
    title: str
    description: Optional[str] = None
    due_date: Optional[datetime] = None
    priority: TaskPriority = TaskPriority.medium
    status: TaskStatus = TaskStatus.pending
    created_at: datetime = Field(default_factory=_now_utc)
    updated_at: datetime = Field(default_factory=_now_utc)

    @field_validator("created_at", "updated_at", "due_date")
    @classmethod
    def _ensure_timezone(cls, value: Optional[datetime]) -> Optional[datetime]:
        if value is None:
            return value
        if value.tzinfo is None:
            return value.replace(tzinfo=timezone.utc)
        return value.astimezone(timezone.utc)

    def to_dict(self) -> Dict[str, Any]:
        return self.model_dump(mode="python", exclude_none=True)

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "Task":
        # Convert Firestore datetime objects to ISO strings
        for field in ["created_at", "updated_at", "due_date"]:
            if field in data and data[field] and hasattr(data[field], "isoformat"):
                data[field] = data[field].isoformat()
        return cls(**data)



