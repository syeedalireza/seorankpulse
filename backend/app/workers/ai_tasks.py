"""
Celery tasks for AI-powered analysis.
"""

from celery import Task
from app.workers.celery_app import celery_app
from app.services.ai.content_scorer import ContentQualityScorer
from app.services.ai.alt_text_generator import AltTextGenerator
from app.core.config import settings


@celery_app.task(bind=True, name="ai.score_content_quality")
def score_content_quality_task(self: Task, page_id: int, api_key: str = None):
    """
    Score content quality using AI.
    
    Args:
        page_id: ID of page to analyze.
        api_key: OpenAI API key (optional, uses env if not provided).
    """
    import asyncio
    from app.db.session import AsyncSessionLocal
    from app.models.page import Page
    from sqlalchemy import select
    
    async def _score():
        async with AsyncSessionLocal() as db:
            # Get page
            result = await db.execute(select(Page).where(Page.id == page_id))
            page = result.scalar_one_or_none()
            
            if not page:
                return {'error': 'Page not found'}
            
            # Build content
            content_parts = []
            if page.title:
                content_parts.append(page.title)
            if page.meta_description:
                content_parts.append(page.meta_description)
            if page.h1_tags:
                content_parts.extend(page.h1_tags)
            
            content = ' '.join(content_parts)
            
            # Score content
            key = api_key or settings.OPENAI_API_KEY
            scorer = ContentQualityScorer(api_key=key)
            
            result = await scorer.score_content(
                content=content,
                url=page.url
            )
            
            return result
    
    return asyncio.run(_score())


@celery_app.task(bind=True, name="ai.generate_alt_texts")
def generate_alt_texts_task(self: Task, project_id: int, api_key: str = None):
    """
    Generate alt text for all images in a project.
    
    Args:
        project_id: Project ID.
        api_key: OpenAI API key (optional).
    """
    import asyncio
    
    async def _generate():
        # In production, this would:
        # 1. Get all pages with images
        # 2. Extract image URLs
        # 3. Generate alt text for each
        # 4. Store results
        
        generator = AltTextGenerator(api_key=api_key or settings.OPENAI_API_KEY)
        
        # Placeholder - would process actual images
        return {
            'project_id': project_id,
            'status': 'completed',
            'images_processed': 0
        }
    
    return asyncio.run(_generate())


@celery_app.task(bind=True, name="ai.generate_content_brief")
def generate_content_brief_task(
    self: Task,
    topic: str,
    target_keyword: str,
    competitors: list,
    api_key: str = None
):
    """
    Generate content brief using AI.
    
    Args:
        topic: Content topic.
        target_keyword: Target keyword.
        competitors: List of competitor URLs.
        api_key: OpenAI API key (optional).
    """
    import asyncio
    
    async def _generate():
        scorer = ContentQualityScorer(api_key=api_key or settings.OPENAI_API_KEY)
        
        brief = await scorer.generate_content_brief(
            topic=topic,
            target_keyword=target_keyword,
            competitors=competitors
        )
        
        return brief
    
    return asyncio.run(_generate())


@celery_app.task(bind=True, name="ai.batch_score_pages")
def batch_score_pages_task(self: Task, project_id: int, page_ids: list, api_key: str = None):
    """
    Score multiple pages in batch.
    
    Args:
        project_id: Project ID.
        page_ids: List of page IDs to score.
        api_key: OpenAI API key (optional).
    """
    results = []
    
    for page_id in page_ids:
        result = score_content_quality_task.apply(args=[page_id, api_key])
        results.append(result.get())
    
    return {
        'project_id': project_id,
        'total_scored': len(results),
        'results': results
    }
