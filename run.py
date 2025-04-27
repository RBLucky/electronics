#!/usr/bin/env python
"""
Main script to run the electronics price comparison system.
"""
import os
import sys
import logging
from datetime import datetime
from scrapy.crawler import CrawlerProcess
from scrapy.utils.project import get_project_settings

# Ensure the project's directory is in the Python path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from electronics_scraper.spiders.bobshop_spider import BobShopSpider
from electronics_scraper.spiders.revibe_spider import RevibeSpider
from electronics_scraper.spiders.istore_spider import IStorePreOwnedSpider
from electronics_scraper.spiders.gorilla_spider import GorillaPhoneSpider
from electronics_scraper.spiders.backmarket_spider import BackMarketSpider


def setup_logging():
    """Set up logging configuration"""
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    os.makedirs('logs', exist_ok=True)
    
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s [%(levelname)s] %(message)s",
        handlers=[
            logging.FileHandler(f"logs/scraper_{timestamp}.log"),
            logging.StreamHandler()
        ]
    )


def run_spiders():
    """Run all spiders to collect and process electronics data"""
    # Ensure directories exist
    os.makedirs('results', exist_ok=True)
    
    # Set up logging
    setup_logging()
    
    logging.info("Starting electronics price comparison crawler...")
    
    # Get project settings
    settings = get_project_settings()
    
    # Initialize crawler process
    process = CrawlerProcess(settings)
    
    # Register spiders to crawl
    spiders = [
        BobShopSpider,
        RevibeSpider,
        IStorePreOwnedSpider,
        GorillaPhoneSpider,
        BackMarketSpider
    ]
    
    for spider_class in spiders:
        logging.info(f"Adding spider: {spider_class.name}")
        process.crawl(spider_class)
    
    # Start crawling
    logging.info("Starting crawl process")
    process.start()
    
    logging.info("Crawling completed. Check the 'results' directory for opportunities.")


if __name__ == "__main__":
    run_spiders()