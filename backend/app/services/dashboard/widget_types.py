"""
Available widget types for custom dashboards.
"""

from enum import Enum
from typing import Dict, List


class WidgetType(str, Enum):
    """Available widget types."""
    
    # Overview widgets
    SEO_SCORE = "seo_score"
    TOTAL_PAGES = "total_pages"
    ERROR_COUNT = "error_count"
    PERFORMANCE_SCORE = "performance_score"
    
    # Chart widgets
    STATUS_CODE_CHART = "status_code_chart"
    RESPONSE_TIME_CHART = "response_time_chart"
    CRAWL_DEPTH_CHART = "crawl_depth_chart"
    ISSUES_TREND_CHART = "issues_trend_chart"
    
    # List widgets
    TOP_PAGES = "top_pages"
    ERROR_PAGES = "error_pages"
    SLOW_PAGES = "slow_pages"
    MISSING_META = "missing_meta"
    
    # Analysis widgets
    DUPLICATE_CONTENT = "duplicate_content"
    BROKEN_LINKS = "broken_links"
    IMAGE_ANALYSIS = "image_analysis"
    ACCESSIBILITY_SCORE = "accessibility_score"
    
    # Ranking widgets
    KEYWORD_RANKINGS = "keyword_rankings"
    RANKING_CHANGES = "ranking_changes"
    COMPETITOR_COMPARISON = "competitor_comparison"
    
    # Alert widgets
    RECENT_ALERTS = "recent_alerts"
    CRITICAL_ISSUES = "critical_issues"
    
    # Custom widgets
    CUSTOM_METRIC = "custom_metric"
    TEXT_NOTE = "text_note"


class WidgetConfiguration:
    """
    Widget configuration templates.
    """
    
    @staticmethod
    def get_available_widgets() -> List[Dict]:
        """
        Get list of available widget types with their configurations.
        
        Returns:
            list: Available widgets with metadata.
        """
        return [
            {
                'type': WidgetType.SEO_SCORE,
                'name': 'SEO Score',
                'description': 'Display overall SEO score',
                'category': 'overview',
                'default_size': {'width': 3, 'height': 2},
                'config_schema': {
                    'show_trend': {'type': 'boolean', 'default': True},
                    'time_range': {'type': 'select', 'options': ['7d', '30d', '90d'], 'default': '30d'},
                },
            },
            {
                'type': WidgetType.STATUS_CODE_CHART,
                'name': 'Status Code Distribution',
                'description': 'Pie chart showing HTTP status codes',
                'category': 'charts',
                'default_size': {'width': 6, 'height': 4},
                'config_schema': {
                    'chart_type': {'type': 'select', 'options': ['pie', 'bar', 'donut'], 'default': 'pie'},
                },
            },
            {
                'type': WidgetType.TOP_PAGES,
                'name': 'Top Pages',
                'description': 'List of top performing pages',
                'category': 'lists',
                'default_size': {'width': 6, 'height': 6},
                'config_schema': {
                    'sort_by': {'type': 'select', 'options': ['traffic', 'score', 'links'], 'default': 'score'},
                    'limit': {'type': 'number', 'default': 10, 'min': 5, 'max': 50},
                },
            },
            {
                'type': WidgetType.ERROR_PAGES,
                'name': 'Error Pages',
                'description': 'List of pages with errors',
                'category': 'lists',
                'default_size': {'width': 6, 'height': 6},
                'config_schema': {
                    'show_404_only': {'type': 'boolean', 'default': False},
                    'limit': {'type': 'number', 'default': 10},
                },
            },
            {
                'type': WidgetType.KEYWORD_RANKINGS,
                'name': 'Keyword Rankings',
                'description': 'Display keyword position tracking',
                'category': 'rankings',
                'default_size': {'width': 8, 'height': 6},
                'config_schema': {
                    'keywords': {'type': 'array', 'default': []},
                    'show_competitors': {'type': 'boolean', 'default': True},
                },
            },
            {
                'type': WidgetType.DUPLICATE_CONTENT,
                'name': 'Duplicate Content',
                'description': 'Show duplicate content groups',
                'category': 'analysis',
                'default_size': {'width': 6, 'height': 5},
                'config_schema': {
                    'similarity_threshold': {'type': 'number', 'default': 80, 'min': 50, 'max': 100},
                },
            },
            {
                'type': WidgetType.ACCESSIBILITY_SCORE,
                'name': 'Accessibility Score',
                'description': 'WCAG compliance score',
                'category': 'overview',
                'default_size': {'width': 3, 'height': 2},
                'config_schema': {
                    'standard': {'type': 'select', 'options': ['WCAG2A', 'WCAG2AA', 'WCAG2AAA'], 'default': 'WCAG2AA'},
                },
            },
            {
                'type': WidgetType.RECENT_ALERTS,
                'name': 'Recent Alerts',
                'description': 'Latest SEO alerts and warnings',
                'category': 'alerts',
                'default_size': {'width': 4, 'height': 6},
                'config_schema': {
                    'severity': {'type': 'multiselect', 'options': ['info', 'warning', 'error', 'critical'], 'default': ['warning', 'error', 'critical']},
                    'limit': {'type': 'number', 'default': 5},
                },
            },
            {
                'type': WidgetType.COMPETITOR_COMPARISON,
                'name': 'Competitor Comparison',
                'description': 'Compare metrics with competitors',
                'category': 'rankings',
                'default_size': {'width': 12, 'height': 6},
                'config_schema': {
                    'competitors': {'type': 'array', 'default': []},
                    'metrics': {'type': 'multiselect', 'options': ['seo_score', 'speed', 'accessibility'], 'default': ['seo_score']},
                },
            },
            {
                'type': WidgetType.RESPONSE_TIME_CHART,
                'name': 'Response Time Trend',
                'description': 'Line chart showing response time over time',
                'category': 'charts',
                'default_size': {'width': 8, 'height': 4},
                'config_schema': {
                    'time_range': {'type': 'select', 'options': ['24h', '7d', '30d'], 'default': '7d'},
                },
            },
            {
                'type': WidgetType.TEXT_NOTE,
                'name': 'Text Note',
                'description': 'Custom text note or annotation',
                'category': 'custom',
                'default_size': {'width': 4, 'height': 3},
                'config_schema': {
                    'content': {'type': 'textarea', 'default': ''},
                    'markdown': {'type': 'boolean', 'default': True},
                },
            },
        ]
    
    @staticmethod
    def get_widget_categories() -> List[str]:
        """Get list of widget categories."""
        return [
            'overview',
            'charts',
            'lists',
            'analysis',
            'rankings',
            'alerts',
            'custom',
        ]
    
    @staticmethod
    def validate_widget_config(widget_type: str, config: Dict) -> bool:
        """
        Validate widget configuration.
        
        Args:
            widget_type: Type of widget.
            config: Widget configuration.
        
        Returns:
            bool: True if valid.
        """
        # Simplified validation
        # In production, use proper schema validation
        return isinstance(config, dict)
    
    @staticmethod
    def get_default_layout() -> Dict:
        """
        Get default dashboard layout.
        
        Returns:
            dict: Default layout configuration.
        """
        return {
            'grid_columns': 12,
            'row_height': 60,
            'margin': [10, 10],
            'container_padding': [10, 10],
            'is_draggable': True,
            'is_resizable': True,
            'responsive_breakpoints': {
                'lg': 1200,
                'md': 996,
                'sm': 768,
                'xs': 480,
            },
        }
