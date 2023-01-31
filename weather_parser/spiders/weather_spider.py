import os
import scrapy
import datetime
import sqlite3

from weather_parser.items import WeatherParserItem

weather_api_token = os.getenv("WEATHER_API_TOKEN")
db_path = os.getenv("DB_PATH")

def get_cities_list():
    connection = sqlite3.connect(db_path)
    query = "SELECT city_name FROM cities"
    cursor = connection.cursor()
    cursor.execute(query)
    res = cursor.fetchall()
    return [item[0] for item in res]

class WeatherSpider(scrapy.Spider):
    name = 'weather'
    
    # города получаем из БД
    cities = get_cities_list()
    
    # так как мы работаем с api openweathermap, сразу составим список ссылок с нужными городами
    start_urls = [f"https://api.openweathermap.org/data/2.5/weather?units=metric&q={city}&appid={weather_api_token}" for city in cities]

    def parse(self, response):
        weather_item = WeatherParserItem()
        res = response.json()
        weather_item["name"] = res["name"]
        weather_item["temperature"] = res["main"]["temp"]
        
        # openweathermap отображает давление в гектопаскалях, для перевода в мм рт. ст. следует умножить значение на 0.75
        weather_item["pressure"] = res["main"]["pressure"]*0.75
        weather_item["wind_speed"] = res["wind"]["speed"]
        
        # значение времени в микросекундах избыточно и неудобно для чтения пользователем
        weather_item["date"] = str(datetime.datetime.now()).split(".")[0]
        yield weather_item
