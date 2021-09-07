# Наименование вакансии.
# Предлагаемую зарплату (отдельно минимальную и максимальную).
# Ссылку на саму вакансию.
# Сайт, откуда собрана вакансия.
# По желанию можно добавить ещё параметры вакансии (например, работодателя и расположение). Структура должна быть одинаковая для вакансий с обоих сайтов. Общий результат можно вывести с помощью dataFrame через pandas.

from bs4 import BeautifulSoup
import requests
import pandas as pd
import pprint

def request_hh_api(url):
    headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/92.0.4515.159 Safari/537.36"}
    response = requests.get(url, headers=headers).json()
    data = []
    for item in response['items']:
        data_item = {}
        data_item["site"] = "www.hh.ru (API)"
        data_item["name"] = item["name"]
        data_item["url"] = "https://hh.ru/vacancy/{}".format(item["id"])
        if item["salary"] is not None:
            data_item["salary"] = item["salary"]
        data_item["employer"] = item["employer"]["name"]
        data_item["location"] = item["area"]["name"]
        data.append(data_item)
    return data

def parse_hh_page(url):
    headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/92.0.4515.159 Safari/537.36"}
    response = requests.get(url, headers=headers).text
    soup = BeautifulSoup(response, 'lxml')
    vacancies = soup.select("div.vacancy-serp div.vacancy-serp-item")
    data = []
    for vacancy in vacancies:
        data_item = {}

        data_item["site"] = "www.hh.ru"
        vacation_info = vacancy.find(name="a", attrs={"data-qa": "vacancy-serp__vacancy-title"})
        data_item["name"] = vacation_info.text
        data_item["url"] = vacation_info["href"]
        # salary
        tag = vacancy.find(name="span", attrs={"data-qa": "vacancy-serp__vacancy-compensation"})
        if tag is not None:
            # data_item["salary"] = tag.text.replace("\u202f", "")
            data_item["salary"] = tag.text.replace("\u202f", "")
        # employer
        tag = vacancy.find(name="a", attrs={"data-qa": "vacancy-serp__vacancy-employer"})
        if tag is not None:
            data_item["employer"] = tag.text
        # location
        tag = vacancy.find(name="span", attrs={"data-qa": "vacancy-serp__vacancy-address"})
        if tag is not None:
            data_item["location"] = tag.text

        data.append(data_item)
    return data


def parse_superjob_page(url):
    headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/92.0.4515.159 Safari/537.36"}
    response = requests.get(url, headers=headers).text
    soup = BeautifulSoup(response, 'lxml')
    vacancies = soup.select("div.f-test-search-result-item div.Fo44F")
    data = []
    for vacancy in vacancies:
        data_item = {}

        data_item["site"] = "www.superjob.ru"
        data_item["name"] = vacancy.select("a._6AfZ9")[0].text
        data_item["url"] = "https://www.superjob.ru" + vacancy.select("a.icMQ_")[0]["href"]
        # salary
        list = vacancy.select("span.f-test-text-company-item-salary")
        if len(list) > 0:
            data_item["salary"] = list[0].text
        # employer
        list = vacancy.select("a._205Zx")
        if len(list) > 0:
            data_item["employer"] = list[0].text
        # location
        list = vacancy.select("span.f-test-text-company-item-location")
        if len(list) > 0:
            list = list[0].select("span")
            if len(list) > 2:
                data_item["location"] = list[2].text

        data.append(data_item)
    return data


pp = pprint.PrettyPrinter(indent=4)

all_data = []

print("Request www.hh.ru api", end="")
all_data += request_hh_api("https://api.hh.ru/vacancies?text=Python&area=1&per_page=100")
print(". Found {} vacancies.".format(len(all_data)))
print()

page_count = 5
for i in range(1, page_count + 1):
    print("Parse www.hh.ru page number {} of {}".format(i, page_count), end="")
    new_data = parse_hh_page("https://hh.ru/search/vacancy?area=1&fromSearchLine=true&st=searchVacancy&text=python&page={}".format(i - 1))
    print(". Found {} vacancies.".format(len(new_data)))
    all_data += new_data
print()

for i in range(1, page_count + 1):
    print("Parse www.superjob.ru page number {} of {}".format(i, page_count), end="")
    new_data = parse_superjob_page("https://www.superjob.ru/vacancy/search/?keywords=python&geo%5Bt%5D%5B0%5D=4&page={}".format(i))
    print(". Found {} vacancies.".format(len(new_data)))
    all_data += new_data
print()

pp.pprint(all_data)
print("\nTotal count: {}".format(len(all_data)))
