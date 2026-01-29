"""
Schemas for team collaboration features.
"""

from datetime import datetime
from typing import Optional
from pydantic import BaseModel, Field


class TeamMemberBase(BaseModel):
    """Base team member schema."""
    role: str = Field(..., description="Team member role")


class TeamMemberCreate(TeamMemberBase):
    """Schema for inviting team member."""
    user_email: str = Field(..., description="Email of user to invite")


class TeamMemberResponse(TeamMemberBase):
    """Schema for team member response."""
    id: int
    project_id: int
    user_id: int
    invited_at: datetime
    joined_at: Optional[datetime] = None
    
    class Config:
        from_attributes = True


class CommentBase(BaseModel):
    """Base comment schema."""
    content: str = Field(..., min_length=1, max_length=5000)


class CommentCreate(CommentBase):
    """Schema for creating comment."""
    page_id: Optional[int] = None


class CommentResponse(CommentBase):
    """Schema for comment response."""
    id: int
    project_id: int
    user_id: int
    page_id: Optional[int] = None
    created_at: datetime
    updated_at: Optional[datetime] = None
    
    class Config:
        from_attributes = True


class TaskBase(BaseModel):
    """Base task schema."""
    title: str = Field(..., min_length=1, max_length=255)
    description: Optional[str] = None
    priority: str = Field(default="medium", pattern="^(low|medium|high|critical)$")
    status: str = Field(default="todo", pattern="^(todo|in_progress|done)$")


class TaskCreate(TaskBase):
    """Schema for creating task."""
    assigned_to: Optional[int] = None
    page_id: Optional[int] = None
    due_date: Optional[datetime] = None


class TaskUpdate(BaseModel):
    """Schema for updating task."""
    title: Optional[str] = None
    description: Optional[str] = None
    priority: Optional[str] = None
    status: Optional[str] = None
    assigned_to: Optional[int] = None
    due_date: Optional[datetime] = None


class TaskResponse(TaskBase):
    """Schema for task response."""
    id: int
    project_id: int
    created_by: int
    assigned_to: Optional[int] = None
    page_id: Optional[int] = None
    created_at: datetime
    updated_at: Optional[datetime] = None
    due_date: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    
    class Config:
        from_attributes = True
