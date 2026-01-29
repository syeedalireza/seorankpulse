"""
Analysis API endpoints.

Handles SEO analysis and reporting.
"""

from typing import List

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.dependencies import get_current_user, get_db
from app.models.crawl_job import CrawlJob
from app.models.page import Page
from app.models.project import Project
from app.models.user import User
from app.schemas.page import PageAnalysis, PageSummary, PageWithIssues


router = APIRouter()


@router.get("/crawl/{crawl_id}/pages", response_model=List[PageSummary])
async def get_crawl_pages(
    crawl_id: int,
    skip: int = 0,
    limit: int = 100,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> List[Page]:
    """
    Get all pages from a crawl job.
    
    Args:
        crawl_id: Crawl job ID.
        skip: Number of records to skip.
        limit: Maximum number of records.
        db: Database session.
        current_user: Authenticated user.
    
    Returns:
        list[Page]: List of crawled pages.
    
    Raises:
        HTTPException: If crawl not found or access denied.
    """
    # Verify crawl job access
    result = await db.execute(
        select(CrawlJob)
        .join(Project)
        .where(
            CrawlJob.id == crawl_id,
            Project.user_id == current_user.id,
        )
    )
    crawl_job = result.scalar_one_or_none()
    
    if not crawl_job:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Crawl job not found",
        )
    
    # Get pages
    result = await db.execute(
        select(Page)
        .where(Page.crawl_job_id == crawl_id)
        .offset(skip)
        .limit(limit)
    )
    pages = result.scalars().all()
    
    return pages


@router.get("/crawl/{crawl_id}/issues", response_model=List[PageWithIssues])
async def get_crawl_issues(
    crawl_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> List[dict]:
    """
    Get all SEO issues found in a crawl.
    
    Args:
        crawl_id: Crawl job ID.
        db: Database session.
        current_user: Authenticated user.
    
    Returns:
        list[dict]: List of pages with SEO issues.
    
    Raises:
        HTTPException: If crawl not found or access denied.
    """
    # Verify crawl job access
    result = await db.execute(
        select(CrawlJob)
        .join(Project)
        .where(
            CrawlJob.id == crawl_id,
            Project.user_id == current_user.id,
        )
    )
    crawl_job = result.scalar_one_or_none()
    
    if not crawl_job:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Crawl job not found",
        )
    
    # Get all pages
    result = await db.execute(
        select(Page).where(Page.crawl_job_id == crawl_id)
    )
    pages = result.scalars().all()
    
    # Analyze each page for issues
    pages_with_issues = []
    for page in pages:
        issues, warnings, score = analyze_page_seo(page)
        
        if issues or warnings:
            page_dict = page.__dict__.copy()
            page_dict["issues"] = issues
            page_dict["warnings"] = warnings
            page_dict["seo_score"] = score
            pages_with_issues.append(page_dict)
    
    return pages_with_issues


@router.get("/page/{page_id}", response_model=PageAnalysis)
async def get_page_analysis(
    page_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> dict:
    """
    Get detailed SEO analysis for a specific page.
    
    Args:
        page_id: Page ID.
        db: Database session.
        current_user: Authenticated user.
    
    Returns:
        dict: Detailed page analysis.
    
    Raises:
        HTTPException: If page not found or access denied.
    """
    # Verify page access
    result = await db.execute(
        select(Page)
        .join(CrawlJob)
        .join(Project)
        .where(
            Page.id == page_id,
            Project.user_id == current_user.id,
        )
    )
    page = result.scalar_one_or_none()
    
    if not page:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Page not found",
        )
    
    # Perform detailed analysis
    issues, warnings, score = analyze_page_seo(page)
    
    return {
        "page": page,
        "seo_score": score,
        "issues": issues,
        "warnings": warnings,
        "suggestions": generate_suggestions(page, issues, warnings),
        "title_analysis": analyze_title(page),
        "meta_analysis": analyze_meta(page),
        "headings_analysis": analyze_headings(page),
        "images_analysis": analyze_images(page),
        "links_analysis": analyze_links(page),
        "content_analysis": analyze_content(page),
    }


def analyze_page_seo(page: Page) -> tuple[list[str], list[str], int]:
    """
    Analyze a page for SEO issues and calculate score.
    
    This is a simplified version. In production, this would be
    a more comprehensive analysis service.
    
    Args:
        page: Page model instance.
    
    Returns:
        tuple: (issues, warnings, score)
    """
    issues = []
    warnings = []
    score = 100
    
    # Check status code
    if not page.is_success:
        issues.append(f"HTTP {page.status_code} error")
        score -= 50
    
    # Check title
    if not page.title:
        issues.append("Missing title tag")
        score -= 15
    elif len(page.title) < 30:
        warnings.append("Title is too short (< 30 chars)")
        score -= 5
    elif len(page.title) > 60:
        warnings.append("Title is too long (> 60 chars)")
        score -= 5
    
    # Check meta description
    if not page.meta_description:
        issues.append("Missing meta description")
        score -= 10
    elif len(page.meta_description) < 120:
        warnings.append("Meta description is too short")
        score -= 3
    elif len(page.meta_description) > 160:
        warnings.append("Meta description is too long")
        score -= 3
    
    # Check H1
    if not page.h1_tags or len(page.h1_tags) == 0:
        issues.append("Missing H1 tag")
        score -= 10
    elif len(page.h1_tags) > 1:
        warnings.append("Multiple H1 tags found")
        score -= 5
    
    # Check images
    if page.images_without_alt > 0:
        warnings.append(f"{page.images_without_alt} images missing alt text")
        score -= min(page.images_without_alt * 2, 10)
    
    # Ensure score doesn't go below 0
    score = max(0, score)
    
    return issues, warnings, score


def generate_suggestions(page: Page, issues: list, warnings: list) -> list[str]:
    """Generate actionable suggestions based on issues."""
    suggestions = []
    
    if "Missing title tag" in issues:
        suggestions.append("Add a unique, descriptive title tag (50-60 characters)")
    
    if "Missing meta description" in issues:
        suggestions.append("Add a compelling meta description (120-160 characters)")
    
    if "Missing H1 tag" in issues:
        suggestions.append("Add a single, descriptive H1 heading")
    
    return suggestions


def analyze_title(page: Page) -> dict:
    """Analyze title tag."""
    return {
        "present": bool(page.title),
        "length": len(page.title) if page.title else 0,
        "optimal_length": 50 <= len(page.title or "") <= 60,
    }


def analyze_meta(page: Page) -> dict:
    """Analyze meta tags."""
    return {
        "description_present": bool(page.meta_description),
        "description_length": len(page.meta_description) if page.meta_description else 0,
        "description_optimal": 120 <= len(page.meta_description or "") <= 160,
        "canonical_present": bool(page.canonical_url),
    }


def analyze_headings(page: Page) -> dict:
    """Analyze heading structure."""
    return {
        "h1_count": len(page.h1_tags) if page.h1_tags else 0,
        "h2_count": len(page.h2_tags) if page.h2_tags else 0,
        "h3_count": len(page.h3_tags) if page.h3_tags else 0,
        "h1_optimal": len(page.h1_tags or []) == 1,
    }


def analyze_images(page: Page) -> dict:
    """Analyze images."""
    return {
        "total_images": page.images_count,
        "images_without_alt": page.images_without_alt,
        "alt_coverage_percentage": (
            ((page.images_count - page.images_without_alt) / page.images_count * 100)
            if page.images_count > 0
            else 100
        ),
    }


def analyze_links(page: Page) -> dict:
    """Analyze links."""
    return {
        "internal_links": page.internal_links_count,
        "external_links": page.external_links_count,
        "total_links": page.internal_links_count + page.external_links_count,
    }


def analyze_content(page: Page) -> dict:
    """Analyze content metrics."""
    return {
        "word_count": page.word_count,
        "text_to_html_ratio": page.text_to_html_ratio,
        "page_size_bytes": page.page_size_bytes,
    }
