"""
Crawl Job model representing crawl execution instances.
"""

from datetime import datetime
from enum import Enum
from typing import TYPE_CHECKING

from sqlalchemy import DateTime, Enum as SQLEnum, ForeignKey, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.sql import func

from app.db.base import Base

if TYPE_CHECKING:
    from app.models.page import Page
    from app.models.project import Project


class CrawlStatus(str, Enum):
    """Enumeration of possible crawl job statuses."""
    
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


class CrawlJob(Base):
    """
    Crawl Job model representing a single crawl execution.
    
    A project can have multiple crawl jobs over time.
    
    Attributes:
        id: Primary key.
        project_id: Foreign key to the project.
        status: Current status of the crawl job.
        celery_task_id: Celery task ID for tracking background job.
        started_at: Timestamp when crawl started.
        completed_at: Timestamp when crawl completed.
        pages_crawled: Number of pages successfully crawled.
        pages_total: Total number of pages discovered.
        error_message: Error message if crawl failed.
        created_at: Timestamp of job creation.
        updated_at: Timestamp of last update.
        project: Relationship to the associated project.
        pages: Relationship to crawled pages.
    """
    
    __tablename__ = "crawl_jobs"
    
    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    
    # Foreign keys
    project_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey("projects.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    
    # Status tracking
    status: Mapped[CrawlStatus] = mapped_column(
        SQLEnum(CrawlStatus),
        default=CrawlStatus.PENDING,
        nullable=False,
        index=True,
    )
    celery_task_id: Mapped[str | None] = mapped_column(String(255), nullable=True, index=True)
    
    # Timing
    started_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    completed_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    
    # Statistics
    pages_crawled: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    pages_total: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    
    # Error handling
    error_message: Mapped[str | None] = mapped_column(Text, nullable=True)
    
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
    project: Mapped["Project"] = relationship("Project", back_populates="crawl_jobs")
    pages: Mapped[list["Page"]] = relationship(
        "Page",
        back_populates="crawl_job",
        cascade="all, delete-orphan",
    )
    
    def __repr__(self) -> str:
        """String representation of CrawlJob."""
        return f"<CrawlJob(id={self.id}, project_id={self.project_id}, status={self.status})>"
    
    @property
    def duration_seconds(self) -> int | None:
        """Calculate crawl duration in seconds."""
        if self.started_at and self.completed_at:
            delta = self.completed_at - self.started_at
            return int(delta.total_seconds())
        return None
    
    @property
    def is_running(self) -> bool:
        """Check if crawl is currently running."""
        return self.status == CrawlStatus.RUNNING
    
    @property
    def is_finished(self) -> bool:
        """Check if crawl has finished (completed, failed, or cancelled)."""
        return self.status in (CrawlStatus.COMPLETED, CrawlStatus.FAILED, CrawlStatus.CANCELLED)
