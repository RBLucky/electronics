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
        "https://www.backmarket.com/en-us/l/android-smartphones/52395319-44d0-4b36-951e-fe9234a54847",
        "https://www.backmarket.com/en-us/l/ipad-mini/5e829871-a097-4814-b6a1-b0e9167b7cb1",
        "https://www.backmarket.com/en-us/l/apple-ipad/f78ae8f5-4611-4ad0-b2ad-ced07765b847",
        "https://www.backmarket.com/en-us/l/apple-ipad-air/ff63f59b-a54d-445b-8d34-d5457e66f5d1",
        "https://www.backmarket.com/en-us/l/ipad-pro/a1733845-a071-4904-b2c6-eb0f332f7ef3",
        "https://www.backmarket.com/en-us/l/samsung-galaxy-tab/9da6c79a-baa0-4807-bb7d-18afd94dd3ed",
        "https://www.backmarket.com/en-us/l/microsoft-surface/4e604590-e4e2-48e7-9a0a-953760f94cf0",
        "https://www.backmarket.com/en-us/l/android-tablets/5950ae53-49d1-47f2-9722-323ea7fd53f3",
        "https://www.backmarket.com/en-us/l/apple-macbook/a059fa0c-b88d-4095-b6a2-dcbeb9dd5b33",
        "https://www.backmarket.com/en-us/l/windows-laptops/95d6f541-323f-4e25-bc85-5f567700354b",
        "https://www.backmarket.com/en-us/l/chromebook-laptop/1c5f4bcd-4d1c-4f29-8a47-de7c52e89565",
        "https://www.backmarket.com/en-us/l/2-in-1-hybrid-pcs/ea86b5b6-0422-4b65-8418-9762f31ccdff",
        "https://www.backmarket.com/en-us/l/gaming-laptops/15d04ae7-46e5-4ba9-af98-49c2e8f9e47b",
        "https://www.backmarket.com/en-us/l/computers-laptops/41f464b5-9356-48d3-86c3-a2bf52ced60e",
        "https://www.backmarket.com/en-us/l/watches/4ee50ebd-1eb4-4436-a797-80828ce28cc5",
        "https://www.backmarket.com/en-us/l/sony-playstation/dcbd8534-a5cd-4df0-9d54-dc80814fbcf6",
        "https://www.backmarket.com/en-us/l/microsoft-xbox/95a6d5f7-222b-45c9-a99b-e27cb10395af?p=0#model=999%2520Xbox%2520Original",
        "https://www.backmarket.com/en-us/l/nintendo-switch/a14cbb76-cdfc-4658-a0b9-d1275ba984e8",
        "https://www.backmarket.com/en-us/l/retro-gaming/22619a61-9184-4ce7-837b-81caa17c853f",
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