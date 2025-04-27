"""
Spider for Revibe electronics website.
"""
import scrapy
from electronics_scraper.spiders.base_spider import BaseSpider


class RevibeSpider(BaseSpider):
    """
    Spider for scraping electronics data from Revibe.
    """
    name = "revibe"
    allowed_domains = ["revibe.co.za"]
    start_urls = [
        "https://revibe.co.za/collections/pre-owned-iphones",
        "https://revibe.co.za/collections/pre-owned-samsung",
        "https://revibe.co.za/collections/pre-owned-macbooks",
        "https://revibe.co.za/collections/pre-owned-ipads"
    ]
    
    def __init__(self, *args, **kwargs):
        super(RevibeSpider, self).__init__(*args, **kwargs)
        self.website = "Revibe"
    
    def parse(self, response):
        """
        Parse the product listing page and follow links to product pages.
        """
        # Extract product links
        product_links = response.css('div.product-grid-item a.product-link::attr(href)').getall()
        
        # Follow each product link
        for link in product_links:
            full_url = response.urljoin(link)
            yield scrapy.Request(url=full_url, callback=self.parse_product)
            
        # Follow pagination
        next_page = response.css('ul.pagination-custom li.pagination-next a::attr(href)').get()
        if next_page:
            next_page_url = response.urljoin(next_page)
            yield scrapy.Request(url=next_page_url, callback=self.parse)
    
    def parse_product(self, response):
        """
        Parse individual product pages.
        """
        # Extract product details
        name = response.css('h1.product-title::text').get()
        price_str = response.css('span.product-price ::text').get()
        image_url = response.css('img.product-featured-img::attr(src)').get()
        
        # Extract specifications from product description
        specs_text = ' '.join(response.css('div.product-description ::text').getall())
        
        # Extract category from breadcrumbs or URL
        category = response.url.split('/collections/')[1].split('/')[0].replace('-', ' ')
        
        # Create item
        yield self.create_item(
            name=name,
            price=price_str,
            url=response.url,
            specs_text=specs_text,
            category=category,
            image_url=image_url
        )