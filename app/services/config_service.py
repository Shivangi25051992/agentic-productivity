from __future__ import annotations

import base64
import os
from dataclasses import dataclass
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional

from cryptography.fernet import Fernet, InvalidToken
from dotenv import set_key
from google.cloud import firestore
from pydantic import ValidationError

from app.models.app_config import AppConfig


CONFIG_COLLECTION = "app_configs"


def _now_utc() -> datetime:
    return datetime.now(timezone.utc)


def _get_firestore_client() -> firestore.Client:
    project_id = os.getenv("GOOGLE_CLOUD_PROJECT")
    if project_id:
        return firestore.Client(project=project_id)
    return firestore.Client()


db = _get_firestore_client()


def _get_env_path() -> Optional[str]:
    # Try to find .env in project root
    cwd = os.getcwd()
    env_path = os.path.join(cwd, ".env")
    return env_path if os.path.exists(env_path) else None


def _load_or_generate_key() -> bytes:
    key_b64 = os.getenv("ENCRYPTION_KEY")
    if key_b64:
        try:
            # Validate base64
            base64.urlsafe_b64decode(key_b64)
            return key_b64.encode("utf-8")
        except Exception:
            pass
    # Generate new key
    key = Fernet.generate_key()
    # Persist to .env if available
    env_path = _get_env_path()
    if env_path:
        try:
            set_key(env_path, "ENCRYPTION_KEY", key.decode("utf-8"))
        except Exception:
            pass
    return key


def _get_fernet() -> Fernet:
    key = _load_or_generate_key()
    return Fernet(key)


def encrypt_sensitive_field(value: Optional[str]) -> Optional[str]:
    if value is None:
        return None
    f = _get_fernet()
    token = f.encrypt(value.encode("utf-8"))
    return token.decode("utf-8")


def decrypt_sensitive_field(encrypted_value: Optional[str]) -> Optional[str]:
    if not encrypted_value:
        return None
    f = _get_fernet()
    try:
        plain = f.decrypt(encrypted_value.encode("utf-8"))
        return plain.decode("utf-8")
    except InvalidToken:
        # Key rotated or bad ciphertext
        return None


def _serialize_config_for_storage(cfg: AppConfig) -> Dict[str, Any]:
    data = cfg.model_dump(mode="python", exclude_none=True)
    # Encrypt sensitive fields
    for key in [
        "openai_api_key",
        "google_application_credentials_json",
        "gemini_api_key",
    ]:
        if key in data and data[key] is not None:
            data[key] = encrypt_sensitive_field(str(data[key]))
    # firebase_config and smtp_config contain secrets; encrypt whole JSON strings
    if cfg.firebase_config:
        import json

        data["firebase_config"] = encrypt_sensitive_field(json.dumps(cfg.firebase_config))
    if cfg.smtp_config is not None:
        import json

        data["smtp_config"] = encrypt_sensitive_field(cfg.smtp_config.model_dump_json())
    return data


def _deserialize_config_from_storage(data: Dict[str, Any]) -> AppConfig:
    # Decrypt sensitive fields
    for key in [
        "openai_api_key",
        "google_application_credentials_json",
        "gemini_api_key",
    ]:
        if key in data and data[key] is not None:
            data[key] = decrypt_sensitive_field(data[key])

    # Decrypt JSON blobs
    if "firebase_config" in data and data["firebase_config"] is not None:
        import json

        dec = decrypt_sensitive_field(data["firebase_config"]) or "{}"
        data["firebase_config"] = json.loads(dec)

    if "smtp_config" in data and data["smtp_config"] is not None:
        import json

        dec = decrypt_sensitive_field(data["smtp_config"]) or "{}"
        data["smtp_config"] = json.loads(dec)

    return AppConfig(**data)


def save_config(config: AppConfig) -> AppConfig:
    # Deactivate existing active configs
    for doc in db.collection(CONFIG_COLLECTION).where("is_active", "==", True).stream():
        doc.reference.update({"is_active": False, "updated_at": _now_utc()})

    data = _serialize_config_for_storage(config)
    db.collection(CONFIG_COLLECTION).document(config.config_id).set(data)
    return config


def get_active_config() -> Optional[AppConfig]:
    # Keep this simple to avoid composite-index requirements in local/dev
    docs = (
        db.collection(CONFIG_COLLECTION)
        .where("is_active", "==", True)
        .limit(1)
        .stream()
    )
    for doc in docs:
        data = doc.to_dict() or {}
        try:
            return _deserialize_config_from_storage(data)
        except ValidationError:
            continue
    return None


def update_config(config_id: str, updates: Dict[str, Any]) -> Optional[AppConfig]:
    doc_ref = db.collection(CONFIG_COLLECTION).document(config_id)
    doc = doc_ref.get()
    if not doc.exists:
        return None
    current = doc.to_dict() or {}

    # Handle sensitive fields encryption in updates
    sensitive_keys = {
        "openai_api_key",
        "google_application_credentials_json",
        "gemini_api_key",
        "firebase_config",
        "smtp_config",
    }
    final_updates: Dict[str, Any] = {}
    for k, v in updates.items():
        if k in sensitive_keys and v is not None:
            if k in {"firebase_config", "smtp_config"}:
                import json

                v = encrypt_sensitive_field(json.dumps(v))
            else:
                v = encrypt_sensitive_field(str(v))
        final_updates[k] = v

    final_updates["updated_at"] = _now_utc()
    doc_ref.update(final_updates)
    # Return merged object
    merged = {**current, **final_updates}
    try:
        return _deserialize_config_from_storage(merged)
    except ValidationError:
        return None


def list_config_history(limit: int = 50) -> List[AppConfig]:
    docs = (
        db.collection(CONFIG_COLLECTION)
        .order_by("created_at", direction=firestore.Query.DESCENDING)
        .limit(limit)
        .stream()
    )
    items: List[AppConfig] = []
    for doc in docs:
        data = doc.to_dict() or {}
        try:
            items.append(_deserialize_config_from_storage(data))
        except ValidationError:
            continue
    return items


def rotate_encryption_key(new_key: Optional[str] = None) -> str:
    """Rotate the Fernet encryption key.

    - Generate a new key if not provided.
    - Re-encrypt all encrypted fields in config history.
    - Persist the new key to .env if available.
    Returns the new key (base64 urlsafe str).
    """
    current_key_b64 = os.getenv("ENCRYPTION_KEY")
    new_key_b = new_key.encode("utf-8") if new_key else Fernet.generate_key()

    # Update env
    os.environ["ENCRYPTION_KEY"] = new_key_b.decode("utf-8")
    env_path = _get_env_path()
    if env_path:
        try:
            set_key(env_path, "ENCRYPTION_KEY", new_key_b.decode("utf-8"))
        except Exception:
            pass

    # Re-encrypt all configs
    items = list_config_history(limit=1000)
    for item in items:
        # decrypt using old key context
        if current_key_b64:
            os.environ["ENCRYPTION_KEY"] = current_key_b64
        decrypted = _serialize_config_for_storage(_deserialize_config_from_storage(item.model_dump()))  # decrypt then reencrypt

        # switch to new key and re-encrypt
        os.environ["ENCRYPTION_KEY"] = new_key_b.decode("utf-8")
        data = _serialize_config_for_storage(AppConfig(**item.model_dump()))
        db.collection(CONFIG_COLLECTION).document(item.config_id).set(data)

    return new_key_b.decode("utf-8")


