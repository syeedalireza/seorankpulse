"""Initial migration - create all tables

Revision ID: 001_initial
Revises: 
Create Date: 2026-01-28 12:00:00

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = '001_initial'
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Create users table
    op.create_table(
        'users',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('email', sa.String(length=255), nullable=False),
        sa.Column('hashed_password', sa.String(length=255), nullable=False),
        sa.Column('full_name', sa.String(length=255), nullable=True),
        sa.Column('is_active', sa.Boolean(), nullable=False, server_default='true'),
        sa.Column('is_superuser', sa.Boolean(), nullable=False, server_default='false'),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_users_id'), 'users', ['id'], unique=False)
    op.create_index(op.f('ix_users_email'), 'users', ['email'], unique=True)

    # Create projects table
    op.create_table(
        'projects',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('name', sa.String(length=255), nullable=False),
        sa.Column('domain', sa.String(length=255), nullable=False),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('user_id', sa.Integer(), nullable=False),
        sa.Column('max_depth', sa.Integer(), nullable=False, server_default='10'),
        sa.Column('crawl_delay_ms', sa.Integer(), nullable=False, server_default='1000'),
        sa.Column('user_agent', sa.String(length=255), nullable=False, server_default='SEO-Analyzer-Bot/1.0'),
        sa.Column('respect_robots_txt', sa.Boolean(), nullable=False, server_default='true'),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_projects_id'), 'projects', ['id'], unique=False)
    op.create_index(op.f('ix_projects_domain'), 'projects', ['domain'], unique=False)
    op.create_index(op.f('ix_projects_user_id'), 'projects', ['user_id'], unique=False)

    # Create crawl_jobs table
    op.create_table(
        'crawl_jobs',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('project_id', sa.Integer(), nullable=False),
        sa.Column('status', sa.Enum('PENDING', 'RUNNING', 'COMPLETED', 'FAILED', 'CANCELLED', name='crawlstatus'), nullable=False),
        sa.Column('celery_task_id', sa.String(length=255), nullable=True),
        sa.Column('started_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('completed_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('pages_crawled', sa.Integer(), nullable=False, server_default='0'),
        sa.Column('pages_total', sa.Integer(), nullable=False, server_default='0'),
        sa.Column('error_message', sa.Text(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.ForeignKeyConstraint(['project_id'], ['projects.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_crawl_jobs_id'), 'crawl_jobs', ['id'], unique=False)
    op.create_index(op.f('ix_crawl_jobs_project_id'), 'crawl_jobs', ['project_id'], unique=False)
    op.create_index(op.f('ix_crawl_jobs_status'), 'crawl_jobs', ['status'], unique=False)
    op.create_index(op.f('ix_crawl_jobs_celery_task_id'), 'crawl_jobs', ['celery_task_id'], unique=False)

    # Create pages table
    op.create_table(
        'pages',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('crawl_job_id', sa.Integer(), nullable=False),
        sa.Column('url', sa.Text(), nullable=False),
        sa.Column('url_hash', sa.String(length=64), nullable=False),
        sa.Column('status_code', sa.Integer(), nullable=False),
        sa.Column('response_time_ms', sa.Integer(), nullable=True),
        sa.Column('title', sa.String(length=1000), nullable=True),
        sa.Column('meta_description', sa.Text(), nullable=True),
        sa.Column('meta_keywords', sa.Text(), nullable=True),
        sa.Column('canonical_url', sa.Text(), nullable=True),
        sa.Column('h1_tags', postgresql.JSON(astext_type=sa.Text()), nullable=True),
        sa.Column('h2_tags', postgresql.JSON(astext_type=sa.Text()), nullable=True),
        sa.Column('h3_tags', postgresql.JSON(astext_type=sa.Text()), nullable=True),
        sa.Column('images_count', sa.Integer(), nullable=False, server_default='0'),
        sa.Column('images_without_alt', sa.Integer(), nullable=False, server_default='0'),
        sa.Column('internal_links_count', sa.Integer(), nullable=False, server_default='0'),
        sa.Column('external_links_count', sa.Integer(), nullable=False, server_default='0'),
        sa.Column('word_count', sa.Integer(), nullable=False, server_default='0'),
        sa.Column('text_to_html_ratio', sa.Float(), nullable=True),
        sa.Column('page_size_bytes', sa.Integer(), nullable=True),
        sa.Column('schema_org_types', postgresql.JSON(astext_type=sa.Text()), nullable=True),
        sa.Column('og_tags', postgresql.JSON(astext_type=sa.Text()), nullable=True),
        sa.Column('has_robots_noindex', sa.Boolean(), nullable=False, server_default='false'),
        sa.Column('has_robots_nofollow', sa.Boolean(), nullable=False, server_default='false'),
        sa.Column('depth', sa.Integer(), nullable=False, server_default='0'),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.ForeignKeyConstraint(['crawl_job_id'], ['crawl_jobs.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('url_hash')
    )
    op.create_index(op.f('ix_pages_id'), 'pages', ['id'], unique=False)
    op.create_index(op.f('ix_pages_crawl_job_id'), 'pages', ['crawl_job_id'], unique=False)
    op.create_index(op.f('ix_pages_url_hash'), 'pages', ['url_hash'], unique=True)
    op.create_index(op.f('ix_pages_status_code'), 'pages', ['status_code'], unique=False)


def downgrade() -> None:
    # Drop tables in reverse order
    op.drop_index(op.f('ix_pages_status_code'), table_name='pages')
    op.drop_index(op.f('ix_pages_url_hash'), table_name='pages')
    op.drop_index(op.f('ix_pages_crawl_job_id'), table_name='pages')
    op.drop_index(op.f('ix_pages_id'), table_name='pages')
    op.drop_table('pages')
    
    op.drop_index(op.f('ix_crawl_jobs_celery_task_id'), table_name='crawl_jobs')
    op.drop_index(op.f('ix_crawl_jobs_status'), table_name='crawl_jobs')
    op.drop_index(op.f('ix_crawl_jobs_project_id'), table_name='crawl_jobs')
    op.drop_index(op.f('ix_crawl_jobs_id'), table_name='crawl_jobs')
    op.drop_table('crawl_jobs')
    
    op.drop_index(op.f('ix_projects_user_id'), table_name='projects')
    op.drop_index(op.f('ix_projects_domain'), table_name='projects')
    op.drop_index(op.f('ix_projects_id'), table_name='projects')
    op.drop_table('projects')
    
    op.drop_index(op.f('ix_users_email'), table_name='users')
    op.drop_index(op.f('ix_users_id'), table_name='users')
    op.drop_table('users')
    
    # Drop enum type
    sa.Enum(name='crawlstatus').drop(op.get_bind())
