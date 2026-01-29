"""
Server log file parser for Apache and Nginx logs.

Parses access logs to extract request information for SEO analysis.
"""

import re
from datetime import datetime
from typing import Dict, List, Optional, Generator
from collections import defaultdict


class LogFileParser:
    """
    Parse Apache and Nginx access logs.
    
    Supports common log formats:
    - Apache Common Log Format
    - Apache Combined Log Format
    - Nginx default format
    """
    
    # Apache Combined Log Format regex
    APACHE_COMBINED_PATTERN = re.compile(
        r'(?P<ip>[\d.]+) '
        r'- - '
        r'\[(?P<datetime>[^\]]+)\] '
        r'"(?P<method>\w+) (?P<url>[^ ]+) HTTP/[\d.]+" '
        r'(?P<status>\d+) '
        r'(?P<size>\d+|-) '
        r'"(?P<referrer>[^"]*)" '
        r'"(?P<user_agent>[^"]*)"'
    )
    
    # Nginx default format regex
    NGINX_PATTERN = re.compile(
        r'(?P<ip>[\d.]+) '
        r'- - '
        r'\[(?P<datetime>[^\]]+)\] '
        r'"(?P<method>\w+) (?P<url>[^ ]+) HTTP/[\d.]+" '
        r'(?P<status>\d+) '
        r'(?P<size>\d+) '
        r'"(?P<referrer>[^"]*)" '
        r'"(?P<user_agent>[^"]*)"'
    )
    
    def __init__(self, log_format: str = 'auto'):
        """
        Initialize log parser.
        
        Args:
            log_format: Log format ('apache', 'nginx', or 'auto' for detection).
        """
        self.log_format = log_format
    
    def parse_line(self, line: str) -> Optional[Dict]:
        """
        Parse a single log line.
        
        Args:
            line: Log line string.
        
        Returns:
            dict: Parsed log entry or None if parsing failed.
        """
        # Try Apache format first
        match = self.APACHE_COMBINED_PATTERN.match(line)
        
        if not match and self.log_format != 'apache':
            # Try Nginx format
            match = self.NGINX_PATTERN.match(line)
        
        if not match:
            return None
        
        data = match.groupdict()
        
        # Parse datetime
        try:
            dt_str = data['datetime']
            # Format: 10/Oct/2000:13:55:36 -0700
            dt = datetime.strptime(dt_str.split()[0], '%d/%b/%Y:%H:%M:%S')
            data['timestamp'] = dt
        except:
            data['timestamp'] = None
        
        # Convert status to int
        try:
            data['status'] = int(data['status'])
        except:
            data['status'] = 0
        
        # Convert size to int
        try:
            data['size'] = int(data['size']) if data['size'] != '-' else 0
        except:
            data['size'] = 0
        
        # Extract bot information
        data['is_bot'] = self._detect_bot(data['user_agent'])
        data['bot_name'] = self._identify_bot(data['user_agent'])
        
        return data
    
    def parse_file(self, file_path: str, limit: Optional[int] = None) -> List[Dict]:
        """
        Parse entire log file.
        
        Args:
            file_path: Path to log file.
            limit: Maximum number of lines to parse.
        
        Returns:
            list: List of parsed log entries.
        """
        entries = []
        
        with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
            for idx, line in enumerate(f):
                if limit and idx >= limit:
                    break
                
                entry = self.parse_line(line.strip())
                if entry:
                    entries.append(entry)
        
        return entries
    
    def parse_file_generator(self, file_path: str) -> Generator[Dict, None, None]:
        """
        Parse log file as generator for large files.
        
        Args:
            file_path: Path to log file.
        
        Yields:
            dict: Parsed log entry.
        """
        with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
            for line in f:
                entry = self.parse_line(line.strip())
                if entry:
                    yield entry
    
    def _detect_bot(self, user_agent: str) -> bool:
        """
        Detect if user agent is a bot.
        
        Args:
            user_agent: User agent string.
        
        Returns:
            bool: True if bot detected.
        """
        bot_indicators = [
            'bot', 'crawler', 'spider', 'scraper',
            'Googlebot', 'Bingbot', 'Yahoo', 'DuckDuckBot',
            'Baiduspider', 'YandexBot', 'Sogou', 'Exabot',
            'facebookexternalhit', 'ia_archiver', 'AhrefsBot',
            'SemrushBot', 'MJ12bot', 'DotBot',
        ]
        
        user_agent_lower = user_agent.lower()
        return any(indicator.lower() in user_agent_lower for indicator in bot_indicators)
    
    def _identify_bot(self, user_agent: str) -> Optional[str]:
        """
        Identify specific bot name.
        
        Args:
            user_agent: User agent string.
        
        Returns:
            str: Bot name or None if not a bot.
        """
        bots = {
            'Googlebot': 'Googlebot',
            'Bingbot': 'Bingbot',
            'Yahoo! Slurp': 'Yahoo',
            'DuckDuckBot': 'DuckDuckGo',
            'Baiduspider': 'Baidu',
            'YandexBot': 'Yandex',
            'Sogou': 'Sogou',
            'Exabot': 'Exabot',
            'facebookexternalhit': 'Facebook',
            'LinkedInBot': 'LinkedIn',
            'TwitterBot': 'Twitter',
            'Slackbot': 'Slack',
            'AhrefsBot': 'Ahrefs',
            'SemrushBot': 'Semrush',
            'MJ12bot': 'Majestic',
            'DotBot': 'DotBot',
            'Applebot': 'Apple',
        }
        
        for bot_signature, bot_name in bots.items():
            if bot_signature.lower() in user_agent.lower():
                return bot_name
        
        if self._detect_bot(user_agent):
            return 'Other Bot'
        
        return None


def parse_log_file(file_path: str, log_format: str = 'auto') -> List[Dict]:
    """
    Convenience function to parse a log file.
    
    Args:
        file_path: Path to log file.
        log_format: Log format ('apache', 'nginx', or 'auto').
    
    Returns:
        list: Parsed log entries.
    """
    parser = LogFileParser(log_format=log_format)
    return parser.parse_file(file_path)
