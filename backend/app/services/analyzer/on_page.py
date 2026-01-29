"""
On-page SEO analysis utilities.

This module provides functions for analyzing on-page SEO elements
like meta tags, headings, images, etc.
"""

from typing import Dict, List, Tuple
from bs4 import BeautifulSoup


def analyze_title_tag(title: str) -> Dict:
    """
    Analyze title tag for SEO best practices.
    
    Args:
        title: Title tag content.
    
    Returns:
        dict: Analysis results with issues and score.
    """
    issues = []
    warnings = []
    score = 100
    
    if not title:
        issues.append("Missing title tag")
        score = 0
    else:
        length = len(title)
        
        if length < 30:
            issues.append(f"Title too short ({length} chars, recommended 50-60)")
            score -= 20
        elif length < 50:
            warnings.append(f"Title could be longer ({length} chars)")
            score -= 5
        elif length > 60:
            warnings.append(f"Title too long ({length} chars, may be truncated)")
            score -= 10
        
        # Check for keyword stuffing (repeated words)
        words = title.lower().split()
        word_counts = {}
        for word in words:
            if len(word) > 3:  # Ignore short words
                word_counts[word] = word_counts.get(word, 0) + 1
        
        repeated = [word for word, count in word_counts.items() if count > 2]
        if repeated:
            warnings.append(f"Possible keyword stuffing: {', '.join(repeated)}")
            score -= 10
    
    return {
        "present": bool(title),
        "length": len(title) if title else 0,
        "optimal_length": 50 <= len(title or "") <= 60,
        "score": max(0, score),
        "issues": issues,
        "warnings": warnings,
    }


def analyze_meta_description(description: str) -> Dict:
    """
    Analyze meta description for SEO best practices.
    
    Args:
        description: Meta description content.
    
    Returns:
        dict: Analysis results.
    """
    issues = []
    warnings = []
    score = 100
    
    if not description:
        issues.append("Missing meta description")
        score = 0
    else:
        length = len(description)
        
        if length < 120:
            warnings.append(f"Description too short ({length} chars, recommended 150-160)")
            score -= 15
        elif length > 160:
            warnings.append(f"Description too long ({length} chars, may be truncated)")
            score -= 10
    
    return {
        "present": bool(description),
        "length": len(description) if description else 0,
        "optimal_length": 120 <= len(description or "") <= 160,
        "score": max(0, score),
        "issues": issues,
        "warnings": warnings,
    }


def analyze_headings(h1_tags: List[str], h2_tags: List[str], h3_tags: List[str]) -> Dict:
    """
    Analyze heading structure for SEO best practices.
    
    Args:
        h1_tags: List of H1 tag contents.
        h2_tags: List of H2 tag contents.
        h3_tags: List of H3 tag contents.
    
    Returns:
        dict: Heading analysis results.
    """
    issues = []
    warnings = []
    score = 100
    
    h1_count = len(h1_tags) if h1_tags else 0
    h2_count = len(h2_tags) if h2_tags else 0
    h3_count = len(h3_tags) if h3_tags else 0
    
    # Check H1
    if h1_count == 0:
        issues.append("Missing H1 tag")
        score -= 25
    elif h1_count > 1:
        warnings.append(f"Multiple H1 tags ({h1_count} found, recommended: 1)")
        score -= 10
    else:
        h1_length = len(h1_tags[0])
        if h1_length < 20:
            warnings.append(f"H1 too short ({h1_length} chars)")
            score -= 5
        elif h1_length > 70:
            warnings.append(f"H1 too long ({h1_length} chars)")
            score -= 5
    
    # Check heading hierarchy
    if h3_count > 0 and h2_count == 0:
        warnings.append("H3 tags present but no H2 tags (poor hierarchy)")
        score -= 5
    
    return {
        "h1_count": h1_count,
        "h2_count": h2_count,
        "h3_count": h3_count,
        "h1_optimal": h1_count == 1,
        "has_proper_hierarchy": h1_count >= 1 and (h3_count == 0 or h2_count > 0),
        "score": max(0, score),
        "issues": issues,
        "warnings": warnings,
    }


def analyze_images(images_count: int, images_without_alt: int) -> Dict:
    """
    Analyze image optimization for SEO.
    
    Args:
        images_count: Total number of images.
        images_without_alt: Number of images without alt tags.
    
    Returns:
        dict: Image analysis results.
    """
    issues = []
    warnings = []
    score = 100
    
    if images_count > 0:
        alt_coverage = ((images_count - images_without_alt) / images_count) * 100
        
        if images_without_alt > 0:
            if alt_coverage < 50:
                issues.append(f"{images_without_alt} images missing alt tags (critical)")
                score -= 30
            else:
                warnings.append(f"{images_without_alt} images missing alt tags")
                score -= images_without_alt * 2  # 2 points per image
    
    return {
        "total_images": images_count,
        "images_with_alt": images_count - images_without_alt,
        "images_without_alt": images_without_alt,
        "alt_coverage_percent": round(
            ((images_count - images_without_alt) / images_count * 100)
            if images_count > 0
            else 100,
            2
        ),
        "score": max(0, score),
        "issues": issues,
        "warnings": warnings,
    }


def analyze_internal_links(internal_count: int, external_count: int) -> Dict:
    """
    Analyze internal and external linking patterns.
    
    Args:
        internal_count: Number of internal links.
        external_count: Number of external links.
    
    Returns:
        dict: Link analysis results.
    """
    warnings = []
    score = 100
    
    total = internal_count + external_count
    
    if internal_count == 0 and total > 0:
        warnings.append("No internal links found (poor internal linking)")
        score -= 15
    
    if total == 0:
        warnings.append("No links found on page")
        score -= 10
    
    # Calculate ratio
    internal_ratio = (internal_count / total * 100) if total > 0 else 0
    
    if internal_ratio < 30 and total > 5:
        warnings.append("Low internal linking ratio (< 30%)")
        score -= 10
    
    return {
        "internal_links": internal_count,
        "external_links": external_count,
        "total_links": total,
        "internal_ratio_percent": round(internal_ratio, 2),
        "score": max(0, score),
        "warnings": warnings,
    }


def calculate_overall_seo_score(
    title_score: int,
    meta_score: int,
    headings_score: int,
    images_score: int,
    links_score: int,
    content_score: int = 100,
) -> Tuple[int, str]:
    """
    Calculate overall SEO score from individual component scores.
    
    Weights are assigned based on SEO importance.
    
    Args:
        title_score: Title tag score (0-100).
        meta_score: Meta description score (0-100).
        headings_score: Headings structure score (0-100).
        images_score: Images optimization score (0-100).
        links_score: Internal linking score (0-100).
        content_score: Content quality score (0-100).
    
    Returns:
        tuple: (overall_score, grade)
    """
    # Weighted average
    weights = {
        "title": 0.25,
        "meta": 0.15,
        "headings": 0.20,
        "images": 0.15,
        "links": 0.15,
        "content": 0.10,
    }
    
    weighted_score = (
        title_score * weights["title"] +
        meta_score * weights["meta"] +
        headings_score * weights["headings"] +
        images_score * weights["images"] +
        links_score * weights["links"] +
        content_score * weights["content"]
    )
    
    overall_score = int(weighted_score)
    
    # Assign grade
    if overall_score >= 90:
        grade = "A+"
    elif overall_score >= 80:
        grade = "A"
    elif overall_score >= 70:
        grade = "B"
    elif overall_score >= 60:
        grade = "C"
    elif overall_score >= 50:
        grade = "D"
    else:
        grade = "F"
    
    return overall_score, grade
