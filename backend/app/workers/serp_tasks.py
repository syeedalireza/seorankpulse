"""
Celery tasks for SERP tracking and keyword monitoring.
"""

from celery import Task
from app.workers.celery_app import celery_app
from app.services.integrations.serp_client import SerpAPIClient
from app.core.config import settings
from datetime import datetime


@celery_app.task(bind=True, name="serp.check_keyword_rankings")
def check_keyword_rankings_task(self: Task, keyword_ids: list):
    """
    Check rankings for keywords.
    
    Args:
        keyword_ids: List of keyword IDs to check.
    """
    import asyncio
    from app.db.session import AsyncSessionLocal
    
    async def _check():
        async with AsyncSessionLocal() as db:
            # In production, fetch keywords from database
            # For now, return placeholder
            
            client = SerpAPIClient(api_key=settings.SERP_API_KEY)
            
            try:
                # Check rankings
                # results = await client.check_rankings(...)
                
                return {
                    'status': 'completed',
                    'keywords_checked': len(keyword_ids),
                    'timestamp': datetime.utcnow().isoformat()
                }
            finally:
                await client.close()
    
    return asyncio.run(_check())


@celery_app.task(bind=True, name="serp.scheduled_check")
def scheduled_serp_check_task(self: Task, project_id: int):
    """
    Scheduled SERP position check for all project keywords.
    
    Args:
        project_id: Project ID.
    """
    import asyncio
    from app.db.session import AsyncSessionLocal
    from app.models.project import Project
    from sqlalchemy import select
    
    async def _check():
        async with AsyncSessionLocal() as db:
            # Get project
            result = await db.execute(select(Project).where(Project.id == project_id))
            project = result.scalar_one_or_none()
            
            if not project:
                return {'error': 'Project not found'}
            
            # Get tracked keywords (would be from database)
            # Check rankings
            # Store results
            # Trigger alerts if significant changes
            
            return {
                'project_id': project_id,
                'status': 'completed',
                'checked_at': datetime.utcnow().isoformat()
            }
    
    return asyncio.run(_check())


@celery_app.task(bind=True, name="serp.bulk_check")
def bulk_serp_check_task(self: Task, project_id: int, keywords: list, location: str = "United States"):
    """
    Bulk check rankings for multiple keywords.
    
    Args:
        project_id: Project ID.
        keywords: List of keywords to check.
        location: Search location.
    """
    import asyncio
    from app.db.session import AsyncSessionLocal
    from app.models.project import Project
    from sqlalchemy import select
    
    async def _check():
        async with AsyncSessionLocal() as db:
            # Get project
            result = await db.execute(select(Project).where(Project.id == project_id))
            project = result.scalar_one_or_none()
            
            if not project:
                return {'error': 'Project not found'}
            
            client = SerpAPIClient(api_key=settings.SERP_API_KEY)
            
            try:
                rankings = await client.check_rankings(
                    keywords=keywords,
                    domain=project.domain,
                    location=location
                )
                
                # Store rankings in database
                
                return {
                    'project_id': project_id,
                    'keywords_checked': len(keywords),
                    'rankings': rankings
                }
            finally:
                await client.close()
    
    return asyncio.run(_check())


@celery_app.task(bind=True, name="serp.track_competitors")
def track_competitors_task(self: Task, keyword: str, competitors: list, location: str = "United States"):
    """
    Track competitor rankings for a keyword.
    
    Args:
        keyword: Keyword to track.
        competitors: List of competitor domains.
        location: Search location.
    """
    import asyncio
    
    async def _track():
        client = SerpAPIClient(api_key=settings.SERP_API_KEY)
        
        try:
            result = await client.track_competitors(
                keyword=keyword,
                competitors=competitors,
                location=location
            )
            
            return result
        finally:
            await client.close()
    
    return asyncio.run(_track())
