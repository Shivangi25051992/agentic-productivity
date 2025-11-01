from __future__ import annotations

import json
import logging
from datetime import datetime, timezone
from typing import Any, Dict, Optional


logger = logging.getLogger("admin_audit")


def _now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def audit_log(action: str, actor: str, ip: Optional[str] = None, extra: Optional[Dict[str, Any]] = None) -> None:
    payload = {
        "ts": _now_iso(),
        "action": action,
        "actor": actor,
        "ip": ip,
        "extra": extra or {},
    }
    logger.info(json.dumps(payload))






