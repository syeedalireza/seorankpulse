"""
API endpoints for custom dashboard management.
"""

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_
from typing import List

from app.core.dependencies import get_current_user, get_db
from app.models.user import User
from app.models.dashboard import Dashboard, DashboardWidget
from app.schemas.dashboard import (
    DashboardCreate,
    DashboardUpdate,
    DashboardResponse,
    DashboardListResponse,
    DashboardWidgetCreate,
    DashboardWidgetResponse,
)
from app.services.dashboard.widget_types import WidgetConfiguration

router = APIRouter()


@router.post("/dashboards", response_model=DashboardResponse)
async def create_dashboard(
    dashboard: DashboardCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Create a new custom dashboard."""
    # Create dashboard
    new_dashboard = Dashboard(
        user_id=current_user.id,
        project_id=dashboard.project_id,
        name=dashboard.name,
        description=dashboard.description,
        layout=dashboard.layout or WidgetConfiguration.get_default_layout(),
        is_public=dashboard.is_public,
        is_default=dashboard.is_default
    )
    
    db.add(new_dashboard)
    await db.flush()
    
    # Add widgets if provided
    for widget_data in dashboard.widgets:
        widget = DashboardWidget(
            dashboard_id=new_dashboard.id,
            widget_type=widget_data.widget_type,
            title=widget_data.title,
            position_x=widget_data.position_x,
            position_y=widget_data.position_y,
            width=widget_data.width,
            height=widget_data.height,
            config=widget_data.config
        )
        db.add(widget)
    
    await db.commit()
    await db.refresh(new_dashboard)
    
    return new_dashboard


@router.get("/dashboards", response_model=DashboardListResponse)
async def get_dashboards(
    project_id: int = None,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Get all dashboards for current user."""
    query = select(Dashboard).where(
        or_(
            Dashboard.user_id == current_user.id,
            Dashboard.is_public == True
        )
    )
    
    if project_id:
        query = query.where(Dashboard.project_id == project_id)
    
    result = await db.execute(query)
    dashboards = result.scalars().all()
    
    return DashboardListResponse(
        dashboards=dashboards,
        total=len(dashboards)
    )


@router.get("/dashboards/{dashboard_id}", response_model=DashboardResponse)
async def get_dashboard(
    dashboard_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Get a specific dashboard."""
    result = await db.execute(
        select(Dashboard).where(Dashboard.id == dashboard_id)
    )
    
    dashboard = result.scalar_one_or_none()
    
    if not dashboard:
        raise HTTPException(status_code=404, detail="Dashboard not found")
    
    # Check access
    if dashboard.user_id != current_user.id and not dashboard.is_public:
        raise HTTPException(status_code=403, detail="Access denied")
    
    return dashboard


@router.put("/dashboards/{dashboard_id}", response_model=DashboardResponse)
async def update_dashboard(
    dashboard_id: int,
    dashboard_update: DashboardUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Update a dashboard."""
    result = await db.execute(
        select(Dashboard).where(
            Dashboard.id == dashboard_id,
            Dashboard.user_id == current_user.id
        )
    )
    
    dashboard = result.scalar_one_or_none()
    
    if not dashboard:
        raise HTTPException(status_code=404, detail="Dashboard not found or access denied")
    
    # Update fields
    if dashboard_update.name is not None:
        dashboard.name = dashboard_update.name
    if dashboard_update.description is not None:
        dashboard.description = dashboard_update.description
    if dashboard_update.layout is not None:
        dashboard.layout = dashboard_update.layout
    if dashboard_update.is_public is not None:
        dashboard.is_public = dashboard_update.is_public
    if dashboard_update.is_default is not None:
        dashboard.is_default = dashboard_update.is_default
    
    await db.commit()
    await db.refresh(dashboard)
    
    return dashboard


@router.delete("/dashboards/{dashboard_id}")
async def delete_dashboard(
    dashboard_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Delete a dashboard."""
    result = await db.execute(
        select(Dashboard).where(
            Dashboard.id == dashboard_id,
            Dashboard.user_id == current_user.id
        )
    )
    
    dashboard = result.scalar_one_or_none()
    
    if not dashboard:
        raise HTTPException(status_code=404, detail="Dashboard not found or access denied")
    
    await db.delete(dashboard)
    await db.commit()
    
    return {"message": "Dashboard deleted successfully"}


# Widget Endpoints

@router.post("/dashboards/{dashboard_id}/widgets", response_model=DashboardWidgetResponse)
async def add_widget(
    dashboard_id: int,
    widget: DashboardWidgetCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Add a widget to a dashboard."""
    # Verify dashboard ownership
    dashboard_result = await db.execute(
        select(Dashboard).where(
            Dashboard.id == dashboard_id,
            Dashboard.user_id == current_user.id
        )
    )
    
    if not dashboard_result.scalar_one_or_none():
        raise HTTPException(status_code=404, detail="Dashboard not found or access denied")
    
    # Create widget
    new_widget = DashboardWidget(
        dashboard_id=dashboard_id,
        widget_type=widget.widget_type,
        title=widget.title,
        position_x=widget.position_x,
        position_y=widget.position_y,
        width=widget.width,
        height=widget.height,
        config=widget.config
    )
    
    db.add(new_widget)
    await db.commit()
    await db.refresh(new_widget)
    
    return new_widget


@router.put("/dashboards/{dashboard_id}/widgets/{widget_id}", response_model=DashboardWidgetResponse)
async def update_widget(
    dashboard_id: int,
    widget_id: int,
    widget_update: DashboardWidgetCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Update a widget."""
    # Verify dashboard ownership
    dashboard_result = await db.execute(
        select(Dashboard).where(
            Dashboard.id == dashboard_id,
            Dashboard.user_id == current_user.id
        )
    )
    
    if not dashboard_result.scalar_one_or_none():
        raise HTTPException(status_code=403, detail="Access denied")
    
    # Get widget
    widget_result = await db.execute(
        select(DashboardWidget).where(
            and_(
                DashboardWidget.id == widget_id,
                DashboardWidget.dashboard_id == dashboard_id
            )
        )
    )
    
    widget = widget_result.scalar_one_or_none()
    
    if not widget:
        raise HTTPException(status_code=404, detail="Widget not found")
    
    # Update widget
    widget.widget_type = widget_update.widget_type
    widget.title = widget_update.title
    widget.position_x = widget_update.position_x
    widget.position_y = widget_update.position_y
    widget.width = widget_update.width
    widget.height = widget_update.height
    widget.config = widget_update.config
    
    await db.commit()
    await db.refresh(widget)
    
    return widget


@router.delete("/dashboards/{dashboard_id}/widgets/{widget_id}")
async def delete_widget(
    dashboard_id: int,
    widget_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Delete a widget from a dashboard."""
    # Verify dashboard ownership
    dashboard_result = await db.execute(
        select(Dashboard).where(
            Dashboard.id == dashboard_id,
            Dashboard.user_id == current_user.id
        )
    )
    
    if not dashboard_result.scalar_one_or_none():
        raise HTTPException(status_code=403, detail="Access denied")
    
    # Get and delete widget
    widget_result = await db.execute(
        select(DashboardWidget).where(
            and_(
                DashboardWidget.id == widget_id,
                DashboardWidget.dashboard_id == dashboard_id
            )
        )
    )
    
    widget = widget_result.scalar_one_or_none()
    
    if not widget:
        raise HTTPException(status_code=404, detail="Widget not found")
    
    await db.delete(widget)
    await db.commit()
    
    return {"message": "Widget deleted successfully"}


@router.get("/widgets/types")
async def get_widget_types(
    current_user: User = Depends(get_current_user),
):
    """Get available widget types and their configurations."""
    return {
        "widget_types": WidgetConfiguration.get_available_widgets(),
        "categories": WidgetConfiguration.get_widget_categories(),
    }
