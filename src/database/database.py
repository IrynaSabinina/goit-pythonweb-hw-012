from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import declarative_base, sessionmaker

from src.conf.config import settings

import logging
from sqlalchemy.engine import Engine

# Увімкнення логів SQL-запитів
logging.getLogger("sqlalchemy.engine").setLevel(logging.DEBUG)

# Asynchronous database connection URL for PostgreSQL
SQLALCHEMY_DATABASE_URL = settings.database_url.replace(
    "postgresql://", "postgresql+asyncpg://"
)

# Asynchronous SQLAlchemy engine
engine = create_async_engine(SQLALCHEMY_DATABASE_URL, echo=True)

# Asynchronous session factory
AsyncSessionLocal = sessionmaker(
    bind=engine,
    class_=AsyncSession,
    expire_on_commit=False,
)

# Base class for ORM models
Base = declarative_base()


async def get_db() -> AsyncSession:
    """
    Dependency to provide an asynchronous database session.

    This function yields an async session that ensures proper resource
    management using a context manager.

    Yields:
        AsyncSession: SQLAlchemy asynchronous session instance.
    """
    async with AsyncSessionLocal() as session:
        yield session
