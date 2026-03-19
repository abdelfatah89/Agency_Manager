import logging
import os
from pathlib import Path

import pymysql

from services.db_services.sql_migration_runner import run_sql_migrations


logger = logging.getLogger(__name__)


def _project_root() -> Path:
    return Path(__file__).resolve().parents[2]


def _env(name: str, default: str = "") -> str:
    return os.getenv(name, default).strip()


def _sql_dir() -> Path:
    candidates = [
        _project_root() / "sql",
        Path.cwd() / "sql",
    ]
    for path in candidates:
        if path.exists():
            return path
    return candidates[0]


def setup_database() -> bool:
    """Simple DB bootstrap for AppServ-managed MySQL.

    Steps:
    1) connect with MySQL root credentials from .env
    2) create DB/user/grants
    3) apply 001 schema
    4) apply migrations
    """
    root_user = _env("MYSQL_ROOT_USER", "root")
    root_password = _env("MYSQL_ROOT_PASSWORD")
    host = _env("MYSQL_HOST", _env("DB_HOST", "localhost"))
    port = int(_env("MYSQL_PORT", _env("DB_PORT", "3306")) or "3306")

    db_name = _env("DB_NAME", "konach")
    app_user = _env("DB_USER", "konach_user")
    app_password = _env("DB_PASSWORD", "strong_password")

    if not root_password:
        logger.error("MYSQL_ROOT_PASSWORD is required for initial database setup")
        return False

    if not db_name or not app_user or not app_password:
        logger.error("DB_NAME, DB_USER and DB_PASSWORD must be set")
        return False

    try:
        logger.info("Connecting to MySQL as root at %s:%s", host, port)
        conn = pymysql.connect(
            host=host,
            port=port,
            user=root_user,
            password=root_password,
            database="mysql",
            autocommit=True,
        )
        try:
            with conn.cursor() as cursor:
                cursor.execute(
                    f"CREATE DATABASE IF NOT EXISTS `{db_name}` CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci"
                )
                cursor.execute(
                    f"CREATE USER IF NOT EXISTS '{app_user}'@'localhost' IDENTIFIED BY %s",
                    (app_password,),
                )
                cursor.execute(
                    f"ALTER USER '{app_user}'@'localhost' IDENTIFIED BY %s",
                    (app_password,),
                )
                cursor.execute(
                    f"GRANT ALL PRIVILEGES ON `{db_name}`.* TO '{app_user}'@'localhost'"
                )
                cursor.execute("FLUSH PRIVILEGES")
        finally:
            conn.close()

        logger.info("Verifying connection with application user")
        app_conn = pymysql.connect(
            host=host,
            port=port,
            user=app_user,
            password=app_password,
            database=db_name,
            autocommit=True,
        )
        app_conn.close()

        sql_dir = _sql_dir()
        schema_file = sql_dir / "001_initial_schema.sql"
        if schema_file.exists():
            logger.info("Applying base schema: %s", schema_file)
            schema_sql = schema_file.read_text(encoding="utf-8")
            conn_db = pymysql.connect(
                host=host,
                port=port,
                user=app_user,
                password=app_password,
                database=db_name,
                autocommit=True,
            )
            try:
                with conn_db.cursor() as cursor:
                    for statement in [s.strip() for s in schema_sql.split(";") if s.strip()]:
                        cursor.execute(statement)
            finally:
                conn_db.close()

        logger.info("Running SQL migrations from: %s", sql_dir)
        db_url = f"mysql+pymysql://{app_user}:{app_password}@{host}:{port}/{db_name}"
        run_sql_migrations(database_url=db_url, migrations_dir=sql_dir, applied_by="simple_db_setup")

        logger.info("Simple database setup completed successfully")
        return True
    except Exception:
        logger.exception("Simple database setup failed")
        return False
