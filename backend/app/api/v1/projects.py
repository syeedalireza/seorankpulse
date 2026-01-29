"""
Projects API endpoints.

Handles project CRUD operations.
"""

from typing import List

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.dependencies import get_current_user, get_db
from app.models.project import Project
from app.models.user import User
from app.models.crawl_job import CrawlJob
from app.schemas.project import (
    Project as ProjectSchema,
    ProjectCreate,
    ProjectUpdate,
    ProjectWithStats,
)


router = APIRouter()


@router.get("/", response_model=List[ProjectWithStats])
async def list_projects(
    skip: int = 0,
    limit: int = 50,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> List[Project]:
    """
    List all projects for the current user.
    
    Args:
        skip: Number of records to skip (pagination).
        limit: Maximum number of records to return.
        db: Database session.
        current_user: Authenticated user.
    
    Returns:
        list[Project]: List of user's projects with statistics.
    """
    # Query projects with crawl statistics
    result = await db.execute(
        select(Project)
        .where(Project.user_id == current_user.id)
        .offset(skip)
        .limit(limit)
    )
    projects = result.scalars().all()
    
    # Add statistics to each project
    projects_with_stats = []
    for project in projects:
        # Count total crawls
        crawls_result = await db.execute(
            select(func.count(CrawlJob.id))
            .where(CrawlJob.project_id == project.id)
        )
        total_crawls = crawls_result.scalar()
        
        # Get last crawl date
        last_crawl_result = await db.execute(
            select(CrawlJob.created_at)
            .where(CrawlJob.project_id == project.id)
            .order_by(CrawlJob.created_at.desc())
            .limit(1)
        )
        last_crawl = last_crawl_result.scalar_one_or_none()
        
        project_dict = {
            **project.__dict__,
            "total_crawls": total_crawls or 0,
            "last_crawl_date": last_crawl,
            "total_pages": 0,  # Will be calculated from latest crawl
        }
        projects_with_stats.append(project_dict)
    
    return projects_with_stats


@router.post("/", response_model=ProjectSchema, status_code=status.HTTP_201_CREATED)
async def create_project(
    project_in: ProjectCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> Project:
    """
    Create a new project.
    
    Args:
        project_in: Project creation data.
        db: Database session.
        current_user: Authenticated user.
    
    Returns:
        Project: The created project.
    """
    project = Project(
        **project_in.model_dump(),
        user_id=current_user.id,
    )
    
    db.add(project)
    await db.commit()
    await db.refresh(project)
    
    return project


@router.get("/{project_id}", response_model=ProjectSchema)
async def get_project(
    project_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> Project:
    """
    Get a specific project by ID.
    
    Args:
        project_id: Project ID.
        db: Database session.
        current_user: Authenticated user.
    
    Returns:
        Project: The requested project.
    
    Raises:
        HTTPException: If project not found or access denied.
    """
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
    
    return project


@router.patch("/{project_id}", response_model=ProjectSchema)
async def update_project(
    project_id: int,
    project_update: ProjectUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> Project:
    """
    Update a project.
    
    Args:
        project_id: Project ID.
        project_update: Updated project data.
        db: Database session.
        current_user: Authenticated user.
    
    Returns:
        Project: The updated project.
    
    Raises:
        HTTPException: If project not found or access denied.
    """
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
    
    # Update fields
    update_data = project_update.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(project, field, value)
    
    await db.commit()
    await db.refresh(project)
    
    return project


@router.delete("/{project_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_project(
    project_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> None:
    """
    Delete a project.
    
    Args:
        project_id: Project ID.
        db: Database session.
        current_user: Authenticated user.
    
    Raises:
        HTTPException: If project not found or access denied.
    """
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
    
    await db.delete(project)
    await db.commit()
