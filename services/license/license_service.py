import json
import logging
import os
import sys
from dataclasses import dataclass
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Any, Dict, Optional

from sqlalchemy import text
from sqlalchemy.exc import SQLAlchemyError, ProgrammingError

from services.db_services.db_config import SessionLocal

from .machine_fingerprint import collect_machine_fingerprint_payload
from .license_validator import (
    encode_request_code,
    is_license_expired,
    parse_license_blob,
    validate_hwid_match,
    verify_license_signature,
)


logger = logging.getLogger(__name__)

APP_LICENSE_DIR_ENV = "KONACH_LICENSE_DIR"
APP_PUBLIC_KEY_ENV = "KONACH_LICENSE_PUBLIC_KEY_PEM"
APP_PUBLIC_KEY_FILE_ENV = "KONACH_LICENSE_PUBLIC_KEY_FILE"
APP_VERSION_ENV = "KONACH_APP_VERSION"
DEFAULT_APP_VERSION = "1.0.0"


class LicenseError(RuntimeError):
    pass


@dataclass(frozen=True)
class LicenseValidationResult:
    is_valid: bool
    reason: str
    machine_fingerprint: str
    payload: Optional[Dict[str, Any]] = None


def _runtime_dir() -> Path:
    if getattr(sys, "frozen", False):
        return Path(sys.executable).resolve().parent
    return Path(__file__).resolve().parents[2]


def _license_dir() -> Path:
    custom = os.getenv(APP_LICENSE_DIR_ENV, "").strip()
    if custom:
        path = Path(custom)
    else:
        base = os.getenv("PROGRAMDATA", str(Path.home()))
        path = Path(base) / "KONACH" / "license"
    path.mkdir(parents=True, exist_ok=True)
    return path


def _license_file_path() -> Path:
    return _license_dir() / "license.json"


def _request_file_path() -> Path:
    return _license_dir() / "request_code.txt"


def _candidate_public_key_paths() -> list[Path]:
    custom_path = os.getenv(APP_PUBLIC_KEY_FILE_ENV, "").strip()
    runtime_dir = _runtime_dir()
    candidates = [
        Path(custom_path) if custom_path else None,
        runtime_dir / "config" / "license_public_key.pem",
        runtime_dir / "public_key.pem",
        Path.cwd() / "config" / "license_public_key.pem",
        Path.cwd() / "public_key.pem",
    ]

    paths: list[Path] = []
    seen: set[str] = set()
    for path in candidates:
        if path is None:
            continue
        key = str(path)
        if key in seen:
            continue
        seen.add(key)
        paths.append(path)
    return paths


def _public_key_pem() -> str:
    pem = os.getenv(APP_PUBLIC_KEY_ENV, "").strip()
    if pem:
        return pem.replace("\\n", "\n")

    for path in _candidate_public_key_paths():
        try:
            if path.exists():
                content = path.read_text(encoding="utf-8").strip()
                if content:
                    logger.info("Loaded license public key from %s", path)
                    return content
        except Exception:
            logger.exception("Failed to read public key from %s", path)

    raise LicenseError(
        "Missing KONACH license public key. Set KONACH_LICENSE_PUBLIC_KEY_PEM or provide config/license_public_key.pem."
    )


def _log_validation_event(event_type: str, event_result: str, message: str, payload: Optional[Dict[str, Any]]) -> None:
    details = payload or {}
    machine = collect_machine_fingerprint_payload()

    try:
        with SessionLocal() as session:
            tables_ready = session.execute(text("SHOW TABLES LIKE 'license_audit_log'"))
            if tables_ready.scalar_one_or_none() is None:
                return

            session.execute(
                text(
                    """
                    INSERT INTO license_audit_log (
                        licensed_machine_id,
                        app_installation_id,
                        event_type,
                        event_result,
                        event_message,
                        event_details_json
                    ) VALUES (
                        NULL,
                        NULL,
                        :event_type,
                        :event_result,
                        :event_message,
                        :event_details_json
                    )
                    """
                ),
                {
                    "event_type": event_type,
                    "event_result": event_result,
                    "event_message": message[:1024],
                    "event_details_json": json.dumps(
                        {
                            "machine": machine,
                            "payload": details,
                        },
                        ensure_ascii=False,
                    ),
                },
            )
            session.commit()
    except ProgrammingError:
        logger.warning("License audit table not ready; skipping DB audit")
    except SQLAlchemyError:
        logger.exception("Failed to write license audit event")


def get_request_code() -> str:
    machine = collect_machine_fingerprint_payload()
    payload = {
        "app_id": "KONACH",
        "app_version": os.getenv(APP_VERSION_ENV, DEFAULT_APP_VERSION),
        "requested_at": datetime.now(tz=timezone.utc).isoformat(),
        "machine_name": machine["machine_name"],
        "hwid": machine["hardware_fingerprint"],
        "bios_uuid": machine["bios_uuid"],
        "disk_serial": machine["disk_serial"],
        "windows_machine_guid": machine["windows_machine_guid"],
        "mac_address": machine["mac_address"],
        "expires_at": (datetime.now(tz=timezone.utc) + timedelta(days=1)).isoformat(),
    }
    request_code = encode_request_code(payload)
    _request_file_path().write_text(request_code, encoding="utf-8")
    return request_code


def import_license_blob(license_blob: str) -> Dict[str, Any]:
    data = parse_license_blob(license_blob)
    verify_license_signature(data, _public_key_pem())
    _license_file_path().write_text(json.dumps(data, ensure_ascii=False, sort_keys=True), encoding="utf-8")
    logger.info("License file imported successfully")
    return data


def _load_local_license_data() -> Optional[Dict[str, Any]]:
    path = _license_file_path()
    if not path.exists():
        return None
    raw = path.read_text(encoding="utf-8").strip()
    if not raw:
        return None
    return parse_license_blob(raw)


def validate_current_license() -> LicenseValidationResult:
    machine = collect_machine_fingerprint_payload()
    current_hwid = machine["hardware_fingerprint"]

    data = _load_local_license_data()
    if not data:
        request_code = get_request_code()
        result = LicenseValidationResult(
            is_valid=False,
            reason="No license installed. Request code generated.",
            machine_fingerprint=current_hwid,
            payload={"request_code": request_code},
        )
        _log_validation_event("startup_validation", "missing", result.reason, result.payload)
        return result

    try:
        verify_license_signature(data, _public_key_pem())
        if str(data.get("app_id") or "KONACH").strip().upper() != "KONACH":
            raise ValueError("License app_id is invalid")
        if str(data.get("status") or "active").strip().lower() != "active":
            raise ValueError("License status is not active")
        validate_hwid_match(data, current_hwid)
        if is_license_expired(data):
            raise ValueError("License is expired")
    except Exception as exc:
        result = LicenseValidationResult(
            is_valid=False,
            reason=str(exc),
            machine_fingerprint=current_hwid,
            payload=data,
        )
        _log_validation_event("startup_validation", "invalid", result.reason, result.payload)
        return result

    result = LicenseValidationResult(
        is_valid=True,
        reason="License is valid",
        machine_fingerprint=current_hwid,
        payload=data,
    )
    _log_validation_event("startup_validation", "ok", result.reason, result.payload)
    return result


def ensure_license_or_raise() -> LicenseValidationResult:
    result = validate_current_license()
    if not result.is_valid:
        raise LicenseError(result.reason)
    return result
