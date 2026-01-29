"""
Database session management using SQLAlchemy async.

This module configures the async database engine and session factory.
"""

from sqlalchemy.ext.asyncio import (
    AsyncEngine,
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)
from sqlalchemy.pool import NullPool

from app.core.config import settings


# Create async engine
# Using NullPool for development to avoid connection pool issues
engine: AsyncEngine = create_async_engine(
    settings.DATABASE_URL,
    echo=settings.DEBUG,
    future=True,
    pool_pre_ping=True,
    poolclass=NullPool if settings.is_development else None,
)

# Create async session factory
async_session_maker = async_sessionmaker(
    engine,
    class_=AsyncSession,
    expire_on_commit=False,
    autocommit=False,
    autoflush=False,
)


async def get_db_session() -> AsyncSession:
    """
    Get a database session.
    
    Returns:
        AsyncSession: SQLAlchemy async session.
    """
    async with async_session_maker() as session:
        return session
