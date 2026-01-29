"""
Pydantic schemas for Project model.
"""

from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Field, HttpUrl, ConfigDict, field_validator


class ProjectBase(BaseModel):
    """Base project schema with common attributes."""
    
    name: str = Field(..., min_length=1, max_length=255, description="Project name")
    domain: str = Field(..., min_length=1, max_length=255, description="Domain to analyze")
    description: Optional[str] = Field(None, description="Project description")
    
    @field_validator("domain")
    @classmethod
    def validate_domain(cls, v: str) -> str:
        """Validate and normalize domain."""
        # Remove protocol if present
        domain = v.lower()
        for prefix in ["https://", "http://", "www."]:
            if domain.startswith(prefix):
                domain = domain[len(prefix):]
        
        # Remove trailing slash
        domain = domain.rstrip("/")
        
        return domain


class ProjectCreate(ProjectBase):
    """Schema for creating a new project."""
    
    max_depth: int = Field(default=10, ge=1, le=50, description="Maximum crawl depth")
    crawl_delay_ms: int = Field(
        default=1000,
        ge=100,
        le=10000,
        description="Delay between requests (ms)",
    )
    user_agent: Optional[str] = Field(
        default="SEO-Analyzer-Bot/1.0",
        max_length=255,
        description="User agent string",
    )
    respect_robots_txt: bool = Field(default=True, description="Respect robots.txt")


class ProjectUpdate(BaseModel):
    """Schema for updating project information."""
    
    name: Optional[str] = Field(None, min_length=1, max_length=255)
    description: Optional[str] = None
    max_depth: Optional[int] = Field(None, ge=1, le=50)
    crawl_delay_ms: Optional[int] = Field(None, ge=100, le=10000)
    user_agent: Optional[str] = Field(None, max_length=255)
    respect_robots_txt: Optional[bool] = None


class ProjectSummary(BaseModel):
    """Minimal project schema for listings."""
    
    model_config = ConfigDict(from_attributes=True)
    
    id: int
    name: str
    domain: str
    created_at: datetime


class ProjectInDB(ProjectBase):
    """Schema for project as stored in database."""
    
    model_config = ConfigDict(from_attributes=True)
    
    id: int
    user_id: int
    max_depth: int
    crawl_delay_ms: int
    user_agent: str
    respect_robots_txt: bool
    created_at: datetime
    updated_at: datetime


class Project(ProjectInDB):
    """Schema for project in API responses."""
    
    pass


class ProjectWithStats(Project):
    """Schema for project with crawl statistics."""
    
    total_crawls: int = Field(default=0, description="Total number of crawls")
    last_crawl_date: Optional[datetime] = Field(None, description="Date of last crawl")
    total_pages: int = Field(default=0, description="Total pages crawled")
