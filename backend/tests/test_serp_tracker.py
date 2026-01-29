"""
Tests for SERP tracking.
"""

import pytest
from app.services.integrations.serp_client import RankingTracker
from datetime import datetime


def test_ranking_tracker():
    """Test ranking tracker initialization."""
    tracker = RankingTracker()
    assert tracker is not None
    assert tracker.historical_data == []


def test_add_ranking_data():
    """Test adding ranking data."""
    tracker = RankingTracker()
    
    tracker.add_ranking_data(
        keyword='seo tools',
        position=5,
        timestamp=datetime.utcnow()
    )
    
    assert len(tracker.historical_data) == 1
    assert tracker.historical_data[0]['keyword'] == 'seo tools'
    assert tracker.historical_data[0]['position'] == 5


def test_calculate_ranking_changes():
    """Test ranking change calculation."""
    tracker = RankingTracker()
    
    # Add two data points
    tracker.add_ranking_data('seo tools', 10, datetime.utcnow())
    tracker.add_ranking_data('seo tools', 5, datetime.utcnow())
    
    changes = tracker.calculate_changes('seo tools')
    
    assert changes['current_position'] == 5
    assert changes['previous_position'] == 10
    assert changes['change'] == 5  # Improved by 5 positions
    assert changes['status'] == 'improved'
