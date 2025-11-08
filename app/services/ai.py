from __future__ import annotations

import os
from datetime import datetime, timezone
from typing import Any, Dict, Optional

from pydantic import BaseModel, Field, ValidationError

from app.models.task import TaskPriority
from app.models.fitness_log import FitnessLogType


class ParsedTask(BaseModel):
    title: str
    description: Optional[str] = None
    due_date: Optional[datetime] = None
    priority: TaskPriority = TaskPriority.medium


def _ensure_utc(dt: Optional[datetime]) -> Optional[datetime]:
    if dt is None:
        return None
    if dt.tzinfo is None:
        return dt.replace(tzinfo=timezone.utc)
    return dt.astimezone(timezone.utc)


def parse_natural_language_task(input_text: str) -> ParsedTask:
    """Parse a natural language task description using OpenAI.

    Falls back to a simple heuristic if OPENAI_API_KEY is not set or request fails.
    """
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        # Fallback: use the entire text as title
        return ParsedTask(title=input_text.strip()[:200])

    try:
        from openai import OpenAI  # local import to avoid import cost if unused

        client = OpenAI(api_key=api_key)
        system_msg = (
            "You are Yuvi, a friendly AI assistant helping users manage their tasks. "
            "Extract a JSON object with keys: title (string), description (string), "
            "due_date (ISO 8601), priority (low|medium|high). If missing, infer conservatively."
        )
        user_msg = f"Task: {input_text}"

        # Chat Completions API
        resp = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": system_msg},
                {"role": "user", "content": user_msg},
            ],
            temperature=0.2,
        )
        content = resp.choices[0].message.content or "{}"

        import json

        # Try to find JSON block in content
        try:
            data: Dict[str, Any] = json.loads(content)
        except json.JSONDecodeError:
            # naive extraction of JSON substring
            start = content.find("{")
            end = content.rfind("}")
            if start != -1 and end != -1 and end > start:
                data = json.loads(content[start : end + 1])
            else:
                return ParsedTask(title=input_text.strip()[:200])

        # Normalize and coerce fields
        title = str(data.get("title") or input_text).strip()[:200]
        description = data.get("description")
        due_date_raw = data.get("due_date")
        due_date_dt: Optional[datetime] = None
        if isinstance(due_date_raw, str) and due_date_raw:
            try:
                # fromisoformat may fail if Z used; handle Z
                if due_date_raw.endswith("Z"):
                    due_date_raw = due_date_raw[:-1] + "+00:00"
                due_date_dt = datetime.fromisoformat(due_date_raw)
            except Exception:
                due_date_dt = None
        priority_raw = (data.get("priority") or "medium").lower()
        priority = TaskPriority(priority_raw) if priority_raw in TaskPriority.__members__.values() else TaskPriority.medium

        return ParsedTask(
            title=title,
            description=description,
            due_date=_ensure_utc(due_date_dt),
            priority=priority,
        )
    except Exception:
        # Fallback on any AI errors
        return ParsedTask(title=input_text.strip()[:200])


class ParsedFitnessLog(BaseModel):
    log_type: FitnessLogType
    content: str
    calories: Optional[int] = None
    timestamp: Optional[datetime] = None
    ai_parsed_data: Dict[str, Any] = Field(default_factory=dict)


def parse_natural_language_fitness(input_text: str) -> ParsedFitnessLog:
    """Parse a natural language fitness entry (meal/workout).

    Uses OpenAI if available, falls back to heuristics.
    Expected JSON keys: log_type (meal|workout), content, calories (int), timestamp (ISO8601).
    """
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        # Heuristic fallback
        text_lower = input_text.lower()
        log_type = FitnessLogType.meal if any(k in text_lower for k in ["ate", "meal", "calorie", "breakfast", "lunch", "dinner"]) else FitnessLogType.workout
        calories = None
        # crude calorie extraction
        import re

        m = re.search(r"(\d{2,5})\s*(?:k?cal|calories?)", text_lower)
        if m:
            try:
                calories = int(m.group(1))
            except Exception:
                calories = None
        return ParsedFitnessLog(log_type=log_type, content=input_text.strip(), calories=calories, timestamp=None)

    try:
        from openai import OpenAI

        client = OpenAI(api_key=api_key)
        system_msg = (
            "You are Yuvi, a supportive AI health companion helping users track their fitness. "
            "Extract a JSON object with keys: log_type (meal|workout), content (string), "
            "calories (integer, null if unknown), timestamp (ISO 8601)."
        )
        user_msg = f"Fitness entry: {input_text}"
        resp = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": system_msg},
                {"role": "user", "content": user_msg},
            ],
            temperature=0.2,
        )
        content = resp.choices[0].message.content or "{}"

        import json

        try:
            data: Dict[str, Any] = json.loads(content)
        except json.JSONDecodeError:
            start = content.find("{")
            end = content.rfind("}")
            if start != -1 and end != -1 and end > start:
                data = json.loads(content[start : end + 1])
            else:
                return ParsedFitnessLog(log_type=FitnessLogType.meal, content=input_text.strip(), calories=None, timestamp=None)

        log_type_raw = (data.get("log_type") or "meal").lower()
        log_type = FitnessLogType(log_type_raw) if log_type_raw in FitnessLogType.__members__.values() else FitnessLogType.meal
        content_text = str(data.get("content") or input_text).strip()
        calories_raw = data.get("calories")
        calories_val: Optional[int] = None
        try:
            calories_val = int(calories_raw) if calories_raw is not None else None
        except Exception:
            calories_val = None
        ts_raw = data.get("timestamp")
        ts_dt: Optional[datetime] = None
        if isinstance(ts_raw, string_types := str) and ts_raw:
            try:
                if ts_raw.endswith("Z"):
                    ts_raw = ts_raw[:-1] + "+00:00"
                ts_dt = datetime.fromisoformat(ts_raw)
            except Exception:
                ts_dt = None

        return ParsedFitnessLog(
            log_type=log_type,
            content=content_text,
            calories=calories_val,
            timestamp=_ensure_utc(ts_dt) if ts_dt else None,
            ai_parsed_data=data,
        )
    except Exception:
        return ParsedFitnessLog(log_type=FitnessLogType.meal, content=input_text.strip(), calories=None, timestamp=None)


