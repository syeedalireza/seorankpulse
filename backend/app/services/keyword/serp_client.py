"""
SERP (Search Engine Results Page) API client.

This module provides integration with SERP APIs for keyword ranking
and search volume data.
"""

from typing import Dict, List, Optional
import httpx

from app.core.config import settings


class SerpAPIClient:
    """
    Client for SERP API (optional service).
    
    Provides keyword ranking and search volume data.
    Note: Requires SERP API subscription.
    """
    
    def __init__(self, api_key: Optional[str] = None):
        """
        Initialize SERP API client.
        
        Args:
            api_key: Optional API key.
        """
        self.api_key = api_key or settings.SERP_API_KEY
        self.base_url = "https://serpapi.com/search"
    
    async def check_keyword_ranking(
        self,
        keyword: str,
        domain: str,
        location: str = "United States",
    ) -> Dict:
        """
        Check ranking position for a keyword.
        
        Args:
            keyword: Keyword to check.
            domain: Domain to find in results.
            location: Geographic location for search.
        
        Returns:
            dict: Ranking information.
        """
        if not self.api_key:
            return {
                "keyword": keyword,
                "domain": domain,
                "position": None,
                "error": "SERP API key not configured",
            }
        
        params = {
            "q": keyword,
            "location": location,
            "api_key": self.api_key,
            "engine": "google",
        }
        
        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(
                    self.base_url,
                    params=params,
                    timeout=30.0,
                )
                
                if response.status_code == 200:
                    data = response.json()
                    organic_results = data.get("organic_results", [])
                    
                    # Find domain in results
                    for i, result in enumerate(organic_results):
                        result_domain = result.get("domain", "")
                        if domain in result_domain:
                            return {
                                "keyword": keyword,
                                "domain": domain,
                                "position": i + 1,
                                "title": result.get("title"),
                                "url": result.get("link"),
                            }
                    
                    return {
                        "keyword": keyword,
                        "domain": domain,
                        "position": None,
                        "message": "Domain not found in top 100 results",
                    }
            
            return {"error": "API request failed"}
        
        except Exception as e:
            return {
                "keyword": keyword,
                "domain": domain,
                "position": None,
                "error": str(e),
            }
    
    async def get_search_volume(self, keyword: str) -> Dict:
        """
        Get search volume data for a keyword.
        
        Note: This typically requires a paid SERP API plan.
        
        Args:
            keyword: Keyword to check.
        
        Returns:
            dict: Search volume data.
        """
        # Placeholder - actual implementation would use SERP API
        # or Google Ads API for accurate volume data
        return {
            "keyword": keyword,
            "monthly_volume": "Not available",
            "competition": "Unknown",
            "note": "Configure SERP API for actual data",
        }


# Global client instance
serp_client = SerpAPIClient()
