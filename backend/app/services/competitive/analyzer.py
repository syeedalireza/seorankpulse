"""
Multi-site competitive analysis.

Compare your site with competitors on:
- Technical SEO
- Content quality
- Performance
- Rankings
- Backlinks (via API integration)
"""

from typing import Dict, List, Optional
from collections import defaultdict


class CompetitiveAnalyzer:
    """
    Analyze and compare multiple sites for competitive intelligence.
    
    Provides:
    - Side-by-side comparisons
    - Competitive gap analysis
    - Strength/weakness identification
    - Market positioning
    """
    
    def __init__(self):
        """Initialize competitive analyzer."""
        pass
    
    def compare_sites(
        self,
        your_site_data: Dict,
        competitor_data: List[Dict]
    ) -> Dict:
        """
        Compare your site with competitors.
        
        Args:
            your_site_data: Your site's crawl and analysis data.
            competitor_data: List of competitor site data.
        
        Returns:
            dict: Comparative analysis.
        """
        comparison = {
            'your_site': self._extract_metrics(your_site_data),
            'competitors': [
                {
                    'domain': comp.get('domain'),
                    'metrics': self._extract_metrics(comp),
                }
                for comp in competitor_data
            ],
        }
        
        # Add comparative insights
        comparison['insights'] = self._generate_insights(comparison)
        comparison['rankings'] = self._calculate_rankings(comparison)
        
        return comparison
    
    def _extract_metrics(self, site_data: Dict) -> Dict:
        """
        Extract key metrics from site data.
        
        Args:
            site_data: Site crawl data.
        
        Returns:
            dict: Extracted metrics.
        """
        return {
            # Technical metrics
            'total_pages': site_data.get('total_pages', 0),
            'avg_response_time': site_data.get('avg_response_time', 0),
            'error_pages': site_data.get('error_count', 0),
            'error_rate': site_data.get('error_rate', 0),
            
            # SEO metrics
            'avg_seo_score': site_data.get('avg_seo_score', 0),
            'pages_with_title': site_data.get('pages_with_title', 0),
            'pages_with_meta_desc': site_data.get('pages_with_meta_desc', 0),
            'avg_title_length': site_data.get('avg_title_length', 0),
            'avg_meta_desc_length': site_data.get('avg_meta_desc_length', 0),
            
            # Content metrics
            'avg_word_count': site_data.get('avg_word_count', 0),
            'avg_internal_links': site_data.get('avg_internal_links', 0),
            
            # Performance
            'avg_page_size': site_data.get('avg_page_size', 0),
            'core_web_vitals_score': site_data.get('cwv_score', 0),
            
            # Accessibility
            'accessibility_score': site_data.get('accessibility_score', 0),
            
            # Issues
            'critical_issues': site_data.get('critical_issues', 0),
            'total_issues': site_data.get('total_issues', 0),
        }
    
    def _generate_insights(self, comparison: Dict) -> Dict:
        """
        Generate competitive insights.
        
        Args:
            comparison: Comparison data.
        
        Returns:
            dict: Insights and recommendations.
        """
        your_metrics = comparison['your_site']
        competitor_metrics = [c['metrics'] for c in comparison['competitors']]
        
        insights = {
            'advantages': [],
            'disadvantages': [],
            'opportunities': [],
        }
        
        # Compare each metric
        metrics_to_compare = [
            ('avg_seo_score', 'higher_better', 'SEO Score'),
            ('avg_response_time', 'lower_better', 'Response Time'),
            ('error_rate', 'lower_better', 'Error Rate'),
            ('avg_word_count', 'higher_better', 'Content Length'),
            ('accessibility_score', 'higher_better', 'Accessibility'),
        ]
        
        for metric_key, direction, metric_name in metrics_to_compare:
            your_value = your_metrics.get(metric_key, 0)
            
            if not competitor_metrics:
                continue
            
            comp_values = [c.get(metric_key, 0) for c in competitor_metrics if c.get(metric_key)]
            
            if not comp_values:
                continue
            
            avg_comp = sum(comp_values) / len(comp_values)
            best_comp = max(comp_values) if direction == 'higher_better' else min(comp_values)
            
            # Determine if you're ahead or behind
            if direction == 'higher_better':
                if your_value > avg_comp:
                    insights['advantages'].append(
                        f"{metric_name}: You're {((your_value - avg_comp) / avg_comp * 100):.1f}% above average"
                    )
                elif your_value < avg_comp:
                    insights['disadvantages'].append(
                        f"{metric_name}: You're {((avg_comp - your_value) / avg_comp * 100):.1f}% below average"
                    )
                    insights['opportunities'].append(
                        f"Improve {metric_name} to match competitors"
                    )
            else:  # lower_better
                if your_value < avg_comp:
                    insights['advantages'].append(
                        f"{metric_name}: You're {((avg_comp - your_value) / avg_comp * 100):.1f}% better than average"
                    )
                elif your_value > avg_comp:
                    insights['disadvantages'].append(
                        f"{metric_name}: You're {((your_value - avg_comp) / avg_comp * 100):.1f}% worse than average"
                    )
                    insights['opportunities'].append(
                        f"Reduce {metric_name} to match competitors"
                    )
        
        return insights
    
    def _calculate_rankings(self, comparison: Dict) -> Dict:
        """
        Calculate where you rank among competitors for each metric.
        
        Args:
            comparison: Comparison data.
        
        Returns:
            dict: Rankings for each metric.
        """
        all_sites = [comparison['your_site']] + [c['metrics'] for c in comparison['competitors']]
        total_sites = len(all_sites)
        
        rankings = {}
        
        # Metrics where higher is better
        higher_better = ['avg_seo_score', 'avg_word_count', 'accessibility_score']
        
        # Metrics where lower is better
        lower_better = ['avg_response_time', 'error_rate', 'total_issues']
        
        for metric in higher_better:
            values = [(i, site.get(metric, 0)) for i, site in enumerate(all_sites)]
            sorted_values = sorted(values, key=lambda x: x[1], reverse=True)
            
            your_rank = next(idx + 1 for idx, (site_idx, val) in enumerate(sorted_values) if site_idx == 0)
            
            rankings[metric] = {
                'rank': your_rank,
                'total': total_sites,
                'percentile': round((total_sites - your_rank) / total_sites * 100, 1),
            }
        
        for metric in lower_better:
            values = [(i, site.get(metric, 0)) for i, site in enumerate(all_sites)]
            sorted_values = sorted(values, key=lambda x: x[1])
            
            your_rank = next(idx + 1 for idx, (site_idx, val) in enumerate(sorted_values) if site_idx == 0)
            
            rankings[metric] = {
                'rank': your_rank,
                'total': total_sites,
                'percentile': round((total_sites - your_rank) / total_sites * 100, 1),
            }
        
        return rankings
    
    def generate_competitive_matrix(
        self,
        sites_data: List[Dict]
    ) -> Dict:
        """
        Generate competitive matrix showing all sites.
        
        Args:
            sites_data: List of all sites to compare.
        
        Returns:
            dict: Competitive matrix.
        """
        matrix = {
            'sites': [],
            'metrics': [
                'SEO Score',
                'Response Time',
                'Error Rate',
                'Content Quality',
                'Accessibility',
                'Performance',
            ],
        }
        
        for site in sites_data:
            metrics = self._extract_metrics(site)
            
            matrix['sites'].append({
                'domain': site.get('domain'),
                'metrics': {
                    'SEO Score': metrics.get('avg_seo_score', 0),
                    'Response Time': metrics.get('avg_response_time', 0),
                    'Error Rate': metrics.get('error_rate', 0),
                    'Content Quality': metrics.get('avg_word_count', 0),
                    'Accessibility': metrics.get('accessibility_score', 0),
                    'Performance': metrics.get('core_web_vitals_score', 0),
                },
            })
        
        return matrix


async def compare_competitors(
    your_domain: str,
    your_data: Dict,
    competitors: List[Dict]
) -> Dict:
    """
    Convenience function to compare with competitors.
    
    Args:
        your_domain: Your domain.
        your_data: Your site data.
        competitors: List of competitor data.
    
    Returns:
        dict: Competitive analysis.
    """
    analyzer = CompetitiveAnalyzer()
    return analyzer.compare_sites(your_data, competitors)
