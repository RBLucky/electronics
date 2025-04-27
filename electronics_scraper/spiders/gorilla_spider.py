"""
Spider for Gorilla Phones electronics website.
"""
import scrapy
from electronics_scraper.spiders.base_spider import BaseSpider


class GorillaPhoneSpider(BaseSpider):
    """
    Spider for scraping electronics data from Gorilla Phones.
    """
    name = "gorilla"
    allowed_domains = ["gorillaphones.co.za"]
    start_urls = [
        "https://gorillaphones.co.za/collections/certified-pre-owned-phones",
        "https://gorillaphones.co.za/collections/certified-pre-owned-ipads",
        "https://gorillaphones.co.za/collections/certified-pre-owned-macbooks"
    ]
    
    def __init__(self, *args, **kwargs):
        super(GorillaPhoneSpider, self).__init__(*args, **kwargs)
        self.website = "Gorilla Phones"
    
    def parse(self, response):
        """
        Parse the product listing page and follow links to product pages.
        """
        # Extract product links
        product_links = response.css('div.collection-item a.collection-item-name::attr(href)').getall()
        
        # Follow each product link
        for link in product_links:
            full_url = response.urljoin(link)
            yield scrapy.Request(url=full_url, callback=self.parse_product)
            
        # Follow pagination
        next_page = response.css('ul.pagination a[rel="next"]::attr(href)').get()
        if next_page:
            next_page_url = response.urljoin(next_page)
            yield scrapy.Request(url=next_page_url, callback=self.parse)
    
    def parse_product(self, response):
        """
        Parse individual product pages.
        """
        # Extract product details
        name = response.css('h1.product-title::text').get()
        price_str = response.css('div.price-wrapper span.price::text').get()
        image_url = response.css('div.product-gallery img::attr(src)').get()
        
        # Extract specifications from product description
        specs_text = ' '.join(response.css('div.product-description ::text').getall())
        
        # Extract category from breadcrumbs
        category_text = response.css('nav.breadcrumb span.breadcrumb-item:nth-child(2)::text').get()
        category = category_text.strip() if category_text else None
        
        # Create item
        yield self.create_item(
            name=name,
            price=price_str,
            url=response.url,
            specs_text=specs_text,
            category=category,
            image_url=image_url
        )