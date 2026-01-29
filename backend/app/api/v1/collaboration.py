"""
API endpoints for team collaboration features.
"""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_, or_
from typing import List

from app.core.dependencies import get_current_user, get_db
from app.models.user import User
from app.models.project import Project
from app.models.team import TeamMember, Comment, Task
from app.schemas.collaboration import (
    TeamMemberCreate,
    TeamMemberResponse,
    CommentCreate,
    CommentResponse,
    TaskCreate,
    TaskUpdate,
    TaskResponse,
)

router = APIRouter()


# Team Management Endpoints

@router.post("/projects/{project_id}/team/invite", response_model=TeamMemberResponse)
async def invite_team_member(
    project_id: int,
    member: TeamMemberCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Invite a team member to a project."""
    # Verify project ownership/admin
    result = await db.execute(
        select(Project).where(
            Project.id == project_id,
            Project.user_id == current_user.id
        )
    )
    project = result.scalar_one_or_none()
    
    if not project:
        raise HTTPException(status_code=404, detail="Project not found or access denied")
    
    # Find user by email
    user_result = await db.execute(
        select(User).where(User.email == member.user_email)
    )
    invited_user = user_result.scalar_one_or_none()
    
    if not invited_user:
        raise HTTPException(status_code=404, detail="User not found")
    
    # Check if already a member
    existing = await db.execute(
        select(TeamMember).where(
            and_(
                TeamMember.project_id == project_id,
                TeamMember.user_id == invited_user.id
            )
        )
    )
    
    if existing.scalar_one_or_none():
        raise HTTPException(status_code=400, detail="User is already a team member")
    
    # Create team member
    team_member = TeamMember(
        project_id=project_id,
        user_id=invited_user.id,
        role=member.role
    )
    
    db.add(team_member)
    await db.commit()
    await db.refresh(team_member)
    
    return team_member


@router.get("/projects/{project_id}/team", response_model=List[TeamMemberResponse])
async def get_team_members(
    project_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Get all team members for a project."""
    # Verify access
    result = await db.execute(
        select(TeamMember).where(
            and_(
                TeamMember.project_id == project_id,
                TeamMember.user_id == current_user.id
            )
        )
    )
    
    if not result.scalar_one_or_none():
        raise HTTPException(status_code=403, detail="Access denied")
    
    # Get all members
    members_result = await db.execute(
        select(TeamMember).where(TeamMember.project_id == project_id)
    )
    
    return members_result.scalars().all()


@router.delete("/projects/{project_id}/team/{user_id}")
async def remove_team_member(
    project_id: int,
    user_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Remove a team member from a project."""
    # Verify ownership
    project_result = await db.execute(
        select(Project).where(
            Project.id == project_id,
            Project.user_id == current_user.id
        )
    )
    
    if not project_result.scalar_one_or_none():
        raise HTTPException(status_code=403, detail="Only project owner can remove members")
    
    # Find and delete member
    member_result = await db.execute(
        select(TeamMember).where(
            and_(
                TeamMember.project_id == project_id,
                TeamMember.user_id == user_id
            )
        )
    )
    
    member = member_result.scalar_one_or_none()
    
    if not member:
        raise HTTPException(status_code=404, detail="Team member not found")
    
    await db.delete(member)
    await db.commit()
    
    return {"message": "Team member removed successfully"}


# Comment Endpoints

@router.post("/projects/{project_id}/comments", response_model=CommentResponse)
async def create_comment(
    project_id: int,
    comment: CommentCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Create a comment on a page or project."""
    # Verify team membership
    member_result = await db.execute(
        select(TeamMember).where(
            and_(
                TeamMember.project_id == project_id,
                TeamMember.user_id == current_user.id
            )
        )
    )
    
    if not member_result.scalar_one_or_none():
        raise HTTPException(status_code=403, detail="Access denied")
    
    # Create comment
    new_comment = Comment(
        project_id=project_id,
        user_id=current_user.id,
        page_id=comment.page_id,
        content=comment.content
    )
    
    db.add(new_comment)
    await db.commit()
    await db.refresh(new_comment)
    
    return new_comment


@router.get("/projects/{project_id}/comments", response_model=List[CommentResponse])
async def get_comments(
    project_id: int,
    page_id: int = None,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Get comments for a project or specific page."""
    # Verify access
    member_result = await db.execute(
        select(TeamMember).where(
            and_(
                TeamMember.project_id == project_id,
                TeamMember.user_id == current_user.id
            )
        )
    )
    
    if not member_result.scalar_one_or_none():
        raise HTTPException(status_code=403, detail="Access denied")
    
    # Build query
    query = select(Comment).where(Comment.project_id == project_id)
    
    if page_id:
        query = query.where(Comment.page_id == page_id)
    
    query = query.order_by(Comment.created_at.desc())
    
    comments_result = await db.execute(query)
    return comments_result.scalars().all()


# Task Endpoints

@router.post("/projects/{project_id}/tasks", response_model=TaskResponse)
async def create_task(
    project_id: int,
    task: TaskCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Create a task for SEO issue tracking."""
    # Verify membership
    member_result = await db.execute(
        select(TeamMember).where(
            and_(
                TeamMember.project_id == project_id,
                TeamMember.user_id == current_user.id
            )
        )
    )
    
    if not member_result.scalar_one_or_none():
        raise HTTPException(status_code=403, detail="Access denied")
    
    # Create task
    new_task = Task(
        project_id=project_id,
        created_by=current_user.id,
        assigned_to=task.assigned_to,
        page_id=task.page_id,
        title=task.title,
        description=task.description,
        priority=task.priority,
        status=task.status,
        due_date=task.due_date
    )
    
    db.add(new_task)
    await db.commit()
    await db.refresh(new_task)
    
    return new_task


@router.get("/projects/{project_id}/tasks", response_model=List[TaskResponse])
async def get_tasks(
    project_id: int,
    status: str = None,
    assigned_to_me: bool = False,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Get tasks for a project."""
    # Verify access
    member_result = await db.execute(
        select(TeamMember).where(
            and_(
                TeamMember.project_id == project_id,
                TeamMember.user_id == current_user.id
            )
        )
    )
    
    if not member_result.scalar_one_or_none():
        raise HTTPException(status_code=403, detail="Access denied")
    
    # Build query
    query = select(Task).where(Task.project_id == project_id)
    
    if status:
        query = query.where(Task.status == status)
    
    if assigned_to_me:
        query = query.where(Task.assigned_to == current_user.id)
    
    query = query.order_by(Task.created_at.desc())
    
    tasks_result = await db.execute(query)
    return tasks_result.scalars().all()


@router.put("/tasks/{task_id}", response_model=TaskResponse)
async def update_task(
    task_id: int,
    task_update: TaskUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Update a task."""
    # Get task
    task_result = await db.execute(
        select(Task).where(Task.id == task_id)
    )
    
    task = task_result.scalar_one_or_none()
    
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    
    # Verify access (team member or creator)
    member_result = await db.execute(
        select(TeamMember).where(
            and_(
                TeamMember.project_id == task.project_id,
                TeamMember.user_id == current_user.id
            )
        )
    )
    
    if not member_result.scalar_one_or_none():
        raise HTTPException(status_code=403, detail="Access denied")
    
    # Update fields
    if task_update.title is not None:
        task.title = task_update.title
    if task_update.description is not None:
        task.description = task_update.description
    if task_update.priority is not None:
        task.priority = task_update.priority
    if task_update.status is not None:
        task.status = task_update.status
        if task_update.status == "done":
            from datetime import datetime
            task.completed_at = datetime.utcnow()
    if task_update.assigned_to is not None:
        task.assigned_to = task_update.assigned_to
    if task_update.due_date is not None:
        task.due_date = task_update.due_date
    
    await db.commit()
    await db.refresh(task)
    
    return task


@router.delete("/tasks/{task_id}")
async def delete_task(
    task_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Delete a task."""
    # Get task
    task_result = await db.execute(
        select(Task).where(Task.id == task_id)
    )
    
    task = task_result.scalar_one_or_none()
    
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    
    # Only creator or project owner can delete
    if task.created_by != current_user.id:
        project_result = await db.execute(
            select(Project).where(
                Project.id == task.project_id,
                Project.user_id == current_user.id
            )
        )
        
        if not project_result.scalar_one_or_none():
            raise HTTPException(status_code=403, detail="Access denied")
    
    await db.delete(task)
    await db.commit()
    
    return {"message": "Task deleted successfully"}
