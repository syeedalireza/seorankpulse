"""
Redirect chain detection and analysis.

This module tracks redirect chains to identify:
- Redirect loops
- Long redirect chains
- Mixed protocol redirects (HTTP <-> HTTPS)
- Redirect optimization opportunities
"""

import httpx
from typing import Dict, List, Optional, Tuple
from collections import deque


class RedirectChainAnalyzer:
    """
    Analyze redirect chains for SEO optimization.
    
    Detects:
    - Redirect chains (multiple hops)
    - Redirect loops
    - Temporary vs permanent redirects
    - Protocol changes (HTTP/HTTPS)
    - Cross-domain redirects
    """
    
    def __init__(self, max_redirects: int = 10):
        """
        Initialize redirect chain analyzer.
        
        Args:
            max_redirects: Maximum redirects to follow.
        """
        self.max_redirects = max_redirects
    
    async def analyze_url(self, url: str) -> Dict:
        """
        Analyze redirect chain for a URL.
        
        Args:
            url: URL to analyze.
        
        Returns:
            dict: Redirect chain analysis.
        """
        chain = []
        current_url = url
        visited = set()
        
        async with httpx.AsyncClient(
            follow_redirects=False,
            timeout=30.0
        ) as client:
            
            for hop in range(self.max_redirects):
                if current_url in visited:
                    # Redirect loop detected
                    return {
                        'url': url,
                        'has_redirects': True,
                        'has_loop': True,
                        'chain_length': len(chain),
                        'chain': chain,
                        'final_url': current_url,
                        'issues': ['Redirect loop detected'],
                        'severity': 'critical',
                    }
                
                visited.add(current_url)
                
                try:
                    response = await client.get(current_url)
                    
                    # Record this hop
                    hop_info = {
                        'url': current_url,
                        'status_code': response.status_code,
                        'hop_number': hop + 1,
                    }
                    
                    # Check if it's a redirect
                    if 300 <= response.status_code < 400:
                        location = response.headers.get('location')
                        
                        if not location:
                            hop_info['error'] = 'Redirect without Location header'
                            chain.append(hop_info)
                            break
                        
                        # Resolve relative URLs
                        if location.startswith('/'):
                            from urllib.parse import urlparse, urlunparse
                            parsed = urlparse(current_url)
                            location = urlunparse((
                                parsed.scheme,
                                parsed.netloc,
                                location,
                                '', '', ''
                            ))
                        
                        hop_info['redirect_type'] = self._classify_redirect(
                            response.status_code
                        )
                        hop_info['next_url'] = location
                        
                        chain.append(hop_info)
                        current_url = location
                    
                    else:
                        # Final destination (non-redirect)
                        hop_info['is_final'] = True
                        chain.append(hop_info)
                        break
                
                except Exception as e:
                    chain.append({
                        'url': current_url,
                        'error': str(e),
                        'hop_number': hop + 1,
                    })
                    break
        
        # Analyze the chain
        return self._analyze_chain(url, chain)
    
    def _classify_redirect(self, status_code: int) -> str:
        """
        Classify redirect type.
        
        Args:
            status_code: HTTP status code.
        
        Returns:
            str: Redirect type description.
        """
        redirect_types = {
            301: 'Permanent (301)',
            302: 'Temporary (302)',
            303: 'See Other (303)',
            307: 'Temporary (307)',
            308: 'Permanent (308)',
        }
        return redirect_types.get(status_code, f'Unknown ({status_code})')
    
    def _analyze_chain(self, original_url: str, chain: List[Dict]) -> Dict:
        """
        Analyze redirect chain and identify issues.
        
        Args:
            original_url: Original URL.
            chain: List of redirect hops.
        
        Returns:
            dict: Chain analysis with issues and recommendations.
        """
        chain_length = len(chain)
        has_redirects = chain_length > 1
        
        if not chain:
            return {
                'url': original_url,
                'has_redirects': False,
                'error': 'Failed to analyze',
            }
        
        final_hop = chain[-1]
        final_url = final_hop.get('url')
        
        issues = []
        warnings = []
        recommendations = []
        
        # Check chain length
        if chain_length > 3:
            issues.append(f"Long redirect chain ({chain_length} hops)")
            recommendations.append("Reduce redirect chain to maximum 1 hop")
        elif chain_length > 1:
            warnings.append(f"Redirect chain has {chain_length} hops")
            recommendations.append("Consider direct redirect to final destination")
        
        # Check redirect types
        redirect_types = [
            hop.get('redirect_type')
            for hop in chain
            if 'redirect_type' in hop
        ]
        
        if 'Temporary (302)' in redirect_types or 'Temporary (307)' in redirect_types:
            warnings.append("Contains temporary redirects")
            recommendations.append("Use permanent redirects (301/308) for SEO")
        
        # Check for protocol changes
        urls_in_chain = [hop['url'] for hop in chain]
        has_http = any(url.startswith('http://') for url in urls_in_chain)
        has_https = any(url.startswith('https://') for url in urls_in_chain)
        
        if has_http and has_https:
            warnings.append("Mixed HTTP/HTTPS in redirect chain")
        
        # Check for domain changes
        domains = []
        for url in urls_in_chain:
            from urllib.parse import urlparse
            domain = urlparse(url).netloc
            if domain:
                domains.append(domain)
        
        unique_domains = set(domains)
        if len(unique_domains) > 1:
            warnings.append(f"Redirects across {len(unique_domains)} domains")
        
        # Determine severity
        if issues:
            severity = 'high'
        elif warnings:
            severity = 'medium'
        else:
            severity = 'low'
        
        return {
            'url': original_url,
            'has_redirects': has_redirects,
            'has_loop': False,
            'chain_length': chain_length,
            'chain': chain,
            'final_url': final_url,
            'final_status': final_hop.get('status_code'),
            'issues': issues,
            'warnings': warnings,
            'recommendations': recommendations,
            'severity': severity,
            'redirect_types': redirect_types,
            'domains_in_chain': list(unique_domains),
        }
    
    async def batch_analyze(self, urls: List[str]) -> List[Dict]:
        """
        Analyze redirect chains for multiple URLs.
        
        Args:
            urls: List of URLs to analyze.
        
        Returns:
            list: Redirect chain analyses.
        """
        results = []
        
        for url in urls:
            result = await self.analyze_url(url)
            results.append(result)
        
        return results


async def analyze_redirect_chain(url: str) -> Dict:
    """
    Convenience function to analyze a single URL's redirect chain.
    
    Args:
        url: URL to analyze.
    
    Returns:
        dict: Redirect chain analysis.
    """
    analyzer = RedirectChainAnalyzer()
    return await analyzer.analyze_url(url)


def visualize_redirect_chain(chain_analysis: Dict) -> str:
    """
    Create text visualization of redirect chain.
    
    Args:
        chain_analysis: Redirect chain analysis.
    
    Returns:
        str: ASCII visualization of the chain.
    """
    if not chain_analysis.get('has_redirects'):
        return f"{chain_analysis['url']} (No redirects)"
    
    lines = []
    lines.append(f"Redirect Chain for: {chain_analysis['url']}")
    lines.append("=" * 80)
    
    for hop in chain_analysis.get('chain', []):
        hop_num = hop.get('hop_number', 0)
        url = hop.get('url', '')
        status = hop.get('status_code', 0)
        
        if hop.get('is_final'):
            lines.append(f"{hop_num}. [{status}] {url} (FINAL)")
        else:
            redirect_type = hop.get('redirect_type', 'Unknown')
            next_url = hop.get('next_url', '')
            lines.append(f"{hop_num}. [{status}] {url}")
            lines.append(f"    └─> {redirect_type} to: {next_url}")
    
    lines.append("=" * 80)
    
    if chain_analysis.get('issues'):
        lines.append("ISSUES:")
        for issue in chain_analysis['issues']:
            lines.append(f"  - {issue}")
    
    if chain_analysis.get('warnings'):
        lines.append("WARNINGS:")
        for warning in chain_analysis['warnings']:
            lines.append(f"  - {warning}")
    
    if chain_analysis.get('recommendations'):
        lines.append("RECOMMENDATIONS:")
        for rec in chain_analysis['recommendations']:
            lines.append(f"  - {rec}")
    
    return '\n'.join(lines)


def generate_redirect_map(analyses: List[Dict]) -> Dict:
    """
    Generate redirect map showing all redirect relationships.
    
    Args:
        analyses: List of redirect chain analyses.
    
    Returns:
        dict: Redirect map structure.
    """
    redirect_map = {
        'nodes': [],
        'edges': [],
    }
    
    node_ids = set()
    
    for analysis in analyses:
        if not analysis.get('has_redirects'):
            continue
        
        chain = analysis.get('chain', [])
        
        for hop in chain:
            url = hop.get('url')
            if url and url not in node_ids:
                node_ids.add(url)
                redirect_map['nodes'].append({
                    'id': url,
                    'label': url,
                    'status_code': hop.get('status_code'),
                    'is_final': hop.get('is_final', False),
                })
            
            if 'next_url' in hop:
                redirect_map['edges'].append({
                    'from': url,
                    'to': hop['next_url'],
                    'type': hop.get('redirect_type'),
                })
    
    return redirect_map
