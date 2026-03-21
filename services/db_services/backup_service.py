import gzip
import logging
import os
import shutil
from datetime import datetime
from pathlib import Path
from typing import Optional, Tuple

from services.subprocess_utils import run_hidden_subprocess

try:
    from .db_config import DB_CONFIG
except ImportError:
    import sys
    PROJECT_ROOT_FALLBACK = Path(__file__).resolve().parents[2]
    if str(PROJECT_ROOT_FALLBACK) not in sys.path:
        sys.path.insert(0, str(PROJECT_ROOT_FALLBACK))
    from services.db_services.db_config import DB_CONFIG


PROJECT_ROOT = Path(__file__).resolve().parents[2]
BACKUP_ROOT = Path(os.getenv("DB_BACKUP_DIR", str(PROJECT_ROOT / "backups" / "database")))
BACKUP_RETENTION_COUNT = int(os.getenv("DB_BACKUP_RETENTION_COUNT", "5") or "5")
BACKUP_ENABLED = os.getenv("DB_BACKUP_ENABLED", "1").strip() not in {"0", "false", "False"}
MYSQLDUMP_PATH = os.getenv("MYSQLDUMP_PATH", "").strip()
RCLONE_SYNC_ENABLED = os.getenv("DB_BACKUP_RCLONE_ENABLED", "0").strip() in {"1", "true", "True"}
RCLONE_PATH = os.getenv("RCLONE_PATH", "").strip()
RCLONE_REMOTE_NAME = os.getenv("DB_BACKUP_RCLONE_REMOTE", "database_backup").strip()
RCLONE_REMOTE_PATH = os.getenv("DB_BACKUP_RCLONE_REMOTE_PATH", "databases").strip()
RCLONE_SOURCE_DIR = Path(os.getenv("DB_BACKUP_RCLONE_SOURCE_DIR", str(BACKUP_ROOT))).expanduser()


logger = logging.getLogger(__name__)


def _find_rclone() -> Optional[str]:
    if RCLONE_PATH and Path(RCLONE_PATH).exists():
        return RCLONE_PATH
    local_candidates = [
        PROJECT_ROOT / "rclone.exe",
        PROJECT_ROOT / "rclone" / "rclone.exe",
        PROJECT_ROOT / "rclone" / "rclone",
    ]
    for candidate in local_candidates:
        if candidate.exists():
            return str(candidate)
    return shutil.which("rclone")


def _run_rclone_sync() -> Tuple[bool, str]:
    """Copy local backup folder to cloud using rclone."""
    if not RCLONE_SYNC_ENABLED:
        return True, "rclone sync disabled"

    rclone_bin = _find_rclone()
    if not rclone_bin:
        return False, "rclone not found. Install rclone or set RCLONE_PATH"

    if not RCLONE_REMOTE_NAME:
        return False, "DB_BACKUP_RCLONE_REMOTE is empty"

    source_dir = RCLONE_SOURCE_DIR
    source_dir.mkdir(parents=True, exist_ok=True)

    remote_target = f"{RCLONE_REMOTE_NAME}:{RCLONE_REMOTE_PATH}" if RCLONE_REMOTE_PATH else f"{RCLONE_REMOTE_NAME}:"
    cmd = [rclone_bin, "copy", str(source_dir), remote_target]

    try:
        proc = run_hidden_subprocess(cmd, capture_output=True, check=False)
        if proc.returncode != 0:
            stderr = proc.stderr.decode("utf-8", errors="ignore").strip()
            return False, f"rclone copy failed ({proc.returncode}): {stderr or 'unknown error'}"
        return True, f"rclone copy completed to {remote_target}"
    except Exception as err:
        logger.exception("rclone copy failed")
        return False, f"rclone copy exception: {err}"


def _ensure_backup_dir() -> None:
    BACKUP_ROOT.mkdir(parents=True, exist_ok=True)


def _find_mysqldump() -> Optional[str]:
    if MYSQLDUMP_PATH and Path(MYSQLDUMP_PATH).exists():
        return MYSQLDUMP_PATH
    return shutil.which("mysqldump")


def _backup_file_path(now: datetime) -> Path:
    stamp = now.strftime("%Y%m%d_%H%M%S")
    db_name = DB_CONFIG.get("database") or "database"
    return BACKUP_ROOT / f"{db_name}_{stamp}.sql.gz"


def _has_backup_for_day(day: datetime) -> bool:
    date_key = day.strftime("%Y%m%d")
    db_name = DB_CONFIG.get("database") or "database"
    pattern = f"{db_name}_{date_key}_*.sql.gz"
    return any(BACKUP_ROOT.glob(pattern))


def _cleanup_old_backups() -> None:
    if BACKUP_RETENTION_COUNT <= 0:
        return

    backups = sorted(
        BACKUP_ROOT.glob("*.sql.gz"),
        key=lambda p: p.stat().st_mtime,
        reverse=True,
    )

    for file_path in backups[BACKUP_RETENTION_COUNT:]:
        try:
            file_path.unlink(missing_ok=True)
        except Exception as err:
            logger.warning("Could not clean old backup '%s': %s", file_path, err)


def run_backup_now(reason: str = "manual") -> Tuple[bool, Optional[Path], str]:
    """Create one compressed .sql.gz backup using mysqldump."""
    if not BACKUP_ENABLED:
        return False, None, "Backup disabled by DB_BACKUP_ENABLED"

    _ensure_backup_dir()
    mysqldump_bin = _find_mysqldump()
    if not mysqldump_bin:
        return False, None, "mysqldump not found. Install MySQL client or set MYSQLDUMP_PATH"

    user = DB_CONFIG.get("user")
    password = DB_CONFIG.get("password")
    host = DB_CONFIG.get("host")
    port = str(DB_CONFIG.get("port") or 3306)
    database = DB_CONFIG.get("database")

    if not all([user, host, database]):
        return False, None, "Missing database settings (user/host/database)"

    out_path = _backup_file_path(datetime.now())
    cmd = [
        mysqldump_bin,
        "--no-defaults",
        "--single-transaction",
        "--routines",
        "--triggers",
        "--events",
        "-h",
        str(host),
        "-P",
        port,
        "-u",
        str(user),
        f"-p{password or ''}",
        str(database),
    ]

    try:
        proc = run_hidden_subprocess(cmd, capture_output=True, check=False)
        if proc.returncode != 0:
            stderr = proc.stderr.decode("utf-8", errors="ignore").strip()
            return False, None, f"mysqldump failed ({proc.returncode}): {stderr or 'unknown error'}"

        with gzip.open(out_path, "wb") as gz_file:
            gz_file.write(proc.stdout)

        _cleanup_old_backups()

        sync_ok, sync_message = _run_rclone_sync()
        return True, out_path, f"Backup created ({reason}); {sync_message}"
    except Exception as err:
        return False, None, f"Backup exception: {err}"


if __name__ == "__main__":
    ok, path, message = run_backup_now(reason="direct-script")
    if ok:
        logger.info("%s: %s", message, path)
    else:
        logger.warning("%s", message)