"""
API endpoints for exporting data (Excel, Sitemap, CSV).
"""

from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import Response
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from typing import Optional

from app.core.dependencies import get_current_user, get_db
from app.models.user import User
from app.models.project import Project
from app.models.page import Page
from app.models.crawl_job import CrawlJob
from app.services.export.excel_exporter import export_to_excel
from app.services.export.sitemap_generator import generate_sitemap_with_index

router = APIRouter()


@router.get("/projects/{project_id}/export/excel")
async def export_to_excel_file(
    project_id: int,
    crawl_job_id: Optional[int] = None,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Export crawl data to Excel with multiple sheets."""
    # Verify project access
    project_result = await db.execute(
        select(Project).where(
            Project.id == project_id,
            Project.user_id == current_user.id
        )
    )
    
    project = project_result.scalar_one_or_none()
    
    if not project:
        raise HTTPException(status_code=404, detail="Project not found or access denied")
    
    # Get latest crawl job if not specified
    if not crawl_job_id:
        crawl_result = await db.execute(
            select(CrawlJob).where(
                CrawlJob.project_id == project_id
            ).order_by(CrawlJob.created_at.desc()).limit(1)
        )
        crawl_job = crawl_result.scalar_one_or_none()
    else:
        crawl_result = await db.execute(
            select(CrawlJob).where(CrawlJob.id == crawl_job_id)
        )
        crawl_job = crawl_result.scalar_one_or_none()
    
    if not crawl_job:
        raise HTTPException(status_code=404, detail="No crawl data found")
    
    # Get pages
    pages_result = await db.execute(
        select(Page).where(Page.crawl_job_id == crawl_job.id)
    )
    pages = pages_result.scalars().all()
    
    # Convert to dict format
    pages_data = [
        {
            'url': p.url,
            'status_code': p.status_code,
            'title': p.title,
            'meta_description': p.meta_description,
            'h1_tags': p.h1_tags,
            'h2_tags': p.h2_tags,
            'h3_tags': p.h3_tags,
            'word_count': p.word_count,
            'internal_links_count': p.internal_links_count,
            'external_links_count': p.external_links_count,
            'images_count': p.images_count,
            'images_without_alt': p.images_without_alt,
            'response_time_ms': p.response_time_ms,
            'depth': p.depth,
            'canonical_url': p.canonical_url,
            'og_tags': p.og_tags,
        }
        for p in pages
    ]
    
    # Calculate summary
    summary = {
        'total_pages': len(pages),
        'success_count': sum(1 for p in pages if 200 <= p.status_code < 300),
        'redirect_count': sum(1 for p in pages if 300 <= p.status_code < 400),
        'client_error_count': sum(1 for p in pages if 400 <= p.status_code < 500),
        'server_error_count': sum(1 for p in pages if p.status_code >= 500),
        'avg_response_time': sum(p.response_time_ms or 0 for p in pages) / len(pages) if pages else 0,
    }
    
    # Collect issues
    issues = []
    for p in pages:
        if not p.title:
            issues.append({
                'severity': 'Error',
                'type': 'Missing Title',
                'url': p.url,
                'description': 'Page is missing title tag',
                'recommendation': 'Add a descriptive title tag'
            })
        
        if not p.meta_description:
            issues.append({
                'severity': 'Warning',
                'type': 'Missing Meta Description',
                'url': p.url,
                'description': 'Page is missing meta description',
                'recommendation': 'Add a compelling meta description'
            })
    
    # Generate Excel file
    excel_bytes = export_to_excel(
        pages=pages_data,
        summary=summary,
        issues=issues[:100],  # Limit issues
        project_name=project.name
    )
    
    # Return as downloadable file
    return Response(
        content=excel_bytes,
        media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        headers={
            "Content-Disposition": f"attachment; filename={project.name}_seo_report.xlsx"
        }
    )


@router.get("/projects/{project_id}/export/sitemap")
async def export_sitemap(
    project_id: int,
    crawl_job_id: Optional[int] = None,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Generate XML sitemap from crawl results."""
    # Verify project access
    project_result = await db.execute(
        select(Project).where(
            Project.id == project_id,
            Project.user_id == current_user.id
        )
    )
    
    project = project_result.scalar_one_or_none()
    
    if not project:
        raise HTTPException(status_code=404, detail="Project not found or access denied")
    
    # Get pages
    if not crawl_job_id:
        pages_result = await db.execute(
            select(Page).join(
                Page.crawl_job
            ).where(
                Page.crawl_job.has(project_id=project_id)
            ).limit(50000)
        )
    else:
        pages_result = await db.execute(
            select(Page).where(Page.crawl_job_id == crawl_job_id).limit(50000)
        )
    
    pages = pages_result.scalars().all()
    
    # Convert to dict format
    pages_data = [
        {
            'url': p.url,
            'status_code': p.status_code,
            'depth': p.depth,
            'created_at': p.created_at,
        }
        for p in pages
    ]
    
    # Generate sitemap
    sitemap_data = generate_sitemap_with_index(
        domain=project.domain,
        pages=pages_data
    )
    
    # Return main sitemap
    sitemap_xml = sitemap_data['sitemaps'][0]
    
    return Response(
        content=sitemap_xml,
        media_type="application/xml",
        headers={
            "Content-Disposition": f"attachment; filename=sitemap.xml"
        }
    )


@router.get("/projects/{project_id}/export/csv")
async def export_to_csv(
    project_id: int,
    crawl_job_id: Optional[int] = None,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Export crawl data to CSV."""
    # Verify project access
    project_result = await db.execute(
        select(Project).where(
            Project.id == project_id,
            Project.user_id == current_user.id
        )
    )
    
    project = project_result.scalar_one_or_none()
    
    if not project:
        raise HTTPException(status_code=404, detail="Project not found or access denied")
    
    # Get pages
    if not crawl_job_id:
        pages_result = await db.execute(
            select(Page).join(
                Page.crawl_job
            ).where(
                Page.crawl_job.has(project_id=project_id)
            )
        )
    else:
        pages_result = await db.execute(
            select(Page).where(Page.crawl_job_id == crawl_job_id)
        )
    
    pages = pages_result.scalars().all()
    
    # Generate CSV
    import csv
    import io
    
    output = io.StringIO()
    writer = csv.writer(output)
    
    # Header
    writer.writerow([
        'URL', 'Status Code', 'Title', 'Meta Description',
        'H1', 'Word Count', 'Internal Links', 'External Links',
        'Images', 'Images without Alt', 'Response Time (ms)', 'Depth'
    ])
    
    # Data rows
    for p in pages:
        h1 = p.h1_tags[0] if p.h1_tags else ''
        
        writer.writerow([
            p.url,
            p.status_code,
            p.title or '',
            p.meta_description or '',
            h1,
            p.word_count,
            p.internal_links_count,
            p.external_links_count,
            p.images_count,
            p.images_without_alt,
            p.response_time_ms or 0,
            p.depth
        ])
    
    csv_content = output.getvalue()
    
    return Response(
        content=csv_content,
        media_type="text/csv",
        headers={
            "Content-Disposition": f"attachment; filename={project.name}_pages.csv"
        }
    )
