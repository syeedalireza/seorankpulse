"""
Tests for authentication API endpoints.
"""

import pytest
from fastapi.testclient import TestClient
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.security import get_password_hash
from app.models.user import User


@pytest.mark.asyncio
async def test_register_user(client: TestClient, db_session: AsyncSession):
    """Test user registration endpoint."""
    response = client.post(
        "/api/v1/auth/register",
        json={
            "email": "test@example.com",
            "password": "testpassword123",
            "full_name": "Test User",
        },
    )
    
    assert response.status_code == 201
    data = response.json()
    assert data["email"] == "test@example.com"
    assert data["full_name"] == "Test User"
    assert "hashed_password" not in data


@pytest.mark.asyncio
async def test_register_duplicate_email(client: TestClient, db_session: AsyncSession):
    """Test that duplicate email registration fails."""
    # First registration
    client.post(
        "/api/v1/auth/register",
        json={
            "email": "duplicate@example.com",
            "password": "password123",
        },
    )
    
    # Try to register again with same email
    response = client.post(
        "/api/v1/auth/register",
        json={
            "email": "duplicate@example.com",
            "password": "different_password",
        },
    )
    
    assert response.status_code == 400
    assert "already registered" in response.json()["detail"].lower()


@pytest.mark.asyncio
async def test_login_success(client: TestClient, db_session: AsyncSession):
    """Test successful login."""
    # Create user first
    user = User(
        email="login@example.com",
        hashed_password=get_password_hash("correctpassword"),
        is_active=True,
    )
    db_session.add(user)
    await db_session.commit()
    
    # Login
    response = client.post(
        "/api/v1/auth/login",
        json={
            "email": "login@example.com",
            "password": "correctpassword",
        },
    )
    
    assert response.status_code == 200
    data = response.json()
    assert "access_token" in data
    assert "refresh_token" in data
    assert data["token_type"] == "bearer"


@pytest.mark.asyncio
async def test_login_wrong_password(client: TestClient, db_session: AsyncSession):
    """Test login with wrong password."""
    # Create user
    user = User(
        email="user@example.com",
        hashed_password=get_password_hash("correctpassword"),
        is_active=True,
    )
    db_session.add(user)
    await db_session.commit()
    
    # Try login with wrong password
    response = client.post(
        "/api/v1/auth/login",
        json={
            "email": "user@example.com",
            "password": "wrongpassword",
        },
    )
    
    assert response.status_code == 401
