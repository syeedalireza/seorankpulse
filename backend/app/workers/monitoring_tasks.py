"""
Celery tasks for monitoring, alerts, and health checks.
"""

from celery import Task
from app.workers.celery_app import celery_app
from app.services.monitoring.alert_manager import AlertManager
from app.services.monitoring.scheduler import ContinuousMonitor
from datetime import datetime


@celery_app.task(bind=True, name="monitoring.send_alert")
def send_alert_task(self: Task, alert_id: int, channels: list):
    """
    Send alert notification.
    
    Args:
        alert_id: Alert ID.
        channels: List of notification channels (email, slack, webhook).
    """
    import asyncio
    
    async def _send():
        alert_manager = AlertManager()
        
        # Find alert
        alert = next((a for a in alert_manager.alerts if a['id'] == alert_id), None)
        
        if not alert:
            return {'error': 'Alert not found'}
        
        # Send to channels
        result = await alert_manager.send_alert(alert, channels)
        
        return result
    
    return asyncio.run(_send())


@celery_app.task(bind=True, name="monitoring.check_health")
def check_health_task(self: Task, project_id: int):
    """
    Run health check on a project.
    
    Args:
        project_id: Project ID.
    """
    import asyncio
    
    async def _check():
        monitor = ContinuousMonitor(project_id)
        health = await monitor.check_health()
        
        # If health check fails, create alerts
        
        return health
    
    return asyncio.run(_check())


@celery_app.task(bind=True, name="monitoring.compare_with_history")
def compare_with_history_task(self: Task, project_id: int):
    """
    Compare current metrics with historical data and trigger alerts.
    
    Args:
        project_id: Project ID.
    """
    import asyncio
    from app.db.session import AsyncSessionLocal
    from app.services.monitoring.historical_tracker import HistoricalTracker
    from app.services.monitoring.alert_manager import AlertManager
    
    async def _compare():
        async with AsyncSessionLocal() as db:
            tracker = HistoricalTracker(db)
            
            # Get recent snapshots
            snapshots = await tracker.get_snapshots(project_id, limit=2)
            
            if len(snapshots) < 2:
                return {'message': 'Not enough historical data'}
            
            # Compare snapshots
            old_metrics = snapshots[1].get('metrics', {})
            new_metrics = snapshots[0].get('metrics', {})
            
            # Check for significant changes
            alert_manager = AlertManager()
            alerts = alert_manager.check_metric_changes(
                project_id=project_id,
                old_metrics=old_metrics,
                new_metrics=new_metrics
            )
            
            # Send alerts
            for alert in alerts:
                await alert_manager.send_alert(alert, channels=['email'])
            
            return {
                'project_id': project_id,
                'alerts_created': len(alerts),
                'timestamp': datetime.utcnow().isoformat()
            }
    
    return asyncio.run(_compare())


@celery_app.task(bind=True, name="monitoring.detect_anomalies")
def detect_anomalies_task(self: Task, project_id: int, threshold: float = 20.0):
    """
    Detect anomalies in project metrics.
    
    Args:
        project_id: Project ID.
        threshold: Percentage threshold for anomaly detection.
    """
    import asyncio
    from app.db.session import AsyncSessionLocal
    from app.services.monitoring.historical_tracker import HistoricalTracker
    
    async def _detect():
        async with AsyncSessionLocal() as db:
            tracker = HistoricalTracker(db)
            
            # Get snapshots
            snapshots = await tracker.get_snapshots(project_id, limit=10)
            
            if not snapshots:
                return {'message': 'No historical data'}
            
            # Detect anomalies
            anomalies = tracker.detect_anomalies(snapshots, threshold=threshold)
            
            # Create alerts for anomalies
            # ...
            
            return {
                'project_id': project_id,
                'anomalies_detected': len(anomalies),
                'anomalies': anomalies
            }
    
    return asyncio.run(_detect())


@celery_app.task(bind=True, name="monitoring.save_snapshot")
def save_snapshot_task(self: Task, project_id: int, crawl_job_id: int):
    """
    Save a metrics snapshot after crawl completion.
    
    Args:
        project_id: Project ID.
        crawl_job_id: Crawl job ID.
    """
    import asyncio
    from app.db.session import AsyncSessionLocal
    from app.services.monitoring.historical_tracker import HistoricalTracker, create_metrics_snapshot
    
    async def _save():
        async with AsyncSessionLocal() as db:
            # Gather metrics from crawl
            crawl_data = {}  # Would fetch from database
            analysis_data = {}  # Would fetch from analysis
            
            # Create snapshot
            metrics = create_metrics_snapshot(crawl_data, analysis_data)
            
            # Save to database
            tracker = HistoricalTracker(db)
            snapshot = await tracker.save_snapshot(
                project_id=project_id,
                crawl_job_id=crawl_job_id,
                metrics=metrics
            )
            
            return snapshot
    
    return asyncio.run(_save())
