"""
Page model representing crawled web pages.
"""

from datetime import datetime
from typing import TYPE_CHECKING

from sqlalchemy import DateTime, Float, ForeignKey, Integer, String, Text, JSON
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.sql import func

from app.db.base import Base

if TYPE_CHECKING:
    from app.models.crawl_job import CrawlJob


class Page(Base):
    """
    Page model representing a crawled web page.
    
    Stores all SEO-relevant data extracted from a single page.
    
    Attributes:
        id: Primary key.
        crawl_job_id: Foreign key to the crawl job.
        url: The full URL of the page.
        url_hash: Hash of URL for fast lookups.
        status_code: HTTP status code.
        response_time_ms: Response time in milliseconds.
        title: Page title tag content.
        meta_description: Meta description content.
        meta_keywords: Meta keywords content.
        canonical_url: Canonical URL if specified.
        h1_tags: List of H1 tag contents (JSON).
        h2_tags: List of H2 tag contents (JSON).
        h3_tags: List of H3 tag contents (JSON).
        images_count: Total number of images.
        images_without_alt: Number of images missing alt tags.
        internal_links_count: Number of internal links.
        external_links_count: Number of external links.
        word_count: Total word count.
        text_to_html_ratio: Ratio of text content to HTML size.
        page_size_bytes: Total page size in bytes.
        schema_org_types: Schema.org types found (JSON).
        og_tags: Open Graph tags (JSON).
        has_robots_noindex: Whether page has noindex directive.
        has_robots_nofollow: Whether page has nofollow directive.
        depth: Depth from homepage.
        created_at: Timestamp of page record creation.
        crawl_job: Relationship to the crawl job.
    """
    
    __tablename__ = "pages"
    
    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    
    # Foreign keys
    crawl_job_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey("crawl_jobs.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    
    # URL information
    url: Mapped[str] = mapped_column(Text, nullable=False)
    url_hash: Mapped[str] = mapped_column(String(64), nullable=False, index=True, unique=True)
    
    # HTTP information
    status_code: Mapped[int] = mapped_column(Integer, nullable=False, index=True)
    response_time_ms: Mapped[int | None] = mapped_column(Integer, nullable=True)
    
    # Meta tags
    title: Mapped[str | None] = mapped_column(String(1000), nullable=True)
    meta_description: Mapped[str | None] = mapped_column(Text, nullable=True)
    meta_keywords: Mapped[str | None] = mapped_column(Text, nullable=True)
    canonical_url: Mapped[str | None] = mapped_column(Text, nullable=True)
    
    # Headings (stored as JSON arrays)
    h1_tags: Mapped[list | None] = mapped_column(JSON, nullable=True)
    h2_tags: Mapped[list | None] = mapped_column(JSON, nullable=True)
    h3_tags: Mapped[list | None] = mapped_column(JSON, nullable=True)
    
    # Images
    images_count: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    images_without_alt: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    
    # Links
    internal_links_count: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    external_links_count: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    
    # Content analysis
    word_count: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    text_to_html_ratio: Mapped[float | None] = mapped_column(Float, nullable=True)
    page_size_bytes: Mapped[int | None] = mapped_column(Integer, nullable=True)
    
    # Structured data
    schema_org_types: Mapped[list | None] = mapped_column(JSON, nullable=True)
    og_tags: Mapped[dict | None] = mapped_column(JSON, nullable=True)
    
    # Robots directives
    has_robots_noindex: Mapped[bool] = mapped_column(default=False, nullable=False)
    has_robots_nofollow: Mapped[bool] = mapped_column(default=False, nullable=False)
    
    # Crawl metadata
    depth: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
    )
    
    # Relationships
    crawl_job: Mapped["CrawlJob"] = relationship("CrawlJob", back_populates="pages")
    
    def __repr__(self) -> str:
        """String representation of Page."""
        return f"<Page(id={self.id}, url={self.url[:50]}, status={self.status_code})>"
    
    @property
    def is_success(self) -> bool:
        """Check if page was successfully crawled (2xx status)."""
        return 200 <= self.status_code < 300
    
    @property
    def is_redirect(self) -> bool:
        """Check if page is a redirect (3xx status)."""
        return 300 <= self.status_code < 400
    
    @property
    def is_client_error(self) -> bool:
        """Check if page returned client error (4xx status)."""
        return 400 <= self.status_code < 500
    
    @property
    def is_server_error(self) -> bool:
        """Check if page returned server error (5xx status)."""
        return self.status_code >= 500
    
    @property
    def title_length(self) -> int:
        """Get title length."""
        return len(self.title) if self.title else 0
    
    @property
    def meta_description_length(self) -> int:
        """Get meta description length."""
        return len(self.meta_description) if self.meta_description else 0
