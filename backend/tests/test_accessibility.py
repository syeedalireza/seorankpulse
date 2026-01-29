"""
Tests for accessibility auditing.
"""

import pytest
from app.services.analyzer.accessibility import generate_accessibility_report


def test_generate_accessibility_report():
    """Test accessibility report generation."""
    audit_results = [
        {
            'url': 'https://example.com/page1',
            'success': True,
            'score': 85,
            'summary': {
                'total_violations': 5,
                'critical': 1,
                'serious': 2,
                'moderate': 2,
                'minor': 0,
                'passes': 20,
            },
            'violations': {
                'critical': [{'id': 'color-contrast', 'description': 'Low contrast', 'nodes_affected': 3}],
                'serious': [],
                'moderate': [],
                'minor': [],
            },
        },
        {
            'url': 'https://example.com/page2',
            'success': True,
            'score': 95,
            'summary': {
                'total_violations': 1,
                'critical': 0,
                'serious': 0,
                'moderate': 1,
                'minor': 0,
                'passes': 25,
            },
            'violations': {
                'critical': [],
                'serious': [],
                'moderate': [],
                'minor': [],
            },
        },
    ]
    
    report = generate_accessibility_report(audit_results)
    
    assert report['summary']['total_pages_audited'] == 2
    assert report['summary']['successful_audits'] == 2
    assert report['summary']['total_violations'] == 6
    assert report['summary']['total_critical'] == 1
    assert report['summary']['average_score'] == 90.0
