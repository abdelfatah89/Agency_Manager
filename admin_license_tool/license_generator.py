import argparse
import hashlib
import json
import uuid
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Tuple

from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PrivateKey

from services.license.license_validator import decode_request_code
try:
    from .utils import resolve_existing_path
except ImportError:
    from utils import resolve_existing_path


def _urlsafe_b64encode(data: bytes) -> str:
    import base64

    return base64.urlsafe_b64encode(data).decode("ascii").rstrip("=")


def load_private_key(private_key_path: Path) -> Ed25519PrivateKey:
    key_path = resolve_existing_path(private_key_path, "Private key")
    private_pem = key_path.read_bytes()
    key = serialization.load_pem_private_key(private_pem, password=None)
    if not isinstance(key, Ed25519PrivateKey):
        raise ValueError("Key is not Ed25519 private key")
    return key


def _derive_public_key_pem(private_key_path: Path) -> str:
    key = load_private_key(private_key_path)
    public_key = key.public_key()
    return public_key.public_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PublicFormat.SubjectPublicKeyInfo,
    ).decode("utf-8").strip()


def _assert_key_compatibility(private_key_path: Path, public_key_path: Path | None) -> None:
    if public_key_path is None:
        return
    resolved_public = resolve_existing_path(public_key_path, "Client public key")
    expected = resolved_public.read_text(encoding="utf-8").strip()
    derived = _derive_public_key_pem(private_key_path)
    if expected != derived:
        raise ValueError(
            "Private key does not match client verification key. Use matching key pair or deploy the correct public key."
        )


def issue_license(
    request_code: str,
    customer: str,
    days: int = 365,
    status: str = "active",
    private_key_path: Path = Path("keys/private_key.pem"),
    expected_public_key_path: Path | None = None,
    out_path: Path = Path("license.json"),
) -> Tuple[dict, str]:
    request_payload = decode_request_code(request_code)
    hwid = str(request_payload.get("hwid") or request_payload.get("hardware_fingerprint") or "").strip()
    if not hwid:
        raise ValueError("Request code missing hwid")

    key_path = resolve_existing_path(private_key_path, "Private key")
    _assert_key_compatibility(key_path, expected_public_key_path)

    now = datetime.now(tz=timezone.utc)
    valid_days = days if days and days > 0 else 36500
    expires_at = (now + timedelta(days=valid_days)).isoformat()

    license_payload = {
        "license_id": str(uuid.uuid4()),
        "app_id": "KONACH",
        "hwid": hwid,
        "customer": customer,
        "machine_name": request_payload.get("machine_name", ""),
        "request_code": request_code,
        "request_hash": _urlsafe_b64encode(hashlib.sha256(request_code.encode("utf-8")).digest()),
        "status": str(status).strip().lower() or "active",
        "issued_at": now.isoformat(),
        "expires_at": expires_at,
    }

    private_key = load_private_key(key_path)
    canonical = json.dumps(license_payload, sort_keys=True, separators=(",", ":")).encode("utf-8")
    signature = private_key.sign(canonical)
    license_payload["signature"] = _urlsafe_b64encode(signature)

    blob = json.dumps(license_payload, ensure_ascii=False, sort_keys=True)
    out_path.write_text(blob, encoding="utf-8")
    return license_payload, blob


def main() -> int:
    parser = argparse.ArgumentParser(description="Issue signed KONACH machine-bound license")
    parser.add_argument("--request-code", required=True, help="Machine request code from client app")
    parser.add_argument("--customer", required=True, help="Customer name")
    parser.add_argument("--days", type=int, default=365, help="Validity in days (0 = no expiry)")
    parser.add_argument("--status", default="active", choices=["active", "revoked", "suspended"])
    parser.add_argument("--private-key", default="keys/private_key.pem")
    parser.add_argument("--expected-public-key", default="config/license_public_key.pem")
    parser.add_argument("--out", default="license.json")
    args = parser.parse_args()

    issue_license(
        request_code=args.request_code,
        customer=args.customer,
        days=args.days,
        status=args.status,
        private_key_path=Path(args.private_key),
        expected_public_key_path=Path(args.expected_public_key) if args.expected_public_key else None,
        out_path=Path(args.out),
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
