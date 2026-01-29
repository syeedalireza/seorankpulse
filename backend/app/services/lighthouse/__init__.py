"""
Lighthouse service for Core Web Vitals and performance analysis.
"""

from app.services.lighthouse.lighthouse_client import (
    LighthouseClient,
    run_lighthouse_audit,
)

__all__ = ['LighthouseClient', 'run_lighthouse_audit']
