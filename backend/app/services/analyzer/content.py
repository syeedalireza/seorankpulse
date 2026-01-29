"""
Content analysis utilities.

This module provides functions for analyzing text content quality,
readability, and SEO-relevant metrics.
"""

import re
from typing import Dict, List
from collections import Counter

import nltk
from bs4 import BeautifulSoup


def calculate_readability_score(text: str) -> Dict[str, float]:
    """
    Calculate Flesch Reading Ease and other readability metrics.
    
    Flesch Reading Ease formula:
    206.835 - 1.015 * (words/sentences) - 84.6 * (syllables/words)
    
    Args:
        text: The text to analyze.
    
    Returns:
        dict: Readability scores and interpretation.
    """
    # Clean text
    text = re.sub(r'\s+', ' ', text).strip()
    
    if not text:
        return {
            "flesch_reading_ease": 0.0,
            "flesch_kincaid_grade": 0.0,
            "interpretation": "No content",
        }
    
    # Count sentences
    sentences = re.split(r'[.!?]+', text)
    sentences = [s.strip() for s in sentences if s.strip()]
    num_sentences = len(sentences) or 1
    
    # Count words
    words = text.split()
    num_words = len(words) or 1
    
    # Count syllables (simplified approximation)
    num_syllables = sum(count_syllables(word) for word in words)
    
    # Calculate Flesch Reading Ease
    flesch = 206.835 - 1.015 * (num_words / num_sentences) - 84.6 * (num_syllables / num_words)
    
    # Calculate Flesch-Kincaid Grade Level
    fk_grade = 0.39 * (num_words / num_sentences) + 11.8 * (num_syllables / num_words) - 15.59
    
    # Interpret score
    if flesch >= 90:
        interpretation = "Very Easy"
    elif flesch >= 80:
        interpretation = "Easy"
    elif flesch >= 70:
        interpretation = "Fairly Easy"
    elif flesch >= 60:
        interpretation = "Standard"
    elif flesch >= 50:
        interpretation = "Fairly Difficult"
    elif flesch >= 30:
        interpretation = "Difficult"
    else:
        interpretation = "Very Difficult"
    
    return {
        "flesch_reading_ease": round(flesch, 2),
        "flesch_kincaid_grade": round(fk_grade, 2),
        "interpretation": interpretation,
        "total_words": num_words,
        "total_sentences": num_sentences,
        "avg_words_per_sentence": round(num_words / num_sentences, 2),
    }


def count_syllables(word: str) -> int:
    """
    Count syllables in a word (simplified algorithm).
    
    Args:
        word: The word to count syllables for.
    
    Returns:
        int: Estimated syllable count.
    """
    word = word.lower().strip()
    vowels = "aeiouy"
    count = 0
    previous_was_vowel = False
    
    for char in word:
        is_vowel = char in vowels
        if is_vowel and not previous_was_vowel:
            count += 1
        previous_was_vowel = is_vowel
    
    # Adjust for silent 'e'
    if word.endswith('e'):
        count -= 1
    
    # Ensure at least one syllable
    if count == 0:
        count = 1
    
    return count


def extract_keywords(text: str, top_n: int = 10) -> List[Dict]:
    """
    Extract top keywords from text using TF-IDF-like approach.
    
    Args:
        text: Text to analyze.
        top_n: Number of top keywords to return.
    
    Returns:
        list: List of keywords with frequency and density.
    """
    # Clean and tokenize
    text_lower = text.lower()
    words = re.findall(r'\b[a-z]{3,}\b', text_lower)
    
    # Common stop words
    stop_words = {
        'the', 'a', 'an', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for',
        'of', 'with', 'by', 'from', 'as', 'is', 'was', 'are', 'were', 'been',
        'be', 'have', 'has', 'had', 'do', 'does', 'did', 'will', 'would',
        'should', 'could', 'may', 'might', 'can', 'this', 'that', 'these',
        'those', 'it', 'its', 'they', 'them', 'their', 'what', 'which',
    }
    
    # Filter stop words
    filtered_words = [w for w in words if w not in stop_words]
    
    # Count frequencies
    word_counts = Counter(filtered_words)
    total_words = len(filtered_words)
    
    # Calculate density
    keywords = []
    for word, count in word_counts.most_common(top_n):
        density = (count / total_words * 100) if total_words > 0 else 0
        keywords.append({
            "keyword": word,
            "count": count,
            "density_percent": round(density, 2),
        })
    
    return keywords


def calculate_content_metrics(html: str, text: str) -> Dict:
    """
    Calculate various content quality metrics.
    
    Args:
        html: Raw HTML content.
        text: Extracted text content.
    
    Returns:
        dict: Content metrics.
    """
    html_size = len(html)
    text_size = len(text)
    
    # Word count
    words = text.split()
    word_count = len(words)
    
    # Character count
    char_count = len(text)
    
    # Sentence count
    sentences = re.split(r'[.!?]+', text)
    sentence_count = len([s for s in sentences if s.strip()])
    
    # Paragraph count (from HTML)
    soup = BeautifulSoup(html, 'lxml')
    paragraphs = soup.find_all('p')
    paragraph_count = len(paragraphs)
    
    # Text to HTML ratio
    text_to_html_ratio = (text_size / html_size * 100) if html_size > 0 else 0
    
    # Average word length
    avg_word_length = (
        sum(len(word) for word in words) / word_count
        if word_count > 0
        else 0
    )
    
    return {
        "word_count": word_count,
        "character_count": char_count,
        "sentence_count": sentence_count,
        "paragraph_count": paragraph_count,
        "avg_words_per_sentence": round(word_count / sentence_count, 2) if sentence_count > 0 else 0,
        "avg_word_length": round(avg_word_length, 2),
        "text_to_html_ratio": round(text_to_html_ratio, 2),
        "html_size_bytes": html_size,
        "text_size_bytes": text_size,
    }


def analyze_keyword_usage(text: str, target_keyword: str) -> Dict:
    """
    Analyze how a target keyword is used in the content.
    
    Args:
        text: Content text.
        target_keyword: Keyword to analyze.
    
    Returns:
        dict: Keyword usage analysis.
    """
    text_lower = text.lower()
    keyword_lower = target_keyword.lower()
    
    # Count occurrences
    count = text_lower.count(keyword_lower)
    
    # Calculate density
    words = text.split()
    total_words = len(words)
    density = (count / total_words * 100) if total_words > 0 else 0
    
    # Find positions (for prominence analysis)
    positions = []
    start = 0
    while True:
        pos = text_lower.find(keyword_lower, start)
        if pos == -1:
            break
        positions.append(pos)
        start = pos + 1
    
    # Check if in first paragraph (important for SEO)
    first_300_chars = text_lower[:300]
    in_first_paragraph = keyword_lower in first_300_chars
    
    return {
        "keyword": target_keyword,
        "count": count,
        "density_percent": round(density, 2),
        "in_first_paragraph": in_first_paragraph,
        "positions": positions[:5],  # First 5 positions
        "optimal_density": 1.0 <= density <= 3.0,
    }
