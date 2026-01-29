"""
Content gap analysis - find topics competitors rank for but you don't.
"""

from typing import Dict, List, Set


class ContentGapFinder:
    """
    Identify content gaps between your site and competitors.
    
    Finds:
    - Topics competitors cover that you don't
    - Keywords they rank for
    - Pages they have that you lack
    - Content opportunities
    """
    
    def find_missing_topics(
        self,
        your_pages: List[Dict],
        competitor_pages: List[Dict]
    ) -> Dict:
        """
        Find topics covered by competitors but not by you.
        
        Args:
            your_pages: Your pages data.
            competitor_pages: Competitor pages data.
        
        Returns:
            dict: Missing topics and opportunities.
        """
        # Extract topics from titles and H1s
        your_topics = self._extract_topics(your_pages)
        competitor_topics = self._extract_topics(competitor_pages)
        
        # Find gaps
        missing_topics = competitor_topics - your_topics
        
        return {
            'your_topic_count': len(your_topics),
            'competitor_topic_count': len(competitor_topics),
            'missing_topics': sorted(list(missing_topics)),
            'coverage_percentage': round(
                len(your_topics) / len(competitor_topics) * 100, 2
            ) if competitor_topics else 100,
        }
    
    def _extract_topics(self, pages: List[Dict]) -> Set[str]:
        """
        Extract topics from pages.
        
        Args:
            pages: List of page data.
        
        Returns:
            set: Set of topics (keywords from titles and H1s).
        """
        topics = set()
        
        for page in pages:
            # Extract from title
            title = page.get('title', '')
            if title:
                # Simple tokenization
                words = title.lower().split()
                # Remove common words
                stop_words = {'the', 'a', 'an', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for'}
                significant_words = [w for w in words if w not in stop_words and len(w) > 3]
                topics.update(significant_words)
            
            # Extract from H1
            h1_tags = page.get('h1_tags', [])
            for h1 in h1_tags:
                words = h1.lower().split()
                significant_words = [w for w in words if len(w) > 3]
                topics.update(significant_words)
        
        return topics
    
    def find_missing_page_types(
        self,
        your_pages: List[Dict],
        competitor_pages: List[Dict]
    ) -> Dict:
        """
        Identify types of pages competitors have that you don't.
        
        Args:
            your_pages: Your pages.
            competitor_pages: Competitor pages.
        
        Returns:
            dict: Missing page types.
        """
        your_types = self._classify_page_types(your_pages)
        competitor_types = self._classify_page_types(competitor_pages)
        
        missing_types = set(competitor_types.keys()) - set(your_types.keys())
        
        return {
            'your_page_types': list(your_types.keys()),
            'competitor_page_types': list(competitor_types.keys()),
            'missing_page_types': list(missing_types),
            'recommendations': [
                f"Consider adding {page_type} pages"
                for page_type in missing_types
            ],
        }
    
    def _classify_page_types(self, pages: List[Dict]) -> Dict[str, int]:
        """
        Classify pages into types.
        
        Args:
            pages: List of pages.
        
        Returns:
            dict: Page type counts.
        """
        types = {}
        
        for page in pages:
            url = page.get('url', '').lower()
            
            # Simple classification based on URL patterns
            if '/blog/' in url or '/article/' in url:
                page_type = 'blog'
            elif '/product/' in url or '/shop/' in url:
                page_type = 'product'
            elif '/category/' in url:
                page_type = 'category'
            elif '/about' in url:
                page_type = 'about'
            elif '/contact' in url:
                page_type = 'contact'
            elif '/faq' in url or '/help/' in url:
                page_type = 'support'
            else:
                page_type = 'other'
            
            types[page_type] = types.get(page_type, 0) + 1
        
        return types
