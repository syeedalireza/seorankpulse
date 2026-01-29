"""
Celery application configuration.

This module initializes and configures the Celery app for background tasks.
"""

from celery import Celery
from celery.schedules import crontab

from app.core.config import settings

# Create Celery app
celery_app = Celery(
    "seo_analyzer",
    broker=settings.CELERY_BROKER_URL,
    backend=settings.CELERY_RESULT_BACKEND,
    include=[
        "app.workers.crawl_tasks",
        "app.workers.analysis_tasks",
        "app.workers.report_tasks",
        "app.workers.ai_tasks",
        "app.workers.serp_tasks",
        "app.workers.monitoring_tasks",
    ],
)

# Configure Celery
celery_app.conf.update(
    task_serializer="json",
    accept_content=["json"],
    result_serializer="json",
    timezone="UTC",
    enable_utc=True,
    task_track_started=True,
    task_time_limit=3600,  # 1 hour max per task
    task_soft_time_limit=3300,  # 55 minutes soft limit
    worker_prefetch_multiplier=1,
    worker_max_tasks_per_child=1000,
    task_acks_late=True,
    task_reject_on_worker_lost=True,
    result_expires=86400,  # Results expire after 24 hours
)

# Periodic tasks schedule
celery_app.conf.beat_schedule = {
    "cleanup-old-results": {
        "task": "app.workers.crawl_tasks.cleanup_old_results",
        "schedule": crontab(hour=2, minute=0),  # Run daily at 2 AM
    },
    
    # SERP Tracking (daily at 6 AM)
    "daily-serp-check": {
        "task": "serp.scheduled_check",
        "schedule": crontab(hour=6, minute=0),
        # Note: In production, this would iterate over all projects with SERP tracking enabled
    },
    
    # Health Checks (every 6 hours)
    "periodic-health-check": {
        "task": "monitoring.check_health",
        "schedule": crontab(minute=0, hour="*/6"),
    },
    
    # Anomaly Detection (daily at 3 AM)
    "detect-anomalies": {
        "task": "monitoring.detect_anomalies",
        "schedule": crontab(hour=3, minute=0),
    },
    
    # Save metrics snapshot (after each crawl - triggered by crawl completion)
    # This is event-driven, not periodic
}

if __name__ == "__main__":
    celery_app.start()
