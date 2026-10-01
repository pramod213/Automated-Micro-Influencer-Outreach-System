"""Database engine and session management."""

from contextlib import contextmanager
from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker
from app.config import settings


def create_database_engine():
    """Create SQLAlchemy engine with appropriate configuration."""
    engine = create_engine(
        settings.database_url,
        connect_args={"check_same_thread": False} if settings.database_url.startswith("sqlite") else {},
        pool_pre_ping=True,
        echo=settings.debug,
    )
    return engine


engine = create_database_engine()

SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine,
    class_=Session,
)


def get_db():
    """Dependency for FastAPI to get database session."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@contextmanager
def get_db_context():
    """Context manager for database session outside of FastAPI."""
    db = SessionLocal()
    try:
        yield db
        db.commit()
    except Exception:
        db.rollback()
        raise
    finally:
        db.close()


def init_db():
    """Initialize database tables. Use migrations in production."""
    from app.database.models import Influencer, Message, OutreachLog  # noqa: F401
    from app.database.base import Base
    Base.metadata.create_all(bind=engine)