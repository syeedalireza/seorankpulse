"""
FastAPI dependency injection functions.

This module contains reusable dependencies for database sessions,
authentication, and other cross-cutting concerns.
"""

from typing import AsyncGenerator, Optional

from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.security import decode_token, verify_token_type
from app.db.session import async_session_maker
from app.models.user import User
from app.schemas.user import TokenPayload


# HTTP Bearer token security scheme
security = HTTPBearer()


async def get_db() -> AsyncGenerator[AsyncSession, None]:
    """
    Dependency that provides a database session.
    
    Yields:
        AsyncSession: SQLAlchemy async database session.
    """
    async with async_session_maker() as session:
        try:
            yield session
        finally:
            await session.close()


async def get_current_user(
    db: AsyncSession = Depends(get_db),
    credentials: HTTPAuthorizationCredentials = Depends(security),
) -> User:
    """
    Dependency that extracts and validates the current user from JWT token.
    
    Args:
        db: Database session.
        credentials: HTTP Bearer credentials containing JWT token.
    
    Returns:
        User: The authenticated user.
    
    Raises:
        HTTPException: If token is invalid or user not found.
    """
    token = credentials.credentials
    
    # Decode token
    payload = decode_token(token)
    if payload is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    # Verify token type
    if not verify_token_type(payload, "access"):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token type",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    # Extract user ID from token
    user_id: Optional[int] = payload.get("sub")
    if user_id is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    # Query user from database
    from app.models.user import User
    from sqlalchemy import select
    
    result = await db.execute(select(User).where(User.id == int(user_id)))
    user = result.scalar_one_or_none()
    
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found",
        )
    
    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Inactive user",
        )
    
    return user


async def get_current_active_superuser(
    current_user: User = Depends(get_current_user),
) -> User:
    """
    Dependency that ensures current user is a superuser/admin.
    
    Args:
        current_user: The current authenticated user.
    
    Returns:
        User: The authenticated superuser.
    
    Raises:
        HTTPException: If user is not a superuser.
    """
    if not current_user.is_superuser:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions",
        )
    return current_user


def get_optional_current_user(
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(security),
    db: AsyncSession = Depends(get_db),
) -> Optional[User]:
    """
    Dependency that optionally extracts current user if token is provided.
    
    Unlike get_current_user, this doesn't raise an error if no token is provided.
    Useful for endpoints that work differently for authenticated vs anonymous users.
    
    Args:
        credentials: Optional HTTP Bearer credentials.
        db: Database session.
    
    Returns:
        User | None: The authenticated user or None.
    """
    if credentials is None:
        return None
    
    try:
        # This would need to be implemented similar to get_current_user
        # For now, returning None
        return None
    except HTTPException:
        return None
