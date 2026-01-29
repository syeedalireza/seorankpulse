"""
Historical data tracking for SEO metrics over time.

Tracks changes in:
- SEO scores
- Page rankings
- Technical issues
- Content changes
- Link structure
"""

from datetime import datetime, timedelta
from typing import Dict, List, Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_, desc
import json


class HistoricalTracker:
    """
    Track SEO metrics over time for trend analysis.
    
    Stores snapshots of:
    - Page metrics
    - SEO scores
    - Issue counts
    - Performance metrics
    """
    
    def __init__(self, db: AsyncSession):
        """
        Initialize historical tracker.
        
        Args:
            db: Database session.
        """
        self.db = db
    
    async def save_snapshot(
        self,
        project_id: int,
        crawl_job_id: int,
        metrics: Dict
    ) -> Dict:
        """
        Save a snapshot of current metrics.
        
        Args:
            project_id: Project ID.
            crawl_job_id: Crawl job ID.
            metrics: Dictionary of metrics to save.
        
        Returns:
            dict: Saved snapshot info.
        """
        # This would save to a dedicated historical_snapshots table
        # For now, we'll return the structure
        
        snapshot = {
            'project_id': project_id,
            'crawl_job_id': crawl_job_id,
            'timestamp': datetime.utcnow().isoformat(),
            'metrics': metrics,
        }
        
        return snapshot
    
    async def get_snapshots(
        self,
        project_id: int,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None,
        limit: int = 100
    ) -> List[Dict]:
        """
        Retrieve historical snapshots for a project.
        
        Args:
            project_id: Project ID.
            start_date: Optional start date filter.
            end_date: Optional end date filter.
            limit: Maximum number of snapshots to return.
        
        Returns:
            list: Historical snapshots.
        """
        # Placeholder - would query historical_snapshots table
        return []
    
    async def compare_snapshots(
        self,
        snapshot1_id: int,
        snapshot2_id: int
    ) -> Dict:
        """
        Compare two snapshots to identify changes.
        
        Args:
            snapshot1_id: First snapshot ID (older).
            snapshot2_id: Second snapshot ID (newer).
        
        Returns:
            dict: Comparison results with changes.
        """
        # Placeholder implementation
        return {
            'snapshot1_id': snapshot1_id,
            'snapshot2_id': snapshot2_id,
            'changes': [],
        }
    
    def calculate_trends(self, snapshots: List[Dict]) -> Dict:
        """
        Calculate trends from historical snapshots.
        
        Args:
            snapshots: List of snapshots ordered by time.
        
        Returns:
            dict: Trend analysis.
        """
        if len(snapshots) < 2:
            return {
                'error': 'Need at least 2 snapshots to calculate trends',
            }
        
        # Extract metrics over time
        metrics_over_time = {}
        
        for snapshot in snapshots:
            timestamp = snapshot.get('timestamp')
            metrics = snapshot.get('metrics', {})
            
            for metric_name, metric_value in metrics.items():
                if metric_name not in metrics_over_time:
                    metrics_over_time[metric_name] = []
                
                metrics_over_time[metric_name].append({
                    'timestamp': timestamp,
                    'value': metric_value,
                })
        
        # Calculate trends for each metric
        trends = {}
        
        for metric_name, values in metrics_over_time.items():
            if len(values) < 2:
                continue
            
            first_value = values[0]['value']
            last_value = values[-1]['value']
            
            # Calculate change
            if isinstance(first_value, (int, float)) and isinstance(last_value, (int, float)):
                if first_value == 0:
                    change_pct = 0 if last_value == 0 else 100
                else:
                    change_pct = ((last_value - first_value) / first_value) * 100
                
                trend = 'increasing' if change_pct > 0 else 'decreasing' if change_pct < 0 else 'stable'
                
                trends[metric_name] = {
                    'first_value': first_value,
                    'last_value': last_value,
                    'change': last_value - first_value,
                    'change_percentage': round(change_pct, 2),
                    'trend': trend,
                    'data_points': len(values),
                }
        
        return {
            'period': {
                'start': snapshots[0].get('timestamp'),
                'end': snapshots[-1].get('timestamp'),
                'snapshots': len(snapshots),
            },
            'trends': trends,
        }
    
    def detect_anomalies(self, snapshots: List[Dict], threshold: float = 20.0) -> List[Dict]:
        """
        Detect anomalies in metrics (sudden changes).
        
        Args:
            snapshots: List of snapshots ordered by time.
            threshold: Percentage change threshold to flag as anomaly.
        
        Returns:
            list: Detected anomalies.
        """
        anomalies = []
        
        if len(snapshots) < 2:
            return anomalies
        
        # Compare consecutive snapshots
        for i in range(1, len(snapshots)):
            prev_snapshot = snapshots[i - 1]
            curr_snapshot = snapshots[i]
            
            prev_metrics = prev_snapshot.get('metrics', {})
            curr_metrics = curr_snapshot.get('metrics', {})
            
            # Check each metric
            for metric_name in prev_metrics.keys():
                if metric_name not in curr_metrics:
                    continue
                
                prev_value = prev_metrics[metric_name]
                curr_value = curr_metrics[metric_name]
                
                if not isinstance(prev_value, (int, float)) or not isinstance(curr_value, (int, float)):
                    continue
                
                if prev_value == 0:
                    change_pct = 0 if curr_value == 0 else 100
                else:
                    change_pct = abs((curr_value - prev_value) / prev_value * 100)
                
                if change_pct >= threshold:
                    anomalies.append({
                        'metric': metric_name,
                        'timestamp': curr_snapshot.get('timestamp'),
                        'previous_value': prev_value,
                        'current_value': curr_value,
                        'change_percentage': round(change_pct, 2),
                        'severity': 'critical' if change_pct >= 50 else 'high' if change_pct >= 30 else 'medium',
                    })
        
        return anomalies


def create_metrics_snapshot(crawl_data: Dict, analysis_data: Dict) -> Dict:
    """
    Create a metrics snapshot from crawl and analysis data.
    
    Args:
        crawl_data: Crawl results data.
        analysis_data: Analysis results data.
    
    Returns:
        dict: Metrics snapshot.
    """
    return {
        # Crawl metrics
        'total_pages': crawl_data.get('total_pages', 0),
        'success_pages': crawl_data.get('success_count', 0),
        'error_pages': crawl_data.get('error_count', 0),
        'redirect_pages': crawl_data.get('redirect_count', 0),
        
        # Performance metrics
        'avg_response_time': crawl_data.get('avg_response_time', 0),
        'avg_page_size': crawl_data.get('avg_page_size', 0),
        
        # SEO metrics
        'avg_seo_score': analysis_data.get('avg_seo_score', 0),
        'pages_with_title': analysis_data.get('pages_with_title', 0),
        'pages_with_meta_desc': analysis_data.get('pages_with_meta_desc', 0),
        'pages_with_h1': analysis_data.get('pages_with_h1', 0),
        
        # Issue counts
        'total_issues': analysis_data.get('total_issues', 0),
        'critical_issues': analysis_data.get('critical_issues', 0),
        'duplicate_content_groups': analysis_data.get('duplicate_groups', 0),
        
        # Link metrics
        'orphan_pages': analysis_data.get('orphan_pages', 0),
        'avg_internal_links': analysis_data.get('avg_internal_links', 0),
        
        # Image metrics
        'total_images': analysis_data.get('total_images', 0),
        'images_without_alt': analysis_data.get('images_without_alt', 0),
    }
