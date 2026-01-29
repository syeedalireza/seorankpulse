"""
Pydantic schemas for Page model.
"""

from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Field, HttpUrl, ConfigDict


class PageBase(BaseModel):
    """Base page schema."""
    
    url: str = Field(..., description="Page URL")
    status_code: int = Field(..., description="HTTP status code")


class PageCreate(PageBase):
    """Schema for creating a new page record."""
    
    crawl_job_id: int
    url_hash: str
    response_time_ms: Optional[int] = None
    title: Optional[str] = None
    meta_description: Optional[str] = None
    meta_keywords: Optional[str] = None
    canonical_url: Optional[str] = None
    h1_tags: Optional[list[str]] = None
    h2_tags: Optional[list[str]] = None
    h3_tags: Optional[list[str]] = None
    images_count: int = 0
    images_without_alt: int = 0
    internal_links_count: int = 0
    external_links_count: int = 0
    word_count: int = 0
    text_to_html_ratio: Optional[float] = None
    page_size_bytes: Optional[int] = None
    schema_org_types: Optional[list[str]] = None
    og_tags: Optional[dict] = None
    has_robots_noindex: bool = False
    has_robots_nofollow: bool = False
    depth: int = 0


class PageSummary(BaseModel):
    """Minimal page schema for listings."""
    
    model_config = ConfigDict(from_attributes=True)
    
    id: int
    url: str
    status_code: int
    title: Optional[str]
    depth: int


class PageInDB(PageBase):
    """Schema for page as stored in database."""
    
    model_config = ConfigDict(from_attributes=True)
    
    id: int
    crawl_job_id: int
    url_hash: str
    response_time_ms: Optional[int]
    title: Optional[str]
    meta_description: Optional[str]
    meta_keywords: Optional[str]
    canonical_url: Optional[str]
    h1_tags: Optional[list]
    h2_tags: Optional[list]
    h3_tags: Optional[list]
    images_count: int
    images_without_alt: int
    internal_links_count: int
    external_links_count: int
    word_count: int
    text_to_html_ratio: Optional[float]
    page_size_bytes: Optional[int]
    schema_org_types: Optional[list]
    og_tags: Optional[dict]
    has_robots_noindex: bool
    has_robots_nofollow: bool
    depth: int
    created_at: datetime


class Page(PageInDB):
    """Schema for page in API responses."""
    
    pass


class PageWithIssues(Page):
    """Schema for page with SEO issues."""
    
    issues: list[str] = Field(default_factory=list, description="List of SEO issues")
    warnings: list[str] = Field(default_factory=list, description="List of SEO warnings")
    seo_score: int = Field(..., ge=0, le=100, description="SEO score (0-100)")


class PageAnalysis(BaseModel):
    """Schema for detailed page analysis."""
    
    page: Page
    seo_score: int = Field(..., ge=0, le=100)
    issues: list[dict] = Field(default_factory=list)
    warnings: list[dict] = Field(default_factory=list)
    suggestions: list[str] = Field(default_factory=list)
    
    # Detailed metrics
    title_analysis: dict = Field(default_factory=dict)
    meta_analysis: dict = Field(default_factory=dict)
    headings_analysis: dict = Field(default_factory=dict)
    images_analysis: dict = Field(default_factory=dict)
    links_analysis: dict = Field(default_factory=dict)
    content_analysis: dict = Field(default_factory=dict)
