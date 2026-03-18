import hashlib
import logging
import re
import time
from pathlib import Path
from typing import List, Optional, Tuple

from sqlalchemy import create_engine, text
from sqlalchemy.engine import Engine


logger = logging.getLogger(__name__)

_MIGRATION_FILE_PATTERN = re.compile(r"^(\d{3,})_.*\.sql$")


def _compute_checksum(content: str) -> str:
    return hashlib.sha256(content.encode("utf-8")).hexdigest()


def _discover_migration_files(migrations_dir: Path) -> List[Tuple[int, Path]]:
    files: List[Tuple[int, Path]] = []
    for path in migrations_dir.glob("*.sql"):
        match = _MIGRATION_FILE_PATTERN.match(path.name)
        if not match:
            continue
        files.append((int(match.group(1)), path))
    files.sort(key=lambda item: item[0])
    return files


def _ensure_history_table(connection) -> None:
    connection.execute(
        text(
            """
            CREATE TABLE IF NOT EXISTS schema_migrations (
                id BIGINT AUTO_INCREMENT PRIMARY KEY,
                version INT NOT NULL UNIQUE,
                script_name VARCHAR(255) NOT NULL,
                checksum_sha256 CHAR(64) NOT NULL,
                applied_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
                execution_ms INT NOT NULL DEFAULT 0,
                applied_by VARCHAR(128) NULL,
                notes VARCHAR(512) NULL
            ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
            """
        )
    )


def _get_applied_versions(connection) -> dict:
    rows = connection.execute(
        text("SELECT version, checksum_sha256, script_name, applied_at FROM schema_migrations")
    ).mappings()
    return {int(row["version"]): row for row in rows}


def _split_sql_statements(script: str) -> List[str]:
    """Split SQL script into executable statements while preserving semicolons in strings/comments."""
    statements: List[str] = []
    token: List[str] = []
    in_single = False
    in_double = False
    in_line_comment = False
    in_block_comment = False
    i = 0
    length = len(script)

    while i < length:
        ch = script[i]
        nxt = script[i + 1] if i + 1 < length else ""

        if in_line_comment:
            token.append(ch)
            if ch == "\n":
                in_line_comment = False
            i += 1
            continue

        if in_block_comment:
            token.append(ch)
            if ch == "*" and nxt == "/":
                token.append(nxt)
                in_block_comment = False
                i += 2
            else:
                i += 1
            continue

        if not in_single and not in_double:
            if ch == "-" and nxt == "-":
                token.append(ch)
                token.append(nxt)
                in_line_comment = True
                i += 2
                continue
            if ch == "/" and nxt == "*":
                token.append(ch)
                token.append(nxt)
                in_block_comment = True
                i += 2
                continue

        if ch == "'" and not in_double:
            in_single = not in_single
            token.append(ch)
            i += 1
            continue

        if ch == '"' and not in_single:
            in_double = not in_double
            token.append(ch)
            i += 1
            continue

        if ch == ";" and not in_single and not in_double:
            statement = "".join(token).strip()
            if statement:
                statements.append(statement)
            token = []
            i += 1
            continue

        token.append(ch)
        i += 1

    tail = "".join(token).strip()
    if tail:
        statements.append(tail)

    return statements


def _apply_script(connection, version: int, path: Path, applied_by: Optional[str]) -> None:
    script = path.read_text(encoding="utf-8")
    checksum = _compute_checksum(script)
    statements = _split_sql_statements(script)

    start = time.perf_counter()
    for statement in statements:
        connection.exec_driver_sql(statement)

    execution_ms = int((time.perf_counter() - start) * 1000)
    connection.execute(
        text(
            """
            INSERT INTO schema_migrations (version, script_name, checksum_sha256, execution_ms, applied_by)
            VALUES (:version, :script_name, :checksum, :execution_ms, :applied_by)
            """
        ),
        {
            "version": version,
            "script_name": path.name,
            "checksum": checksum,
            "execution_ms": execution_ms,
            "applied_by": applied_by,
        },
    )


def run_sql_migrations(
    database_url: str,
    migrations_dir: Optional[Path] = None,
    applied_by: Optional[str] = None,
) -> None:
    """Apply missing SQL migrations in ascending version order.

    Raises RuntimeError if a migration checksum mismatch is detected.
    """
    if migrations_dir is None:
        migrations_dir = Path(__file__).resolve().parents[2] / "sql"

    migration_files = _discover_migration_files(migrations_dir)
    if not migration_files:
        logger.info("No SQL migration files found in %s", migrations_dir)
        return

    engine: Engine = create_engine(database_url, future=True)
    with engine.begin() as connection:
        _ensure_history_table(connection)
        applied = _get_applied_versions(connection)

        for version, path in migration_files:
            script = path.read_text(encoding="utf-8")
            checksum = _compute_checksum(script)

            if version in applied:
                row = applied[version]
                if row["checksum_sha256"] != checksum:
                    raise RuntimeError(
                        f"Migration checksum mismatch for version {version}: "
                        f"db has {row['checksum_sha256']} but file {path.name} has {checksum}"
                    )
                continue

            logger.info("Applying SQL migration %s (%s)", version, path.name)
            _apply_script(connection, version, path, applied_by)

    logger.info("SQL migrations are up to date")
