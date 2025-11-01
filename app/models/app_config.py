from __future__ import annotations

from datetime import datetime, timezone
from typing import Any, Dict, Optional
from uuid import uuid4

from pydantic import BaseModel, Field, field_validator


def _now_utc() -> datetime:
    return datetime.now(timezone.utc)


class SmtpConfig(BaseModel):
    host: str
    port: int = 587
    username: Optional[str] = None
    password: Optional[str] = None


class AppConfig(BaseModel):
    config_id: str = Field(default_factory=lambda: str(uuid4()))

    # Sensitive/plain fields (encryption handled in service layer)
    openai_api_key: Optional[str] = None
    google_project_id: Optional[str] = None
    google_application_credentials_json: Optional[str] = None
    gemini_api_key: Optional[str] = None
    firebase_config: Dict[str, Any] = Field(default_factory=dict)
    smtp_config: Optional[SmtpConfig] = None

    app_settings: Dict[str, Any] = Field(default_factory=dict)
    llm_prompt_template: Optional[str] = None
    is_active: bool = True
    created_at: datetime = Field(default_factory=_now_utc)
    updated_at: datetime = Field(default_factory=_now_utc)
    created_by: str

    @field_validator("created_at", "updated_at")
    @classmethod
    def _ensure_timezone(cls, value: datetime) -> datetime:
        if value.tzinfo is None:
            return value.replace(tzinfo=timezone.utc)
        return value.astimezone(timezone.utc)


