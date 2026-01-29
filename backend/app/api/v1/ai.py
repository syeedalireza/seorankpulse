"""
API endpoints for AI-powered SEO features.
"""

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from typing import List, Optional
from pydantic import BaseModel

from app.core.dependencies import get_current_user, get_db
from app.core.config import settings
from app.models.user import User
from app.models.page import Page
from app.services.ai.content_scorer import ContentQualityScorer
from app.services.ai.alt_text_generator import AltTextGenerator

router = APIRouter()


class ContentScoreRequest(BaseModel):
    """Request for content quality scoring."""
    content: str
    url: str
    target_keyword: Optional[str] = None
    context: Optional[dict] = None


class GenerateAltTextRequest(BaseModel):
    """Request for alt text generation."""
    image_url: str
    context: Optional[dict] = None
    max_length: int = 125


class BatchAltTextRequest(BaseModel):
    """Request for batch alt text generation."""
    image_urls: List[str]
    context: Optional[dict] = None


class ContentBriefRequest(BaseModel):
    """Request for content brief generation."""
    topic: str
    target_keyword: str
    competitors: List[str]


@router.post("/ai/content-score")
async def score_content(
    request: ContentScoreRequest,
    current_user: User = Depends(get_current_user),
):
    """Score content quality using AI."""
    # Check if OpenAI API key is configured
    openai_key = getattr(settings, 'OPENAI_API_KEY', None)
    if not openai_key or openai_key == 'your-openai-api-key-here':
        raise HTTPException(
            status_code=400,
            detail="OpenAI API key not configured"
        )
    
    # Score content
    scorer = ContentQualityScorer(api_key=openai_key)
    result = await scorer.score_content(
        content=request.content,
        url=request.url,
        target_keyword=request.target_keyword,
        context=request.context
    )
    
    return result


@router.post("/ai/alt-text/generate")
async def generate_alt_text(
    request: GenerateAltTextRequest,
    current_user: User = Depends(get_current_user),
):
    """Generate alt text for an image using AI."""
    openai_key = getattr(settings, 'OPENAI_API_KEY', None)
    if not openai_key or openai_key == 'your-openai-api-key-here':
        raise HTTPException(
            status_code=400,
            detail="OpenAI API key not configured"
        )
    
    generator = AltTextGenerator(api_key=openai_key)
    result = await generator.generate_alt_text(
        image_url=request.image_url,
        context=request.context,
        max_length=request.max_length
    )
    
    return result


@router.post("/ai/alt-text/batch")
async def batch_generate_alt_text(
    request: BatchAltTextRequest,
    current_user: User = Depends(get_current_user),
):
    """Generate alt text for multiple images."""
    openai_key = getattr(settings, 'OPENAI_API_KEY', None)
    if not openai_key or openai_key == 'your-openai-api-key-here':
        raise HTTPException(
            status_code=400,
            detail="OpenAI API key not configured"
        )
    
    generator = AltTextGenerator(api_key=openai_key)
    results = await generator.batch_generate(
        image_urls=request.image_urls,
        context=request.context
    )
    
    return {
        "total_images": len(request.image_urls),
        "results": results
    }


@router.post("/ai/content-brief")
async def generate_content_brief(
    request: ContentBriefRequest,
    current_user: User = Depends(get_current_user),
):
    """Generate a content brief using AI."""
    openai_key = getattr(settings, 'OPENAI_API_KEY', None)
    if not openai_key or openai_key == 'your-openai-api-key-here':
        raise HTTPException(
            status_code=400,
            detail="OpenAI API key not configured"
        )
    
    scorer = ContentQualityScorer(api_key=openai_key)
    brief = await scorer.generate_content_brief(
        topic=request.topic,
        target_keyword=request.target_keyword,
        competitors=request.competitors
    )
    
    return brief


@router.post("/ai/compare-competitors")
async def compare_content_with_competitors(
    your_content: str,
    competitor_urls: List[str],
    current_user: User = Depends(get_current_user),
):
    """Compare your content with competitors using AI."""
    openai_key = getattr(settings, 'OPENAI_API_KEY', None)
    if not openai_key or openai_key == 'your-openai-api-key-here':
        raise HTTPException(
            status_code=400,
            detail="OpenAI API key not configured"
        )
    
    # In production, fetch competitor content
    competitor_contents = [
        {"url": url, "content": "Sample content"}
        for url in competitor_urls[:3]
    ]
    
    scorer = ContentQualityScorer(api_key=openai_key)
    comparison = await scorer.compare_with_competitors(
        your_content=your_content,
        competitor_contents=competitor_contents
    )
    
    return comparison
