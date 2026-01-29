"""
Log file analyzer for SEO insights and crawl budget analysis.

Analyzes parsed log data to provide insights about:
- Googlebot crawl behavior
- Crawl budget usage
- Status code distribution
- Most crawled pages
- Crawl errors
"""

from collections import defaultdict, Counter
from datetime import datetime, timedelta
from typing import Dict, List


class LogAnalyzer:
    """
    Analyze server logs for SEO insights.
    
    Provides analysis of:
    - Bot traffic patterns
    - Crawl budget consumption
    - Popular pages
    - Error patterns
    - Response time analysis
    """
    
    def __init__(self, log_entries: List[Dict]):
        """
        Initialize log analyzer.
        
        Args:
            log_entries: List of parsed log entries.
        """
        self.entries = log_entries
        self.bot_entries = [e for e in log_entries if e.get('is_bot')]
        self.user_entries = [e for e in log_entries if not e.get('is_bot')]
    
    def analyze_crawl_budget(self, bot_name: str = 'Googlebot') -> Dict:
        """
        Analyze crawl budget usage for a specific bot.
        
        Args:
            bot_name: Name of the bot to analyze (e.g., 'Googlebot').
        
        Returns:
            dict: Crawl budget analysis.
        """
        bot_requests = [
            e for e in self.bot_entries
            if e.get('bot_name') == bot_name
        ]
        
        if not bot_requests:
            return {
                'bot': bot_name,
                'total_requests': 0,
                'error': 'No requests found for this bot',
            }
        
        # Time range
        timestamps = [e['timestamp'] for e in bot_requests if e.get('timestamp')]
        if timestamps:
            start_time = min(timestamps)
            end_time = max(timestamps)
            duration_days = (end_time - start_time).days + 1
        else:
            duration_days = 1
        
        # Requests per day
        daily_requests = len(bot_requests) / duration_days if duration_days > 0 else 0
        
        # Status code distribution
        status_codes = Counter(e['status'] for e in bot_requests)
        
        # Most crawled URLs
        url_counts = Counter(e['url'] for e in bot_requests)
        top_urls = url_counts.most_common(20)
        
        # Response size stats
        sizes = [e['size'] for e in bot_requests if e.get('size', 0) > 0]
        avg_size = sum(sizes) / len(sizes) if sizes else 0
        total_bandwidth = sum(sizes)
        
        # Hourly distribution
        hourly_dist = defaultdict(int)
        for entry in bot_requests:
            if entry.get('timestamp'):
                hour = entry['timestamp'].hour
                hourly_dist[hour] += 1
        
        return {
            'bot': bot_name,
            'total_requests': len(bot_requests),
            'date_range': {
                'start': start_time.isoformat() if timestamps else None,
                'end': end_time.isoformat() if timestamps else None,
                'duration_days': duration_days,
            },
            'requests_per_day': round(daily_requests, 2),
            'status_codes': dict(status_codes),
            'success_rate': round(
                status_codes.get(200, 0) / len(bot_requests) * 100, 2
            ) if bot_requests else 0,
            'top_crawled_urls': [
                {'url': url, 'count': count}
                for url, count in top_urls
            ],
            'bandwidth': {
                'total_bytes': total_bandwidth,
                'total_mb': round(total_bandwidth / 1024 / 1024, 2),
                'average_response_size': round(avg_size, 2),
            },
            'hourly_distribution': dict(hourly_dist),
        }
    
    def analyze_all_bots(self) -> List[Dict]:
        """
        Analyze crawl patterns for all detected bots.
        
        Returns:
            list: Analysis for each bot.
        """
        bot_names = set(e.get('bot_name') for e in self.bot_entries if e.get('bot_name'))
        
        analyses = []
        for bot_name in bot_names:
            analysis = self.analyze_crawl_budget(bot_name)
            analyses.append(analysis)
        
        # Sort by request count
        analyses.sort(key=lambda x: x.get('total_requests', 0), reverse=True)
        
        return analyses
    
    def analyze_status_codes(self) -> Dict:
        """
        Analyze status code distribution.
        
        Returns:
            dict: Status code statistics.
        """
        status_codes = Counter(e['status'] for e in self.entries)
        total = len(self.entries)
        
        # Categorize
        success = sum(count for code, count in status_codes.items() if 200 <= code < 300)
        redirects = sum(count for code, count in status_codes.items() if 300 <= code < 400)
        client_errors = sum(count for code, count in status_codes.items() if 400 <= code < 500)
        server_errors = sum(count for code, count in status_codes.items() if code >= 500)
        
        return {
            'total_requests': total,
            'status_distribution': dict(status_codes),
            'categories': {
                '2xx_success': success,
                '3xx_redirects': redirects,
                '4xx_client_errors': client_errors,
                '5xx_server_errors': server_errors,
            },
            'percentages': {
                'success_rate': round(success / total * 100, 2) if total > 0 else 0,
                'error_rate': round((client_errors + server_errors) / total * 100, 2) if total > 0 else 0,
            },
        }
    
    def find_error_urls(self, min_status: int = 400) -> List[Dict]:
        """
        Find URLs with errors.
        
        Args:
            min_status: Minimum status code to consider as error (default 400).
        
        Returns:
            list: URLs with error counts.
        """
        error_entries = [e for e in self.entries if e['status'] >= min_status]
        
        url_errors = defaultdict(lambda: {'count': 0, 'status_codes': Counter()})
        
        for entry in error_entries:
            url = entry['url']
            status = entry['status']
            url_errors[url]['count'] += 1
            url_errors[url]['status_codes'][status] += 1
        
        # Convert to list and sort by count
        error_list = [
            {
                'url': url,
                'total_errors': data['count'],
                'status_codes': dict(data['status_codes']),
            }
            for url, data in url_errors.items()
        ]
        
        error_list.sort(key=lambda x: x['total_errors'], reverse=True)
        
        return error_list
    
    def analyze_popular_pages(self, limit: int = 50) -> List[Dict]:
        """
        Find most requested pages.
        
        Args:
            limit: Number of top pages to return.
        
        Returns:
            list: Most popular pages with request counts.
        """
        url_counts = Counter(e['url'] for e in self.entries)
        
        return [
            {'url': url, 'requests': count}
            for url, count in url_counts.most_common(limit)
        ]
    
    def analyze_bot_vs_user_traffic(self) -> Dict:
        """
        Compare bot traffic vs user traffic.
        
        Returns:
            dict: Comparison statistics.
        """
        total = len(self.entries)
        bot_count = len(self.bot_entries)
        user_count = len(self.user_entries)
        
        return {
            'total_requests': total,
            'bot_requests': bot_count,
            'user_requests': user_count,
            'bot_percentage': round(bot_count / total * 100, 2) if total > 0 else 0,
            'user_percentage': round(user_count / total * 100, 2) if total > 0 else 0,
        }
    
    def analyze_time_patterns(self) -> Dict:
        """
        Analyze request patterns over time.
        
        Returns:
            dict: Time-based analysis.
        """
        entries_with_time = [e for e in self.entries if e.get('timestamp')]
        
        if not entries_with_time:
            return {'error': 'No timestamp data available'}
        
        # Daily distribution
        daily_counts = defaultdict(int)
        for entry in entries_with_time:
            date = entry['timestamp'].date()
            daily_counts[date.isoformat()] += 1
        
        # Hourly distribution
        hourly_counts = defaultdict(int)
        for entry in entries_with_time:
            hour = entry['timestamp'].hour
            hourly_counts[hour] += 1
        
        # Day of week distribution
        dow_counts = defaultdict(int)
        for entry in entries_with_time:
            dow = entry['timestamp'].strftime('%A')
            dow_counts[dow] += 1
        
        return {
            'daily_distribution': dict(daily_counts),
            'hourly_distribution': dict(hourly_counts),
            'day_of_week_distribution': dict(dow_counts),
        }


def analyze_crawl_budget(log_entries: List[Dict], bot_name: str = 'Googlebot') -> Dict:
    """
    Convenience function to analyze crawl budget.
    
    Args:
        log_entries: Parsed log entries.
        bot_name: Bot to analyze.
    
    Returns:
        dict: Crawl budget analysis.
    """
    analyzer = LogAnalyzer(log_entries)
    return analyzer.analyze_crawl_budget(bot_name)
