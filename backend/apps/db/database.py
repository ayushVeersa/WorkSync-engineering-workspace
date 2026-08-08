from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, sessionmaker

from apps.core.config import settings
from apps.core.logging import get_logger

logger = get_logger(__name__)

engine = create_engine(settings.db_url, connect_args={"check_same_thread": False})

logger.info("Database engine created for %s", settings.db_url)

SessionLocal = sessionmaker(
        autocommit=False,
        autoflush=False,
        bind=engine
        )

Base = declarative_base()

def get_db():
    db = SessionLocal()
    logger.debug("Database session opened")
    try:
        yield db
    finally:
        db.close()
        logger.debug("Database session closed")
