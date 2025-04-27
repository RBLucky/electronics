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
        "https://www.backmarket.com/en-za/l/smartphones/c/smartphones",
        "https://www.backmarket.com/en-za/l/tablets/c/tablets",
        "https://www.backmarket.com/en-za/l/computers/c/computers",
        "https://www.backmarket.com/en-za/l/smartwatches/c/smartwatches"
    ]
    
    def __init__(self, *args, **kwargs):
        super(BackMarketSpider, self).__init__(*args, **kwargs)
        self.website = "BackMarket"
    
    def parse(self, response):
        """
        Parse the product listing page and follow links to product pages.
        """
        # Extract product links
        product_links = response.css('a.productCard::attr(href)').getall()
        
        # Follow each product link
        for link in product_links:
            full_url = response.urljoin(link)
            yield scrapy.Request(url=full_url, callback=self.parse_product)
            
        # Follow pagination
        next_page = response.css('a[data-qa="pagination-next-page"]::attr(href)').get()
        if next_page:
            next_page_url = response.urljoin(next_page)
            yield scrapy.Request(url=next_page_url, callback=self.parse)
    
    def parse_product(self, response):
        """
        Parse individual product pages.
        """
        # Extract product details
        name = response.css('h1.title::text').get()
        price_str = response.css('div[data-qa="product-price"] span[data-test="prices-price"]::text').get()
        image_url = response.css('img.productImage::attr(src)').get()
        
        # Extract specifications 
        specs_text = ' '.join(response.css('div.specs div.specsDetails ::text').getall())
        
        # Extract category from breadcrumbs
        category = response.css('ol.productPathList li:nth-child(2) a::text').get()
        
        # Create item
        yield self.create_item(
            name=name,
            price=price_str,
            url=response.url,
            specs_text=specs_text,
            category=category,
            image_url=image_url
        )