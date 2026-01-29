"""
Accessibility audit using AXE engine.

This module provides WCAG compliance checking and accessibility
analysis for web pages.
"""

from typing import Dict, List, Optional
from playwright.async_api import async_playwright, Browser, Page
import json


class AccessibilityAuditor:
    """
    Audit web pages for accessibility using AXE engine.
    
    Checks for:
    - WCAG 2.1 Level A, AA, and AAA compliance
    - Common accessibility issues
    - Screen reader compatibility
    - Keyboard navigation
    """
    
    # AXE core script - this would be injected into pages
    AXE_SCRIPT_URL = "https://cdnjs.cloudflare.com/ajax/libs/axe-core/4.7.2/axe.min.js"
    
    def __init__(self):
        """Initialize accessibility auditor."""
        self.browser: Optional[Browser] = None
        self.playwright = None
    
    async def __aenter__(self):
        """Async context manager entry."""
        await self.initialize()
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit."""
        await self.close()
    
    async def initialize(self):
        """Initialize Playwright browser."""
        self.playwright = await async_playwright().start()
        self.browser = await self.playwright.chromium.launch(headless=True)
    
    async def close(self):
        """Close browser and cleanup."""
        if self.browser:
            await self.browser.close()
        if self.playwright:
            await self.playwright.stop()
    
    async def audit_url(
        self,
        url: str,
        rules: Optional[List[str]] = None,
        tags: Optional[List[str]] = None
    ) -> Dict:
        """
        Run accessibility audit on a URL.
        
        Args:
            url: URL to audit.
            rules: Specific AXE rules to run (None = all rules).
            tags: WCAG tags to check (e.g., ['wcag2a', 'wcag2aa', 'wcag21aa']).
        
        Returns:
            dict: Accessibility audit results.
        """
        if not self.browser:
            raise RuntimeError("Browser not initialized")
        
        page = await self.browser.new_page()
        
        try:
            # Navigate to page
            await page.goto(url, wait_until='networkidle', timeout=30000)
            
            # Inject AXE core
            await page.add_script_tag(url=self.AXE_SCRIPT_URL)
            
            # Wait for AXE to load
            await page.wait_for_function("typeof axe !== 'undefined'")
            
            # Configure AXE options
            options = {}
            if rules:
                options['rules'] = {rule: {'enabled': True} for rule in rules}
            if tags:
                options['runOnly'] = {'type': 'tag', 'values': tags}
            else:
                # Default to WCAG 2.1 Level AA
                options['runOnly'] = {
                    'type': 'tag',
                    'values': ['wcag2a', 'wcag2aa', 'wcag21aa']
                }
            
            # Run AXE audit
            results = await page.evaluate(f'''
                () => {{
                    return axe.run({json.dumps(options)});
                }}
            ''')
            
            # Process results
            return self._process_results(url, results)
        
        except Exception as e:
            return {
                'url': url,
                'success': False,
                'error': str(e),
            }
        
        finally:
            await page.close()
    
    def _process_results(self, url: str, axe_results: Dict) -> Dict:
        """
        Process AXE results into a structured format.
        
        Args:
            url: Audited URL.
            axe_results: Raw AXE results.
        
        Returns:
            dict: Processed accessibility report.
        """
        violations = axe_results.get('violations', [])
        passes = axe_results.get('passes', [])
        incomplete = axe_results.get('incomplete', [])
        inapplicable = axe_results.get('inapplicable', [])
        
        # Categorize violations by impact
        critical_issues = []
        serious_issues = []
        moderate_issues = []
        minor_issues = []
        
        for violation in violations:
            impact = violation.get('impact', 'moderate')
            
            issue = {
                'id': violation.get('id'),
                'description': violation.get('description'),
                'help': violation.get('help'),
                'help_url': violation.get('helpUrl'),
                'impact': impact,
                'tags': violation.get('tags', []),
                'nodes_affected': len(violation.get('nodes', [])),
                'nodes': [
                    {
                        'html': node.get('html'),
                        'target': node.get('target'),
                        'failure_summary': node.get('failureSummary'),
                    }
                    for node in violation.get('nodes', [])[:5]  # Limit to first 5
                ]
            }
            
            if impact == 'critical':
                critical_issues.append(issue)
            elif impact == 'serious':
                serious_issues.append(issue)
            elif impact == 'moderate':
                moderate_issues.append(issue)
            else:
                minor_issues.append(issue)
        
        # Calculate score
        total_violations = len(violations)
        total_checks = len(violations) + len(passes)
        score = round((1 - total_violations / max(total_checks, 1)) * 100, 2)
        
        # Determine compliance level
        if len(critical_issues) > 0 or len(serious_issues) > 5:
            compliance_level = 'Non-compliant'
        elif len(serious_issues) > 0 or len(moderate_issues) > 10:
            compliance_level = 'Partially compliant'
        elif len(moderate_issues) > 0:
            compliance_level = 'Mostly compliant'
        else:
            compliance_level = 'Fully compliant'
        
        return {
            'url': url,
            'success': True,
            'timestamp': axe_results.get('timestamp'),
            'summary': {
                'total_violations': total_violations,
                'critical': len(critical_issues),
                'serious': len(serious_issues),
                'moderate': len(moderate_issues),
                'minor': len(minor_issues),
                'passes': len(passes),
                'incomplete': len(incomplete),
                'inapplicable': len(inapplicable),
            },
            'score': score,
            'compliance_level': compliance_level,
            'violations': {
                'critical': critical_issues,
                'serious': serious_issues,
                'moderate': moderate_issues,
                'minor': minor_issues,
            },
            'wcag_tags': list(set(
                tag for violation in violations
                for tag in violation.get('tags', [])
                if tag.startswith('wcag')
            )),
        }
    
    async def batch_audit(self, urls: List[str]) -> List[Dict]:
        """
        Audit multiple URLs.
        
        Args:
            urls: List of URLs to audit.
        
        Returns:
            list: Accessibility reports for each URL.
        """
        results = []
        
        for url in urls:
            result = await self.audit_url(url)
            results.append(result)
        
        return results


async def audit_accessibility(url: str, tags: Optional[List[str]] = None) -> Dict:
    """
    Convenience function to audit a single URL.
    
    Args:
        url: URL to audit.
        tags: WCAG tags to check.
    
    Returns:
        dict: Accessibility audit results.
    """
    async with AccessibilityAuditor() as auditor:
        return await auditor.audit_url(url, tags=tags)


def generate_accessibility_report(audit_results: List[Dict]) -> Dict:
    """
    Generate aggregated accessibility report for multiple pages.
    
    Args:
        audit_results: List of audit results.
    
    Returns:
        dict: Aggregated report.
    """
    total_pages = len(audit_results)
    successful_audits = [r for r in audit_results if r.get('success')]
    
    if not successful_audits:
        return {
            'error': 'No successful audits',
        }
    
    # Aggregate stats
    total_violations = sum(
        r['summary']['total_violations']
        for r in successful_audits
    )
    
    total_critical = sum(
        r['summary']['critical']
        for r in successful_audits
    )
    
    total_serious = sum(
        r['summary']['serious']
        for r in successful_audits
    )
    
    # Find pages with most issues
    pages_by_issues = sorted(
        successful_audits,
        key=lambda x: x['summary']['total_violations'],
        reverse=True
    )
    
    # Common violations
    violation_counts = {}
    for result in successful_audits:
        for category in ['critical', 'serious', 'moderate', 'minor']:
            for violation in result['violations'][category]:
                vid = violation['id']
                if vid not in violation_counts:
                    violation_counts[vid] = {
                        'id': vid,
                        'description': violation['description'],
                        'impact': violation['impact'],
                        'count': 0,
                        'pages_affected': 0,
                    }
                violation_counts[vid]['count'] += violation['nodes_affected']
                violation_counts[vid]['pages_affected'] += 1
    
    top_violations = sorted(
        violation_counts.values(),
        key=lambda x: x['pages_affected'],
        reverse=True
    )[:10]
    
    # Calculate average score
    avg_score = sum(r['score'] for r in successful_audits) / len(successful_audits)
    
    return {
        'summary': {
            'total_pages_audited': total_pages,
            'successful_audits': len(successful_audits),
            'total_violations': total_violations,
            'total_critical': total_critical,
            'total_serious': total_serious,
            'average_score': round(avg_score, 2),
        },
        'worst_pages': [
            {
                'url': p['url'],
                'violations': p['summary']['total_violations'],
                'critical': p['summary']['critical'],
                'serious': p['summary']['serious'],
            }
            for p in pages_by_issues[:10]
        ],
        'common_violations': top_violations,
    }
