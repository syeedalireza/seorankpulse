"""
XML Sitemap generator from crawl results.

This module generates XML sitemaps compliant with the sitemaps.org protocol.
"""

from datetime import datetime
from typing import List, Optional
from xml.etree.ElementTree import Element, SubElement, tostring
from xml.dom import minidom


class SitemapGenerator:
    """
    Generate XML sitemaps from crawl results.
    
    Supports:
    - Standard sitemap.xml
    - Sitemap index for large sites
    - Last modified dates
    - Change frequency hints
    - Priority values
    """
    
    def __init__(self, domain: str):
        """
        Initialize sitemap generator.
        
        Args:
            domain: The website domain (e.g., 'example.com').
        """
        self.domain = domain.replace('https://', '').replace('http://', '').rstrip('/')
    
    def generate_sitemap(
        self,
        pages: List[dict],
        include_images: bool = False,
        max_urls: int = 50000,
    ) -> str:
        """
        Generate XML sitemap from page data.
        
        Args:
            pages: List of page dictionaries with URL and metadata.
            include_images: Whether to include image sitemap data.
            max_urls: Maximum URLs per sitemap (50,000 is the standard limit).
        
        Returns:
            str: XML sitemap content.
        """
        # Create root element
        urlset = Element('urlset')
        urlset.set('xmlns', 'http://www.sitemaps.org/schemas/sitemap/0.9')
        
        if include_images:
            urlset.set('xmlns:image', 'http://www.google.com/schemas/sitemap-image/1.1')
        
        # Add URLs (limit to max_urls)
        for page in pages[:max_urls]:
            # Only include successful pages
            if page.get('status_code') == 200:
                url_elem = self._create_url_element(page, include_images)
                urlset.append(url_elem)
        
        # Pretty print XML
        return self._prettify_xml(urlset)
    
    def _create_url_element(self, page: dict, include_images: bool = False) -> Element:
        """
        Create a URL element for the sitemap.
        
        Args:
            page: Page data dictionary.
            include_images: Whether to include image data.
        
        Returns:
            Element: URL element.
        """
        url_elem = Element('url')
        
        # Location (required)
        loc = SubElement(url_elem, 'loc')
        loc.text = page.get('url')
        
        # Last modified (optional)
        if page.get('created_at') or page.get('last_modified'):
            lastmod = SubElement(url_elem, 'lastmod')
            date = page.get('last_modified') or page.get('created_at')
            if isinstance(date, str):
                lastmod.text = date
            else:
                lastmod.text = date.strftime('%Y-%m-%d')
        
        # Change frequency (optional)
        changefreq = SubElement(url_elem, 'changefreq')
        changefreq.text = self._determine_change_frequency(page)
        
        # Priority (optional)
        priority = SubElement(url_elem, 'priority')
        priority.text = str(self._calculate_priority(page))
        
        # Images (optional)
        if include_images and page.get('images_count', 0) > 0:
            # This would require image URL data to be stored
            # For now, we'll skip individual image URLs
            pass
        
        return url_elem
    
    def _determine_change_frequency(self, page: dict) -> str:
        """
        Determine change frequency hint based on page characteristics.
        
        Args:
            page: Page data dictionary.
        
        Returns:
            str: Change frequency value.
        """
        url = page.get('url', '')
        
        # Homepage changes frequently
        if url.endswith('/') and url.count('/') <= 3:
            return 'daily'
        
        # Blog posts change less frequently
        if '/blog/' in url or '/article/' in url or '/post/' in url:
            return 'weekly'
        
        # Static pages
        if '/about' in url or '/contact' in url or '/privacy' in url:
            return 'monthly'
        
        # Default
        return 'weekly'
    
    def _calculate_priority(self, page: dict) -> float:
        """
        Calculate priority value based on page importance.
        
        Args:
            page: Page data dictionary.
        
        Returns:
            float: Priority value (0.0 to 1.0).
        """
        url = page.get('url', '')
        depth = page.get('depth', 0)
        
        # Homepage gets highest priority
        if url.endswith('/') and url.count('/') <= 3:
            return 1.0
        
        # Decrease priority with depth
        if depth == 0:
            return 1.0
        elif depth == 1:
            return 0.8
        elif depth == 2:
            return 0.6
        elif depth == 3:
            return 0.4
        else:
            return 0.3
    
    def generate_sitemap_index(
        self,
        sitemap_urls: List[str],
    ) -> str:
        """
        Generate sitemap index for large sites with multiple sitemaps.
        
        Args:
            sitemap_urls: List of sitemap URLs.
        
        Returns:
            str: XML sitemap index content.
        """
        sitemapindex = Element('sitemapindex')
        sitemapindex.set('xmlns', 'http://www.sitemaps.org/schemas/sitemap/0.9')
        
        for sitemap_url in sitemap_urls:
            sitemap_elem = SubElement(sitemapindex, 'sitemap')
            
            loc = SubElement(sitemap_elem, 'loc')
            loc.text = sitemap_url
            
            lastmod = SubElement(sitemap_elem, 'lastmod')
            lastmod.text = datetime.utcnow().strftime('%Y-%m-%d')
        
        return self._prettify_xml(sitemapindex)
    
    def split_into_multiple_sitemaps(
        self,
        pages: List[dict],
        max_urls_per_sitemap: int = 50000,
    ) -> List[str]:
        """
        Split large page lists into multiple sitemaps.
        
        Args:
            pages: List of all pages.
            max_urls_per_sitemap: Maximum URLs per sitemap file.
        
        Returns:
            list: List of sitemap XML strings.
        """
        sitemaps = []
        
        # Filter successful pages only
        successful_pages = [p for p in pages if p.get('status_code') == 200]
        
        # Split into chunks
        for i in range(0, len(successful_pages), max_urls_per_sitemap):
            chunk = successful_pages[i:i + max_urls_per_sitemap]
            sitemap_xml = self.generate_sitemap(chunk)
            sitemaps.append(sitemap_xml)
        
        return sitemaps
    
    @staticmethod
    def _prettify_xml(elem: Element) -> str:
        """
        Return a pretty-printed XML string.
        
        Args:
            elem: XML element.
        
        Returns:
            str: Formatted XML string.
        """
        rough_string = tostring(elem, encoding='utf-8')
        reparsed = minidom.parseString(rough_string)
        return reparsed.toprettyxml(indent="  ", encoding='utf-8').decode('utf-8')


def generate_sitemap(domain: str, pages: List[dict]) -> str:
    """
    Convenience function to generate a sitemap.
    
    Args:
        domain: Website domain.
        pages: List of page data dictionaries.
    
    Returns:
        str: XML sitemap content.
    """
    generator = SitemapGenerator(domain)
    return generator.generate_sitemap(pages)


def generate_sitemap_with_index(domain: str, pages: List[dict]) -> dict:
    """
    Generate sitemap(s) with index if needed for large sites.
    
    Args:
        domain: Website domain.
        pages: List of page data dictionaries.
    
    Returns:
        dict: Contains 'sitemaps' list and optional 'index'.
    """
    generator = SitemapGenerator(domain)
    
    # Count successful pages
    successful_pages = [p for p in pages if p.get('status_code') == 200]
    
    if len(successful_pages) <= 50000:
        # Single sitemap
        return {
            'sitemaps': [generator.generate_sitemap(successful_pages)],
            'index': None,
            'total_urls': len(successful_pages),
        }
    else:
        # Multiple sitemaps with index
        sitemaps = generator.split_into_multiple_sitemaps(successful_pages)
        
        # Generate URLs for sitemaps (assuming they'll be hosted)
        sitemap_urls = [
            f"https://{domain}/sitemap{i+1}.xml"
            for i in range(len(sitemaps))
        ]
        
        index = generator.generate_sitemap_index(sitemap_urls)
        
        return {
            'sitemaps': sitemaps,
            'index': index,
            'total_urls': len(successful_pages),
            'sitemap_count': len(sitemaps),
        }
