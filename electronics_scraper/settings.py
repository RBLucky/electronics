"""
Scrapy settings for electronics_scraper project.
"""

BOT_NAME = 'electronics_scraper'

SPIDER_MODULES = ['electronics_scraper.spiders']
NEWSPIDER_MODULE = 'electronics_scraper.spiders'

# Crawl responsibly by identifying yourself to websites
USER_AGENT = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'

# Obey robots.txt rules
ROBOTSTXT_OBEY = True

# Configure maximum concurrent requests performed by Scrapy
CONCURRENT_REQUESTS = 8
CONCURRENT_REQUESTS_PER_DOMAIN = 2

# Configure a delay for requests to avoid overloading servers (in seconds)
DOWNLOAD_DELAY = 2

# Disable cookies for enhanced privacy
COOKIES_ENABLED = False

# Configure item pipelines
ITEM_PIPELINES = {
    'electronics_scraper.pipelines.DataProcessingPipeline': 300,
}

# Enable and configure the AutoThrottle extension
AUTOTHROTTLE_ENABLED = True
# The initial delay (in seconds)
AUTOTHROTTLE_START_DELAY = 5
# The maximum delay (in seconds)
AUTOTHROTTLE_MAX_DELAY = 60
# Average number of requests Scrapy should be sending in parallel
AUTOTHROTTLE_TARGET_CONCURRENCY = 1.0
# Enable showing throttling stats for every response received
AUTOTHROTTLE_DEBUG = False

# Set settings whose default value is deprecated to a future-proof value
REQUEST_FINGERPRINTER_IMPLEMENTATION = '2.7'
TWISTED_REACTOR = 'twisted.internet.asyncioreactor.AsyncioSelectorReactor'
FEED_EXPORT_ENCODING = 'utf-8'

# Output encoding
FEED_EXPORT_ENCODING = 'utf-8'

# Log level
LOG_LEVEL = 'INFO'