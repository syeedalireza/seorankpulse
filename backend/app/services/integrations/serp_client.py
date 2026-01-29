"""
SERP (Search Engine Results Page) tracking using SerpAPI.

Track keyword rankings in Google, Bing, etc.
"""

from typing import Dict, List, Optional
import httpx
from datetime import datetime


class SerpAPIClient:
    """
    Track search engine rankings using SerpAPI.
    
    Features:
    - Keyword position tracking
    - Competitor monitoring
    - SERP feature detection (featured snippets, etc.)
    - Historical ranking data
    """
    
    def __init__(self, api_key: str):
        """
        Initialize SERP API client.
        
        Args:
            api_key: SerpAPI key.
        """
        self.api_key = api_key
        self.base_url = "https://serpapi.com/search"
        self.client = httpx.AsyncClient(timeout=30.0)
    
    async def check_rankings(
        self,
        keywords: List[str],
        domain: str,
        location: str = "United States",
        engine: str = "google",
        num_results: int = 100
    ) -> List[Dict]:
        """
        Check rankings for keywords.
        
        Args:
            keywords: List of keywords to check.
            domain: Your domain to find in results.
            location: Geographic location for search.
            engine: Search engine (google, bing, etc.).
            num_results: Number of results to check.
        
        Returns:
            list: Ranking data for each keyword.
        """
        results = []
        
        for keyword in keywords:
            ranking = await self.get_keyword_ranking(
                keyword=keyword,
                domain=domain,
                location=location,
                engine=engine,
                num_results=num_results
            )
            results.append(ranking)
        
        return results
    
    async def get_keyword_ranking(
        self,
        keyword: str,
        domain: str,
        location: str = "United States",
        engine: str = "google",
        num_results: int = 100
    ) -> Dict:
        """
        Get ranking for a single keyword.
        
        Args:
            keyword: Keyword to check.
            domain: Domain to find.
            location: Search location.
            engine: Search engine.
            num_results: Results to check.
        
        Returns:
            dict: Ranking information.
        """
        try:
            params = {
                'api_key': self.api_key,
                'q': keyword,
                'location': location,
                'engine': engine,
                'num': num_results,
            }
            
            response = await self.client.get(self.base_url, params=params)
            data = response.json()
            
            # Find domain in organic results
            organic_results = data.get('organic_results', [])
            
            position = None
            url = None
            title = None
            snippet = None
            
            for idx, result in enumerate(organic_results, 1):
                result_domain = self._extract_domain(result.get('link', ''))
                
                if domain in result_domain:
                    position = idx
                    url = result.get('link')
                    title = result.get('title')
                    snippet = result.get('snippet')
                    break
            
            # Check for SERP features
            serp_features = self._detect_serp_features(data)
            
            return {
                'keyword': keyword,
                'domain': domain,
                'position': position,
                'url': url,
                'title': title,
                'snippet': snippet,
                'location': location,
                'engine': engine,
                'checked_at': datetime.utcnow().isoformat(),
                'serp_features': serp_features,
                'found': position is not None,
            }
        
        except Exception as e:
            return {
                'keyword': keyword,
                'domain': domain,
                'error': str(e),
                'found': False,
            }
    
    def _extract_domain(self, url: str) -> str:
        """Extract domain from URL."""
        from urllib.parse import urlparse
        parsed = urlparse(url)
        return parsed.netloc.replace('www.', '')
    
    def _detect_serp_features(self, serp_data: Dict) -> Dict:
        """
        Detect SERP features in results.
        
        Args:
            serp_data: SerpAPI response data.
        
        Returns:
            dict: Detected SERP features.
        """
        features = {
            'featured_snippet': bool(serp_data.get('answer_box')),
            'knowledge_graph': bool(serp_data.get('knowledge_graph')),
            'local_pack': bool(serp_data.get('local_results')),
            'people_also_ask': bool(serp_data.get('related_questions')),
            'image_pack': bool(serp_data.get('inline_images')),
            'video_results': bool(serp_data.get('inline_videos')),
            'shopping_results': bool(serp_data.get('shopping_results')),
            'top_stories': bool(serp_data.get('top_stories')),
        }
        
        return features
    
    async def track_competitors(
        self,
        keyword: str,
        competitors: List[str],
        location: str = "United States"
    ) -> Dict:
        """
        Track competitor rankings for a keyword.
        
        Args:
            keyword: Keyword to check.
            competitors: List of competitor domains.
            location: Search location.
        
        Returns:
            dict: Competitor ranking data.
        """
        try:
            params = {
                'api_key': self.api_key,
                'q': keyword,
                'location': location,
                'num': 100,
            }
            
            response = await self.client.get(self.base_url, params=params)
            data = response.json()
            
            organic_results = data.get('organic_results', [])
            
            competitor_rankings = []
            
            for comp_domain in competitors:
                for idx, result in enumerate(organic_results, 1):
                    result_domain = self._extract_domain(result.get('link', ''))
                    
                    if comp_domain in result_domain:
                        competitor_rankings.append({
                            'domain': comp_domain,
                            'position': idx,
                            'url': result.get('link'),
                            'title': result.get('title'),
                        })
                        break
            
            return {
                'keyword': keyword,
                'location': location,
                'competitors': competitor_rankings,
                'checked_at': datetime.utcnow().isoformat(),
            }
        
        except Exception as e:
            return {
                'keyword': keyword,
                'error': str(e),
            }
    
    async def get_serp_overview(
        self,
        keyword: str,
        location: str = "United States"
    ) -> Dict:
        """
        Get complete SERP overview for a keyword.
        
        Args:
            keyword: Keyword to analyze.
            location: Search location.
        
        Returns:
            dict: Complete SERP data.
        """
        try:
            params = {
                'api_key': self.api_key,
                'q': keyword,
                'location': location,
                'num': 100,
            }
            
            response = await self.client.get(self.base_url, params=params)
            data = response.json()
            
            organic_results = data.get('organic_results', [])
            
            return {
                'keyword': keyword,
                'location': location,
                'total_results': len(organic_results),
                'top_10_domains': [
                    {
                        'position': idx + 1,
                        'domain': self._extract_domain(result.get('link', '')),
                        'title': result.get('title'),
                        'url': result.get('link'),
                    }
                    for idx, result in enumerate(organic_results[:10])
                ],
                'serp_features': self._detect_serp_features(data),
                'checked_at': datetime.utcnow().isoformat(),
            }
        
        except Exception as e:
            return {
                'keyword': keyword,
                'error': str(e),
            }
    
    async def close(self):
        """Close HTTP client."""
        await self.client.aclose()


class RankingTracker:
    """
    Track ranking changes over time.
    
    Stores historical data and detects:
    - Ranking improvements/drops
    - New rankings
    - Lost rankings
    - Volatility
    """
    
    def __init__(self):
        """Initialize ranking tracker."""
        self.historical_data = []
    
    def add_ranking_data(
        self,
        keyword: str,
        position: Optional[int],
        timestamp: datetime
    ):
        """
        Add ranking data point.
        
        Args:
            keyword: Keyword.
            position: Current position (None if not ranking).
            timestamp: When this was checked.
        """
        self.historical_data.append({
            'keyword': keyword,
            'position': position,
            'timestamp': timestamp,
        })
    
    def calculate_changes(
        self,
        keyword: str,
        days_back: int = 7
    ) -> Dict:
        """
        Calculate ranking changes for a keyword.
        
        Args:
            keyword: Keyword to analyze.
            days_back: How many days to look back.
        
        Returns:
            dict: Change analysis.
        """
        # Filter data for this keyword
        keyword_data = [
            d for d in self.historical_data
            if d['keyword'] == keyword
        ]
        
        if len(keyword_data) < 2:
            return {
                'keyword': keyword,
                'error': 'Insufficient historical data',
            }
        
        # Sort by timestamp
        keyword_data.sort(key=lambda x: x['timestamp'])
        
        latest = keyword_data[-1]
        previous = keyword_data[-2]
        
        latest_pos = latest['position']
        previous_pos = previous['position']
        
        # Calculate change
        if latest_pos is None and previous_pos is None:
            change = 0
            status = 'not_ranking'
        elif latest_pos is None:
            change = -(previous_pos + 100)  # Lost ranking
            status = 'lost'
        elif previous_pos is None:
            change = 100 - latest_pos  # New ranking
            status = 'new'
        else:
            change = previous_pos - latest_pos  # Positive = improvement
            if change > 0:
                status = 'improved'
            elif change < 0:
                status = 'dropped'
            else:
                status = 'stable'
        
        return {
            'keyword': keyword,
            'current_position': latest_pos,
            'previous_position': previous_pos,
            'change': change,
            'status': status,
            'checked_at': latest['timestamp'].isoformat(),
        }


async def check_keyword_rankings(
    keywords: List[str],
    domain: str,
    api_key: str,
    location: str = "United States"
) -> List[Dict]:
    """
    Convenience function to check keyword rankings.
    
    Args:
        keywords: Keywords to check.
        domain: Your domain.
        api_key: SerpAPI key.
        location: Search location.
    
    Returns:
        list: Ranking data.
    """
    client = SerpAPIClient(api_key=api_key)
    try:
        return await client.check_rankings(keywords, domain, location)
    finally:
        await client.close()
