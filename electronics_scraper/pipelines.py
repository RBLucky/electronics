"""
Data processing pipeline for the electronics scraper.
"""
import os
import json
import logging
import pandas as pd
from datetime import datetime

from electronics_scraper.utils.normalizer import normalize_product_name
from electronics_scraper.utils.currency import convert_to_zar
from electronics_scraper.utils.matcher import group_similar_products


class DataProcessingPipeline:
    """Pipeline for processing and analyzing scraped data"""
    
    def __init__(self):
        self.data = []
        self.file_timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        self.logger = logging.getLogger(__name__)
        # Create results directory if it doesn't exist
        os.makedirs('results', exist_ok=True)
    
    def process_item(self, item, spider):
        """Process each scraped item"""
        try:
            # Check if we have valid data
            if not item.get('name') or item.get('price') is None:
                self.logger.warning(f"Skipping item with missing essential data: {dict(item)}")
                return item

            # Add normalized product name
            item['normalized_name'] = normalize_product_name(item.get('name', ''))
            
            # Convert price to ZAR
            item['price_zar'] = convert_to_zar(item.get('price'), item.get('currency', 'ZAR'))
            
            # Create a debug-friendly string representation
            debug_info = f"{item.get('name')} - {item.get('price_zar')} - {item.get('website')}"
            self.logger.info(f"Processed item: {debug_info}")
            
            # Store processed item
            self.data.append(dict(item))
            self.logger.debug(f"Added item to data collection. Total items: {len(self.data)}")
            
            return item
        except Exception as e:
            self.logger.error(f"Error processing item: {e}")
            # Don't lose the item even if processing fails
            return item
    
    def close_spider(self, spider):
        """Process all data after spider completes"""