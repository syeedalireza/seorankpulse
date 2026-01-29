"""
Project model representing SEO analysis projects.
"""

from datetime import datetime
from typing import TYPE_CHECKING

from sqlalchemy import DateTime, ForeignKey, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.sql import func

from app.db.base import Base

if TYPE_CHECKING:
    from app.models.crawl_job import CrawlJob
    from app.models.user import User


class Project(Base):
    """
    Project model representing an SEO analysis project.
    
    Each project is associated with a specific domain/website to analyze.
    
    Attributes:
        id: Primary key.
        name: Project name.
        domain: The domain to analyze (e.g., "example.com").
        description: Optional project description.
        user_id: Foreign key to the owner user.
        max_depth: Maximum crawl depth.
        crawl_delay_ms: Delay between requests in milliseconds.
        user_agent: Custom user agent string.
        respect_robots_txt: Whether to respect robots.txt rules.
        created_at: Timestamp of project creation.
        updated_at: Timestamp of last update.
        owner: Relationship to the owner user.
        crawl_jobs: Relationship to associated crawl jobs.
    """
    
    __tablename__ = "projects"
    
    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    domain: Mapped[str] = mapped_column(String(255), nullable=False, index=True)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    
    # Foreign keys
    user_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    
    # Crawler settings
    max_depth: Mapped[int] = mapped_column(Integer, default=10, nullable=False)
    crawl_delay_ms: Mapped[int] = mapped_column(Integer, default=1000, nullable=False)
    user_agent: Mapped[str] = mapped_column(
        String(255),
        default="SEO-Analyzer-Bot/1.0",
        nullable=False,
    )
    respect_robots_txt: Mapped[bool] = mapped_column(default=True, nullable=False)
    
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False,
    )
    
    # Relationships
    owner: Mapped["User"] = relationship("User", back_populates="projects")
    crawl_jobs: Mapped[list["CrawlJob"]] = relationship(
        "CrawlJob",
        back_populates="project",
        cascade="all, delete-orphan",
    )
    
    def __repr__(self) -> str:
        """String representation of Project."""
        return f"<Project(id={self.id}, name={self.name}, domain={self.domain})>"
