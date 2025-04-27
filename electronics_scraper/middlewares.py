"""
Custom middlewares for the electronics scraper.
"""
import random
import logging
from scrapy.downloadermiddlewares.useragent import UserAgentMiddleware


class RandomUserAgentMiddleware(UserAgentMiddleware):
    """Middleware to rotate user agents."""
    
    def __init__(self, user_agent_list):
        self.user_agent_list = user_agent_list
        self.logger = logging.getLogger(__name__)

    @classmethod
    def from_crawler(cls, crawler):
        user_agent_list = crawler.settings.getlist('USER_AGENT_LIST')
        if not user_agent_list:
            user_agent_list = [crawler.settings.get('USER_AGENT')]
        return cls(user_agent_list)

    def process_request(self, request, spider):
        user_agent = random.choice(self.user_agent_list)
        request.headers['User-Agent'] = user_agent
        self.logger.debug(f"Using User-Agent: {user_agent}")
        
        # Add common headers to make requests look more like a browser
        request.headers['Accept'] = 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8'
        request.headers['Accept-Language'] = 'en-US,en;q=0.5'
        request.headers['Accept-Encoding'] = 'gzip, deflate, br'
        request.headers['Connection'] = 'keep-alive'
        request.headers['Upgrade-Insecure-Requests'] = '1'
        request.headers['Sec-Fetch-Dest'] = 'document'
        request.headers['Sec-Fetch-Mode'] = 'navigate'
        request.headers['Sec-Fetch-Site'] = 'none'
        request.headers['Sec-Fetch-User'] = '?1'
        request.headers['DNT'] = '1'


class ProxyMiddleware:
    """Middleware to rotate proxies."""
    
    def __init__(self, proxy_list):
        self.proxy_list = proxy_list
        self.logger = logging.getLogger(__name__)
    
    @classmethod
    def from_crawler(cls, crawler):
        # You would normally get these from a config file or environment variables
        # For demo purposes using placeholder proxies - replace with real ones
        proxy_list = [
            'http://proxy1.example.com:8080',
            'http://proxy2.example.com:8080',
            'http://proxy3.example.com:8080',
        ]
        return cls(proxy_list)
    
    def process_request(self, request, spider):
        # Only use proxies for certain domains that need them
        if 'backmarket.com' in request.url:
            proxy = random.choice(self.proxy_list)
            request.meta['proxy'] = proxy
            self.logger.debug(f"Using proxy: {proxy} for {request.url}")