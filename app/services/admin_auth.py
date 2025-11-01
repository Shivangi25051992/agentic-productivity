from __future__ import annotations

import hashlib
import time
from datetime import datetime, timedelta, timezone
from typing import Dict, Optional

import bcrypt
import jwt
from fastapi import Depends, Header, HTTPException, Request, status

from app.core.config import (
    ADMIN_IP_WHITELIST,
    ADMIN_PASSWORD,
    ADMIN_PASSWORD_BCRYPT,
    ADMIN_SECRET_KEY,
    ADMIN_USERNAME,
)
from app.services.admin_audit import audit_log


ALGORITHM = "HS256"
ADMIN_TOKEN_TTL_HOURS = 24

# Simple in-memory rate limiting store: {ip_hash: [timestamps]}
_rate_store: Dict[str, list[float]] = {}
_revoked_tokens: set[str] = set()


def _client_ip(request: Request) -> str:
    # Try common headers, fallback to client host
    forwarded = request.headers.get("x-forwarded-for")
    if forwarded:
        return forwarded.split(",")[0].strip()
    return request.client.host if request.client else "unknown"


def _hash_ip(ip: str) -> str:
    return hashlib.sha256(ip.encode("utf-8")).hexdigest()


def _check_ip_whitelist(ip: str) -> None:
    if not ADMIN_IP_WHITELIST:
        return
    if ip not in ADMIN_IP_WHITELIST:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="IP not allowed")


def _check_rate_limit(ip: str) -> None:
    now = time.time()
    window = 60.0 * 60.0  # 1 hour
    max_attempts = 5
    key = _hash_ip(ip)
    bucket = _rate_store.setdefault(key, [])
    # Purge old
    bucket[:] = [t for t in bucket if now - t < window]
    if len(bucket) >= max_attempts:
        raise HTTPException(status_code=status.HTTP_429_TOO_MANY_REQUESTS, detail="Too many login attempts, try later")
    bucket.append(now)


def _verify_password(plain_password: str) -> bool:
    if ADMIN_PASSWORD_BCRYPT:
        try:
            return bcrypt.checkpw(plain_password.encode("utf-8"), ADMIN_PASSWORD_BCRYPT.encode("utf-8"))
        except Exception:
            return False
    if ADMIN_PASSWORD is None:
        return False
    return plain_password == ADMIN_PASSWORD


def create_admin_token(subject: str) -> str:
    if not ADMIN_SECRET_KEY:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Admin secret key not configured")
    now = datetime.now(timezone.utc)
    payload = {
        "sub": subject,
        "iat": int(now.timestamp()),
        "exp": int((now + timedelta(hours=ADMIN_TOKEN_TTL_HOURS)).timestamp()),
        "scope": "admin",
    }
    return jwt.encode(payload, ADMIN_SECRET_KEY, algorithm=ALGORITHM)


def decode_admin_token(token: str) -> dict:
    if not ADMIN_SECRET_KEY:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Admin secret key not configured")
    try:
        return jwt.decode(token, ADMIN_SECRET_KEY, algorithms=[ALGORITHM])
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Token expired")
    except jwt.InvalidTokenError:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token")


def admin_login(username: str, password: str, request: Request) -> str:
    ip = _client_ip(request)
    _check_ip_whitelist(ip)
    _check_rate_limit(ip)

    if username != (ADMIN_USERNAME or ""):
        audit_log("admin_login_failed", actor=username or "", ip=ip, extra={"reason": "bad_username"})
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid credentials")
    if not _verify_password(password):
        audit_log("admin_login_failed", actor=username, ip=ip, extra={"reason": "bad_password"})
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid credentials")

    token = create_admin_token(subject=username)
    audit_log("admin_login_success", actor=username, ip=ip)
    return token


def _extract_bearer_token(authorization: Optional[str]) -> str:
    if not authorization:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Missing Authorization header")
    parts = authorization.split()
    if len(parts) != 2 or parts[0].lower() != "bearer":
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid Authorization header format")
    return parts[1]


def verify_admin_token(authorization: Optional[str] = Header(default=None)) -> str:
    token = _extract_bearer_token(authorization)
    if token in _revoked_tokens:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Token revoked")
    claims = decode_admin_token(token)
    if claims.get("scope") != "admin":
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Invalid scope")
    return claims.get("sub") or "admin"


def admin_logout(authorization: Optional[str] = Header(default=None)) -> None:
    token = _extract_bearer_token(authorization)
    _revoked_tokens.add(token)






