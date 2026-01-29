"""
Pydantic schemas for User model.

These schemas are used for request/response validation and serialization.
"""

from datetime import datetime
from typing import Optional

from pydantic import BaseModel, EmailStr, Field, ConfigDict


class UserBase(BaseModel):
    """Base user schema with common attributes."""
    
    email: EmailStr = Field(..., description="User email address")
    full_name: Optional[str] = Field(None, description="User full name", max_length=255)
    is_active: bool = Field(True, description="Whether user is active")


class UserCreate(BaseModel):
    """Schema for creating a new user."""
    
    email: EmailStr = Field(..., description="User email address")
    password: str = Field(..., min_length=8, max_length=100, description="User password")
    full_name: Optional[str] = Field(None, description="User full name", max_length=255)


class UserUpdate(BaseModel):
    """Schema for updating user information."""
    
    email: Optional[EmailStr] = Field(None, description="User email address")
    password: Optional[str] = Field(None, min_length=8, max_length=100, description="New password")
    full_name: Optional[str] = Field(None, description="User full name", max_length=255)
    is_active: Optional[bool] = Field(None, description="Whether user is active")


class UserInDB(UserBase):
    """Schema for user as stored in database."""
    
    model_config = ConfigDict(from_attributes=True)
    
    id: int
    is_superuser: bool
    created_at: datetime
    updated_at: datetime


class User(UserInDB):
    """Schema for user in API responses."""
    
    pass


class UserWithProjects(User):
    """Schema for user with associated projects."""
    
    from app.schemas.project import ProjectSummary
    
    projects: list[ProjectSummary] = Field(default_factory=list)


# Authentication schemas

class Token(BaseModel):
    """Schema for authentication token response."""
    
    access_token: str = Field(..., description="JWT access token")
    refresh_token: str = Field(..., description="JWT refresh token")
    token_type: str = Field(default="bearer", description="Token type")


class TokenPayload(BaseModel):
    """Schema for decoded JWT token payload."""
    
    sub: int = Field(..., description="Subject (user ID)")
    exp: int = Field(..., description="Expiration timestamp")
    type: str = Field(..., description="Token type (access or refresh)")


class LoginRequest(BaseModel):
    """Schema for login request."""
    
    email: EmailStr = Field(..., description="User email")
    password: str = Field(..., description="User password")


class RefreshTokenRequest(BaseModel):
    """Schema for refresh token request."""
    
    refresh_token: str = Field(..., description="JWT refresh token")
