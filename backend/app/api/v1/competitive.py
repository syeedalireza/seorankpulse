"""
API endpoints for competitive analysis.
"""

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from typing import List
from pydantic import BaseModel

from app.core.dependencies import get_current_user, get_db
from app.models.user import User
from app.models.project import Project
from app.services.competitive.analyzer import CompetitiveAnalyzer
from app.services.competitive.gap_finder import ContentGapFinder

router = APIRouter()


class AddCompetitorRequest(BaseModel):
    """Request to add a competitor."""
    domain: str
    name: str = None


class CompareCompetitorsRequest(BaseModel):
    """Request to compare with competitors."""
    competitor_domains: List[str]


@router.post("/projects/{project_id}/competitors/add")
async def add_competitor(
    project_id: int,
    request: AddCompetitorRequest,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Add a competitor to track."""
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
    
    # In production, store in database
    return {
        "project_id": project_id,
        "competitor_domain": request.domain,
        "competitor_name": request.name or request.domain,
        "added_at": "2026-01-28T00:00:00Z"
    }


@router.get("/projects/{project_id}/competitors")
async def get_competitors(
    project_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Get all tracked competitors for a project."""
    # Verify project access
    result = await db.execute(
        select(Project).where(
            Project.id == project_id,
            Project.user_id == current_user.id
        )
    )
    
    if not result.scalar_one_or_none():
        raise HTTPException(status_code=404, detail="Project not found or access denied")
    
    # In production, retrieve from database
    return {
        "project_id": project_id,
        "competitors": [],
        "total": 0
    }


@router.post("/projects/{project_id}/competitors/compare")
async def compare_with_competitors(
    project_id: int,
    request: CompareCompetitorsRequest,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Run competitive analysis comparison."""
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
    
    # Get your site data (would fetch from latest crawl)
    your_site_data = {
        "domain": project.domain,
        "total_pages": 100,
        "avg_seo_score": 85,
        "avg_response_time": 250,
        "error_count": 5,
    }
    
    # Get competitor data (would trigger crawls)
    competitor_data = [
        {
            "domain": domain,
            "total_pages": 120,
            "avg_seo_score": 80,
            "avg_response_time": 300,
        }
        for domain in request.competitor_domains
    ]
    
    # Run comparison
    analyzer = CompetitiveAnalyzer()
    comparison = analyzer.compare_sites(your_site_data, competitor_data)
    
    return comparison


@router.get("/projects/{project_id}/gaps")
async def get_content_gaps(
    project_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Analyze content gaps compared to competitors."""
    # Verify project access
    result = await db.execute(
        select(Project).where(
            Project.id == project_id,
            Project.user_id == current_user.id
        )
    )
    
    if not result.scalar_one_or_none():
        raise HTTPException(status_code=404, detail="Project not found or access denied")
    
    # Get page data (would fetch from database)
    your_pages = []
    competitor_pages = []
    
    gap_finder = ContentGapFinder()
    missing_topics = gap_finder.find_missing_topics(your_pages, competitor_pages)
    missing_page_types = gap_finder.find_missing_page_types(your_pages, competitor_pages)
    
    return {
        "missing_topics": missing_topics,
        "missing_page_types": missing_page_types,
    }
