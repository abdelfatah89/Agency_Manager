import argparse
import logging
import secrets
import string
import sys
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(BASE_DIR))

import pymysql

from services.app_logging import configure_logging
from services.db_services.sql_migration_runner import run_sql_migrations


logger = logging.getLogger(__name__)


def _strong_password(length: int = 24) -> str:
    alphabet = string.ascii_letters + string.digits + "!@#$%^&*()-_=+"
    return "".join(secrets.choice(alphabet) for _ in range(length))


def _upsert_env(path: Path, values: dict) -> None:
    existing = {}
    if path.exists():
        for line in path.read_text(encoding="utf-8").splitlines():
            if not line or line.strip().startswith("#") or "=" not in line:
                continue
            k, v = line.split("=", 1)
            existing[k.strip()] = v.strip()

    existing.update({k: str(v) for k, v in values.items()})

    lines = [f"{k}={v}" for k, v in sorted(existing.items())]
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> int:
    parser = argparse.ArgumentParser(description="Bootstrap MySQL/MariaDB DB/user and run SQL migrations")
    parser.add_argument("--root-host", default="127.0.0.1")
    parser.add_argument("--root-port", type=int, default=3306)
    parser.add_argument("--root-user", default="root")
    parser.add_argument("--root-password", required=True)
    parser.add_argument("--db-name", default="konach_new")
    parser.add_argument("--app-user", default="konach_app")
    parser.add_argument("--app-password", default="")
    parser.add_argument("--env-file", default=str(BASE_DIR / ".env"))
    args = parser.parse_args()

    configure_logging()

    app_password = args.app_password or _strong_password()

    conn = pymysql.connect(
        host=args.root_host,
        port=args.root_port,
        user=args.root_user,
        password=args.root_password,
        database="mysql",
        autocommit=True,
    )

    try:
        with conn.cursor() as cursor:
            cursor.execute(f"CREATE DATABASE IF NOT EXISTS `{args.db_name}` CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci")
            cursor.execute(f"CREATE USER IF NOT EXISTS '{args.app_user}'@'%' IDENTIFIED BY %s", (app_password,))
            cursor.execute(f"ALTER USER '{args.app_user}'@'%' IDENTIFIED BY %s", (app_password,))
            cursor.execute(
                f"""
                GRANT SELECT, INSERT, UPDATE, DELETE,
                    EXECUTE, CREATE TEMPORARY TABLES
                ON `{args.db_name}`.* TO '{args.app_user}'@'%'
                """
            )
            cursor.execute("FLUSH PRIVILEGES")
    finally:
        conn.close()

    env_values = {
        "DB_HOST": args.root_host,
        "DB_PORT": args.root_port,
        "DB_NAME": args.db_name,
        "DB_USER": args.app_user,
        "DB_PASSWORD": app_password,
    }
    _upsert_env(Path(args.env_file), env_values)

    db_url = f"mysql+pymysql://{args.root_user}:{args.root_password}@{args.root_host}:{args.root_port}/{args.db_name}"
    run_sql_migrations(database_url=db_url, applied_by="bootstrap_database")

    logger.info("Database bootstrap completed successfully")
    logger.info("App user: %s", args.app_user)
    logger.info("Env file updated: %s", args.env_file)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
