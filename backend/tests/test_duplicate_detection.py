"""
Tests for duplicate content detection.
"""

import pytest
from app.services.analyzer.duplicate_detector import (
    DuplicateContentDetector,
    detect_duplicates,
    find_cannibalization_issues
)


def test_simhash_computation():
    """Test SimHash computation."""
    detector = DuplicateContentDetector(similarity_threshold=3)
    
    text1 = "This is a test page about SEO optimization"
    text2 = "This is a test page about SEO optimization"
    
    hash1 = detector.compute_simhash(text1)
    hash2 = detector.compute_simhash(text2)
    
    assert hash1.distance(hash2) == 0  # Identical text


def test_duplicate_detection():
    """Test duplicate detection with sample pages."""
    pages = [
        {
            'url': 'https://example.com/page1',
            'title': 'SEO Best Practices',
            'meta_description': 'Learn SEO best practices',
            'h1_tags': ['SEO Guide'],
        },
        {
            'url': 'https://example.com/page2',
            'title': 'SEO Best Practices',
            'meta_description': 'Learn SEO best practices',
            'h1_tags': ['SEO Guide'],
        },
        {
            'url': 'https://example.com/page3',
            'title': 'Different Content',
            'meta_description': 'Completely different topic',
            'h1_tags': ['Other Topic'],
        },
    ]
    
    results = detect_duplicates(pages, similarity_threshold=3)
    
    assert results['total_pages_analyzed'] == 3
    assert results['exact_duplicate_groups'] >= 1


def test_cannibalization_detection():
    """Test keyword cannibalization detection."""
    pages = [
        {
            'url': 'https://example.com/page1',
            'title': 'Best SEO Tools for 2024',
            'meta_description': 'Top SEO tools',
            'h1_tags': ['SEO Tools'],
        },
        {
            'url': 'https://example.com/page2',
            'title': 'Top SEO Tools Guide',
            'meta_description': 'Best SEO tools guide',
            'h1_tags': ['SEO Tools'],
        },
    ]
    
    issues = find_cannibalization_issues(pages, ['seo tools'])
    
    assert len(issues) > 0
    assert issues[0]['keyword'] == 'seo tools'
    assert issues[0]['page_count'] == 2
