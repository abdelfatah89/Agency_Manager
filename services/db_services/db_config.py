import os
import logging
from functools import wraps
from dotenv import load_dotenv
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker

from services.db_services.simple_db_setup import setup_database

logger = logging.getLogger(__name__)

load_dotenv()

DB_USER = os.getenv("DB_USER", "konach_user")
DB_PASSWORD = os.getenv("DB_PASSWORD", "strong_password")
DB_HOST = os.getenv("DB_HOST", os.getenv("MYSQL_HOST", "localhost"))
DB_PORT = int(os.getenv("DB_PORT") or os.getenv("MYSQL_PORT") or 3306)
_env_db_name = os.getenv("DB_NAME", "").strip()

if not DB_USER or not DB_HOST:
    logger.error("Missing required DB configuration values: DB_USER and DB_HOST must be set")

DB_CANDIDATES = []
if _env_db_name:
    DB_CANDIDATES.append(_env_db_name)
else:
    DB_CANDIDATES.append("konach_new")


def _build_engine(db_name: str):
    return create_engine(
        f"mysql+pymysql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{db_name}",
        echo=False,
        future=True,
        pool_pre_ping=True,
        pool_size=10,
        max_overflow=20,
        pool_recycle=1800,
    )


engine = None
DB_NAME = DB_CANDIDATES[0]

for _candidate in DB_CANDIDATES:
    try:
        _engine = _build_engine(_candidate)
        with _engine.connect() as conn:
            conn.execute(text("SELECT 1"))
        engine = _engine
        DB_NAME = _candidate
        logger.info("Connected to database: %s", DB_NAME)
        break
    except Exception as e:
        logger.warning("Database connection failed for '%s': %s", _candidate, e)

if engine is None:
    # Keep module importable; runtime DB operations will surface connection issues.
    engine = _build_engine(DB_NAME)

DB_CONFIG = {
    "user": DB_USER,
    "password": DB_PASSWORD,
    "host": DB_HOST,
    "port": DB_PORT,
    "database": DB_NAME,
}

SessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False, future=True)


def _rebind_engine(new_engine) -> None:
    global engine
    engine = new_engine
    SessionLocal.configure(bind=engine)


def initialize_database_connection() -> bool:
    """Connect with app credentials; run simple setup if first-run DB is missing."""
    global DB_NAME
    try:
        test_engine = _build_engine(DB_NAME)
        with test_engine.connect() as conn:
            conn.execute(text("SELECT 1"))
        _rebind_engine(test_engine)
        logger.info("Database connection ready: %s", DB_NAME)
        return True
    except Exception as exc:
        logger.warning("Initial DB connection failed: %s", exc)

    logger.info("Attempting first-run simple database setup...")
    if not setup_database():
        logger.error("Simple database setup failed")
        return False

    try:
        test_engine = _build_engine(DB_NAME)
        with test_engine.connect() as conn:
            conn.execute(text("SELECT 1"))
        _rebind_engine(test_engine)
        logger.info("Database connection ready after setup: %s", DB_NAME)
        return True
    except Exception:
        logger.exception("Database connection still failing after setup")
        return False

def with_session(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        session = SessionLocal()
        try:
            result = func(*args, session=session, **kwargs)
            session.commit()
            return result
        except Exception as e:
            session.rollback()
            raise e
        finally:
            session.close()
    return wrapper
