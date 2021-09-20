import scrapy

from pymongo import MongoClient

from scrapy_superjob.items import ScrapySuperjobVacancyItem

db = MongoClient(host='localhost', port=27017).gb_study.lesson_5
db.delete_many({})

class SuperjobSpider(scrapy.Spider):
    name = 'superjob'
    allowed_domains = ['superjob.ru']
    start_urls = ['https://www.superjob.ru/vacancy/search/?keywords=Python&geo%5Bt%5D%5B0%5D=4']

    def parse(self, response, **kwargs):
        # Search next page link
        next_page_url = response.css('a.f-test-link-Dalshe::attr("href")').extract_first()
        if next_page_url is not None:
            url = response.urljoin(next_page_url)
            yield scrapy.Request(url, callback=self.parse)

        # Search vacancies links
        for vacancy in response.css('div.f-test-search-result-item div.Fo44F'):
            item = ScrapySuperjobVacancyItem()
            item['url'] = response.urljoin(vacancy.css('a.icMQ_::attr("href")').extract_first())
            item['name'] = ("".join(vacancy.css('a._6AfZ9 *::text').extract()))
            salary = "".join(vacancy.css('span.f-test-text-company-item-salary *::text').extract())
            if salary is not None:
                # parse salary
                if (pos := salary.find("—")) > -1:
                    item['salary_from'] = "".join(filter(str.isdigit, salary[:pos]))
                    item['salary_to'] = "".join(filter(str.isdigit, salary[pos:]))
                elif salary.find("от ") > -1:
                    item['salary_from'] = "".join(filter(str.isdigit, salary))
                elif salary.find("до ") > -1:
                    item['salary_to'] = "".join(filter(str.isdigit, salary))
                else:
                    item['salary_from'] = "".join(filter(str.isdigit, salary))
                    item['salary_to'] = "".join(filter(str.isdigit, salary))
            # Store into MongoDB
            db.insert(dict(item))
            yield item
