import base64
import hashlib
import hmac
import os
from typing import Dict, Optional, Tuple

from sqlalchemy.exc import SQLAlchemyError

from .db_services.db_config import SessionLocal
from .db_services.db_tables import User
from sqlalchemy import select


PBKDF2_PREFIX = "pbkdf2_sha256"
PBKDF2_ITERATIONS = 390000


def hash_password(password: str, iterations: int = PBKDF2_ITERATIONS) -> str:
    """Hash a password using PBKDF2-SHA256 with random salt."""
    salt = os.urandom(16).hex()
    digest = hashlib.pbkdf2_hmac(
        "sha256",
        password.encode("utf-8"),
        salt.encode("utf-8"),
        iterations,
    )
    token = base64.b64encode(digest).decode("ascii")
    return f"{PBKDF2_PREFIX}${iterations}${salt}${token}"


def verify_password(plain_password: str, stored_password: str) -> bool:
    """Verify plaintext password against stored hash.

    Supports the project PBKDF2 format and a legacy plaintext fallback.
    """
    if not stored_password:
        return False

    if stored_password.startswith(f"{PBKDF2_PREFIX}$"):
        try:
            _prefix, iters_str, salt, expected_b64 = stored_password.split("$", 3)
            digest = hashlib.pbkdf2_hmac(
                "sha256",
                plain_password.encode("utf-8"),
                salt.encode("utf-8"),
                int(iters_str),
            )
            actual_b64 = base64.b64encode(digest).decode("ascii")
            return hmac.compare_digest(actual_b64, expected_b64)
        except Exception:
            return False

    # Legacy fallback (older rows may still contain plaintext).
    return hmac.compare_digest(plain_password, stored_password)


def authenticate_user(username: str, password: str) -> Tuple[Optional[Dict[str, object]], Optional[str]]:
    """Authenticate by username + password.

    Returns: (User | None, error_message | None)
    """
    try:
        with SessionLocal() as session:
            user = session.execute(
                select(User).where(User.username == username)
            ).scalar_one_or_none()

            if user is None or not verify_password(password, user.password_hash):
                return None, "اسم المستخدم أو كلمة المرور غير صحيحة"

            # One-time migration: convert legacy plaintext to hashed format.
            if not user.password_hash.startswith(f"{PBKDF2_PREFIX}$"):
                user.password_hash = hash_password(password)
                session.commit()

            return {
                "id": user.id,
                "username": user.username,
                "role": user.role,
            }, None
    except SQLAlchemyError:
        return None, "تعذر الاتصال بقاعدة البيانات"


def ensure_default_admin_user() -> Optional[Tuple[str, str]]:
    """Create a default admin when users table is empty.

    Returns created credentials (username, password) only when a new user is created.
    """
    default_username = os.getenv("KONACH_DEFAULT_ADMIN_USER", "admin").strip() or "admin"
    default_password = os.getenv("KONACH_DEFAULT_ADMIN_PASS", "admin123")

    try:
        with SessionLocal() as session:
            existing = session.execute(select(User.id).limit(1)).scalar_one_or_none()
            if existing is not None:
                return None

            user = User(
                username=default_username,
                password_hash=hash_password(default_password),
                role="admin",
            )
            session.add(user)
            session.commit()
            return default_username, default_password
    except SQLAlchemyError:
        return None