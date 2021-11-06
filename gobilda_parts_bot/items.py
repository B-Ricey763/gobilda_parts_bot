# Define here the models for your scraped items
#
# See documentation in:
# https://docs.scrapy.org/en/latest/topics/items.html

import scrapy

# Everything need for a single product (motor, servo, etc.)
class Product(scrapy.Item):
    name = scrapy.Field() # formal name of the product
    sku = scrapy.Field() # Stock keeping unit number
    file_urls = scrapy.Field()
    files = scrapy.Field()