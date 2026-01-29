"""
Tests for custom dashboards.
"""

import pytest
from app.models.dashboard import Dashboard, DashboardWidget
from app.services.dashboard.widget_types import WidgetConfiguration


def test_dashboard_creation():
    """Test Dashboard model creation."""
    dashboard = Dashboard(
        user_id=1,
        project_id=1,
        name='My Dashboard',
        description='Custom SEO dashboard',
        layout={},
        is_public=False,
        is_default=True
    )
    
    assert dashboard.name == 'My Dashboard'
    assert dashboard.is_default is True


def test_widget_creation():
    """Test DashboardWidget model creation."""
    widget = DashboardWidget(
        dashboard_id=1,
        widget_type='seo_score',
        title='SEO Score',
        position_x=0,
        position_y=0,
        width=4,
        height=4,
        config={}
    )
    
    assert widget.widget_type == 'seo_score'
    assert widget.width == 4


def test_widget_types_available():
    """Test available widget types."""
    widgets = WidgetConfiguration.get_available_widgets()
    
    assert len(widgets) > 0
    assert any(w['type'] == 'seo_score' for w in widgets)


def test_widget_categories():
    """Test widget categories."""
    categories = WidgetConfiguration.get_widget_categories()
    
    assert 'overview' in categories
    assert 'charts' in categories
    assert 'analysis' in categories
