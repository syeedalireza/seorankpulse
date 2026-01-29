"""
Tests for monitoring and alerting.
"""

import pytest
from app.services.monitoring.alert_manager import AlertManager, AlertSeverity, AlertType
from app.services.monitoring.scheduler import MonitoringScheduler, ScheduleFrequency


def test_alert_creation():
    """Test alert creation."""
    manager = AlertManager()
    
    alert = manager.create_alert(
        project_id=1,
        alert_type=AlertType.METRIC_DROP,
        severity=AlertSeverity.WARNING,
        title='SEO Score Dropped',
        message='SEO score dropped by 15%',
        data={'old_value': 85, 'new_value': 72}
    )
    
    assert alert['title'] == 'SEO Score Dropped'
    assert alert['severity'] == 'warning'
    assert alert['acknowledged'] is False


def test_metric_change_detection():
    """Test metric change detection."""
    manager = AlertManager()
    
    old_metrics = {
        'avg_seo_score': 85,
        'error_pages': 5,
    }
    
    new_metrics = {
        'avg_seo_score': 70,  # Dropped 15 points
        'error_pages': 10,    # Doubled
    }
    
    alerts = manager.check_metric_changes(
        project_id=1,
        old_metrics=old_metrics,
        new_metrics=new_metrics
    )
    
    assert len(alerts) > 0


def test_schedule_creation():
    """Test monitoring schedule creation."""
    scheduler = MonitoringScheduler()
    
    schedule = scheduler.create_schedule(
        project_id=1,
        frequency=ScheduleFrequency.DAILY,
        enabled=True
    )
    
    assert schedule['project_id'] == 1
    assert schedule['frequency'] == 'daily'
    assert schedule['enabled'] is True
