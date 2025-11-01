from __future__ import annotations

import json
import smtplib
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional

from fastapi import APIRouter, Depends, HTTPException, Path, Query, Request, Response, status
from pydantic import BaseModel, Field, ValidationError

from app.models.app_config import AppConfig, SmtpConfig
from app.services.admin_audit import audit_log
from app.services.admin_auth import verify_admin_token
from app.services.config_service import (
    get_active_config,
    list_config_history,
    save_config,
    update_config,
)


router = APIRouter(prefix="/admin/config", tags=["admin"], include_in_schema=False)


def _ensure_utc(dt: Optional[datetime]) -> Optional[datetime]:
    if dt is None:
        return None
    if dt.tzinfo is None:
        return dt.replace(tzinfo=timezone.utc)
    return dt.astimezone(timezone.utc)


def _mask_secret(value: Optional[str]) -> Optional[str]:
    if not value:
        return value
    tail = value[-4:]
    return "****" + tail


def _mask_config(cfg: AppConfig) -> Dict[str, Any]:
    data = cfg.model_dump(mode="python", exclude_none=True)
    # Mask sensitive scalar fields
    for key in [
        "openai_api_key",
        "google_application_credentials_json",
        "gemini_api_key",
    ]:
        if key in data and isinstance(data[key], str):
            data[key] = _mask_secret(data[key])
    # Mask firebase_config values (strings only)
    if "firebase_config" in data and isinstance(data["firebase_config"], dict):
        masked_fb: Dict[str, Any] = {}
        for k, v in data["firebase_config"].items():
            if isinstance(v, str):
                masked_fb[k] = _mask_secret(v)
            else:
                masked_fb[k] = v
        data["firebase_config"] = masked_fb
    # Mask smtp password and username
    if "smtp_config" in data and isinstance(data["smtp_config"], dict):
        sc = data["smtp_config"].copy()
        if "password" in sc and isinstance(sc["password"], str):
            sc["password"] = _mask_secret(sc["password"])
        if "username" in sc and isinstance(sc["username"], str):
            sc["username"] = _mask_secret(sc["username"])
        data["smtp_config"] = sc
    return data


class AppConfigCreate(BaseModel):
    openai_api_key: Optional[str] = None
    google_project_id: Optional[str] = None
    google_application_credentials_json: Optional[str] = None
    gemini_api_key: Optional[str] = None
    firebase_config: Dict[str, Any] = Field(default_factory=dict)
    smtp_config: Optional[SmtpConfig] = None
    app_settings: Dict[str, Any] = Field(default_factory=dict)
    is_active: bool = True
    llm_prompt_template: Optional[str] = None


class AppConfigUpdate(BaseModel):
    openai_api_key: Optional[str] = None
    google_project_id: Optional[str] = None
    google_application_credentials_json: Optional[str] = None
    gemini_api_key: Optional[str] = None
    firebase_config: Optional[Dict[str, Any]] = None
    smtp_config: Optional[SmtpConfig] = None
    app_settings: Optional[Dict[str, Any]] = None
    is_active: Optional[bool] = None
    llm_prompt_template: Optional[str] = None


class ValidationStatus(BaseModel):
    ok: bool
    message: Optional[str] = None


class ConfigValidationResponse(BaseModel):
    openai_api_key: ValidationStatus
    gemini_api_key: ValidationStatus
    google_credentials: ValidationStatus
    firebase_config: ValidationStatus
    smtp: ValidationStatus


def _validate_openai(key: Optional[str]) -> ValidationStatus:
    if not key:
        return ValidationStatus(ok=False, message="Missing OpenAI API key")
    try:
        from openai import OpenAI

        client = OpenAI(api_key=key)
        # lightweight call
        _ = client.models.list()
        return ValidationStatus(ok=True)
    except Exception as exc:
        return ValidationStatus(ok=False, message=str(exc))


def _validate_gemini(key: Optional[str]) -> ValidationStatus:
    if not key:
        return ValidationStatus(ok=False, message="Missing Gemini API key")
    try:
        import google.generativeai as genai

        genai.configure(api_key=key)
        # lightweight call
        _ = genai.list_models()
        return ValidationStatus(ok=True)
    except Exception as exc:
        return ValidationStatus(ok=False, message=str(exc))


def _validate_google_credentials(project_id: Optional[str], credentials_json: Optional[str]) -> ValidationStatus:
    if not project_id:
        return ValidationStatus(ok=False, message="Missing Google project id")
    if not credentials_json:
        return ValidationStatus(ok=False, message="Missing Google application credentials JSON")
    try:
        import json as _json
        from google.oauth2.service_account import Credentials

        info = _json.loads(credentials_json)
        _ = Credentials.from_service_account_info(info)
        # Avoid network calls in validation; credentials object creation suffices
        return ValidationStatus(ok=True)
    except Exception as exc:
        return ValidationStatus(ok=False, message=str(exc))


def _validate_firebase_config(cfg: Dict[str, Any]) -> ValidationStatus:
    required_keys = {"apiKey", "projectId"}
    missing = [k for k in required_keys if k not in cfg]
    if missing:
        return ValidationStatus(ok=False, message=f"Missing keys: {', '.join(missing)}")
    return ValidationStatus(ok=True)


def _validate_smtp(smtp: Optional[SmtpConfig]) -> ValidationStatus:
    if not smtp:
        return ValidationStatus(ok=False, message="Missing SMTP config")
    try:
        with smtplib.SMTP(host=smtp.host, port=smtp.port, timeout=10) as server:
            try:
                server.starttls()
            except Exception:
                pass
            if smtp.username and smtp.password:
                server.login(smtp.username, smtp.password)
        return ValidationStatus(ok=True)
    except Exception as exc:
        return ValidationStatus(ok=False, message=str(exc))


# Accept both /admin/config and /admin/config/
@router.post("", response_model=Dict[str, Any])
@router.post("/", response_model=Dict[str, Any])
def create_config(
    payload: AppConfigCreate,
    admin_subject: str = Depends(verify_admin_token),
    request: Request = None,
) -> Dict[str, Any]:
    cfg = AppConfig(
        openai_api_key=payload.openai_api_key,
        google_project_id=payload.google_project_id,
        google_application_credentials_json=payload.google_application_credentials_json,
        gemini_api_key=payload.gemini_api_key,
        firebase_config=payload.firebase_config or {},
        smtp_config=payload.smtp_config,
        app_settings=payload.app_settings or {},
        is_active=payload.is_active,
        llm_prompt_template=payload.llm_prompt_template,
        created_by=admin_subject,
    )
    saved = save_config(cfg)
    # Ensure exactly one active config after save (auto-activate latest)
    if saved.is_active:
        try:
            # Activate by id via same logic as endpoint
            items = list_config_history(limit=100)
            for item in items:
                if item.config_id == saved.config_id:
                    update_config(item.config_id, {"is_active": True})
                else:
                    update_config(item.config_id, {"is_active": False})
        except Exception:
            pass
    audit_log("admin_config_create", actor=admin_subject, ip=request.client.host if request and request.client else None)
    return {"config": _mask_config(saved)}


@router.get("/active", response_model=Dict[str, Any])
def get_active(admin_subject: str = Depends(verify_admin_token)) -> Dict[str, Any]:
    cfg = get_active_config()
    if not cfg:
        raise HTTPException(status_code=404, detail="No active configuration")
    return {"config": _mask_config(cfg)}


@router.get("/history", response_model=Dict[str, Any])
def history(admin_subject: str = Depends(verify_admin_token), limit: int = Query(50, ge=1, le=200)) -> Dict[str, Any]:
    items = list_config_history(limit=limit)
    return {"items": [_mask_config(c) for c in items]}


@router.put("/{config_id}/activate", response_model=Dict[str, Any])
def activate_config(
    config_id: str = Path(...),
    admin_subject: str = Depends(verify_admin_token),
    request: Request = None,
) -> Dict[str, Any]:
    # Deactivate others and activate selected
    items = list_config_history(limit=1000)
    for item in items:
        if item.config_id == config_id:
            update_config(item.config_id, {"is_active": True})
        else:
            update_config(item.config_id, {"is_active": False})
    active = get_active_config()
    if not active or active.config_id != config_id:
        raise HTTPException(status_code=404, detail="Config not found or activation failed")
    audit_log("admin_config_activate", actor=admin_subject, ip=request.client.host if request and request.client else None, extra={"config_id": config_id})
    return {"config": _mask_config(active)}


@router.put("/{config_id}", response_model=Dict[str, Any])
def update_config_endpoint(
    config_id: str,
    payload: AppConfigUpdate,
    admin_subject: str = Depends(verify_admin_token),
    request: Request = None,
) -> Dict[str, Any]:
    updates = payload.model_dump(exclude_none=True)
    updated = update_config(config_id, updates)
    if not updated:
        raise HTTPException(status_code=404, detail="Config not found")
    audit_log("admin_config_update", actor=admin_subject, ip=request.client.host if request and request.client else None, extra={"config_id": config_id})
    return {"config": _mask_config(updated)}


@router.delete("/{config_id}", response_model=Dict[str, Any])
def soft_delete_config(
    config_id: str,
    admin_subject: str = Depends(verify_admin_token),
    request: Request = None,
) -> Dict[str, Any]:
    updated = update_config(config_id, {"is_active": False, "deleted": True})
    if not updated:
        raise HTTPException(status_code=404, detail="Config not found")
    audit_log("admin_config_delete", actor=admin_subject, ip=request.client.host if request and request.client else None, extra={"config_id": config_id})
    return {"deleted": True}


class ConfigTestPayload(BaseModel):
    openai_api_key: Optional[str] = None
    gemini_api_key: Optional[str] = None
    google_project_id: Optional[str] = None
    google_application_credentials_json: Optional[str] = None
    firebase_config: Optional[Dict[str, Any]] = None
    smtp_config: Optional[SmtpConfig] = None


@router.post("/test", response_model=Dict[str, Any])
def test_config(
    payload: ConfigTestPayload,
    admin_subject: str = Depends(verify_admin_token),
    request: Request = None,
) -> Dict[str, Any]:
    results = {
        "openai_api_key": _validate_openai(payload.openai_api_key),
        "gemini_api_key": _validate_gemini(payload.gemini_api_key),
        "google_credentials": _validate_google_credentials(
            payload.google_project_id, payload.google_application_credentials_json
        ),
        "firebase_config": _validate_firebase_config(payload.firebase_config or {}),
        "smtp": _validate_smtp(payload.smtp_config),
    }
    audit_log("admin_config_test", actor=admin_subject, ip=request.client.host if request and request.client else None)
    return {
        "validation": {k: v.model_dump() for k, v in results.items()},
        "success": all(v.ok for v in results.values()),
    }


