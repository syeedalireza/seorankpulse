"""
Google Search Console API client.

This module provides integration with Google Search Console API
for URL inspection, indexing status, and search analytics data.
"""

from typing import Dict, List, Optional
from datetime import datetime, timedelta
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError


class GoogleSearchConsoleClient:
    """
    Client for Google Search Console API.
    
    Provides access to:
    - URL Inspection API
    - Search Analytics
    - Sitemap data
    - Index coverage
    """
    
    def __init__(self, credentials: Credentials):
        """
        Initialize GSC client.
        
        Args:
            credentials: Google OAuth2 credentials.
        """
        self.credentials = credentials
        self.service = build('searchconsole', 'v1', credentials=credentials)
    
    def inspect_url(self, site_url: str, inspection_url: str) -> Dict:
        """
        Inspect a URL using URL Inspection API.
        
        Args:
            site_url: The Search Console property URL (e.g., 'https://example.com/').
            inspection_url: The URL to inspect.
        
        Returns:
            dict: URL inspection results including indexing status, mobile usability, etc.
        """
        try:
            request_body = {
                'inspectionUrl': inspection_url,
                'siteUrl': site_url,
            }
            
            response = self.service.urlInspection().index().inspect(
                body=request_body
            ).execute()
            
            inspection_result = response.get('inspectionResult', {})
            index_status = inspection_result.get('indexStatusResult', {})
            mobile_usability = inspection_result.get('mobileUsabilityResult', {})
            amp_result = inspection_result.get('ampResult', {})
            
            return {
                'success': True,
                'url': inspection_url,
                'indexing_state': index_status.get('verdict'),
                'coverage_state': index_status.get('coverageState'),
                'indexed': index_status.get('verdict') == 'PASS',
                'crawled_as': index_status.get('crawledAs'),
                'googlebot_can_access': index_status.get('robotsTxtState') == 'ALLOWED',
                'page_fetch_state': index_status.get('pageFetchState'),
                'canonical_url': index_status.get('googleCanonical'),
                'user_canonical_url': index_status.get('userCanonical'),
                'sitemap': index_status.get('sitemap'),
                'referring_urls': index_status.get('referringUrls', []),
                'mobile_friendly': mobile_usability.get('verdict') == 'PASS',
                'mobile_issues': mobile_usability.get('issues', []),
                'amp_valid': amp_result.get('verdict') == 'PASS' if amp_result else None,
                'last_crawl_time': index_status.get('lastCrawlTime'),
            }
        
        except HttpError as e:
            return {
                'success': False,
                'url': inspection_url,
                'error': str(e),
            }
    
    def batch_inspect_urls(self, site_url: str, urls: List[str], max_requests: int = 2000) -> List[Dict]:
        """
        Inspect multiple URLs (up to 2000 per day per property).
        
        Args:
            site_url: The Search Console property URL.
            urls: List of URLs to inspect.
            max_requests: Maximum number of requests (API limit is 2000/day).
        
        Returns:
            list: List of inspection results.
        """
        results = []
        
        for url in urls[:max_requests]:
            result = self.inspect_url(site_url, url)
            results.append(result)
        
        return results
    
    def get_search_analytics(
        self,
        site_url: str,
        start_date: datetime,
        end_date: datetime,
        dimensions: Optional[List[str]] = None,
        row_limit: int = 25000,
    ) -> Dict:
        """
        Get search analytics data from GSC.
        
        Args:
            site_url: The Search Console property URL.
            start_date: Start date for the report.
            end_date: End date for the report.
            dimensions: Dimensions to group by (e.g., ['query', 'page', 'country', 'device']).
            row_limit: Maximum number of rows to return (max 25,000).
        
        Returns:
            dict: Search analytics data with clicks, impressions, CTR, position.
        """
        if dimensions is None:
            dimensions = ['query', 'page']
        
        try:
            request_body = {
                'startDate': start_date.strftime('%Y-%m-%d'),
                'endDate': end_date.strftime('%Y-%m-%d'),
                'dimensions': dimensions,
                'rowLimit': row_limit,
            }
            
            response = self.service.searchanalytics().query(
                siteUrl=site_url,
                body=request_body
            ).execute()
            
            rows = response.get('rows', [])
            
            return {
                'success': True,
                'total_rows': len(rows),
                'data': rows,
            }
        
        except HttpError as e:
            return {
                'success': False,
                'error': str(e),
            }
    
    def get_top_queries(
        self,
        site_url: str,
        days_back: int = 30,
        limit: int = 100,
    ) -> List[Dict]:
        """
        Get top search queries for a site.
        
        Args:
            site_url: The Search Console property URL.
            days_back: Number of days to look back.
            limit: Number of top queries to return.
        
        Returns:
            list: Top queries with clicks, impressions, CTR, and position.
        """
        end_date = datetime.now()
        start_date = end_date - timedelta(days=days_back)
        
        result = self.get_search_analytics(
            site_url=site_url,
            start_date=start_date,
            end_date=end_date,
            dimensions=['query'],
            row_limit=limit,
        )
        
        if result.get('success'):
            # Sort by clicks
            queries = sorted(
                result['data'],
                key=lambda x: x.get('clicks', 0),
                reverse=True
            )
            return queries[:limit]
        
        return []
    
    def get_top_pages(
        self,
        site_url: str,
        days_back: int = 30,
        limit: int = 100,
    ) -> List[Dict]:
        """
        Get top pages by clicks.
        
        Args:
            site_url: The Search Console property URL.
            days_back: Number of days to look back.
            limit: Number of top pages to return.
        
        Returns:
            list: Top pages with performance metrics.
        """
        end_date = datetime.now()
        start_date = end_date - timedelta(days=days_back)
        
        result = self.get_search_analytics(
            site_url=site_url,
            start_date=start_date,
            end_date=end_date,
            dimensions=['page'],
            row_limit=limit,
        )
        
        if result.get('success'):
            # Sort by clicks
            pages = sorted(
                result['data'],
                key=lambda x: x.get('clicks', 0),
                reverse=True
            )
            return pages[:limit]
        
        return []
    
    def get_sitemaps(self, site_url: str) -> List[Dict]:
        """
        Get submitted sitemaps for a property.
        
        Args:
            site_url: The Search Console property URL.
        
        Returns:
            list: List of sitemaps with status information.
        """
        try:
            response = self.service.sitemaps().list(
                siteUrl=site_url
            ).execute()
            
            sitemaps = response.get('sitemap', [])
            
            return [
                {
                    'path': sitemap.get('path'),
                    'last_submitted': sitemap.get('lastSubmitted'),
                    'last_downloaded': sitemap.get('lastDownloaded'),
                    'is_pending': sitemap.get('isPending'),
                    'is_index': sitemap.get('isSitemapsIndex'),
                    'warnings': sitemap.get('warnings'),
                    'errors': sitemap.get('errors'),
                }
                for sitemap in sitemaps
            ]
        
        except HttpError as e:
            return []
    
    def submit_sitemap(self, site_url: str, sitemap_url: str) -> Dict:
        """
        Submit a sitemap to Google Search Console.
        
        Args:
            site_url: The Search Console property URL.
            sitemap_url: URL of the sitemap to submit.
        
        Returns:
            dict: Submission result.
        """
        try:
            self.service.sitemaps().submit(
                siteUrl=site_url,
                feedpath=sitemap_url
            ).execute()
            
            return {
                'success': True,
                'sitemap_url': sitemap_url,
            }
        
        except HttpError as e:
            return {
                'success': False,
                'error': str(e),
            }


def create_gsc_client_from_file(credentials_file: str) -> GoogleSearchConsoleClient:
    """
    Create GSC client from credentials JSON file.
    
    Args:
        credentials_file: Path to OAuth2 credentials JSON.
    
    Returns:
        GoogleSearchConsoleClient: Initialized client.
    """
    from google.oauth2 import service_account
    
    credentials = service_account.Credentials.from_service_account_file(
        credentials_file,
        scopes=['https://www.googleapis.com/auth/webmasters.readonly']
    )
    
    return GoogleSearchConsoleClient(credentials)
