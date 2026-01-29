"""
Alert management for SEO monitoring.

Sends alerts when:
- Critical issues are detected
- Metrics drop significantly
- New errors appear
- Rankings change
"""

from typing import Dict, List, Optional
from datetime import datetime
from enum import Enum


class AlertSeverity(str, Enum):
    """Alert severity levels."""
    INFO = "info"
    WARNING = "warning"
    ERROR = "error"
    CRITICAL = "critical"


class AlertType(str, Enum):
    """Types of alerts."""
    METRIC_DROP = "metric_drop"
    METRIC_SPIKE = "metric_spike"
    NEW_ERRORS = "new_errors"
    BROKEN_LINKS = "broken_links"
    DUPLICATE_CONTENT = "duplicate_content"
    PERFORMANCE_DEGRADATION = "performance_degradation"
    ACCESSIBILITY_ISSUE = "accessibility_issue"
    CRAWL_ERROR = "crawl_error"


class AlertManager:
    """
    Manage and send SEO monitoring alerts.
    
    Supports multiple notification channels:
    - Email
    - Slack
    - Webhook
    - In-app notifications
    """
    
    def __init__(self):
        """Initialize alert manager."""
        self.alerts = []
    
    def create_alert(
        self,
        project_id: int,
        alert_type: AlertType,
        severity: AlertSeverity,
        title: str,
        message: str,
        data: Optional[Dict] = None
    ) -> Dict:
        """
        Create a new alert.
        
        Args:
            project_id: Project ID.
            alert_type: Type of alert.
            severity: Alert severity.
            title: Alert title.
            message: Alert message.
            data: Additional data.
        
        Returns:
            dict: Created alert.
        """
        alert = {
            'id': len(self.alerts) + 1,
            'project_id': project_id,
            'type': alert_type.value,
            'severity': severity.value,
            'title': title,
            'message': message,
            'data': data or {},
            'created_at': datetime.utcnow().isoformat(),
            'acknowledged': False,
        }
        
        self.alerts.append(alert)
        
        return alert
    
    def check_metric_changes(
        self,
        project_id: int,
        old_metrics: Dict,
        new_metrics: Dict,
        thresholds: Optional[Dict] = None
    ) -> List[Dict]:
        """
        Check for significant metric changes and create alerts.
        
        Args:
            project_id: Project ID.
            old_metrics: Previous metrics.
            new_metrics: Current metrics.
            thresholds: Custom thresholds for alerts (percentage).
        
        Returns:
            list: Created alerts.
        """
        if thresholds is None:
            thresholds = {
                'avg_seo_score': 10,  # Alert if score drops > 10%
                'total_issues': 20,   # Alert if issues increase > 20%
                'error_pages': 10,    # Alert if errors increase > 10%
                'success_pages': 15,  # Alert if success pages drop > 15%
            }
        
        created_alerts = []
        
        for metric_name, threshold in thresholds.items():
            if metric_name not in old_metrics or metric_name not in new_metrics:
                continue
            
            old_value = old_metrics[metric_name]
            new_value = new_metrics[metric_name]
            
            if not isinstance(old_value, (int, float)) or not isinstance(new_value, (int, float)):
                continue
            
            if old_value == 0:
                continue
            
            change_pct = ((new_value - old_value) / old_value) * 100
            
            # Determine if alert should be created
            should_alert = False
            severity = AlertSeverity.WARNING
            
            # Metrics where decrease is bad
            if metric_name in ['avg_seo_score', 'success_pages', 'pages_with_title']:
                if change_pct < -threshold:
                    should_alert = True
                    severity = AlertSeverity.ERROR if abs(change_pct) > threshold * 2 else AlertSeverity.WARNING
            
            # Metrics where increase is bad
            elif metric_name in ['total_issues', 'error_pages', 'critical_issues']:
                if change_pct > threshold:
                    should_alert = True
                    severity = AlertSeverity.ERROR if change_pct > threshold * 2 else AlertSeverity.WARNING
            
            if should_alert:
                alert = self.create_alert(
                    project_id=project_id,
                    alert_type=AlertType.METRIC_DROP if change_pct < 0 else AlertType.METRIC_SPIKE,
                    severity=severity,
                    title=f"{metric_name.replace('_', ' ').title()} Changed Significantly",
                    message=f"{metric_name} changed from {old_value} to {new_value} ({change_pct:+.1f}%)",
                    data={
                        'metric': metric_name,
                        'old_value': old_value,
                        'new_value': new_value,
                        'change_percentage': round(change_pct, 2),
                    }
                )
                created_alerts.append(alert)
        
        return created_alerts
    
    def check_new_errors(
        self,
        project_id: int,
        old_error_pages: List[str],
        new_error_pages: List[str]
    ) -> Optional[Dict]:
        """
        Check for new error pages.
        
        Args:
            project_id: Project ID.
            old_error_pages: Previous error page URLs.
            new_error_pages: Current error page URLs.
        
        Returns:
            dict: Alert if new errors found, None otherwise.
        """
        new_errors = set(new_error_pages) - set(old_error_pages)
        
        if new_errors:
            return self.create_alert(
                project_id=project_id,
                alert_type=AlertType.NEW_ERRORS,
                severity=AlertSeverity.ERROR,
                title=f"{len(new_errors)} New Error Page(s) Detected",
                message=f"Found {len(new_errors)} new error pages that were not present in the previous crawl",
                data={
                    'new_error_count': len(new_errors),
                    'new_errors': list(new_errors)[:10],  # Limit to first 10
                }
            )
        
        return None
    
    def check_broken_links(
        self,
        project_id: int,
        broken_links: List[Dict]
    ) -> Optional[Dict]:
        """
        Check for broken internal links.
        
        Args:
            project_id: Project ID.
            broken_links: List of broken link information.
        
        Returns:
            dict: Alert if broken links found.
        """
        if broken_links:
            return self.create_alert(
                project_id=project_id,
                alert_type=AlertType.BROKEN_LINKS,
                severity=AlertSeverity.WARNING,
                title=f"{len(broken_links)} Broken Link(s) Detected",
                message=f"Found {len(broken_links)} broken internal links",
                data={
                    'broken_link_count': len(broken_links),
                    'broken_links': broken_links[:10],
                }
            )
        
        return None
    
    def check_performance_degradation(
        self,
        project_id: int,
        old_avg_response_time: float,
        new_avg_response_time: float,
        threshold_ms: float = 500.0
    ) -> Optional[Dict]:
        """
        Check for performance degradation.
        
        Args:
            project_id: Project ID.
            old_avg_response_time: Previous average response time (ms).
            new_avg_response_time: Current average response time (ms).
            threshold_ms: Threshold for alerting (ms increase).
        
        Returns:
            dict: Alert if performance degraded.
        """
        increase = new_avg_response_time - old_avg_response_time
        
        if increase > threshold_ms:
            return self.create_alert(
                project_id=project_id,
                alert_type=AlertType.PERFORMANCE_DEGRADATION,
                severity=AlertSeverity.WARNING,
                title="Performance Degradation Detected",
                message=f"Average response time increased by {increase:.0f}ms "
                        f"(from {old_avg_response_time:.0f}ms to {new_avg_response_time:.0f}ms)",
                data={
                    'old_avg_response_time': old_avg_response_time,
                    'new_avg_response_time': new_avg_response_time,
                    'increase_ms': increase,
                }
            )
        
        return None
    
    async def send_alert(self, alert: Dict, channels: List[str]) -> Dict:
        """
        Send alert to specified channels.
        
        Args:
            alert: Alert dictionary.
            channels: List of channels to send to (email, slack, webhook).
        
        Returns:
            dict: Send results.
        """
        results = {}
        
        for channel in channels:
            if channel == 'email':
                results['email'] = await self._send_email(alert)
            elif channel == 'slack':
                results['slack'] = await self._send_slack(alert)
            elif channel == 'webhook':
                results['webhook'] = await self._send_webhook(alert)
        
        return results
    
    async def _send_email(self, alert: Dict) -> bool:
        """Send alert via email (placeholder)."""
        # Implement email sending logic
        return True
    
    async def _send_slack(self, alert: Dict) -> bool:
        """Send alert to Slack (placeholder)."""
        # Implement Slack integration
        return True
    
    async def _send_webhook(self, alert: Dict) -> bool:
        """Send alert to webhook (placeholder)."""
        # Implement webhook posting
        return True
    
    def get_alerts(
        self,
        project_id: Optional[int] = None,
        severity: Optional[AlertSeverity] = None,
        limit: int = 50
    ) -> List[Dict]:
        """
        Get alerts with optional filters.
        
        Args:
            project_id: Filter by project ID.
            severity: Filter by severity.
            limit: Maximum alerts to return.
        
        Returns:
            list: Filtered alerts.
        """
        filtered = self.alerts
        
        if project_id is not None:
            filtered = [a for a in filtered if a['project_id'] == project_id]
        
        if severity is not None:
            filtered = [a for a in filtered if a['severity'] == severity.value]
        
        # Sort by created_at descending
        filtered.sort(key=lambda x: x['created_at'], reverse=True)
        
        return filtered[:limit]
