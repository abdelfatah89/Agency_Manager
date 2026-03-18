import argparse
import logging
import sys
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(BASE_DIR))

from services.app_logging import configure_logging
from services.db_services.sql_migration_runner import run_sql_migrations


logger = logging.getLogger(__name__)


def main() -> int:
    parser = argparse.ArgumentParser(description="Run SQL migrations using privileged DB account")
    parser.add_argument("--host", default="127.0.0.1")
    parser.add_argument("--port", type=int, default=3306)
    parser.add_argument("--user", default="root")
    parser.add_argument("--password", required=True)
    parser.add_argument("--db-name", default="konach_new")
    args = parser.parse_args()

    configure_logging()
    db_url = f"mysql+pymysql://{args.user}:{args.password}@{args.host}:{args.port}/{args.db_name}"

    try:
        run_sql_migrations(database_url=db_url, applied_by="root_upgrade_runner")
        logger.info("Privileged SQL migrations completed")
        return 0
    except Exception:
        logger.exception("Privileged SQL migrations failed")
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
