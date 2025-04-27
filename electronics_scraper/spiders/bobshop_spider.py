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
        "https://www.bobshop.co.za/cell-phones-accessories/smart-watches/c/18112"
        "https://www.bobshop.co.za/cell-phones-accessories/smart-watch-accessories/c/18113",
        "https://www.bobshop.co.za/gaming/consoles/c/10123",
    ]
    
    def __init__(self, *args, **kwargs):
        super(BobShopSpider, self).__init__(*args, **kwargs)
        self.website = "BobShop"
    
    def parse(self, response):
        """
        Parse the product listing page and follow links to product pages.
        """
        # Extract product links
        product_links = response.css('div.product-item a.product-item__title::attr(href)').getall()
        
        # Follow each product link
        for link in product_links:
            full_url = response.urljoin(link)
            yield scrapy.Request(url=full_url, callback=self.parse_product)
            
        # Follow pagination
        next_page = response.css('a.pagination__next::attr(href)').get()
        if next_page:
            next_page_url = response.urljoin(next_page)
            yield scrapy.Request(url=next_page_url, callback=self.parse)
    
    def parse_product(self, response):
        """
        Parse individual product pages.
        """
        # Extract product details
        name = response.css('h1.product-single__title::text').get()
        price_str = response.css('span.product__price::text').get()
        image_url = response.css('img.product-featured-media::attr(src)').get()
        specs_text = ' '.join(response.css('div.product-single__description ::text').getall())
        
        # Extract category from breadcrumbs
        category = response.css('nav.breadcrumb li:nth-child(2) a::text').get()
        
        # Create item
        yield self.create_item(
            name=name,
            price=price_str,
            url=response.url,
            specs_text=specs_text,
            category=category,
            image_url=image_url
        )