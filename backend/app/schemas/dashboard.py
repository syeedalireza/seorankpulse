"""
Dashboard schemas.
"""

from datetime import datetime
from typing import Dict, List, Optional
from pydantic import BaseModel, Field


class DashboardWidgetBase(BaseModel):
    """Base widget schema."""
    widget_type: str = Field(..., description="Type of widget")
    title: str = Field(..., min_length=1, max_length=255)
    position_x: int = Field(default=0, ge=0)
    position_y: int = Field(default=0, ge=0)
    width: int = Field(default=4, ge=1, le=12)
    height: int = Field(default=4, ge=1, le=12)
    config: Dict = Field(default_factory=dict)


class DashboardWidgetCreate(DashboardWidgetBase):
    """Schema for creating widget."""
    pass


class DashboardWidgetResponse(DashboardWidgetBase):
    """Schema for widget response."""
    id: int
    dashboard_id: int
    created_at: datetime
    updated_at: Optional[datetime] = None
    
    class Config:
        from_attributes = True


class DashboardBase(BaseModel):
    """Base dashboard schema."""
    name: str = Field(..., min_length=1, max_length=255)
    description: Optional[str] = None
    is_public: bool = False
    is_default: bool = False


class DashboardCreate(DashboardBase):
    """Schema for creating dashboard."""
    project_id: Optional[int] = None
    layout: Dict = Field(default_factory=dict)
    widgets: List[DashboardWidgetCreate] = Field(default_factory=list)


class DashboardUpdate(BaseModel):
    """Schema for updating dashboard."""
    name: Optional[str] = None
    description: Optional[str] = None
    layout: Optional[Dict] = None
    is_public: Optional[bool] = None
    is_default: Optional[bool] = None


class DashboardResponse(DashboardBase):
    """Schema for dashboard response."""
    id: int
    user_id: int
    project_id: Optional[int] = None
    layout: Dict
    created_at: datetime
    updated_at: Optional[datetime] = None
    widgets: List[DashboardWidgetResponse] = []
    
    class Config:
        from_attributes = True


class DashboardListResponse(BaseModel):
    """Schema for dashboard list."""
    dashboards: List[DashboardResponse]
    total: int
