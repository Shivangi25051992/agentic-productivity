from __future__ import annotations

from typing import Dict

from fastapi import APIRouter, Depends, Header, HTTPException, status
from pydantic import BaseModel

from app.models import User
from app.services.auth import (
    get_current_user,
    login_user_by_token,
    signup_or_get_user_by_token,
)
from app.services.invitation_service import get_invitation_service


router = APIRouter(prefix="/auth", tags=["auth"])


class TokenPayload(BaseModel):
    id_token: str


@router.post("/signup", response_model=User)
def signup(payload: TokenPayload) -> User:
    if not payload.id_token:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="id_token is required")
    
    # Create user
    user = signup_or_get_user_by_token(payload.id_token)
    
    # Send notification to admin
    invitation_service = get_invitation_service()
    invitation_service.send_signup_notification(user.email)
    
    return user


@router.post("/login", response_model=User)
def login(payload: TokenPayload) -> User:
    if not payload.id_token:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="id_token is required")
    return login_user_by_token(payload.id_token)


@router.get("/me", response_model=User)
def me(current_user: User = Depends(get_current_user)) -> User:
    return current_user







