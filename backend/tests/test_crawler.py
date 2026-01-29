"""
Tests for web crawler functionality.
"""

import pytest

from app.services.crawler.url_parser import (
    normalize_url,
    get_url_hash,
    is_same_domain,
    is_valid_url,
    get_domain_from_url,
)


def test_normalize_url():
    """Test URL normalization."""
    # Test trailing slash removal
    assert normalize_url("https://example.com/page/") == "https://example.com/page"
    
    # Test lowercase
    assert normalize_url("HTTPS://EXAMPLE.COM/Page") == "https://example.com/Page"
    
    # Test default port removal
    assert normalize_url("https://example.com:443/") == "https://example.com/"
    assert normalize_url("http://example.com:80/") == "http://example.com/"


def test_get_url_hash():
    """Test URL hashing for uniqueness."""
    url1 = "https://example.com/page"
    url2 = "https://example.com/page/"  # Should normalize to same
    
    hash1 = get_url_hash(url1)
    hash2 = get_url_hash(url2)
    
    assert hash1 == hash2
    assert len(hash1) == 64  # SHA-256 hex length


def test_is_same_domain():
    """Test same domain checking."""
    assert is_same_domain("https://example.com/page1", "https://example.com/page2")
    assert is_same_domain("http://www.example.com/", "https://example.com/")
    assert not is_same_domain("https://example.com/", "https://different.com/")


def test_is_valid_url():
    """Test URL validation."""
    assert is_valid_url("https://example.com/page")
    assert is_valid_url("http://example.com")
    assert not is_valid_url("javascript:void(0)")
    assert not is_valid_url("mailto:test@example.com")
    assert not is_valid_url("invalid-url")


def test_get_domain_from_url():
    """Test domain extraction."""
    assert get_domain_from_url("https://www.example.com/page") == "example.com"
    assert get_domain_from_url("http://example.com:8080/") == "example.com:8080"
