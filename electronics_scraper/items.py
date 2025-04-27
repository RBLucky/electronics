"""
Item definitions for the electronics scraper.
"""
import re
from datetime import datetime
import scrapy


class ElectronicsItem(scrapy.Item):
    """Data structure for storing electronics information"""
    
    # Define all fields
    name = scrapy.Field()
    price = scrapy.Field()
    currency = scrapy.Field()
    specs = scrapy.Field()
    url = scrapy.Field()
    website = scrapy.Field()
    category = scrapy.Field()
    image_url = scrapy.Field()
    timestamp = scrapy.Field()
    normalized_name = scrapy.Field()
    price_zar = scrapy.Field()
    
    def __init__(self, name=None, price=None, currency=None, specs=None, url=None, 
                 website=None, category=None, image_url=None, *args, **kwargs):
        """Initialize with optional direct attributes"""
        super(ElectronicsItem, self).__init__(*args, **kwargs)
        
        # Set provided values
        if name is not None:
            self['name'] = name.strip() if name else ""
        
        if price is not None:
            self['price'] = self._clean_price(price)
        
        if currency is not None:
            self['currency'] = currency if currency else "ZAR"  # Default to South African Rand
        
        if specs is not None:
            self['specs'] = specs if specs else {}
        
        if url is not None:
            self['url'] = url
        
        if website is not None:
            self['website'] = website
        
        if category is not None:
            self['category'] = category
        
        if image_url is not None:
            self['image_url'] = image_url
        
        # Add timestamp automatically
        self['timestamp'] = datetime.now().isoformat()
    
    def _clean_price(self, price):
        """Convert price string to float"""
        if not price:
            return None
        
        # Remove currency symbols, spaces, commas, etc.
        if isinstance(price, str):
            # Remove all non-numeric characters except for decimal points
            price = re.sub(r'[^\d.]', '', price.replace(',', '.'))
            try:
                return float(price)
            except ValueError:
                return None
        return float(price) if price else None
    
    def to_dict(self):
        """Convert item to dictionary for storage/comparison"""
        return dict(self)