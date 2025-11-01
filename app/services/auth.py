from __future__ import annotations

import os
from typing import Any, Dict, Optional

import firebase_admin
from fastapi import Header, HTTPException, status
from firebase_admin import auth as fb_auth
from firebase_admin import credentials

from app.models import User
from app.services.database import create_user, get_user


_FIREBASE_APP_INITIALIZED = False


def _init_firebase_app() -> None:
    global _FIREBASE_APP_INITIALIZED
    if _FIREBASE_APP_INITIALIZED:
        return
    try:
        firebase_admin.get_app()
        _FIREBASE_APP_INITIALIZED = True
        return
    except ValueError:
        pass

    # Initialize with default credentials (uses GOOGLE_APPLICATION_CREDENTIALS if set)
    project_id = os.getenv("FIREBASE_PROJECT_ID") or os.getenv("GOOGLE_CLOUD_PROJECT")
    cred = credentials.ApplicationDefault()
    if project_id:
        firebase_admin.initialize_app(cred, {"projectId": project_id})
    else:
        firebase_admin.initialize_app(cred)
    _FIREBASE_APP_INITIALIZED = True


def verify_firebase_id_token(id_token: str) -> Dict[str, Any]:
    """Verify a Firebase ID token and return decoded claims.

    Raises HTTPException with 401 on invalid token.
    """
    _init_firebase_app()
    try:
        decoded = fb_auth.verify_id_token(id_token)
        return decoded
    except fb_auth.InvalidIdTokenError:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid ID token")
    except fb_auth.ExpiredIdTokenError:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Expired ID token")
    except fb_auth.RevokedIdTokenError:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Revoked ID token")
    except Exception:
        # Do not leak internals
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Token verification failed")


def _extract_bearer_token(authorization: Optional[str]) -> str:
    if not authorization:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Missing Authorization header")
    parts = authorization.split()
    if len(parts) != 2 or parts[0].lower() != "bearer":
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid Authorization header format")
    return parts[1]


def get_current_user(authorization: Optional[str] = Header(default=None)) -> User:
    """FastAPI dependency to protect routes and return the current user.

    Requires header: Authorization: Bearer <id_token>
    """
    token = _extract_bearer_token(authorization)
    claims = verify_firebase_id_token(token)
    uid = claims.get("uid")
    email = claims.get("email")
    if not uid or not email:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Token missing required claims")

    user = get_user(uid)
    if not user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="User not registered. Please sign up.")
    return user


def signup_or_get_user_by_token(id_token: str) -> User:
    """Verify token and ensure a user record exists; create if missing.

    Returns a User model.
    """
    claims = verify_firebase_id_token(id_token)
    uid = claims.get("uid")
    email = claims.get("email")
    if not uid or not email:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Token missing required claims")

    existing = get_user(uid)
    if existing:
        return existing
    # Auto-create minimal user record
    user = User(user_id=uid, email=email)
    return create_user(user)


def login_user_by_token(id_token: str) -> User:
    """Verify token and return the existing user. Does not create new users."""
    claims = verify_firebase_id_token(id_token)
    uid = claims.get("uid")
    email = claims.get("email")
    if not uid or not email:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Token missing required claims")
    user = get_user(uid)
    if not user:
        # Explicitly require signup when user does not exist
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found. Please sign up.")
    return user






