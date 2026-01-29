"""
URL parsing and normalization utilities.

This module provides functions for URL validation, normalization,
and extraction from HTML content.
"""

import hashlib
from typing import Optional, Set
from urllib.parse import urljoin, urlparse, urlunparse

from bs4 import BeautifulSoup


def normalize_url(url: str) -> str:
    """
    Normalize a URL to a canonical form.
    
    This function:
    - Converts scheme and netloc to lowercase
    - Removes default ports (80 for HTTP, 443 for HTTPS)
    - Removes trailing slashes from path (except for root)
    - Sorts query parameters
    - Removes fragments
    
    Args:
        url: The URL to normalize.
    
    Returns:
        str: Normalized URL.
    """
    parsed = urlparse(url)
    
    # Lowercase scheme and netloc
    scheme = parsed.scheme.lower()
    netloc = parsed.netloc.lower()
    
    # Remove default ports
    if netloc.endswith(':80') and scheme == 'http':
        netloc = netloc[:-3]
    elif netloc.endswith(':443') and scheme == 'https':
        netloc = netloc[:-4]
    
    # Clean path
    path = parsed.path
    if path and path != '/' and path.endswith('/'):
        path = path.rstrip('/')
    
    # Reconstruct URL without fragment
    normalized = urlunparse((
        scheme,
        netloc,
        path or '/',
        parsed.params,
        parsed.query,
        '',  # No fragment
    ))
    
    return normalized


def get_url_hash(url: str) -> str:
    """
    Generate a SHA-256 hash of a URL.
    
    Used for fast lookups and deduplication.
    
    Args:
        url: The URL to hash.
    
    Returns:
        str: Hexadecimal hash string.
    """
    normalized = normalize_url(url)
    return hashlib.sha256(normalized.encode('utf-8')).hexdigest()


def is_same_domain(url1: str, url2: str) -> bool:
    """
    Check if two URLs are from the same domain.
    
    Args:
        url1: First URL.
        url2: Second URL.
    
    Returns:
        bool: True if same domain, False otherwise.
    """
    domain1 = urlparse(url1).netloc.lower()
    domain2 = urlparse(url2).netloc.lower()
    
    # Remove www. prefix for comparison
    domain1 = domain1.replace('www.', '')
    domain2 = domain2.replace('www.', '')
    
    return domain1 == domain2


def extract_links_from_html(
    html: str,
    base_url: str,
    same_domain_only: bool = True,
) -> Set[str]:
    """
    Extract all links from HTML content.
    
    Args:
        html: HTML content.
        base_url: Base URL for resolving relative links.
        same_domain_only: If True, only return links from same domain.
    
    Returns:
        set: Set of normalized URLs.
    """
    soup = BeautifulSoup(html, 'lxml')
    links = set()
    
    for tag in soup.find_all('a', href=True):
        href = tag.get('href', '').strip()
        
        # Skip empty, javascript, mailto, tel links
        if not href or href.startswith(('#', 'javascript:', 'mailto:', 'tel:')):
            continue
        
        # Resolve relative URLs
        absolute_url = urljoin(base_url, href)
        
        # Filter by domain if requested
        if same_domain_only and not is_same_domain(absolute_url, base_url):
            continue
        
        # Skip non-HTTP(S) schemes
        scheme = urlparse(absolute_url).scheme
        if scheme not in ('http', 'https'):
            continue
        
        # Normalize and add
        try:
            normalized = normalize_url(absolute_url)
            links.add(normalized)
        except Exception:
            # Skip invalid URLs
            continue
    
    return links


def get_domain_from_url(url: str) -> str:
    """
    Extract domain from URL.
    
    Args:
        url: The URL.
    
    Returns:
        str: Domain name.
    """
    parsed = urlparse(url)
    domain = parsed.netloc.lower()
    
    # Remove www. prefix
    if domain.startswith('www.'):
        domain = domain[4:]
    
    return domain


def is_valid_url(url: str) -> bool:
    """
    Check if a URL is valid.
    
    Args:
        url: The URL to validate.
    
    Returns:
        bool: True if valid, False otherwise.
    """
    try:
        parsed = urlparse(url)
        return all([
            parsed.scheme in ('http', 'https'),
            parsed.netloc,
        ])
    except Exception:
        return False
