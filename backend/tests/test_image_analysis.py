"""
Tests for image analysis.
"""

import pytest


def test_image_score_calculation():
    """Test image optimization score calculation."""
    from app.services.analyzer.image_analyzer import ImageAnalyzer
    
    analyzer = ImageAnalyzer()
    
    # Test good image
    score = analyzer._calculate_image_score(
        file_size=50 * 1024,  # 50KB
        width=800,
        height=600,
        format_name='JPEG'
    )
    
    assert score['score'] >= 80
    assert score['grade'] in ['A', 'B']
    
    # Test oversized image
    score_bad = analyzer._calculate_image_score(
        file_size=2 * 1024 * 1024,  # 2MB
        width=5000,
        height=5000,
        format_name='PNG'
    )
    
    assert score_bad['score'] < score['score']
    assert len(score_bad['issues']) > 0


def test_format_recommendations():
    """Test image format recommendations."""
    from app.services.analyzer.image_analyzer import ImageAnalyzer
    
    analyzer = ImageAnalyzer()
    
    # JPEG should suggest WebP
    rec = analyzer._recommend_format(
        current_format='JPEG',
        width=1920,
        height=1080,
        mode='RGB'
    )
    
    assert 'WebP' in rec['recommended_format']
    assert len(rec['recommendations']) > 0
