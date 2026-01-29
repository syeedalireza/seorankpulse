"""
API endpoints for list mode crawling.
"""

from fastapi import APIRouter, Depends, File, Form, HTTPException, UploadFile
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List, Optional

from app.core.dependencies import get_current_user, get_db
from app.models.user import User
from app.models.project import Project
from app.services.crawler.list_mode import ListModeCrawler
from pydantic import BaseModel


router = APIRouter()


class URLListRequest(BaseModel):
    """Request model for URL list analysis."""
    urls: List[str]
    enable_js: bool = False


class URLListResponse(BaseModel):
    """Response model for URL list analysis."""
    total_urls: int
    analyzed: int
    pages: List[dict]


@router.post("/projects/{project_id}/list-crawl", response_model=URLListResponse)
async def analyze_url_list(
    project_id: int,
    request: URLListRequest,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Analyze a list of URLs without traditional crawling.
    
    This endpoint allows analyzing specific URLs without following links.
    """
    # Get project
    from sqlalchemy import select
    result = await db.execute(
        select(Project).where(
            Project.id == project_id,
            Project.user_id == current_user.id
        )
    )
    project = result.scalar_one_or_none()
    
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    
    # Validate URLs
    validation = ListModeCrawler.validate_urls(request.urls)
    
    if validation['valid'] == 0:
        raise HTTPException(
            status_code=400,
            detail=f"No valid URLs found. Invalid URLs: {validation['invalid_urls'][:5]}"
        )
    
    # Analyze URLs
    crawler = ListModeCrawler(project, enable_js=request.enable_js)
    results = await crawler.analyze_url_list(validation['valid_urls'])
    
    return URLListResponse(**results)


@router.post("/projects/{project_id}/list-crawl/upload")
async def upload_url_list(
    project_id: int,
    file: UploadFile = File(...),
    url_column: str = Form("url"),
    enable_js: bool = Form(False),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Upload a file containing URLs for analysis.
    
    Supports CSV, Excel (.xlsx, .xls), and plain text files.
    """
    # Get project
    from sqlalchemy import select
    result = await db.execute(
        select(Project).where(
            Project.id == project_id,
            Project.user_id == current_user.id
        )
    )
    project = result.scalar_one_or_none()
    
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    
    # Read file content
    content = await file.read()
    
    # Parse URLs based on file type
    filename = file.filename.lower()
    
    try:
        if filename.endswith('.csv'):
            urls = ListModeCrawler.parse_csv_file(content, url_column)
        elif filename.endswith(('.xlsx', '.xls')):
            urls = ListModeCrawler.parse_excel_file(content, url_column)
        elif filename.endswith('.txt'):
            urls = ListModeCrawler.parse_text_file(content)
        else:
            raise HTTPException(
                status_code=400,
                detail="Unsupported file type. Use CSV, Excel, or TXT."
            )
    
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Failed to parse file: {str(e)}")
    
    if not urls:
        raise HTTPException(status_code=400, detail="No URLs found in file")
    
    # Validate URLs
    validation = ListModeCrawler.validate_urls(urls)
    
    if validation['valid'] == 0:
        raise HTTPException(
            status_code=400,
            detail=f"No valid URLs found in file. Total URLs: {validation['total']}"
        )
    
    # Analyze URLs
    crawler = ListModeCrawler(project, enable_js=enable_js)
    results = await crawler.analyze_url_list(validation['valid_urls'])
    
    return {
        **results,
        'validation': {
            'total_in_file': validation['total'],
            'valid': validation['valid'],
            'invalid': validation['invalid'],
        }
    }
