from __future__ import annotations

from datetime import datetime, timezone
from enum import Enum
from typing import Any, Dict, Optional
from uuid import uuid4

from pydantic import BaseModel, Field, field_validator


def _now_utc() -> datetime:
    return datetime.now(timezone.utc)


class FitnessLogType(str, Enum):
    meal = "meal"
    workout = "workout"
    water = "water"
    supplement = "supplement"


class FitnessLog(BaseModel):
    log_id: str = Field(default_factory=lambda: str(uuid4()))
    user_id: str
    log_type: FitnessLogType
    content: str
    calories: Optional[int] = None
    timestamp: datetime = Field(default_factory=_now_utc)
    ai_parsed_data: Dict[str, Any] = Field(default_factory=dict)
    client_generated_id: Optional[str] = None  # 🔑 For optimistic UI matching

    @field_validator("timestamp")
    @classmethod
    def _ensure_timezone(cls, value: datetime) -> datetime:
        if value.tzinfo is None:
            return value.replace(tzinfo=timezone.utc)
        return value.astimezone(timezone.utc)

    def to_dict(self) -> Dict[str, Any]:
        return self.model_dump(mode="python", exclude_none=True)

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "FitnessLog":
        # Convert Firestore datetime objects to ISO strings
        if "timestamp" in data and hasattr(data["timestamp"], "isoformat"):
            data["timestamp"] = data["timestamp"].isoformat()
        return cls(**data)



