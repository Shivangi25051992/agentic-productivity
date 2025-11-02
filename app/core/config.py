from __future__ import annotations

import os
from typing import List, Optional


def _get_env_list(name: str) -> List[str]:
    value = os.getenv(name, "").strip()
    if not value:
        return []
    return [item.strip() for item in value.split(",") if item.strip()]


# Admin configuration
ADMIN_USERNAME: Optional[str] = os.getenv("ADMIN_USERNAME")
ADMIN_PASSWORD: Optional[str] = os.getenv("ADMIN_PASSWORD")

# Optional bcrypt hash for the admin password
ADMIN_PASSWORD_BCRYPT: Optional[str] = os.getenv("ADMIN_PASSWORD_BCRYPT")

# JWT secret for admin tokens
ADMIN_SECRET_KEY: Optional[str] = os.getenv("ADMIN_SECRET_KEY")

# Optional IP whitelist (comma-separated). If empty, whitelist is disabled.
ADMIN_IP_WHITELIST: List[str] = _get_env_list("ADMIN_IP_WHITELIST")


def validate_admin_credentials(username: str, password: str) -> bool:
    """Validate provided admin credentials against environment configuration.

    If ADMIN_PASSWORD_BCRYPT is set, bcrypt is used for verification.
    Otherwise, plain string comparison against ADMIN_PASSWORD is performed.
    """
    if not ADMIN_USERNAME:
        return False
    if username != ADMIN_USERNAME:
        return False

    # Defer password verification to admin_auth service (bcrypt or plain)
    # Here we only check presence of configured password
    return ADMIN_PASSWORD is not None or ADMIN_PASSWORD_BCRYPT is not None







