"""
Base spider class with common functionality for all electronics spiders.
"""
import re
import scrapy
from electronics_scraper.items import ElectronicsItem
from electronics_scraper.utils.normalizer import extract_specs


class BaseSpider(scrapy.Spider):
    """
    Base spider class for electronics websites with common functionality.
    """
    
    # Override these in child classes
    name = "base"
    allowed_domains = []
    start_urls = []
    
    def __init__(self, *args, **kwargs):
        super(BaseSpider, self).__init__(*args, **kwargs)
        self.website = None  # Override in child classes
    
    def parse(self, response):
        """
        Base parse method to be implemented by child classes.
        """
        raise NotImplementedError("Child spiders must implement the parse method")
    
    def extract_price(self, price_str):
        """
        Extract price from a string and return a float.
        
        Args:
            price_str (str): String containing the price
            
        Returns:
            float: Extracted price value
        """
        if not price_str:
            return None
            
        # Remove non-numeric characters
        price_clean = re.sub(r'[^\d.,]', '', price_str)
        price_clean = price_clean.replace(',', '.')
        
        try:
            # Handle case where we have multiple dots (e.g., "1.234.56")
            parts = price_clean.split('.')
            if len(parts) > 2:
                # Keep last dot as decimal separator
                price_clean = ''.join(parts[:-1]) + '.' + parts[-1]
                
            return float(price_clean)
        except ValueError:
            return None
    
    def extract_currency(self, price_str):
        """
        Extract currency symbol from price string.
        
        Args:
            price_str (str): String containing the price with currency
            
        Returns:
            str: Currency code (ZAR, USD, EUR, etc.)
        """
        if not price_str:
            return "ZAR"  # Default currency
        
        # Common currency symbols mapped to codes
        currency_map = {
            'R': 'ZAR',
            '$': 'USD',
            '€': 'EUR',
            '£': 'GBP'
        }
        
        # Extract currency symbol
        for symbol, code in currency_map.items():
            if symbol in price_str:
                return code
        
        return "ZAR"  # Default to ZAR
    
    def create_item(self, name, price, url, specs_text=None, currency=None, 
                   category=None, image_url=None):
        """
        Create an ElectronicsItem with the given parameters.
        
        Args:
            name (str): Product name
            price (str or float): Product price
            url (str): Product page URL
            specs_text (str): Text containing specifications
            currency (str): Currency code
            category (str): Product category
            image_url (str): Product image URL
            
        Returns:
            ElectronicsItem: The created item
        """
        if not currency and isinstance(price, str):
            currency = self.extract_currency(price)
        
        if isinstance(price, str):
            price = self.extract_price(price)
        
        specs = extract_specs(specs_text) if specs_text else {}
        
        return ElectronicsItem(
            name=name,
            price=price,
            currency=currency or "ZAR",
            specs=specs,
            url=url,
            website=self.website,
            category=category,
            image_url=image_url
        )