"""
Spider for BackMarket electronics website.
"""
import scrapy
from electronics_scraper.spiders.base_spider import BaseSpider


class BackMarketSpider(BaseSpider):
    """
    Spider for scraping electronics data from BackMarket.
    """
    name = "backmarket"
    allowed_domains = ["backmarket.com"]
    start_urls = [
        "https://www.backmarket.com/en-us/l/iphone/e8724fea-197e-4815-85ce-21b8068020cc",
        "https://www.backmarket.com/en-us/l/samsung/12ed7728-38c7-45de-972c-b5c128e9889c",
        "https://www.backmarket.com/en-us/l/google-pixel/5b368baa-338c-4f22-aa3e-6e95f39101dd",
        # Use fewer URLs during debugging to avoid getting blocked
    ]
    
    def __init__(self, *args, **kwargs):
        super(BackMarketSpider, self).__init__(*args, **kwargs)
        self.website = "BackMarket"
    
    def start_requests(self):
        """
        Start with just one URL and use playwright for JavaScript rendering.
        """
        if self.debug_mode:
            # In debug mode, just use the first URL
            yield scrapy.Request(
                url=self.start_urls[0],
                callback=self.parse,
                errback=self.handle_error,
                meta={
                    "playwright": True,  # Use Playwright for JavaScript rendering
                    "playwright_include_page": True,  # Get access to the page object
                }
            )
        else:
            for url in self.start_urls:
                yield scrapy.Request(
                    url=url,
                    callback=self.parse,
                    errback=self.handle_error,
                    meta={
                        "playwright": True,
                        "playwright_include_page": True,
                    }
                )
    
    async def parse(self, response):
        """
        Parse the product listing page and follow links to product pages.
        Using async for Playwright compatibility.
        """
        # Debug the response
        self.debug_response(response)
        
        # Close the page once we're done with it
        page = response.meta.get("playwright_page")
        if page:
            await page.close()
        
        self.logger.info(f"Parsing BackMarket listing page: {response.url}")
        
        # Extract product links with multiple selectors
        product_links = []
        
        # Original selector
        links1 = response.css('a.productCard::attr(href)').getall()
        
        # Alternative selectors
        links2 = response.css('a[data-test="product-thumb"]::attr(href)').getall()
        links3 = response.css('div.productCard a::attr(href)').getall()
        
        # Combine all links
        product_links = list(set(links1 + links2 + links3))
        
        self.logger.info(f"Found {len(product_links)} product links")
        
        # Test selectors if no links found
        if not product_links and self.debug_mode:
            self.logger.warning("No product links found, testing HTML structure")
            self.test_backmarket_structure(response)
        
        # Follow each product link (limit to 3 in debug mode)
        count = 0
        for link in product_links:
            full_url = response.urljoin(link)
            yield scrapy.Request(
                url=full_url, 
                callback=self.parse_product,
                errback=self.handle_error,
                meta={
                    "playwright": True,
                }
            )
            
            count += 1
            if self.debug_mode and count >= 3:
                self.logger.info("Debug mode: limiting to 3 product pages")
                break
            
        # Follow pagination
        next_page = response.css('a[data-qa="pagination-next-page"]::attr(href)').get()
        if next_page and not self.debug_mode:  # Skip pagination in debug mode
            next_page_url = response.urljoin(next_page)
            self.logger.info(f"Following pagination to: {next_page_url}")
            yield scrapy.Request(
                url=next_page_url, 
                callback=self.parse,
                errback=self.handle_error,
                meta={
                    "playwright": True,
                    "playwright_include_page": True,
                }
            )
    
    def parse_product(self, response):
        """
        Parse individual product pages.
        """
        self.logger.info(f"Parsing BackMarket product: {response.url}")
        
        # Try multiple different CSS selectors since the site might change
        name = None
        for selector in [
            'h1.title::text',
            'h1[data-test="product-title"]::text',
            'h1.product-title::text'
        ]:
            name = response.css(selector).get()
            if name:
                break
                
        price_str = None
        for selector in [
            'div[data-qa="product-price"] span[data-test="prices-price"]::text',
            'span[data-test="prices-price"]::text',
            'div.price span::text'
        ]:
            price_str = response.css(selector).get()
            if price_str:
                break
                
        image_url = None
        for selector in [
            'img.productImage::attr(src)',
            'img.product-image::attr(src)',
            'div.product-images img::attr(src)'
        ]:
            image_url = response.css(selector).get()
            if image_url:
                break
                
        # Extract specifications 
        specs_selectors = [
            'div.specs div.specsDetails ::text',
            'div.product-specs ::text', 
            'div.product-details ::text'
        ]
        
        specs_text = ""
        for selector in specs_selectors:
            specs = response.css(selector).getall()
            if specs:
                specs_text = ' '.join(specs)
                break
        
        # Extract category from breadcrumbs
        category = None
        for selector in [
            'ol.productPathList li:nth-child(2) a::text',
            'nav.breadcrumb li:nth-child(2) a::text',
            'div.breadcrumbs a:nth-child(2)::text'
        ]:
            category = response.css(selector).get()
            if category:
                break
        
        # Debug output
        self.logger.info(f"Extracted name: {name}")
        self.logger.info(f"Extracted price: {price_str}")
        
        # If debugging and data is missing, test selectors
        if (not name or not price_str) and self.debug_mode:
            self.test_selectors(response)
        
        # Create item if we have the minimum data
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
            self.logger.warning(f"Could not extract essential data from {response.url}")
    
    def handle_error(self, failure):
        """
        Handle request errors.
        """
        self.logger.error(f"Request failed: {failure.request.url}")
        self.logger.error(f"Error: {repr(failure)}")
        
        # Save the error response if available
        if hasattr(failure.value, 'response') and failure.value.response:
            filename = f"error_{self.name}_{failure.value.response.status}.html"
            with open(filename, 'wb') as f:
                f.write(failure.value.response.body)
            self.logger.info(f"Saved error response to {filename}")
    
    def test_backmarket_structure(self, response):
        """
        Test the structure of the BackMarket page to understand what's happening.
        """
        self.logger.info("Testing BackMarket page structure")
        
        # Check if we're hitting a captcha or anti-bot page
        captcha_elements = response.css('div.captcha, div.recaptcha, form#challenge-form').getall()
        if captcha_elements:
            self.logger.error("CAPTCHA detected! The site is blocking us.")
            
        # Check for other common elements
        self.logger.info(f"Page title: {response.css('title::text').get()}")
        
        # Look for body text to see if there's an error message
        body_text = ' '.join(response.css('body ::text').getall())
        if "access denied" in body_text.lower() or "blocked" in body_text.lower():
            self.logger.error("Access denied message detected in page")