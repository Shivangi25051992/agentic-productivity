from __future__ import annotations

from datetime import datetime, timezone
from typing import Any, Dict
from uuid import uuid4

from pydantic import BaseModel, EmailStr, Field, field_validator


def _now_utc() -> datetime:
    return datetime.now(timezone.utc)


class User(BaseModel):
    """Represents an application user."""

    user_id: str = Field(default_factory=lambda: str(uuid4()))
    email: EmailStr
    created_at: datetime = Field(default_factory=_now_utc)
    preferences: Dict[str, Any] = Field(default_factory=dict)

    @field_validator("created_at")
    @classmethod
    def _ensure_timezone(cls, value: datetime) -> datetime:
        if value.tzinfo is None:
            return value.replace(tzinfo=timezone.utc)
        return value.astimezone(timezone.utc)

    def to_dict(self) -> Dict[str, Any]:
        """Serialize to Firestore-compatible dict."""
        return self.model_dump(mode="python", exclude_none=True)

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "User":
        return cls(**data)







