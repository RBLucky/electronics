# Modified settings.py - add these new settings
DOWNLOAD_DELAY = 5  # Increase from 2 to 5 seconds
RANDOMIZE_DOWNLOAD_DELAY = True

# Rotate user agents
USER_AGENT_LIST = [
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36',
    'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.1 Safari/605.1.15',
    'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36',
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:123.0) Gecko/20100101 Firefox/123.0'
]

# Add a middleware to rotate user agents
DOWNLOADER_MIDDLEWARES = {
    'scrapy.downloadermiddlewares.useragent.UserAgentMiddleware': None,
    'electronics_scraper.middlewares.RandomUserAgentMiddleware': 400,
    'electronics_scraper.middlewares.ProxyMiddleware': 350,
}

# For sites like BackMarket that require JavaScript
DOWNLOAD_HANDLERS = {
    "http": "scrapy_playwright.handler.ScrapyPlaywrightDownloadHandler",
    "https": "scrapy_playwright.handler.ScrapyPlaywrightDownloadHandler",
}

PLAYWRIGHT_LAUNCH_OPTIONS = {
    "headless": True,
    "timeout": 30 * 1000,  # 30 seconds
}