"""
Web crawler/spider implementation.

This module implements an async web crawler that respects robots.txt,
handles rate limiting, and extracts SEO-relevant data.
"""

import asyncio
import time
from typing import Dict, List, Optional, Set
from urllib.robotparser import RobotFileParser

import httpx
from bs4 import BeautifulSoup

from app.models.project import Project
from app.services.crawler.url_parser import (
    extract_links_from_html,
    get_url_hash,
    is_same_domain,
    is_valid_url,
    normalize_url,
)
from app.services.crawler.js_renderer import JavaScriptRenderer


class WebCrawler:
    """
    Asynchronous web crawler for SEO analysis.
    
    This crawler:
    - Respects robots.txt
    - Implements rate limiting
    - Extracts SEO metadata
    - Handles redirects
    - Tracks crawl depth
    """
    
    def __init__(self, project: Project, enable_js: bool = False):
        """
        Initialize the crawler.
        
        Args:
            project: Project model with crawl configuration.
            enable_js: Whether to enable JavaScript rendering with Playwright.
        """
        self.project = project
        self.start_url = f"https://{project.domain}"
        
        # Crawl settings
        self.max_depth = project.max_depth
        self.delay_ms = project.crawl_delay_ms
        self.user_agent = project.user_agent
        self.respect_robots = project.respect_robots_txt
        self.enable_js = enable_js
        
        # State tracking
        self.visited_urls: Set[str] = set()
        self.url_queue: List[tuple[str, int]] = []  # (url, depth)
        self.robots_parser: Optional[RobotFileParser] = None
        
        # HTTP client
        self.client = httpx.AsyncClient(
            timeout=30.0,
            follow_redirects=True,
            headers={"User-Agent": self.user_agent},
        )
        
        # JavaScript renderer (initialized when needed)
        self.js_renderer: Optional[JavaScriptRenderer] = None
    
    async def __aenter__(self):
        """Async context manager entry."""
        await self.initialize()
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit."""
        await self.client.aclose()
        if self.js_renderer:
            await self.js_renderer.close()
    
    async def initialize(self) -> None:
        """Initialize the crawler (load robots.txt, etc.)."""
        if self.respect_robots:
            await self._load_robots_txt()
        
        # Initialize JavaScript renderer if enabled
        if self.enable_js:
            self.js_renderer = JavaScriptRenderer()
            await self.js_renderer.initialize()
    
    async def _load_robots_txt(self) -> None:
        """Load and parse robots.txt file."""
        robots_url = f"{self.start_url}/robots.txt"
        
        try:
            response = await self.client.get(robots_url)
            if response.status_code == 200:
                self.robots_parser = RobotFileParser()
                self.robots_parser.parse(response.text.splitlines())
        except Exception:
            # If robots.txt doesn't exist or fails, allow all
            pass
    
    def can_fetch(self, url: str) -> bool:
        """
        Check if URL can be fetched according to robots.txt.
        
        Args:
            url: The URL to check.
        
        Returns:
            bool: True if allowed, False otherwise.
        """
        if not self.respect_robots or not self.robots_parser:
            return True
        
        return self.robots_parser.can_fetch(self.user_agent, url)
    
    async def crawl(self) -> Dict:
        """
        Start crawling from the start URL.
        
        Returns:
            dict: Crawl statistics and results.
        """
        # Add start URL to queue
        self.url_queue.append((self.start_url, 0))
        
        pages_data = []
        start_time = time.time()
        
        while self.url_queue and len(self.visited_urls) < 1000:  # Safety limit
            url, depth = self.url_queue.pop(0)
            
            # Check depth limit
            if depth > self.max_depth:
                continue
            
            # Check if already visited
            url_hash = get_url_hash(url)
            if url_hash in self.visited_urls:
                continue
            
            # Check robots.txt
            if not self.can_fetch(url):
                continue
            
            # Mark as visited
            self.visited_urls.add(url_hash)
            
            # Fetch and parse page
            page_data = await self.fetch_page(url, depth)
            if page_data:
                pages_data.append(page_data)
                
                # Extract and queue links if not at max depth
                if depth < self.max_depth and page_data.get('links'):
                    for link in page_data['links']:
                        self.url_queue.append((link, depth + 1))
            
            # Rate limiting
            await asyncio.sleep(self.delay_ms / 1000.0)
        
        elapsed = time.time() - start_time
        
        return {
            "pages": pages_data,
            "total_pages": len(pages_data),
            "elapsed_seconds": elapsed,
        }
    
    async def fetch_page(self, url: str, depth: int) -> Optional[Dict]:
        """
        Fetch and parse a single page.
        
        Args:
            url: The URL to fetch.
            depth: Current crawl depth.
        
        Returns:
            dict | None: Page data or None if fetch failed.
        """
        try:
            # Use JavaScript rendering if enabled
            if self.enable_js and self.js_renderer:
                return await self._fetch_with_js(url, depth)
            
            # Otherwise use standard HTTP fetch
            start_time = time.time()
            response = await self.client.get(url)
            response_time = int((time.time() - start_time) * 1000)
            
            # Parse HTML if successful
            if response.status_code == 200 and 'text/html' in response.headers.get('content-type', ''):
                return self._parse_html(url, response.text, response.status_code, response_time, depth)
            else:
                # Still record non-HTML pages
                return {
                    "url": url,
                    "url_hash": get_url_hash(url),
                    "status_code": response.status_code,
                    "response_time_ms": response_time,
                    "depth": depth,
                }
        
        except Exception as e:
            # Record error
            return {
                "url": url,
                "url_hash": get_url_hash(url),
                "status_code": 0,
                "error": str(e),
                "depth": depth,
            }
    
    async def _fetch_with_js(self, url: str, depth: int) -> Dict:
        """
        Fetch page with JavaScript rendering using Playwright.
        
        Args:
            url: The URL to fetch.
            depth: Current crawl depth.
        
        Returns:
            dict: Page data with JS-rendered content.
        """
        start_time = time.time()
        js_result = await self.js_renderer.render_page(url)
        response_time = int((time.time() - start_time) * 1000)
        
        if js_result.get('html'):
            page_data = self._parse_html(
                url,
                js_result['html'],
                js_result.get('status_code', 200),
                response_time,
                depth
            )
            # Add JS-specific metadata
            page_data['javascript_rendered'] = True
            page_data['final_url'] = js_result.get('final_url', url)
            page_data['js_performance'] = js_result.get('performance', {})
            return page_data
        else:
            return {
                "url": url,
                "url_hash": get_url_hash(url),
                "status_code": js_result.get('status_code', 0),
                "response_time_ms": response_time,
                "depth": depth,
                "error": js_result.get('error'),
                "javascript_rendered": False,
            }
    
    def _parse_html(
        self,
        url: str,
        html: str,
        status_code: int,
        response_time: int,
        depth: int,
    ) -> Dict:
        """
        Parse HTML and extract SEO data.
        
        Args:
            url: Page URL.
            html: HTML content.
            status_code: HTTP status code.
            response_time: Response time in ms.
            depth: Crawl depth.
        
        Returns:
            dict: Extracted page data.
        """
        soup = BeautifulSoup(html, 'lxml')
        
        # Extract meta tags
        title = soup.find('title')
        title_text = title.get_text(strip=True) if title else None
        
        meta_desc = soup.find('meta', attrs={'name': 'description'})
        meta_description = meta_desc.get('content') if meta_desc else None
        
        meta_keywords = soup.find('meta', attrs={'name': 'keywords'})
        keywords = meta_keywords.get('content') if meta_keywords else None
        
        # Extract canonical
        canonical = soup.find('link', attrs={'rel': 'canonical'})
        canonical_url = canonical.get('href') if canonical else None
        
        # Extract headings
        h1_tags = [h.get_text(strip=True) for h in soup.find_all('h1')]
        h2_tags = [h.get_text(strip=True) for h in soup.find_all('h2')]
        h3_tags = [h.get_text(strip=True) for h in soup.find_all('h3')]
        
        # Analyze images
        images = soup.find_all('img')
        images_count = len(images)
        images_without_alt = sum(1 for img in images if not img.get('alt'))
        
        # Extract links
        links = extract_links_from_html(html, url, same_domain_only=True)
        all_links = extract_links_from_html(html, url, same_domain_only=False)
        internal_links = links
        external_links = all_links - internal_links
        
        # Content analysis
        text = soup.get_text(separator=' ', strip=True)
        word_count = len(text.split())
        text_size = len(text)
        html_size = len(html)
        text_to_html_ratio = text_size / html_size if html_size > 0 else 0
        
        # Robots meta tags
        robots_meta = soup.find('meta', attrs={'name': 'robots'})
        robots_content = robots_meta.get('content', '').lower() if robots_meta else ''
        has_noindex = 'noindex' in robots_content
        has_nofollow = 'nofollow' in robots_content
        
        # Schema.org structured data
        schema_types = []
        for script in soup.find_all('script', type='application/ld+json'):
            # Simplified schema extraction
            schema_types.append('ld+json')
        
        # Open Graph tags
        og_tags = {}
        for meta in soup.find_all('meta', property=lambda x: x and x.startswith('og:')):
            og_tags[meta.get('property')] = meta.get('content')
        
        return {
            "url": url,
            "url_hash": get_url_hash(url),
            "status_code": status_code,
            "response_time_ms": response_time,
            "title": title_text,
            "meta_description": meta_description,
            "meta_keywords": keywords,
            "canonical_url": canonical_url,
            "h1_tags": h1_tags,
            "h2_tags": h2_tags,
            "h3_tags": h3_tags,
            "images_count": images_count,
            "images_without_alt": images_without_alt,
            "internal_links_count": len(internal_links),
            "external_links_count": len(external_links),
            "word_count": word_count,
            "text_to_html_ratio": text_to_html_ratio,
            "page_size_bytes": html_size,
            "schema_org_types": schema_types if schema_types else None,
            "og_tags": og_tags if og_tags else None,
            "has_robots_noindex": has_noindex,
            "has_robots_nofollow": has_nofollow,
            "depth": depth,
            "links": list(internal_links),  # For queuing
        }
