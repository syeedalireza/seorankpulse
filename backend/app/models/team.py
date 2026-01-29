"""
Team collaboration models.
"""

from datetime import datetime
from typing import TYPE_CHECKING
from enum import Enum

from sqlalchemy import DateTime, ForeignKey, Integer, String, Text, Boolean
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.sql import func

from app.db.base import Base

if TYPE_CHECKING:
    from app.models.user import User
    from app.models.project import Project


class TeamRole(str, Enum):
    """Team member roles."""
    OWNER = "owner"
    ADMIN = "admin"
    ANALYST = "analyst"
    VIEWER = "viewer"


class TeamMember(Base):
    """
    Team member model for project collaboration.
    
    Represents a user's membership and role in a project team.
    """
    
    __tablename__ = "team_members"
    
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    
    # Foreign keys
    project_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey("projects.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    
    user_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    
    # Role and permissions
    role: Mapped[str] = mapped_column(String(50), nullable=False, default="viewer")
    
    # Metadata
    invited_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
    )
    
    joined_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
    )
    
    # Relationships
    project: Mapped["Project"] = relationship("Project", back_populates="team_members")
    user: Mapped["User"] = relationship("User")


class Comment(Base):
    """
    Comment model for discussions on pages/issues.
    
    Allows team members to discuss and collaborate on SEO issues.
    """
    
    __tablename__ = "comments"
    
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    
    # Foreign keys
    project_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey("projects.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    
    user_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
    )
    
    page_id: Mapped[int | None] = mapped_column(
        Integer,
        ForeignKey("pages.id", ondelete="CASCADE"),
        nullable=True,
    )
    
    # Comment content
    content: Mapped[str] = mapped_column(Text, nullable=False)
    
    # Metadata
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
    )
    
    updated_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
        onupdate=func.now(),
        nullable=True,
    )
    
    # Relationships
    user: Mapped["User"] = relationship("User")


class Task(Base):
    """
    Task model for SEO action items.
    
    Tracks tasks and assignments for fixing SEO issues.
    """
    
    __tablename__ = "tasks"
    
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    
    # Foreign keys
    project_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey("projects.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    
    created_by: Mapped[int] = mapped_column(
        Integer,
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
    )
    
    assigned_to: Mapped[int | None] = mapped_column(
        Integer,
        ForeignKey("users.id", ondelete="SET NULL"),
        nullable=True,
    )
    
    page_id: Mapped[int | None] = mapped_column(
        Integer,
        ForeignKey("pages.id", ondelete="CASCADE"),
        nullable=True,
    )
    
    # Task details
    title: Mapped[str] = mapped_column(String(255), nullable=False)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    priority: Mapped[str] = mapped_column(String(50), default="medium")  # low, medium, high, critical
    status: Mapped[str] = mapped_column(String(50), default="todo")  # todo, in_progress, done
    
    # Metadata
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
    )
    
    updated_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
        onupdate=func.now(),
        nullable=True,
    )
    
    due_date: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
    )
    
    completed_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
    )
    
    # Relationships
    creator: Mapped["User"] = relationship("User", foreign_keys=[created_by])
    assignee: Mapped["User | None"] = relationship("User", foreign_keys=[assigned_to])
