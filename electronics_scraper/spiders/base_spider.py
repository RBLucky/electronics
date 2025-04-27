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
        self.debug_mode = kwargs.get('debug', True)  # Enable debugging by default
    
    def parse(self, response):
        """
        Base parse method to be implemented by child classes.
        """
        if self.debug_mode:
            self.debug_response(response)
        raise NotImplementedError("Child spiders must implement the parse method")
    
    def debug_response(self, response):
        """
        Debug the response to identify issues with selectors.
        """
        self.logger.info(f"Status code: {response.status} for URL: {response.url}")
        
        if response.status != 200:
            self.logger.error(f"Failed to fetch page: {response.url}, Status: {response.status}")
            
            # Log headers for debugging
            self.logger.debug(f"Response Headers: {response.headers}")
            
            # Save the response body for inspection
            filename = f"debug_{self.name}_{response.status}.html"
            with open(filename, 'wb') as f:
                f.write(response.body)
            self.logger.info(f"Saved response body to {filename}")
        else:
            self.logger.info(f"Successfully fetched page: {response.url}")
    
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
        
        self.logger.debug(f"Extracting price from: {price_str}")
            
        # Remove non-numeric characters
        price_clean = re.sub(r'[^\d.,]', '', price_str)
        price_clean = price_clean.replace(',', '.')
        
        try:
            # Handle case where we have multiple dots (e.g., "1.234.56")
            parts = price_clean.split('.')
            if len(parts) > 2:
                # Keep last dot as decimal separator
                price_clean = ''.join(parts[:-1]) + '.' + parts[-1]
                
            price_value = float(price_clean)
            self.logger.debug(f"Extracted price: {price_value}")
            return price_value
        except ValueError:
            self.logger.warning(f"Could not extract price from: {price_str}")
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
        self.logger.debug(f"Creating item with name: {name}, price: {price}, url: {url}")
        
        if not currency and isinstance(price, str):
            currency = self.extract_currency(price)
        
        if isinstance(price, str):
            price = self.extract_price(price)
        
        specs = extract_specs(specs_text) if specs_text else {}
        
        item = ElectronicsItem(
            name=name,
            price=price,
            currency=currency or "ZAR",
            specs=specs,
            url=url,
            website=self.website,
            category=category,
            image_url=image_url
        )
        
        self.logger.info(f"Created item: {name} - Price: {price} {currency}")
        return item
    
    def test_selectors(self, response):
        """
        Test different selectors to help debug extraction issues.
        """
        self.logger.info("TESTING SELECTORS ON PAGE: " + response.url)
        
        # Test various selectors for product titles
        title_selectors = [
            'h1::text',
            'h1.product-title::text', 
            'h1.product-name::text',
            'h1.product-single__title::text',
            '.product-title::text',
            '.product-name::text',
            'div.title h1::text'
        ]
        
        # Test various selectors for prices
        price_selectors = [
            '.price::text',
            'span.price::text',
            '.product__price::text',
            'div.price span::text',
            'span.product-price::text',
            'div[data-qa="product-price"] span::text'
        ]
        
        # Log results for each selector
        self.logger.info("=== TITLE SELECTORS ===")
        for selector in title_selectors:
            result = response.css(selector).getall()
            self.logger.info(f"Selector '{selector}': {result}")
        
        self.logger.info("=== PRICE SELECTORS ===")
        for selector in price_selectors:
            result = response.css(selector).getall()
            self.logger.info(f"Selector '{selector}': {result}")