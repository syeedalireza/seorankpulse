"""
Custom dashboard models.
"""

from datetime import datetime
from typing import TYPE_CHECKING
from sqlalchemy import DateTime, ForeignKey, Integer, String, Text, JSON, Boolean
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.sql import func

from app.db.base import Base

if TYPE_CHECKING:
    from app.models.user import User
    from app.models.project import Project


class Dashboard(Base):
    """
    Custom dashboard model.
    
    Allows users to create personalized dashboards with custom widgets.
    """
    
    __tablename__ = "dashboards"
    
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    
    # Foreign keys
    user_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    
    project_id: Mapped[int | None] = mapped_column(
        Integer,
        ForeignKey("projects.id", ondelete="CASCADE"),
        nullable=True,
        index=True,
    )
    
    # Dashboard details
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    
    # Layout configuration (JSON)
    layout: Mapped[dict] = mapped_column(JSON, nullable=False, default=dict)
    
    # Sharing and permissions
    is_public: Mapped[bool] = mapped_column(Boolean, default=False)
    is_default: Mapped[bool] = mapped_column(Boolean, default=False)
    
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
    widgets: Mapped[list["DashboardWidget"]] = relationship(
        "DashboardWidget",
        back_populates="dashboard",
        cascade="all, delete-orphan"
    )


class DashboardWidget(Base):
    """
    Dashboard widget model.
    
    Represents individual widgets on a dashboard.
    """
    
    __tablename__ = "dashboard_widgets"
    
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    
    # Foreign key
    dashboard_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey("dashboards.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    
    # Widget configuration
    widget_type: Mapped[str] = mapped_column(String(100), nullable=False)
    title: Mapped[str] = mapped_column(String(255), nullable=False)
    
    # Position and size
    position_x: Mapped[int] = mapped_column(Integer, default=0)
    position_y: Mapped[int] = mapped_column(Integer, default=0)
    width: Mapped[int] = mapped_column(Integer, default=4)
    height: Mapped[int] = mapped_column(Integer, default=4)
    
    # Widget settings (JSON)
    config: Mapped[dict] = mapped_column(JSON, nullable=False, default=dict)
    
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
    dashboard: Mapped["Dashboard"] = relationship("Dashboard", back_populates="widgets")
