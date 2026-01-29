"""
JavaScript rendering service using Playwright.

This module provides functionality to render JavaScript-heavy pages
using a headless browser for accurate SEO analysis.
"""

import asyncio
from typing import Dict, Optional
from playwright.async_api import async_playwright, Browser, BrowserContext, Page


class JavaScriptRenderer:
    """
    Renders pages with JavaScript using Playwright/Chromium.
    
    This allows crawling of SPAs and JavaScript-rendered content
    that would be missed by static HTML parsing.
    """
    
    def __init__(self):
        """Initialize the JavaScript renderer."""
        self.browser: Optional[Browser] = None
        self.context: Optional[BrowserContext] = None
        self.playwright = None
    
    async def __aenter__(self):
        """Async context manager entry."""
        await self.initialize()
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit."""
        await self.close()
    
    async def initialize(self) -> None:
        """Initialize the Playwright browser."""
        self.playwright = await async_playwright().start()
        self.browser = await self.playwright.chromium.launch(
            headless=True,
            args=[
                '--no-sandbox',
                '--disable-setuid-sandbox',
                '--disable-dev-shm-usage',
                '--disable-gpu',
            ]
        )
        self.context = await self.browser.new_context(
            viewport={'width': 1920, 'height': 1080},
            user_agent='Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
        )
    
    async def close(self) -> None:
        """Close the browser and cleanup resources."""
        if self.context:
            await self.context.close()
        if self.browser:
            await self.browser.close()
        if self.playwright:
            await self.playwright.stop()
    
    async def render_page(self, url: str, wait_until: str = 'networkidle') -> Dict:
        """
        Render a page with JavaScript and extract content.
        
        Args:
            url: The URL to render.
            wait_until: When to consider navigation succeeded.
                       Options: 'load', 'domcontentloaded', 'networkidle'
        
        Returns:
            dict: Rendered page data including HTML, status, and metrics.
        """
        if not self.context:
            raise RuntimeError("Renderer not initialized. Use async context manager.")
        
        page: Page = await self.context.new_page()
        
        try:
            # Navigate to page and wait for JavaScript execution
            response = await page.goto(
                url,
                wait_until=wait_until,
                timeout=30000
            )
            
            # Wait an additional moment for any async JS to complete
            await page.wait_for_timeout(1000)
            
            # Extract data
            html_content = await page.content()
            title = await page.title()
            url_after_js = page.url  # May differ if JS redirected
            
            # Get performance metrics
            performance_timing = await page.evaluate('''() => {
                const timing = performance.timing;
                return {
                    loadTime: timing.loadEventEnd - timing.navigationStart,
                    domContentLoaded: timing.domContentLoadedEventEnd - timing.navigationStart,
                    responseTime: timing.responseEnd - timing.requestStart
                };
            }''')
            
            # Check for meta tags that might have been added by JS
            meta_tags = await page.evaluate('''() => {
                const metas = {};
                document.querySelectorAll('meta[name]').forEach(meta => {
                    metas[meta.getAttribute('name')] = meta.getAttribute('content');
                });
                return metas;
            }''')
            
            # Get viewport screenshot (optional, for visual validation)
            # screenshot = await page.screenshot(type='png', full_page=False)
            
            return {
                'html': html_content,
                'title': title,
                'url': url,
                'final_url': url_after_js,
                'status_code': response.status if response else 0,
                'meta_tags': meta_tags,
                'performance': {
                    'load_time_ms': performance_timing.get('loadTime', 0),
                    'dom_content_loaded_ms': performance_timing.get('domContentLoaded', 0),
                    'response_time_ms': performance_timing.get('responseTime', 0),
                },
                'javascript_rendered': True,
            }
        
        except Exception as e:
            return {
                'html': None,
                'title': None,
                'url': url,
                'final_url': url,
                'status_code': 0,
                'error': str(e),
                'javascript_rendered': False,
            }
        
        finally:
            await page.close()
    
    async def check_js_framework(self, url: str) -> Dict:
        """
        Detect JavaScript frameworks and libraries on a page.
        
        Args:
            url: The URL to check.
        
        Returns:
            dict: Detected frameworks and technologies.
        """
        if not self.context:
            raise RuntimeError("Renderer not initialized.")
        
        page: Page = await self.context.new_page()
        
        try:
            await page.goto(url, wait_until='networkidle', timeout=30000)
            
            frameworks = await page.evaluate('''() => {
                const detected = {};
                
                // React
                if (window.React || document.querySelector('[data-reactroot]') || 
                    document.querySelector('[data-reactid]')) {
                    detected.react = true;
                }
                
                // Vue
                if (window.Vue || document.querySelector('[data-v-]')) {
                    detected.vue = true;
                }
                
                // Angular
                if (window.angular || window.ng || document.querySelector('[ng-version]')) {
                    detected.angular = true;
                }
                
                // Next.js
                if (window.__NEXT_DATA__) {
                    detected.nextjs = true;
                }
                
                // Nuxt.js
                if (window.__NUXT__) {
                    detected.nuxtjs = true;
                }
                
                // jQuery
                if (window.jQuery || window.$) {
                    detected.jquery = true;
                }
                
                // Google Analytics
                if (window.ga || window.gtag || window.dataLayer) {
                    detected.google_analytics = true;
                }
                
                return detected;
            }''')
            
            return frameworks
        
        finally:
            await page.close()


async def render_with_javascript(url: str) -> Dict:
    """
    Convenience function to render a single page with JavaScript.
    
    Args:
        url: The URL to render.
    
    Returns:
        dict: Rendered page data.
    """
    async with JavaScriptRenderer() as renderer:
        return await renderer.render_page(url)
