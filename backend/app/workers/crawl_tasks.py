"""
Celery tasks for web crawling.

These tasks handle asynchronous crawling operations.
"""

import asyncio
from datetime import datetime
from typing import Any

from celery import Task
from sqlalchemy import select

from app.db.session import async_session_maker
from app.models.crawl_job import CrawlJob, CrawlStatus
from app.models.project import Project
from app.workers.celery_app import celery_app


class CallbackTask(Task):
    """
    Custom Task class with callbacks for state updates.
    
    This allows us to update the database when task state changes.
    """
    
    def on_success(self, retval: Any, task_id: str, args: tuple, kwargs: dict) -> None:
        """Called when task succeeds."""
        pass
    
    def on_failure(
        self,
        exc: Exception,
        task_id: str,
        args: tuple,
        kwargs: dict,
        einfo: Any,
    ) -> None:
        """Called when task fails."""
        pass


@celery_app.task(bind=True, base=CallbackTask, name="app.workers.crawl_tasks.start_crawl_task")
def start_crawl_task(self, crawl_job_id: int) -> dict:
    """
    Start a web crawl for a project.
    
    This is a Celery task that runs asynchronously to crawl a website.
    
    Args:
        crawl_job_id: ID of the crawl job to execute.
    
    Returns:
        dict: Crawl statistics and results.
    """
    # Run the async crawl in the event loop
    return asyncio.run(_run_crawl(self, crawl_job_id))


async def _run_crawl(task: Task, crawl_job_id: int) -> dict:
    """
    Execute the actual crawl operation (async).
    
    Args:
        task: Celery task instance.
        crawl_job_id: ID of the crawl job.
    
    Returns:
        dict: Crawl results.
    """
    async with async_session_maker() as db:
        try:
            # Get crawl job
            result = await db.execute(
                select(CrawlJob).where(CrawlJob.id == crawl_job_id)
            )
            crawl_job = result.scalar_one_or_none()
            
            if not crawl_job:
                raise ValueError(f"Crawl job {crawl_job_id} not found")
            
            # Update status to running
            crawl_job.status = CrawlStatus.RUNNING
            crawl_job.started_at = datetime.utcnow()
            crawl_job.celery_task_id = task.request.id
            await db.commit()
            
            # Get project settings
            result = await db.execute(
                select(Project).where(Project.id == crawl_job.project_id)
            )
            project = result.scalar_one()
            
            # TODO: Implement actual crawling logic
            # For now, this is a placeholder
            # from app.services.crawler.spider import WebCrawler
            # crawler = WebCrawler(project)
            # results = await crawler.crawl()
            
            # Simulate crawl for now
            await asyncio.sleep(5)
            
            # Update crawl job as completed
            crawl_job.status = CrawlStatus.COMPLETED
            crawl_job.completed_at = datetime.utcnow()
            crawl_job.pages_crawled = 10  # Placeholder
            crawl_job.pages_total = 10  # Placeholder
            await db.commit()
            
            return {
                "crawl_job_id": crawl_job_id,
                "status": "completed",
                "pages_crawled": crawl_job.pages_crawled,
            }
            
        except Exception as e:
            # Mark crawl as failed
            if crawl_job:
                crawl_job.status = CrawlStatus.FAILED
                crawl_job.completed_at = datetime.utcnow()
                crawl_job.error_message = str(e)
                await db.commit()
            
            raise


@celery_app.task(name="app.workers.crawl_tasks.cleanup_old_results")
def cleanup_old_results() -> dict:
    """
    Periodic task to clean up old crawl results.
    
    Runs daily to remove old crawl data and keep database size manageable.
    
    Returns:
        dict: Cleanup statistics.
    """
    # TODO: Implement cleanup logic
    # - Delete crawl jobs older than X days
    # - Archive or compress old data
    # - Clean up orphaned records
    
    return {
        "status": "completed",
        "deleted_count": 0,
    }
