"""
API endpoints for monitoring, alerts, and scheduling.
"""

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from typing import List, Optional
from pydantic import BaseModel

from app.core.dependencies import get_current_user, get_db
from app.models.user import User
from app.models.project import Project
from app.services.monitoring.scheduler import (
    MonitoringScheduler,
    ScheduleFrequency,
    ContinuousMonitor
)
from app.services.monitoring.alert_manager import (
    AlertManager,
    AlertSeverity,
    AlertType
)

router = APIRouter()

# Initialize services (in production, these would be singletons or from DI)
scheduler = MonitoringScheduler()
alert_manager = AlertManager()


# Request/Response Models

class StartMonitoringRequest(BaseModel):
    """Request to start monitoring."""
    frequency: str
    alert_thresholds: Optional[dict] = None


class CreateScheduleRequest(BaseModel):
    """Request to create a schedule."""
    frequency: str
    enabled: bool = True
    config: Optional[dict] = None


class AlertsResponse(BaseModel):
    """Response with alerts list."""
    alerts: List[dict]
    total: int


# Monitoring Endpoints

@router.post("/projects/{project_id}/monitoring/start")
async def start_monitoring(
    project_id: int,
    request: StartMonitoringRequest,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Start continuous monitoring for a project."""
    # Verify project access
    result = await db.execute(
        select(Project).where(
            Project.id == project_id,
            Project.user_id == current_user.id
        )
    )
    
    if not result.scalar_one_or_none():
        raise HTTPException(status_code=404, detail="Project not found or access denied")
    
    # Start monitoring
    try:
        frequency = ScheduleFrequency(request.frequency)
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid frequency")
    
    monitor = ContinuousMonitor(project_id)
    config = await monitor.start_monitoring(
        frequency=frequency,
        alert_thresholds=request.alert_thresholds
    )
    
    return config


@router.post("/projects/{project_id}/monitoring/stop")
async def stop_monitoring(
    project_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Stop continuous monitoring."""
    # Verify project access
    result = await db.execute(
        select(Project).where(
            Project.id == project_id,
            Project.user_id == current_user.id
        )
    )
    
    if not result.scalar_one_or_none():
        raise HTTPException(status_code=404, detail="Project not found or access denied")
    
    monitor = ContinuousMonitor(project_id)
    result = await monitor.stop_monitoring()
    
    return result


@router.get("/projects/{project_id}/monitoring/status")
async def get_monitoring_status(
    project_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Get monitoring status for a project."""
    # Verify project access
    result = await db.execute(
        select(Project).where(
            Project.id == project_id,
            Project.user_id == current_user.id
        )
    )
    
    if not result.scalar_one_or_none():
        raise HTTPException(status_code=404, detail="Project not found or access denied")
    
    monitor = ContinuousMonitor(project_id)
    health = await monitor.check_health()
    
    return health


# Schedule Endpoints

@router.post("/projects/{project_id}/schedule")
async def create_schedule(
    project_id: int,
    request: CreateScheduleRequest,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Create a monitoring schedule."""
    # Verify project access
    result = await db.execute(
        select(Project).where(
            Project.id == project_id,
            Project.user_id == current_user.id
        )
    )
    
    if not result.scalar_one_or_none():
        raise HTTPException(status_code=404, detail="Project not found or access denied")
    
    try:
        frequency = ScheduleFrequency(request.frequency)
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid frequency")
    
    schedule = scheduler.create_schedule(
        project_id=project_id,
        frequency=frequency,
        enabled=request.enabled,
        config=request.config
    )
    
    return schedule


@router.get("/projects/{project_id}/schedules")
async def get_schedules(
    project_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Get all schedules for a project."""
    # Verify project access
    result = await db.execute(
        select(Project).where(
            Project.id == project_id,
            Project.user_id == current_user.id
        )
    )
    
    if not result.scalar_one_or_none():
        raise HTTPException(status_code=404, detail="Project not found or access denied")
    
    schedules = [s for s in scheduler.schedules if s['project_id'] == project_id]
    
    return {"schedules": schedules, "total": len(schedules)}


# Alert Endpoints

@router.get("/alerts", response_model=AlertsResponse)
async def get_alerts(
    project_id: Optional[int] = None,
    severity: Optional[str] = None,
    limit: int = 50,
    current_user: User = Depends(get_current_user),
):
    """Get alerts for current user."""
    severity_enum = None
    if severity:
        try:
            severity_enum = AlertSeverity(severity)
        except ValueError:
            raise HTTPException(status_code=400, detail="Invalid severity")
    
    alerts = alert_manager.get_alerts(
        project_id=project_id,
        severity=severity_enum,
        limit=limit
    )
    
    return AlertsResponse(alerts=alerts, total=len(alerts))


@router.put("/alerts/{alert_id}/acknowledge")
async def acknowledge_alert(
    alert_id: int,
    current_user: User = Depends(get_current_user),
):
    """Acknowledge an alert."""
    # Find alert
    alert = next((a for a in alert_manager.alerts if a['id'] == alert_id), None)
    
    if not alert:
        raise HTTPException(status_code=404, detail="Alert not found")
    
    alert['acknowledged'] = True
    alert['acknowledged_by'] = current_user.id
    alert['acknowledged_at'] = datetime.utcnow().isoformat()
    
    return alert


@router.get("/projects/{project_id}/health")
async def check_project_health(
    project_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Run health check on a project."""
    # Verify project access
    result = await db.execute(
        select(Project).where(
            Project.id == project_id,
            Project.user_id == current_user.id
        )
    )
    
    if not result.scalar_one_or_none():
        raise HTTPException(status_code=404, detail="Project not found or access denied")
    
    monitor = ContinuousMonitor(project_id)
    health = await monitor.check_health()
    
    return health
