import base64
import binascii
import json
from datetime import datetime, timezone
from typing import Any, Dict, Tuple

from cryptography.exceptions import InvalidSignature
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PublicKey


_REQUIRED_LICENSE_FIELDS = {
    "hwid",
    "customer",
    "issued_at",
    "expires_at",
    "signature",
}


def _urlsafe_b64encode(data: bytes) -> str:
    return base64.urlsafe_b64encode(data).decode("ascii").rstrip("=")


def _urlsafe_b64decode(value: str) -> bytes:
    pad = "=" * ((4 - len(value) % 4) % 4)
    return base64.urlsafe_b64decode((value + pad).encode("ascii"))


def encode_request_code(payload: Dict[str, Any]) -> str:
    canonical = json.dumps(payload, sort_keys=True, separators=(",", ":")).encode("utf-8")
    return _urlsafe_b64encode(canonical)


def decode_request_code(request_code: str) -> Dict[str, Any]:
    raw = _urlsafe_b64decode(request_code)
    data = json.loads(raw.decode("utf-8"))
    if not isinstance(data, dict):
        raise ValueError("Request code payload is not an object")
    return data


def parse_license_blob(license_blob: str) -> Dict[str, Any]:
    data = json.loads(license_blob)
    if not isinstance(data, dict):
        raise ValueError("License blob must be a JSON object")
    return data


def _load_public_key(public_key_pem: str) -> Ed25519PublicKey:
    text = public_key_pem.strip().strip('"').strip("'")
    if "BEGIN PUBLIC KEY" in text:
        key = serialization.load_pem_public_key(text.encode("utf-8"))
        if not isinstance(key, Ed25519PublicKey):
            raise ValueError("Public key must be Ed25519")
        return key

    try:
        raw = base64.b64decode(text, validate=True)
    except binascii.Error:
        raw = _urlsafe_b64decode(text)

    if len(raw) == 32:
        return Ed25519PublicKey.from_public_bytes(raw)

    try:
        key = serialization.load_der_public_key(raw)
    except ValueError as exc:
        raise ValueError("Unsupported public key format") from exc

    if not isinstance(key, Ed25519PublicKey):
        raise ValueError("Public key must be Ed25519")
    return key


def _canonical_payload_for_signature(license_data: Dict[str, Any]) -> bytes:
    body = dict(license_data)
    body.pop("signature", None)
    return json.dumps(body, sort_keys=True, separators=(",", ":")).encode("utf-8")


def validate_license_fields(license_data: Dict[str, Any]) -> None:
    missing = [field for field in _REQUIRED_LICENSE_FIELDS if field not in license_data]
    if missing:
        raise ValueError(f"License missing required fields: {', '.join(sorted(missing))}")

    if not isinstance(license_data.get("hwid"), str) or not license_data["hwid"].strip():
        raise ValueError("License hwid is invalid")

    if not isinstance(license_data.get("customer"), str) or not license_data["customer"].strip():
        raise ValueError("License customer is invalid")

    signature = license_data.get("signature")
    if not isinstance(signature, str) or not signature.strip():
        raise ValueError("License signature is invalid")


def verify_license_signature(license_data: Dict[str, Any], public_key_pem: str) -> None:
    validate_license_fields(license_data)
    signature = _urlsafe_b64decode(str(license_data["signature"]))
    canonical = _canonical_payload_for_signature(license_data)
    public_key = _load_public_key(public_key_pem)
    try:
        public_key.verify(signature, canonical)
    except InvalidSignature as exc:
        raise ValueError("License signature is invalid") from exc


def is_license_expired(license_data: Dict[str, Any]) -> bool:
    expires_at = str(license_data.get("expires_at") or "").strip()
    if not expires_at:
        raise ValueError("License expires_at is required")

    expiry = datetime.fromisoformat(expires_at.replace("Z", "+00:00"))
    if expiry.tzinfo is None:
        expiry = expiry.replace(tzinfo=timezone.utc)
    now = datetime.now(tz=timezone.utc)
    return now > expiry


def validate_hwid_match(license_data: Dict[str, Any], current_hwid: str) -> None:
    license_hwid = str(license_data.get("hwid") or "").strip().lower()
    if not license_hwid:
        raise ValueError("License hwid is missing")
    if license_hwid != current_hwid.strip().lower():
        raise ValueError("License is bound to a different machine")
