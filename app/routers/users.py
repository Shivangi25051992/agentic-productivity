from __future__ import annotations

from typing import Any, Dict, List, Optional

from fastapi import APIRouter, HTTPException, Query
from pydantic import BaseModel, EmailStr

from app.models import User
from app.services.database import (
    create_user,
    delete_user,
    get_user,
    list_users,
    update_user,
)


router = APIRouter(prefix="/users", tags=["users"])


class UserCreate(BaseModel):
    email: EmailStr
    preferences: Dict[str, Any] = {}


class UserUpdate(BaseModel):
    email: Optional[EmailStr] = None
    preferences: Optional[Dict[str, Any]] = None


@router.post("/", response_model=User)
def create_user_endpoint(payload: UserCreate) -> User:
    user = User(email=payload.email, preferences=payload.preferences or {})
    return create_user(user)


@router.get("/{user_id}", response_model=User)
def get_user_endpoint(user_id: str) -> User:
    user = get_user(user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user


@router.patch("/{user_id}", response_model=User)
def update_user_endpoint(user_id: str, updates: UserUpdate) -> User:
    updated = update_user(user_id, {k: v for k, v in updates.model_dump(exclude_none=True).items()})
    if not updated:
        raise HTTPException(status_code=404, detail="User not found")
    return updated


@router.delete("/{user_id}")
def delete_user_endpoint(user_id: str) -> Dict[str, bool]:
    deleted = delete_user(user_id)
    if not deleted:
        raise HTTPException(status_code=404, detail="User not found")
    return {"deleted": True}


@router.get("/", response_model=List[User])
def list_users_endpoint(limit: int = Query(50, ge=1, le=500)) -> List[User]:
    return list_users(limit=limit)







