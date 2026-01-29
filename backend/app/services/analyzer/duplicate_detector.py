"""
Duplicate and near-duplicate content detection using SimHash.

This module detects similar and duplicate content across pages
to identify SEO issues like content cannibalization.
"""

from typing import Dict, List, Tuple, Set
import hashlib
import re
from collections import defaultdict
from simhash import Simhash, SimhashIndex


class DuplicateContentDetector:
    """
    Detect duplicate and near-duplicate content using SimHash algorithm.
    
    SimHash is a locality-sensitive hashing technique that allows
    finding similar documents efficiently.
    """
    
    def __init__(self, similarity_threshold: int = 3):
        """
        Initialize duplicate detector.
        
        Args:
            similarity_threshold: Maximum Hamming distance for near-duplicates.
                                 Lower values = more strict matching.
                                 Typical range: 0-10 (3 is recommended).
        """
        self.similarity_threshold = similarity_threshold
        self.simhash_index = None
        self.page_hashes = {}
    
    def compute_simhash(self, text: str) -> Simhash:
        """
        Compute SimHash for text content.
        
        Args:
            text: Text content to hash.
        
        Returns:
            Simhash: SimHash object.
        """
        # Normalize text
        text = self._normalize_text(text)
        
        # Create simhash with 4-grams (groups of 4 characters)
        return Simhash(text, f=64, reg=r'\w+')
    
    def _normalize_text(self, text: str) -> str:
        """
        Normalize text for comparison.
        
        Args:
            text: Original text.
        
        Returns:
            str: Normalized text.
        """
        # Convert to lowercase
        text = text.lower()
        
        # Remove extra whitespace
        text = re.sub(r'\s+', ' ', text).strip()
        
        # Remove common navigation/footer text patterns
        # (customize based on your needs)
        patterns_to_remove = [
            r'copyright \d{4}',
            r'all rights reserved',
            r'privacy policy',
            r'terms of service',
            r'cookie policy',
        ]
        
        for pattern in patterns_to_remove:
            text = re.sub(pattern, '', text, flags=re.IGNORECASE)
        
        return text
    
    def build_index(self, pages: List[Dict]) -> None:
        """
        Build SimHash index from pages.
        
        Args:
            pages: List of page dictionaries with 'url' and content.
        """
        self.page_hashes = {}
        data = []
        
        for page in pages:
            url = page.get('url', '')
            
            # Extract text content
            # Combine title, meta description, and text for analysis
            parts = []
            
            if page.get('title'):
                parts.append(page['title'])
            
            if page.get('meta_description'):
                parts.append(page['meta_description'])
            
            # Get H1-H3 headings
            for h_tag in ['h1_tags', 'h2_tags', 'h3_tags']:
                if page.get(h_tag):
                    parts.extend(page[h_tag])
            
            # Combine all text
            text = ' '.join(parts)
            
            if text.strip():
                simhash = self.compute_simhash(text)
                self.page_hashes[url] = simhash.value
                data.append((url, simhash))
        
        # Build index for fast similarity search
        if data:
            self.simhash_index = SimhashIndex(
                data,
                k=self.similarity_threshold
            )
    
    def find_duplicates(self) -> List[Dict]:
        """
        Find all duplicate and near-duplicate pages.
        
        Returns:
            list: Groups of duplicate/similar pages.
        """
        if not self.simhash_index:
            return []
        
        duplicate_groups = defaultdict(list)
        processed = set()
        
        for url, hash_value in self.page_hashes.items():
            if url in processed:
                continue
            
            # Find similar pages
            simhash_obj = Simhash(hash_value, f=64)
            similar_urls = self.simhash_index.get_near_dups(simhash_obj)
            
            if len(similar_urls) > 1:
                # Create a group
                group_id = min(similar_urls)  # Use lexicographically smallest URL as ID
                duplicate_groups[group_id].extend(similar_urls)
                processed.update(similar_urls)
        
        # Convert to list format
        results = []
        for group_id, urls in duplicate_groups.items():
            # Remove duplicates and sort
            unique_urls = sorted(set(urls))
            
            if len(unique_urls) > 1:
                results.append({
                    'group_id': group_id,
                    'count': len(unique_urls),
                    'urls': unique_urls,
                    'similarity': 'high',  # Based on threshold
                })
        
        return results
    
    def compare_pages(self, url1: str, url2: str) -> Dict:
        """
        Compare two specific pages for similarity.
        
        Args:
            url1: First URL.
            url2: Second URL.
        
        Returns:
            dict: Similarity analysis.
        """
        if url1 not in self.page_hashes or url2 not in self.page_hashes:
            return {
                'error': 'One or both URLs not found in index',
            }
        
        hash1 = Simhash(self.page_hashes[url1], f=64)
        hash2 = Simhash(self.page_hashes[url2], f=64)
        
        distance = hash1.distance(hash2)
        
        # Calculate similarity percentage (approximate)
        # Lower distance = higher similarity
        similarity_pct = max(0, (64 - distance) / 64 * 100)
        
        is_duplicate = distance <= self.similarity_threshold
        
        return {
            'url1': url1,
            'url2': url2,
            'hamming_distance': distance,
            'similarity_percentage': round(similarity_pct, 2),
            'is_duplicate': is_duplicate,
            'is_near_duplicate': distance <= self.similarity_threshold * 2,
        }
    
    def detect_exact_duplicates(self, pages: List[Dict]) -> List[Dict]:
        """
        Detect pages with exactly identical content using MD5 hashing.
        
        Args:
            pages: List of page dictionaries.
        
        Returns:
            list: Groups of exact duplicate pages.
        """
        content_hashes = defaultdict(list)
        
        for page in pages:
            url = page.get('url', '')
            
            # Create content string
            parts = []
            for field in ['title', 'meta_description']:
                if page.get(field):
                    parts.append(page[field])
            
            content = ' '.join(parts).strip()
            
            if content:
                # Create MD5 hash
                content_hash = hashlib.md5(content.encode()).hexdigest()
                content_hashes[content_hash].append(url)
        
        # Find groups with duplicates
        duplicates = []
        for content_hash, urls in content_hashes.items():
            if len(urls) > 1:
                duplicates.append({
                    'content_hash': content_hash,
                    'count': len(urls),
                    'urls': sorted(urls),
                    'type': 'exact_duplicate',
                })
        
        return duplicates


def detect_duplicates(pages: List[Dict], similarity_threshold: int = 3) -> Dict:
    """
    Convenience function to detect duplicate content.
    
    Args:
        pages: List of page dictionaries.
        similarity_threshold: SimHash distance threshold.
    
    Returns:
        dict: Duplicate detection results.
    """
    detector = DuplicateContentDetector(similarity_threshold=similarity_threshold)
    
    # Build index
    detector.build_index(pages)
    
    # Find duplicates
    near_duplicates = detector.find_duplicates()
    exact_duplicates = detector.detect_exact_duplicates(pages)
    
    return {
        'total_pages_analyzed': len(pages),
        'exact_duplicate_groups': len(exact_duplicates),
        'near_duplicate_groups': len(near_duplicates),
        'exact_duplicates': exact_duplicates,
        'near_duplicates': near_duplicates,
        'total_affected_pages': sum(d['count'] for d in exact_duplicates + near_duplicates),
    }


def find_cannibalization_issues(pages: List[Dict], target_keywords: List[str]) -> List[Dict]:
    """
    Find keyword cannibalization issues.
    
    Identifies multiple pages targeting the same keywords.
    
    Args:
        pages: List of page dictionaries.
        target_keywords: List of keywords to check for cannibalization.
    
    Returns:
        list: Cannibalization issues found.
    """
    issues = []
    
    for keyword in target_keywords:
        keyword_lower = keyword.lower()
        matching_pages = []
        
        for page in pages:
            # Check title and meta description
            title = page.get('title', '').lower()
            desc = page.get('meta_description', '').lower()
            h1_tags = [h.lower() for h in page.get('h1_tags', [])]
            
            # Check if keyword appears in key places
            if (keyword_lower in title or 
                keyword_lower in desc or 
                any(keyword_lower in h1 for h1 in h1_tags)):
                matching_pages.append(page.get('url', ''))
        
        if len(matching_pages) > 1:
            issues.append({
                'keyword': keyword,
                'page_count': len(matching_pages),
                'urls': matching_pages,
                'severity': 'high' if len(matching_pages) > 3 else 'medium',
                'recommendation': f"Consolidate content targeting '{keyword}' or differentiate intent",
            })
    
    return issues
