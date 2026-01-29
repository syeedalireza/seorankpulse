"""
Keyword research and tracking utilities.
"""

from typing import Dict, List
import httpx


async def get_google_suggestions(keyword: str) -> List[str]:
    """
    Get Google autocomplete suggestions for a keyword.
    
    This provides long-tail keyword ideas.
    
    Args:
        keyword: Base keyword to get suggestions for.
    
    Returns:
        list: List of suggested keywords.
    """
    url = "http://suggestqueries.google.com/complete/search"
    
    params = {
        "client": "firefox",
        "q": keyword,
    }
    
    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(url, params=params, timeout=10.0)
            
            if response.status_code == 200:
                data = response.json()
                # Google returns suggestions in second element
                if len(data) > 1 and isinstance(data[1], list):
                    return data[1]
        
        return []
    except Exception:
        return []


async def estimate_keyword_difficulty(keyword: str) -> Dict:
    """
    Estimate keyword difficulty (simplified version).
    
    In production, this would use SERP API or similar service.
    
    Args:
        keyword: Keyword to analyze.
    
    Returns:
        dict: Difficulty estimation.
    """
    # Simplified estimation based on keyword characteristics
    words = keyword.split()
    word_count = len(words)
    
    # Long-tail keywords are generally easier
    if word_count >= 4:
        difficulty = "Easy"
        score = 30
    elif word_count == 3:
        difficulty = "Medium"
        score = 50
    elif word_count == 2:
        difficulty = "Hard"
        score = 70
    else:
        difficulty = "Very Hard"
        score = 90
    
    return {
        "keyword": keyword,
        "difficulty": difficulty,
        "difficulty_score": score,
        "word_count": word_count,
        "type": "long-tail" if word_count >= 3 else "short-tail",
    }


async def generate_keyword_variations(keyword: str) -> List[str]:
    """
    Generate keyword variations.
    
    Args:
        keyword: Base keyword.
    
    Returns:
        list: Keyword variations.
    """
    variations = [keyword]
    
    # Get Google suggestions
    suggestions = await get_google_suggestions(keyword)
    variations.extend(suggestions[:10])
    
    # Add common question formats
    question_words = ["what is", "how to", "why", "when", "where"]
    for qw in question_words:
        variations.append(f"{qw} {keyword}")
    
    # Remove duplicates while preserving order
    seen = set()
    unique_variations = []
    for v in variations:
        if v.lower() not in seen:
            seen.add(v.lower())
            unique_variations.append(v)
    
    return unique_variations[:20]  # Limit to 20 variations
