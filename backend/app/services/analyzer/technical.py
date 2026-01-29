"""
Technical SEO analysis utilities.

This module provides functions for analyzing technical SEO aspects
like HTTP status codes, redirects, security, etc.
"""

from typing import Dict, List, Optional
from urllib.parse import urlparse

import httpx


def analyze_http_status(status_code: int) -> Dict:
    """
    Analyze HTTP status code and provide SEO implications.
    
    Args:
        status_code: HTTP status code.
    
    Returns:
        dict: Status analysis with SEO impact.
    """
    status_info = {
        "code": status_code,
        "category": "",
        "severity": "info",
        "seo_impact": "",
        "recommendation": "",
    }
    
    if 200 <= status_code < 300:
        status_info.update({
            "category": "Success",
            "severity": "success",
            "seo_impact": "Positive - Page is accessible",
            "recommendation": "No action needed",
        })
    
    elif status_code == 301:
        status_info.update({
            "category": "Permanent Redirect",
            "severity": "info",
            "seo_impact": "Neutral - Link equity passes through 301",
            "recommendation": "Ensure redirect chain is minimal",
        })
    
    elif status_code == 302:
        status_info.update({
            "category": "Temporary Redirect",
            "severity": "warning",
            "seo_impact": "May not pass full link equity",
            "recommendation": "Use 301 for permanent redirects",
        })
    
    elif status_code == 404:
        status_info.update({
            "category": "Not Found",
            "severity": "error",
            "seo_impact": "Negative - Page is broken",
            "recommendation": "Fix or redirect to relevant page",
        })
    
    elif 500 <= status_code < 600:
        status_info.update({
            "category": "Server Error",
            "severity": "critical",
            "seo_impact": "Very Negative - May affect entire site",
            "recommendation": "Fix server errors immediately",
        })
    
    else:
        status_info.update({
            "category": "Other",
            "severity": "warning",
            "seo_impact": "Unknown",
            "recommendation": "Investigate status code",
        })
    
    return status_info


async def check_https_security(url: str) -> Dict:
    """
    Check if URL uses HTTPS and validate SSL certificate.
    
    Args:
        url: URL to check.
    
    Returns:
        dict: HTTPS analysis results.
    """
    parsed = urlparse(url)
    uses_https = parsed.scheme == "https"
    
    ssl_valid = False
    ssl_info = {}
    
    if uses_https:
        try:
            async with httpx.AsyncClient(verify=True) as client:
                response = await client.get(url, timeout=10.0)
                ssl_valid = True
                ssl_info = {
                    "valid": True,
                    "protocol": "TLS",
                }
        except httpx.HTTPError:
            ssl_valid = False
            ssl_info = {
                "valid": False,
                "error": "SSL certificate validation failed",
            }
    
    return {
        "uses_https": uses_https,
        "ssl_valid": ssl_valid,
        "ssl_info": ssl_info,
        "score": 100 if (uses_https and ssl_valid) else 0,
        "recommendation": (
            "Good - Using HTTPS with valid certificate"
            if uses_https and ssl_valid
            else "Critical - Switch to HTTPS with valid SSL certificate"
        ),
    }


def detect_redirect_chain(
    url: str,
    redirect_history: List[str],
) -> Dict:
    """
    Detect and analyze redirect chains.
    
    Args:
        url: Final URL.
        redirect_history: List of URLs in redirect chain.
    
    Returns:
        dict: Redirect chain analysis.
    """
    chain_length = len(redirect_history)
    
    issues = []
    warnings = []
    
    if chain_length > 3:
        issues.append(f"Long redirect chain ({chain_length} hops)")
    elif chain_length > 1:
        warnings.append(f"Redirect chain detected ({chain_length} hops)")
    
    return {
        "has_redirects": chain_length > 0,
        "chain_length": chain_length,
        "redirect_chain": redirect_history,
        "issues": issues,
        "warnings": warnings,
        "recommendation": (
            "Minimize redirect chains to 1 hop maximum"
            if chain_length > 1
            else "No action needed"
        ),
    }


def analyze_canonical_tag(
    current_url: str,
    canonical_url: Optional[str],
) -> Dict:
    """
    Analyze canonical tag usage.
    
    Args:
        current_url: Current page URL.
        canonical_url: Canonical URL if present.
    
    Returns:
        dict: Canonical tag analysis.
    """
    warnings = []
    
    if not canonical_url:
        warnings.append("No canonical tag found")
    elif canonical_url != current_url:
        warnings.append("Canonical points to different URL")
    
    return {
        "present": bool(canonical_url),
        "canonical_url": canonical_url,
        "self_referencing": canonical_url == current_url if canonical_url else False,
        "warnings": warnings,
    }


def analyze_robots_directives(
    has_noindex: bool,
    has_nofollow: bool,
) -> Dict:
    """
    Analyze robots meta tag directives.
    
    Args:
        has_noindex: Whether page has noindex directive.
        has_nofollow: Whether page has nofollow directive.
    
    Returns:
        dict: Robots directives analysis.
    """
    warnings = []
    
    if has_noindex:
        warnings.append("Page has noindex directive - will not be indexed by search engines")
    
    if has_nofollow:
        warnings.append("Page has nofollow directive - links will not pass equity")
    
    return {
        "noindex": has_noindex,
        "nofollow": has_nofollow,
        "indexable": not has_noindex,
        "warnings": warnings,
        "recommendation": (
            "Remove noindex/nofollow if you want page indexed"
            if (has_noindex or has_nofollow)
            else "Good - Page is indexable"
        ),
    }


def analyze_structured_data(schema_types: Optional[List[str]]) -> Dict:
    """
    Analyze structured data (Schema.org) presence.
    
    Args:
        schema_types: List of schema types found on page.
    
    Returns:
        dict: Structured data analysis.
    """
    has_schema = bool(schema_types) and len(schema_types) > 0
    
    return {
        "present": has_schema,
        "types": schema_types or [],
        "count": len(schema_types) if schema_types else 0,
        "recommendation": (
            f"Good - Found {len(schema_types)} schema types"
            if has_schema
            else "Consider adding Schema.org structured data for rich snippets"
        ),
    }


def check_mobile_friendly(html: str) -> Dict:
    """
    Check basic mobile-friendliness indicators.
    
    Args:
        html: HTML content.
    
    Returns:
        dict: Mobile-friendliness analysis.
    """
    soup = BeautifulSoup(html, 'lxml')
    
    # Check viewport meta tag
    viewport = soup.find('meta', attrs={'name': 'viewport'})
    has_viewport = bool(viewport)
    
    # Check responsive meta tags
    has_mobile_meta = has_viewport and 'width=device-width' in viewport.get('content', '')
    
    issues = []
    if not has_viewport:
        issues.append("Missing viewport meta tag")
    elif not has_mobile_meta:
        issues.append("Viewport tag doesn't include width=device-width")
    
    return {
        "has_viewport_meta": has_viewport,
        "viewport_content": viewport.get('content') if viewport else None,
        "mobile_friendly": has_mobile_meta,
        "issues": issues,
        "recommendation": (
            "Good - Page has mobile viewport meta tag"
            if has_mobile_meta
            else "Add viewport meta tag: <meta name='viewport' content='width=device-width, initial-scale=1'>"
        ),
    }
