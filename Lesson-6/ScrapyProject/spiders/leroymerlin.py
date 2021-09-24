import scrapy
from ScrapyProject.items import LeroymerlinItem
import uuid
from scrapy.loader import ItemLoader
from scrapy.loader.processors import MapCompose

class LeroymerlinSpider(scrapy.Spider):
    name = 'leroymerlin'
    allowed_domains = ['leroymerlin.ru']
    start_urls = ['https://leroymerlin.ru/catalogue/shlifovalnye-mashiny/']

    def parse(self, response, **kwargs):
        # Search next page link
        next_page_url = response.css('a.bex6mjh_plp.s15wh9uj_plp.l7pdtbg_plp.r1yi03lb_plp.sj1tk7s_plp::attr("href")').extract_first()
        if next_page_url is not None:
            yield scrapy.Request(response.urljoin(next_page_url), callback=self.parse)

        # Search vacancies links
        items = response.css('div.phytpj4_plp.largeCard')
        for item in items:
            item_loader = ItemLoader(item=LeroymerlinItem(), response=response, selector=item)

            item_loader.add_css('name', "span.t9jup0e_plp.p1h8lbu4_plp::text")
            item_loader.add_xpath('url', "a/@href", MapCompose(lambda i: response.urljoin(i)))
            item_loader.add_css('price', "p.t3y6ha_plp.xc1n09g_plp.p1q9hgmc_plp::text",
                                MapCompose(lambda i: i.replace('\xa0', '')))

            item_loader.add_value('file_name', str(uuid.uuid1()))
            item_loader.add_xpath('file_urls', 'a/span/picture/img/@src',
                                  MapCompose(lambda i: response.urljoin(i)))
            yield item_loader.load_item()
