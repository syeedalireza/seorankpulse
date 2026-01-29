"""
List mode crawling - analyze a list of URLs without traditional crawling.

This module allows users to upload a list of URLs (CSV, Excel, or text)
and analyze them without following links (similar to Screaming Frog's List Mode).
"""

import csv
import io
from typing import Dict, List, Optional
import pandas as pd
from app.services.crawler.spider import WebCrawler
from app.models.project import Project


class ListModeCrawler:
    """
    Analyze a list of URLs without traditional crawling.
    
    This is useful for:
    - Auditing specific pages
    - Analyzing exported URL lists
    - Quick checks without full site crawl
    """
    
    def __init__(self, project: Project, enable_js: bool = False):
        """
        Initialize list mode crawler.
        
        Args:
            project: Project configuration.
            enable_js: Whether to enable JavaScript rendering.
        """
        self.project = project
        self.enable_js = enable_js
    
    async def analyze_url_list(self, urls: List[str]) -> Dict:
        """
        Analyze a list of URLs.
        
        Args:
            urls: List of URLs to analyze.
        
        Returns:
            dict: Analysis results for all URLs.
        """
        results = []
        
        # Create a temporary crawler instance
        from app.services.crawler.spider import WebCrawler
        
        # Use project settings but don't follow links
        crawler = WebCrawler(self.project, enable_js=self.enable_js)
        
        async with crawler:
            for url in urls:
                # Fetch and analyze each URL individually
                page_data = await crawler.fetch_page(url, depth=0)
                if page_data:
                    results.append(page_data)
        
        return {
            'total_urls': len(urls),
            'analyzed': len(results),
            'pages': results,
        }
    
    @staticmethod
    def parse_csv_file(file_content: bytes, url_column: str = 'url') -> List[str]:
        """
        Parse URLs from CSV file.
        
        Args:
            file_content: CSV file content as bytes.
            url_column: Name of the column containing URLs.
        
        Returns:
            list: Extracted URLs.
        """
        urls = []
        
        try:
            # Decode and parse CSV
            text = file_content.decode('utf-8')
            reader = csv.DictReader(io.StringIO(text))
            
            for row in reader:
                if url_column in row and row[url_column]:
                    urls.append(row[url_column].strip())
        
        except Exception:
            # Fallback: try reading as simple text file (one URL per line)
            text = file_content.decode('utf-8')
            urls = [line.strip() for line in text.split('\n') if line.strip()]
        
        return urls
    
    @staticmethod
    def parse_excel_file(file_content: bytes, url_column: str = 'url', sheet_name: int = 0) -> List[str]:
        """
        Parse URLs from Excel file.
        
        Args:
            file_content: Excel file content as bytes.
            url_column: Name of the column containing URLs.
            sheet_name: Sheet index or name to read from.
        
        Returns:
            list: Extracted URLs.
        """
        urls = []
        
        try:
            # Read Excel file
            df = pd.read_excel(io.BytesIO(file_content), sheet_name=sheet_name)
            
            # Try to find URL column
            if url_column in df.columns:
                urls = df[url_column].dropna().astype(str).tolist()
            elif 'URL' in df.columns:
                urls = df['URL'].dropna().astype(str).tolist()
            elif 'url' in df.columns:
                urls = df['url'].dropna().astype(str).tolist()
            else:
                # Use first column as fallback
                urls = df.iloc[:, 0].dropna().astype(str).tolist()
            
            # Clean URLs
            urls = [url.strip() for url in urls if url.strip()]
        
        except Exception as e:
            raise ValueError(f"Failed to parse Excel file: {str(e)}")
        
        return urls
    
    @staticmethod
    def parse_text_file(file_content: bytes) -> List[str]:
        """
        Parse URLs from plain text file (one URL per line).
        
        Args:
            file_content: Text file content as bytes.
        
        Returns:
            list: Extracted URLs.
        """
        text = file_content.decode('utf-8')
        urls = [line.strip() for line in text.split('\n') if line.strip()]
        return urls
    
    @staticmethod
    def validate_urls(urls: List[str]) -> Dict:
        """
        Validate a list of URLs.
        
        Args:
            urls: List of URLs to validate.
        
        Returns:
            dict: Validation results with valid and invalid URLs.
        """
        from app.services.crawler.url_parser import is_valid_url
        
        valid_urls = []
        invalid_urls = []
        
        for url in urls:
            if is_valid_url(url):
                valid_urls.append(url)
            else:
                invalid_urls.append(url)
        
        return {
            'total': len(urls),
            'valid': len(valid_urls),
            'invalid': len(invalid_urls),
            'valid_urls': valid_urls,
            'invalid_urls': invalid_urls,
        }


async def analyze_url_list(project: Project, urls: List[str], enable_js: bool = False) -> Dict:
    """
    Convenience function to analyze a list of URLs.
    
    Args:
        project: Project configuration.
        urls: List of URLs to analyze.
        enable_js: Whether to enable JavaScript rendering.
    
    Returns:
        dict: Analysis results.
    """
    crawler = ListModeCrawler(project, enable_js=enable_js)
    return await crawler.analyze_url_list(urls)
