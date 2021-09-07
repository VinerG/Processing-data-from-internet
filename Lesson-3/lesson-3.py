import requests
from pymongo import MongoClient

MONGODB_DATABASE = "vacancies"
MONGODB_COLLECTION = "vacancies"


def request_hh_api(url):
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) " +
                      "Chrome/92.0.4515.159 Safari/537.36"}
    response = requests.get(url, headers=headers).json()
    vacancies = []
    for item in response['items']:
        vacancy = {}
        vacancy["site"] = "www.hh.ru"
        vacancy["vacancy_id"] = item["id"]
        vacancy["name"] = item["name"]
        vacancy["url"] = "https://hh.ru/vacancy/{}".format(item["id"])
        if item["salary"] is not None:
            vacancy["salary"] = item["salary"]
        vacancy["employer"] = item["employer"]["name"]
        vacancy["location"] = item["area"]["name"]
        vacancies.append(vacancy)
    return vacancies


# 1. Реализовать функцию, записывающую собранные вакансии в созданную БД.
def post_data_into_db(collection, data):
    return collection.insert_many(data)


# 2. Написать функцию, которая производит поиск и выводит на экран вакансии с заработной платой больше введённой суммы.
def search_vacancy_by_salary(collection, salary):
    return collection.find({"$or": [{"salary.from": {"$gt": salary}}, {"salary.to": {"$gt": salary}}]}, {"_id": False})


# 3. Написать функцию, которая будет добавлять в вашу базу данных только новые вакансии с сайта.
def post_data_into_db_only_new(collection, data):
    count = 0
    for data_item in data:
        if collection.replace_one({"vacancy_id": data_item["vacancy_id"]}, data_item, upsert=True).upserted_id is not None:
            count += 1
    return count


collection = MongoClient('localhost', 27017)[MONGODB_DATABASE][MONGODB_COLLECTION]
collection.delete_many({})

# Retrive 50 vacancies from www.hh.ru by api
print("Request www.hh.ru (API)", end="")
data = request_hh_api("https://api.hh.ru/vacancies?text=Python&area=1&per_page=50")
print(". Found {} vacancy.".format(len(data)))

# Insert found vacancies into mongo
print(post_data_into_db(collection, data).acknowledged)

# Get vacancies with salary > 100 000 from mongo
found_data = list(search_vacancy_by_salary(collection, 100000))
for i in found_data:
    print(i)
print("Found {} vacancies with salary >= 100000.".format(len(found_data)))

# Retrive 70 vacancies from www.hh.ru by api and insert found vacancies into mongo (only new)
print("Request www.hh.ru (API)", end="")
data = request_hh_api("https://api.hh.ru/vacancies?text=Python&area=1&per_page=70")
print(". Found {} vacancy.".format(len(data)))
print("Upserted new records: ", post_data_into_db_only_new(collection, data))
