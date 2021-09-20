# Define here the models for your scraped items
#
# See documentation in:
# https://docs.scrapy.org/en/latest/topics/items.html

import scrapy


class ScrapySuperjobVacancyItem(scrapy.Item):
    url = scrapy.Field()
    name = scrapy.Field()
    salary = scrapy.Field()
    salary_from = scrapy.Field()
    salary_to = scrapy.Field()

