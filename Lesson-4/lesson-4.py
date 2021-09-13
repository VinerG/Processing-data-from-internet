from lxml import html
import requests
from pymongo import MongoClient
from pprint import pprint

HEADERS = {'User-Agent':'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/79.0.3945.130 Safari/537.36'}

XPATH_CONFIG_MAIL_RU = {
    "urls": "//a[contains(@class,'news-visited')]//@href",
    "title": "//div[contains(@class,'article')]//h1[@class='hdr__inner']/text()",
    "time": "//div[contains(@class,'breadcrumbs')][contains(@class,'breadcrumbs_article')]/span[1]//text()",
    "source": "//div[contains(@class,'breadcrumbs')][contains(@class,'breadcrumbs_article')]/span[2]//text()"
}

XPATH_CONFIG_LENTA_RU = {
    "urls": "//div[contains(@class,'item')][contains(@class,'article')]/a[1]/@href",
    "title": "//h1[@class='b-topic__titles']//text()",
    "time": "//div[contains(@class,'b-topic__info')]/time//text()",
    "source": "//div[contains(@class,'b-topic__info')]/span[2]//text()"
}


def parse_main_page(url, config):
    response = requests.get(url, headers = HEADERS)
    root = html.fromstring(response.text)
    result = []
    for item in root.xpath(config["urls"]):
        if (item.find("://") == -1):
            item = url + item
        result.append(item)
    return  result


def parse_news_page(url, config):
    result = {}
    response = requests.get(url, headers=HEADERS)
    root = html.fromstring(response.text)
    result["url"] = url
    result["title"] = ("".join(root.xpath(config["title"]))).replace("\xa0", " ").strip()
    result["time"] = "".join(root.xpath(config["time"]))
    result["source"] = "".join(root.xpath(config["source"]))
    return result


def parse(url, config):
    result = []
    for item in parse_main_page(url, config):
        item_data = parse_news_page(item, config)
        if item_data["title"]:
            result.append(item_data)
    return result


data = []

data += parse("https://mail.ru", XPATH_CONFIG_MAIL_RU)
data += parse("https://lenta.ru", XPATH_CONFIG_LENTA_RU)

# pprint(data)

# Store and retrive data from mongodb
collection = MongoClient('localhost', 27017)["gb_study"]["lesson_4_news"]
collection.delete_many({})
collection.insert_many(data)

pprint(list(collection.find({})))
