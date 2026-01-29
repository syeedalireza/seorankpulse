"""
Tests for team collaboration features.
"""

import pytest
from app.models.team import TeamMember, Comment, Task


def test_team_member_creation():
    """Test TeamMember model creation."""
    member = TeamMember(
        project_id=1,
        user_id=2,
        role='analyst'
    )
    
    assert member.project_id == 1
    assert member.user_id == 2
    assert member.role == 'analyst'


def test_comment_creation():
    """Test Comment model creation."""
    comment = Comment(
        project_id=1,
        user_id=2,
        content='This page needs optimization',
        page_id=100
    )
    
    assert comment.content == 'This page needs optimization'
    assert comment.page_id == 100


def test_task_creation():
    """Test Task model creation."""
    task = Task(
        project_id=1,
        created_by=2,
        assigned_to=3,
        title='Fix broken links',
        description='There are 5 broken links on homepage',
        priority='high',
        status='todo'
    )
    
    assert task.title == 'Fix broken links'
    assert task.priority == 'high'
    assert task.status == 'todo'
