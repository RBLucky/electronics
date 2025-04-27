"""
Spider for BobShop electronics website.
"""
import scrapy
from electronics_scraper.spiders.base_spider import BaseSpider


class BobShopSpider(BaseSpider):
    """
    Spider for scraping electronics data from BobShop.
    """
    name = "bobshop"
    allowed_domains = ["bobshop.co.za"]
    start_urls = [
        "https://www.bobshop.co.za/cell-phones-accessories/cell-phones-smartphones/c/21949",
        "https://www.bobshop.co.za/computers-networking/ipads-tablets-ereaders/c/11448",
        "https://www.bobshop.co.za/computers-networking/laptops-notebooks/c/18836",
        "https://www.bobshop.co.za/cell-phones-accessories/smart-watches/c/18112",  # Fixed missing comma
        "https://www.bobshop.co.za/cell-phones-accessories/smart-watch-accessories/c/18113",
        "https://www.bobshop.co.za/gaming/consoles/c/10123",
    ]
    
    def __init__(self, *args, **kwargs):
        super(BobShopSpider, self).__init__(*args, **kwargs)
        self.website = "BobShop"
    
    def start_requests(self):
        """
        Start with a single URL for testing if in debug mode.
        """
        if self.debug_mode:
            self.logger.info("Starting in debug mode with a single URL")
            yield scrapy.Request(
                url=self.start_urls[0],
                callback=self.parse,
                errback=self.handle_error
            )
        else:
            for url in self.start_urls:
                yield scrapy.Request(
                    url=url,
                    callback=self.parse,
                    errback=self.handle_error
                )
    
    def handle_error(self, failure):
        """
        Handle request errors.
        """
        self.logger.error(f"Request failed: {failure.request.url}")
        self.logger.error(f"Error: {repr(failure)}")
    
    def parse(self, response):
        """
        Parse the product listing page and follow links to product pages.
        """
        # First, call debug method if enabled
        if self.debug_mode:
            self.debug_response(response)
        
        self.logger.info(f"Parsing listing page: {response.url}")
        
        # Extract product links - use multiple selectors for better chance of finding products
        product_links = []
        
        # Original selector
        links1 = response.css('div.product-item a.product-item__title::attr(href)').getall()
        
        # Alternative selectors
        links2 = response.css('div.product-item a.thumb::attr(href)').getall()
        links3 = response.css('div.product-item a[href*="/product/"]::attr(href)').getall()
        
        # Combine and deduplicate
        product_links = list(set(links1 + links2 + links3))
        
        self.logger.info(f"Found {len(product_links)} product links")
        
        # If no links found, test CSS selectors for debugging
        if not product_links and self.debug_mode:
            self.logger.warning("No product links found, testing selector alternatives")
            self.test_listing_selectors(response)
        
        # Follow each product link
        for link in product_links:
            full_url = response.urljoin(link)
            yield scrapy.Request(
                url=full_url, 
                callback=self.parse_product,
                errback=self.handle_error
            )
            
        # Follow pagination - try multiple selectors
        next_page = None
        for selector in [
            'a.pagination__next::attr(href)',
            'li.pagination-next a::attr(href)',
            'a[rel="next"]::attr(href)'
        ]:
            next_page = response.css(selector).get()
            if next_page:
                break
                
        if next_page:
            next_page_url = response.urljoin(next_page)
            self.logger.info(f"Following pagination to: {next_page_url}")
            yield scrapy.Request(
                url=next_page_url, 
                callback=self.parse,
                errback=self.handle_error
            )
        else:
            self.logger.info("No more pages to follow")
    
    def parse_product(self, response):
        """
        Parse individual product pages.
        """
        self.logger.info(f"Parsing product page: {response.url}")
        
        # First try the original selectors
        name = response.css('h1.product-single__title::text').get()
        price_str = response.css('span.product__price::text').get()
        image_url = response.css('img.product-featured-media::attr(src)').get()
        specs_text = ' '.join(response.css('div.product-single__description ::text').getall())
        category = response.css('nav.breadcrumb li:nth-child(2) a::text').get()
        
        # If primary selectors fail, try alternatives
        if not name:
            self.logger.warning("Primary name selector failed, trying alternatives")
            for selector in ['h1::text', '.product-single__title::text', '.product-title::text']:
                name = response.css(selector).get()
                if name:
                    self.logger.info(f"Found name with selector: {selector}")
                    break
                    
        if not price_str:
            self.logger.warning("Primary price selector failed, trying alternatives")
            for selector in ['.price::text', '.product-price::text', '.current-price::text']:
                price_str = response.css(selector).get()
                if price_str:
                    self.logger.info(f"Found price with selector: {selector}")
                    break
        
        # Debug output
        self.logger.info(f"Extracted name: {name}")
        self.logger.info(f"Extracted price: {price_str}")
        
        # If still no data found, test all possible selectors
        if (not name or not price_str) and self.debug_mode:
            self.test_selectors(response)
            
        # Only create item if we have the minimum required data
        if name and price_str:
            yield self.create_item(
                name=name,
                price=price_str,
                url=response.url,
                specs_text=specs_text,
                category=category,
                image_url=image_url
            )
        else:
            self.logger.warning(f"Insufficient data extracted from {response.url}")
            
    def test_listing_selectors(self, response):
        """
        Test various selectors for product listings to help debug.
        """
        self.logger.info("Testing product listing selectors")
        
        # Test various potential product link selectors
        link_selectors = [
            'div.product-item a::attr(href)',
            '.product-item__title::attr(href)',
            '.thumb::attr(href)',
            'a.product-link::attr(href)',
            'a[href*="product"]::attr(href)',
            '.product-card a::attr(href)'
        ]
        
        for selector in link_selectors:
            links = response.css(selector).getall()
            self.logger.info(f"Selector '{selector}' found {len(links)} links")
            if links:
                self.logger.info(f"Example: {links[0]}")