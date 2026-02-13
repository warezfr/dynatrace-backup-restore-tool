"""Database configuration and session management"""
from sqlalchemy import create_engine, event
from sqlalchemy.orm import sessionmaker, declarative_base
from sqlalchemy.pool import StaticPool
from ..core.config import settings

# Configure SQLite with proper settings for backup scenarios
engine = create_engine(
    settings.DATABASE_URL,
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
    echo=settings.DEBUG,
)

# Enable WAL mode for better concurrency
@event.listens_for(engine, "connect")
def set_sqlite_pragma(dbapi_conn, connection_record):
    cursor = dbapi_conn.cursor()
    cursor.execute("PRAGMA journal_mode=WAL")
    cursor.execute("PRAGMA foreign_keys=ON")
    cursor.close()

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def init_db():
    """Initialize database tables"""
    Base.metadata.create_all(bind=engine)
    _migrate_legacy_columns()


def _column_exists(table: str, column: str) -> bool:
    with engine.connect() as conn:
        res = conn.exec_driver_sql(f"PRAGMA table_info({table})")
        cols = [row[1] for row in res.fetchall()]
        return column in cols


def _migrate_legacy_columns():
    """Lightweight migrations for legacy installs"""
    # deployment_type column for dynatrace_environments
    if not _column_exists("dynatrace_environments", "deployment_type"):
        with engine.begin() as conn:
            conn.exec_driver_sql(
                "ALTER TABLE dynatrace_environments "
                "ADD COLUMN deployment_type TEXT DEFAULT 'managed'"
            )
