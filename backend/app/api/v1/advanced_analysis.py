"""
API endpoints for advanced SEO analysis.
"""

from fastapi import APIRouter, Depends, HTTPException, UploadFile, File
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from typing import List, Optional
from pydantic import BaseModel

from app.core.dependencies import get_current_user, get_db
from app.models.user import User
from app.models.project import Project
from app.models.page import Page
from app.services.lighthouse.lighthouse_client import LighthouseClient
from app.services.analyzer.accessibility import AccessibilityAuditor
from app.services.analyzer.duplicate_detector import DuplicateContentDetector, detect_duplicates
from app.services.analyzer.image_analyzer import ImageAnalyzer
from app.services.analyzer.redirect_chain import RedirectChainAnalyzer
from app.services.log_analyzer.parser import LogFileParser
from app.services.log_analyzer.analyzer import LogAnalyzer

router = APIRouter()


class LighthouseRequest(BaseModel):
    """Request for Lighthouse audit."""
    url: str
    categories: Optional[List[str]] = None


class AccessibilityRequest(BaseModel):
    """Request for accessibility audit."""
    url: str
    tags: Optional[List[str]] = None


class DuplicateDetectionRequest(BaseModel):
    """Request for duplicate content detection."""
    similarity_threshold: int = 3


class ImageAnalysisRequest(BaseModel):
    """Request for image analysis."""
    image_url: str


class RedirectChainRequest(BaseModel):
    """Request for redirect chain analysis."""
    url: str


@router.post("/analysis/lighthouse")
async def run_lighthouse_audit(
    request: LighthouseRequest,
    current_user: User = Depends(get_current_user),
):
    """Run Lighthouse audit on a URL."""
    client = LighthouseClient()
    results = await client.audit_url(
        url=request.url,
        categories=request.categories
    )
    
    return results


@router.post("/analysis/accessibility")
async def run_accessibility_audit(
    request: AccessibilityRequest,
    current_user: User = Depends(get_current_user),
):
    """Run accessibility audit using AXE."""
    async with AccessibilityAuditor() as auditor:
        results = await auditor.audit_url(
            url=request.url,
            tags=request.tags
        )
    
    return results


@router.post("/analysis/duplicates")
async def detect_duplicate_content(
    project_id: int,
    request: DuplicateDetectionRequest,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Detect duplicate content in a project."""
    # Verify project access
    result = await db.execute(
        select(Project).where(
            Project.id == project_id,
            Project.user_id == current_user.id
        )
    )
    
    project = result.scalar_one_or_none()
    
    if not project:
        raise HTTPException(status_code=404, detail="Project not found or access denied")
    
    # Get pages from latest crawl
    pages_result = await db.execute(
        select(Page).join(
            Page.crawl_job
        ).where(
            Page.crawl_job.has(project_id=project_id)
        ).limit(1000)
    )
    
    pages = pages_result.scalars().all()
    
    # Convert to dict format
    pages_data = [
        {
            'url': p.url,
            'title': p.title,
            'meta_description': p.meta_description,
            'h1_tags': p.h1_tags,
            'h2_tags': p.h2_tags,
            'h3_tags': p.h3_tags,
        }
        for p in pages
    ]
    
    # Detect duplicates
    results = detect_duplicates(
        pages=pages_data,
        similarity_threshold=request.similarity_threshold
    )
    
    return results


@router.post("/analysis/images")
async def analyze_image(
    request: ImageAnalysisRequest,
    current_user: User = Depends(get_current_user),
):
    """Analyze an image for optimization opportunities."""
    analyzer = ImageAnalyzer()
    
    try:
        result = await analyzer.analyze_image(request.image_url)
        return result
    finally:
        await analyzer.close()


@router.post("/analysis/redirect-chains")
async def analyze_redirect_chain(
    request: RedirectChainRequest,
    current_user: User = Depends(get_current_user),
):
    """Analyze redirect chain for a URL."""
    analyzer = RedirectChainAnalyzer()
    result = await analyzer.analyze_url(request.url)
    
    return result


@router.post("/logs/upload")
async def upload_log_file(
    project_id: int,
    file: UploadFile = File(...),
    log_format: str = "auto",
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Upload and analyze a server log file."""
    # Verify project access
    result = await db.execute(
        select(Project).where(
            Project.id == project_id,
            Project.user_id == current_user.id
        )
    )
    
    if not result.scalar_one_or_none():
        raise HTTPException(status_code=404, detail="Project not found or access denied")
    
    # Save log file temporarily
    import tempfile
    import os
    
    with tempfile.NamedTemporaryFile(delete=False, suffix='.log') as tmp:
        content = await file.read()
        tmp.write(content)
        tmp_path = tmp.name
    
    try:
        # Parse log file
        parser = LogFileParser(log_format=log_format)
        entries = parser.parse_file(tmp_path, limit=10000)  # Limit for performance
        
        # Analyze logs
        analyzer = LogAnalyzer(entries)
        
        # Get various analyses
        bot_analysis = analyzer.analyze_all_bots()
        status_analysis = analyzer.analyze_status_codes()
        error_urls = analyzer.find_error_urls()
        popular_pages = analyzer.analyze_popular_pages()
        traffic_split = analyzer.analyze_bot_vs_user_traffic()
        
        return {
            "file_name": file.filename,
            "total_entries": len(entries),
            "bot_analysis": bot_analysis,
            "status_codes": status_analysis,
            "error_urls": error_urls[:20],
            "popular_pages": popular_pages[:20],
            "traffic_analysis": traffic_split,
        }
    
    finally:
        # Clean up temp file
        if os.path.exists(tmp_path):
            os.unlink(tmp_path)
