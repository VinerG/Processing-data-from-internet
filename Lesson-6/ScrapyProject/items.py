# Define here the models for your scraped items
#
# See documentation in:
# https://docs.scrapy.org/en/latest/topics/items.html

import scrapy
from scrapy.loader.processors import TakeFirst

class LeroymerlinItem(scrapy.Item):
    name = scrapy.Field()
    # photo_file_name = scrapy.Field()
    # photo_url = scrapy.Field()
    params = scrapy.Field()
    url = scrapy.Field()
    price = scrapy.Field()

    file_urls = scrapy.Field()
    files = scrapy.Field()
    file_name = scrapy.Field(
        output_processor=TakeFirst()
    )