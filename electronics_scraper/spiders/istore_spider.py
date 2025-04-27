"""
Spider for iStore Pre-owned electronics website.
"""
import scrapy
from electronics_scraper.spiders.base_spider import BaseSpider


class IStorePreOwnedSpider(BaseSpider):
    """
    Spider for scraping electronics data from iStore Pre-owned section.
    """
    name = "istore"
    allowed_domains = ["istore.co.za"]
    start_urls = [
        "https://istorepreowned.co.za/collections/iphone-savings",
        "https://istorepreowned.co.za/collections/iphone",
        "https://istorepreowned.co.za/collections/ipad",
        "https://istorepreowned.co.za/collections/mac"
        "https://istorepreowned.co.za/collections/apple-watch",
        "https://istorepreowned.co.za/collections/accessories-2",
    ]
    
    def __init__(self, *args, **kwargs):
        super(IStorePreOwnedSpider, self).__init__(*args, **kwargs)
        self.website = "iStore"
    
    def parse(self, response):
        """
        Parse the product listing page and follow links to product pages.
        """
        # Extract product links
        product_links = response.css('div.product-item-info a.product-item-link::attr(href)').getall()
        
        # Follow each product link
        for link in product_links:
            yield scrapy.Request(url=link, callback=self.parse_product)
            
        # Follow pagination
        next_page = response.css('a.action.next::attr(href)').get()
        if next_page:
            yield scrapy.Request(url=next_page, callback=self.parse)
    
    def parse_product(self, response):
        """
        Parse individual product pages.
        """
        # Extract product details
        name = response.css('h1.page-title span::text').get()
        price_str = response.css('span.price::text').get()
        image_url = response.css('img.gallery-placeholder__image::attr(src)').get()
        
        # Extract specifications from product description
        specs_text = ' '.join(response.css('div.product.attribute.description div.value ::text').getall())
        
        # Extract category from breadcrumbs
        category = response.css('div.breadcrumbs li.item:nth-child(2) a::text').get()
        
        # Create item
        yield self.create_item(
            name=name,
            price=price_str,
            url=response.url,
            specs_text=specs_text,
            category=category,
            image_url=image_url
        )