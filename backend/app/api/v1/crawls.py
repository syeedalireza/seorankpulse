"""
Crawl Jobs API endpoints.

Handles crawl job operations and monitoring.
"""

from typing import List

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.dependencies import get_current_user, get_db
from app.models.crawl_job import CrawlJob, CrawlStatus
from app.models.project import Project
from app.models.user import User
from app.schemas.crawl import (
    CrawlJob as CrawlJobSchema,
    CrawlJobCreate,
    CrawlJobSummary,
    CrawlProgress,
)


router = APIRouter()


@router.post("/", response_model=CrawlJobSchema, status_code=status.HTTP_201_CREATED)
async def start_crawl(
    crawl_data: CrawlJobCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> CrawlJob:
    """
    Start a new crawl job for a project.
    
    Args:
        crawl_data: Crawl job creation data.
        db: Database session.
        current_user: Authenticated user.
    
    Returns:
        CrawlJob: The created crawl job.
    
    Raises:
        HTTPException: If project not found or access denied.
    """
    # Verify project exists and belongs to user
    result = await db.execute(
        select(Project).where(
            Project.id == crawl_data.project_id,
            Project.user_id == current_user.id,
        )
    )
    project = result.scalar_one_or_none()
    
    if not project:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Project not found",
        )
    
    # Check if there's already a running crawl for this project
    result = await db.execute(
        select(CrawlJob).where(
            CrawlJob.project_id == project.id,
            CrawlJob.status == CrawlStatus.RUNNING,
        )
    )
    running_crawl = result.scalar_one_or_none()
    
    if running_crawl:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="A crawl is already running for this project",
        )
    
    # Create crawl job
    crawl_job = CrawlJob(
        project_id=project.id,
        status=CrawlStatus.PENDING,
    )
    
    db.add(crawl_job)
    await db.commit()
    await db.refresh(crawl_job)
    
    # TODO: Trigger Celery task here
    # from app.workers.crawl_tasks import start_crawl_task
    # task = start_crawl_task.delay(crawl_job.id)
    # crawl_job.celery_task_id = task.id
    # await db.commit()
    
    return crawl_job


@router.get("/{crawl_id}", response_model=CrawlJobSchema)
async def get_crawl(
    crawl_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> CrawlJob:
    """
    Get a specific crawl job by ID.
    
    Args:
        crawl_id: Crawl job ID.
        db: Database session.
        current_user: Authenticated user.
    
    Returns:
        CrawlJob: The requested crawl job.
    
    Raises:
        HTTPException: If crawl not found or access denied.
    """
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
    
    return crawl_job


@router.get("/project/{project_id}", response_model=List[CrawlJobSummary])
async def list_project_crawls(
    project_id: int,
    skip: int = 0,
    limit: int = 50,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> List[CrawlJob]:
    """
    List all crawl jobs for a project.
    
    Args:
        project_id: Project ID.
        skip: Number of records to skip.
        limit: Maximum number of records.
        db: Database session.
        current_user: Authenticated user.
    
    Returns:
        list[CrawlJob]: List of crawl jobs.
    
    Raises:
        HTTPException: If project not found or access denied.
    """
    # Verify project access
    result = await db.execute(
        select(Project).where(
            Project.id == project_id,
            Project.user_id == current_user.id,
        )
    )
    project = result.scalar_one_or_none()
    
    if not project:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Project not found",
        )
    
    # Get crawl jobs
    result = await db.execute(
        select(CrawlJob)
        .where(CrawlJob.project_id == project_id)
        .order_by(CrawlJob.created_at.desc())
        .offset(skip)
        .limit(limit)
    )
    crawl_jobs = result.scalars().all()
    
    return crawl_jobs


@router.get("/{crawl_id}/progress", response_model=CrawlProgress)
async def get_crawl_progress(
    crawl_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> dict:
    """
    Get real-time progress of a crawl job.
    
    Args:
        crawl_id: Crawl job ID.
        db: Database session.
        current_user: Authenticated user.
    
    Returns:
        dict: Crawl progress information.
    
    Raises:
        HTTPException: If crawl not found or access denied.
    """
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
    
    # Calculate progress percentage
    progress = 0.0
    if crawl_job.pages_total > 0:
        progress = (crawl_job.pages_crawled / crawl_job.pages_total) * 100
    
    return {
        "crawl_job_id": crawl_job.id,
        "status": crawl_job.status,
        "pages_crawled": crawl_job.pages_crawled,
        "pages_total": crawl_job.pages_total,
        "progress_percentage": progress,
        "current_url": None,  # TODO: Get from Redis/Celery
    }


@router.post("/{crawl_id}/cancel", response_model=CrawlJobSchema)
async def cancel_crawl(
    crawl_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> CrawlJob:
    """
    Cancel a running crawl job.
    
    Args:
        crawl_id: Crawl job ID.
        db: Database session.
        current_user: Authenticated user.
    
    Returns:
        CrawlJob: The cancelled crawl job.
    
    Raises:
        HTTPException: If crawl not found, access denied, or not running.
    """
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
    
    if crawl_job.status != CrawlStatus.RUNNING:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Crawl is not running",
        )
    
    # TODO: Cancel Celery task
    # if crawl_job.celery_task_id:
    #     from celery import current_app
    #     current_app.control.revoke(crawl_job.celery_task_id, terminate=True)
    
    crawl_job.status = CrawlStatus.CANCELLED
    await db.commit()
    await db.refresh(crawl_job)
    
    return crawl_job
