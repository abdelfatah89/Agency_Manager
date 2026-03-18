import logging
import os
import sys
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(BASE_DIR))

from services.app_logging import configure_logging
from services.db_services.sql_migration_runner import run_sql_migrations


logger = logging.getLogger(__name__)


def main() -> int:
    configure_logging()
    db_user = os.getenv("DB_USER")
    db_password = os.getenv("DB_PASSWORD")
    db_host = os.getenv("DB_HOST")
    db_port = int(os.getenv("DB_PORT") or 3306)
    db_name = os.getenv("DB_NAME")

    if not all([db_user, db_host, db_name]):
        logger.error("Missing DB env vars. Required: DB_USER, DB_HOST, DB_NAME")
        return 1

    database_url = f"mysql+pymysql://{db_user}:{db_password}@{db_host}:{db_port}/{db_name}"

    try:
        run_sql_migrations(database_url=database_url, applied_by="manual_runner")
        logger.info("SQL migrations completed successfully")
        return 0
    except Exception:
        logger.exception("SQL migration run failed")
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
