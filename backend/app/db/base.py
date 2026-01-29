"""
SQLAlchemy declarative base and model imports.

This module serves as a central import point for all SQLAlchemy models.
All models must be imported here to ensure they're registered with Alembic.
"""

from sqlalchemy.orm import DeclarativeBase


class Base(DeclarativeBase):
    """Base class for all SQLAlchemy ORM models."""
    
    pass


# Import all models here to make them available to Alembic
# This ensures all tables are created during migrations
from app.models.user import User  # noqa: F401, E402
from app.models.project import Project  # noqa: F401, E402
from app.models.crawl_job import CrawlJob  # noqa: F401, E402
from app.models.page import Page  # noqa: F401, E402
from app.models.team import TeamMember, Comment, Task  # noqa: F401, E402
from app.models.dashboard import Dashboard, DashboardWidget  # noqa: F401, E402
