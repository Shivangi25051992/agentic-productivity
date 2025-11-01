from __future__ import annotations

from typing import Dict

from fastapi import APIRouter, Depends, Header, HTTPException, Request, Response, status
from pydantic import BaseModel, Field

from app.services.admin_auth import admin_login, admin_logout, verify_admin_token
from app.services.admin_audit import audit_log


router = APIRouter(prefix="/admin", tags=["admin"], include_in_schema=False)


class AdminLoginPayload(BaseModel):
    username: str = Field(min_length=1)
    password: str = Field(min_length=1)


@router.post("/login")
def admin_login_endpoint(payload: AdminLoginPayload, request: Request, response: Response) -> Dict[str, str]:
    token = admin_login(payload.username, payload.password, request)
    # Security headers
    response.headers["Cache-Control"] = "no-store"
    response.headers["Pragma"] = "no-cache"
    audit_log("admin_login_api", actor=payload.username, ip=request.client.host if request.client else None)
    return {"token": token, "token_type": "bearer"}


@router.post("/logout")
def admin_logout_endpoint(authorization: str | None = Header(default=None)) -> Dict[str, bool]:
    if not authorization:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Missing Authorization header")
    admin_logout(authorization)
    return {"logged_out": True}


@router.get("/verify")
def admin_verify_endpoint(admin_subject: str = Depends(verify_admin_token)) -> Dict[str, str]:
    return {"status": "ok", "admin": admin_subject}






