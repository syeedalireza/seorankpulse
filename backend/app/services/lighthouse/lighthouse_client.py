"""
Lighthouse client for running performance audits and Core Web Vitals analysis.

This module integrates with Google Lighthouse to provide comprehensive
performance metrics including Core Web Vitals (LCP, FID, CLS).
"""

import json
import subprocess
import tempfile
from pathlib import Path
from typing import Dict, Optional
import asyncio


class LighthouseClient:
    """
    Client for running Google Lighthouse audits.
    
    Provides performance metrics, accessibility scores, SEO scores,
    and Core Web Vitals (LCP, FID, CLS, FCP, TTI, TBT).
    """
    
    def __init__(self, chrome_flags: Optional[list] = None):
        """
        Initialize Lighthouse client.
        
        Args:
            chrome_flags: Additional Chrome flags for Lighthouse.
        """
        self.chrome_flags = chrome_flags or [
            '--headless',
            '--no-sandbox',
            '--disable-dev-shm-usage',
        ]
    
    async def audit_url(self, url: str, categories: Optional[list] = None) -> Dict:
        """
        Run a Lighthouse audit on a URL.
        
        Args:
            url: The URL to audit.
            categories: List of categories to audit.
                       Options: 'performance', 'accessibility', 'best-practices', 'seo', 'pwa'
        
        Returns:
            dict: Lighthouse audit results with scores and metrics.
        """
        if categories is None:
            categories = ['performance', 'accessibility', 'seo']
        
        try:
            # Create temporary file for results
            with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as tmp:
                output_path = tmp.name
            
            # Build lighthouse command
            cmd = [
                'npx', 'lighthouse', url,
                '--output=json',
                f'--output-path={output_path}',
                '--quiet',
                '--chrome-flags=' + ' '.join(self.chrome_flags),
            ]
            
            # Add category filters
            for category in categories:
                cmd.append(f'--only-categories={category}')
            
            # Run Lighthouse (asynchronously)
            process = await asyncio.create_subprocess_exec(
                *cmd,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE
            )
            
            stdout, stderr = await process.communicate()
            
            if process.returncode != 0:
                return {
                    'success': False,
                    'error': stderr.decode() if stderr else 'Lighthouse audit failed',
                }
            
            # Read and parse results
            with open(output_path, 'r', encoding='utf-8') as f:
                results = json.load(f)
            
            # Clean up temp file
            Path(output_path).unlink(missing_ok=True)
            
            # Extract key metrics
            return self._extract_metrics(results)
        
        except Exception as e:
            return {
                'success': False,
                'error': str(e),
            }
    
    def _extract_metrics(self, lighthouse_results: Dict) -> Dict:
        """
        Extract key metrics from Lighthouse results.
        
        Args:
            lighthouse_results: Raw Lighthouse JSON results.
        
        Returns:
            dict: Extracted and formatted metrics.
        """
        categories = lighthouse_results.get('categories', {})
        audits = lighthouse_results.get('audits', {})
        
        # Extract category scores
        scores = {
            'performance': categories.get('performance', {}).get('score', 0) * 100,
            'accessibility': categories.get('accessibility', {}).get('score', 0) * 100,
            'best_practices': categories.get('best-practices', {}).get('score', 0) * 100,
            'seo': categories.get('seo', {}).get('score', 0) * 100,
        }
        
        # Core Web Vitals (from performance metrics)
        core_web_vitals = {
            # Largest Contentful Paint (LCP)
            'lcp': audits.get('largest-contentful-paint', {}).get('numericValue', 0) / 1000,
            'lcp_score': audits.get('largest-contentful-paint', {}).get('score', 0) * 100,
            
            # First Input Delay (FID) - estimated via TBT
            'fid_estimate': audits.get('max-potential-fid', {}).get('numericValue', 0),
            'fid_score': audits.get('max-potential-fid', {}).get('score', 0) * 100,
            
            # Cumulative Layout Shift (CLS)
            'cls': audits.get('cumulative-layout-shift', {}).get('numericValue', 0),
            'cls_score': audits.get('cumulative-layout-shift', {}).get('score', 0) * 100,
            
            # First Contentful Paint (FCP)
            'fcp': audits.get('first-contentful-paint', {}).get('numericValue', 0) / 1000,
            'fcp_score': audits.get('first-contentful-paint', {}).get('score', 0) * 100,
            
            # Time to Interactive (TTI)
            'tti': audits.get('interactive', {}).get('numericValue', 0) / 1000,
            'tti_score': audits.get('interactive', {}).get('score', 0) * 100,
            
            # Total Blocking Time (TBT)
            'tbt': audits.get('total-blocking-time', {}).get('numericValue', 0),
            'tbt_score': audits.get('total-blocking-time', {}).get('score', 0) * 100,
            
            # Speed Index
            'speed_index': audits.get('speed-index', {}).get('numericValue', 0) / 1000,
            'speed_index_score': audits.get('speed-index', {}).get('score', 0) * 100,
        }
        
        # Performance metrics
        performance_metrics = {
            'first_paint': audits.get('first-meaningful-paint', {}).get('numericValue', 0) / 1000,
            'dom_size': audits.get('dom-size', {}).get('numericValue', 0),
            'dom_size_score': audits.get('dom-size', {}).get('score', 0) * 100,
        }
        
        # Resource summary
        network_requests = audits.get('network-requests', {}).get('details', {}).get('items', [])
        resource_summary = self._summarize_resources(network_requests)
        
        # Opportunities (performance improvements)
        opportunities = self._extract_opportunities(audits)
        
        return {
            'success': True,
            'url': lighthouse_results.get('finalUrl'),
            'fetch_time': lighthouse_results.get('fetchTime'),
            'scores': scores,
            'core_web_vitals': core_web_vitals,
            'performance_metrics': performance_metrics,
            'resource_summary': resource_summary,
            'opportunities': opportunities,
            'user_agent': lighthouse_results.get('userAgent'),
        }
    
    def _summarize_resources(self, network_requests: list) -> Dict:
        """
        Summarize network resource statistics.
        
        Args:
            network_requests: List of network requests from Lighthouse.
        
        Returns:
            dict: Resource summary statistics.
        """
        total_size = 0
        total_count = len(network_requests)
        by_type = {}
        
        for request in network_requests:
            resource_type = request.get('resourceType', 'other')
            size = request.get('transferSize', 0)
            
            total_size += size
            
            if resource_type not in by_type:
                by_type[resource_type] = {'count': 0, 'size': 0}
            
            by_type[resource_type]['count'] += 1
            by_type[resource_type]['size'] += size
        
        return {
            'total_requests': total_count,
            'total_size_bytes': total_size,
            'total_size_kb': round(total_size / 1024, 2),
            'by_type': by_type,
        }
    
    def _extract_opportunities(self, audits: Dict) -> list:
        """
        Extract performance optimization opportunities.
        
        Args:
            audits: Lighthouse audits object.
        
        Returns:
            list: List of optimization opportunities.
        """
        opportunity_keys = [
            'render-blocking-resources',
            'unused-css-rules',
            'unused-javascript',
            'modern-image-formats',
            'offscreen-images',
            'unminified-css',
            'unminified-javascript',
            'efficiently-encode-images',
            'uses-responsive-images',
            'uses-text-compression',
        ]
        
        opportunities = []
        
        for key in opportunity_keys:
            if key in audits:
                audit = audits[key]
                if audit.get('score', 1) < 1:  # Has potential improvement
                    opportunities.append({
                        'id': key,
                        'title': audit.get('title'),
                        'description': audit.get('description'),
                        'score': audit.get('score', 0) * 100,
                        'savings_ms': audit.get('numericValue', 0),
                        'display_value': audit.get('displayValue'),
                    })
        
        return opportunities


async def run_lighthouse_audit(url: str) -> Dict:
    """
    Convenience function to run a Lighthouse audit on a single URL.
    
    Args:
        url: The URL to audit.
    
    Returns:
        dict: Lighthouse audit results.
    """
    client = LighthouseClient()
    return await client.audit_url(url)


def interpret_core_web_vitals(cwv: Dict) -> Dict:
    """
    Interpret Core Web Vitals scores and provide recommendations.
    
    Args:
        cwv: Core Web Vitals metrics dictionary.
    
    Returns:
        dict: Interpretation with status and recommendations.
    """
    interpretation = {}
    
    # LCP (Largest Contentful Paint)
    lcp = cwv.get('lcp', 0)
    if lcp <= 2.5:
        interpretation['lcp_status'] = 'good'
    elif lcp <= 4.0:
        interpretation['lcp_status'] = 'needs_improvement'
    else:
        interpretation['lcp_status'] = 'poor'
    
    # CLS (Cumulative Layout Shift)
    cls = cwv.get('cls', 0)
    if cls <= 0.1:
        interpretation['cls_status'] = 'good'
    elif cls <= 0.25:
        interpretation['cls_status'] = 'needs_improvement'
    else:
        interpretation['cls_status'] = 'poor'
    
    # FID (First Input Delay)
    fid = cwv.get('fid_estimate', 0)
    if fid <= 100:
        interpretation['fid_status'] = 'good'
    elif fid <= 300:
        interpretation['fid_status'] = 'needs_improvement'
    else:
        interpretation['fid_status'] = 'poor'
    
    # Overall status
    statuses = [
        interpretation['lcp_status'],
        interpretation['cls_status'],
        interpretation['fid_status'],
    ]
    
    if all(s == 'good' for s in statuses):
        interpretation['overall'] = 'good'
    elif any(s == 'poor' for s in statuses):
        interpretation['overall'] = 'poor'
    else:
        interpretation['overall'] = 'needs_improvement'
    
    return interpretation
