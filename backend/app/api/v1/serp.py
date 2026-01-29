"""
API endpoints for SERP tracking and keyword rankings.
"""

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from typing import List, Optional
from pydantic import BaseModel
from datetime import datetime

from app.core.dependencies import get_current_user, get_db
from app.core.config import settings
from app.models.user import User
from app.models.project import Project
from app.services.integrations.serp_client import SerpAPIClient, RankingTracker

router = APIRouter()


class AddKeywordRequest(BaseModel):
    """Request to add keywords for tracking."""
    keywords: List[str]
    location: str = "United States"


class CheckRankingsRequest(BaseModel):
    """Request to check keyword rankings."""
    keywords: List[str]
    location: str = "United States"
    check_competitors: bool = False
    competitor_domains: List[str] = []


@router.post("/keywords")
async def add_keywords(
    request: AddKeywordRequest,
    project_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Add keywords to track for a project."""
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
    
    # In production, store keywords in database
    return {
        "project_id": project_id,
        "keywords_added": request.keywords,
        "location": request.location,
        "total": len(request.keywords)
    }


@router.get("/keywords")
async def get_tracked_keywords(
    project_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Get all tracked keywords for a project."""
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
        "keywords": [],
        "total": 0
    }


@router.post("/keywords/check")
async def check_keyword_rankings(
    request: CheckRankingsRequest,
    project_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Check current keyword rankings."""
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
    
    # Check if API key is configured
    serp_api_key = getattr(settings, 'SERP_API_KEY', None)
    if not serp_api_key or serp_api_key == 'your-serp-api-key-here':
        raise HTTPException(
            status_code=400,
            detail="SERP API key not configured. Please set SERP_API_KEY in environment."
        )
    
    # Check rankings
    client = SerpAPIClient(api_key=serp_api_key)
    
    try:
        rankings = await client.check_rankings(
            keywords=request.keywords,
            domain=project.domain,
            location=request.location
        )
        
        return {
            "project_id": project_id,
            "domain": project.domain,
            "rankings": rankings,
            "checked_at": datetime.utcnow().isoformat()
        }
    
    finally:
        await client.close()


@router.get("/keywords/{keyword_id}/history")
async def get_keyword_history(
    keyword_id: int,
    days_back: int = 30,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Get ranking history for a keyword."""
    # In production, retrieve from database
    return {
        "keyword_id": keyword_id,
        "history": [],
        "days_back": days_back
    }


@router.get("/keywords/{keyword_id}/competitors")
async def get_competitor_rankings(
    keyword_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Get competitor rankings for a keyword."""
    # In production, retrieve from database
    return {
        "keyword_id": keyword_id,
        "competitors": []
    }


@router.post("/keywords/bulk-check")
async def bulk_check_rankings(
    project_id: int,
    location: str = "United States",
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Check rankings for all tracked keywords in a project."""
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
    
    # This would trigger a Celery task for bulk checking
    return {
        "project_id": project_id,
        "status": "queued",
        "message": "Bulk ranking check queued for processing"
    }
