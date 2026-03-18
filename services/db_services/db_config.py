import os
import logging
from functools import wraps
from dotenv import load_dotenv
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker
from sqlalchemy.exc import SQLAlchemyError


logger = logging.getLogger(__name__)

load_dotenv()

DB_USER = os.getenv("DB_USER")
DB_PASSWORD = os.getenv("DB_PASSWORD")
DB_HOST = os.getenv("DB_HOST")
DB_PORT = int(os.getenv("DB_PORT") or 3306)
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
