"""
Pydantic schemas for Crawl Job model.
"""

from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Field, ConfigDict

from app.models.crawl_job import CrawlStatus


class CrawlJobBase(BaseModel):
    """Base crawl job schema."""
    
    pass


class CrawlJobCreate(BaseModel):
    """Schema for creating a new crawl job."""
    
    project_id: int = Field(..., description="Project ID to crawl")


class CrawlJobUpdate(BaseModel):
    """Schema for updating crawl job status."""
    
    status: Optional[CrawlStatus] = None
    pages_crawled: Optional[int] = None
    pages_total: Optional[int] = None
    error_message: Optional[str] = None


class CrawlJobSummary(BaseModel):
    """Minimal crawl job schema for listings."""
    
    model_config = ConfigDict(from_attributes=True)
    
    id: int
    status: CrawlStatus
    pages_crawled: int
    pages_total: int
    created_at: datetime


class CrawlJobInDB(BaseModel):
    """Schema for crawl job as stored in database."""
    
    model_config = ConfigDict(from_attributes=True)
    
    id: int
    project_id: int
    status: CrawlStatus
    celery_task_id: Optional[str]
    started_at: Optional[datetime]
    completed_at: Optional[datetime]
    pages_crawled: int
    pages_total: int
    error_message: Optional[str]
    created_at: datetime
    updated_at: datetime


class CrawlJob(CrawlJobInDB):
    """Schema for crawl job in API responses."""
    
    duration_seconds: Optional[int] = Field(None, description="Crawl duration in seconds")
    
    @property
    def is_running(self) -> bool:
        """Check if crawl is running."""
        return self.status == CrawlStatus.RUNNING
    
    @property
    def is_finished(self) -> bool:
        """Check if crawl is finished."""
        return self.status in (CrawlStatus.COMPLETED, CrawlStatus.FAILED, CrawlStatus.CANCELLED)


class CrawlJobWithPages(CrawlJob):
    """Schema for crawl job with associated pages."""
    
    from app.schemas.page import PageSummary
    
    pages: list[PageSummary] = Field(default_factory=list)


class CrawlProgress(BaseModel):
    """Schema for realtime crawl progress."""
    
    crawl_job_id: int
    status: CrawlStatus
    pages_crawled: int
    pages_total: int
    progress_percentage: float = Field(..., ge=0, le=100)
    current_url: Optional[str] = None
