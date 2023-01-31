import os
import uvicorn
import requests

from fastapi import FastAPI
from apscheduler.schedulers.background import BackgroundScheduler

import database

weather_api_token = os.getenv("WEATHER_API_TOKEN")
db_path = os.getenv("DB_PATH")

app = FastAPI()

def scrape_weather_data():
    # скрипт парсера вызываем из консоли
    os.system('scrapy crawl weather')

@app.on_event('startup')
def app_init():
    # если файла с базой данных не существует, создаём его
    database.database_init(db_path)
    
    # создаём планировщик, чтобы парсер запускался раз в минуту
    scheduler = BackgroundScheduler()
    scheduler.add_job(scrape_weather_data, 'cron', minute='*/1')
    scheduler.start()

@app.post('/weather/{city}')
def add_city(city: str):
    # для начала проверим, не записан ли в БД этот город
    query = "SELECT city_name FROM cities"
    res = database.execute_read_query(db_path, query)
    
    # чтобы не тратить время на "выпрямление" списка кортежей приведём имя города к виду кортежа со строкой
    if (city.title(),) in res:
        return {"message": f"city {city} is already on the list"}
    
    # чтобы понять, существует ли город в базе, сделаем запрос к API
    resp = requests.get(f"https://api.openweathermap.org/data/2.5/weather?units=metric&q={city}&appid={weather_api_token}").json()
    
    # в случае, если города нет, в поле "cod" лежит строковое представление ошибки
    if resp["cod"] == '404':
        return {"message": f"weather data for city {city} is not available"}
    
    # если город существует, в "cod" лежит число 200
    if resp["cod"] == 200:
        query = f"INSERT INTO cities (city_name) VALUES (\"{resp['name']}\");"
        database.execute_query("database/weather.db", query)
        return {"message": f"city {city} was added to the list"}

@app.get('/last_weather')
def get_last_weather(search: str = None):
    query = "SELECT city_name, last_temperature, last_date FROM cities"
    res = database.execute_read_query(db_path, query)
    response = {}
    for item in res:
        if search:
            if search.lower() not in item[0].lower():
                continue
        response[item[0]] = {"Temperature": item[1], "Date": item[2]}
    return response

@app.get('/city_stats')
def get_city_stats(q: str, period_begin: str = None, period_end: str = None):
    # формат даты YYYY-MM-DD HH:MI:SS, нужен для лексикографического сравнения дат
    query = f"SELECT temperature, pressure, wind_speed, date FROM data WHERE data.city_name = \"{q.title()}\""
    
    # сразу создаём запрос для получения средних значений всех параметров
    query_avg = f"SELECT ROUND(avg(temperature), 2), ROUND(avg(pressure), 2), ROUND(avg(wind_speed), 2) FROM data WHERE data.city_name = \"{q.title()}\""
    
    if period_begin:
        query += f" AND data.date > \"{period_begin}\""
        query_avg += f" AND data.date > \"{period_begin}\""
    # дополняем запросы, если пользователь хочет уточнить период
    if period_end:
        query += f" AND data.date < \"{period_end}\""
        query_avg += f" AND data.date < \"{period_end}\""
        
    res = database.execute_read_query(db_path, query)
    res_avg = database.execute_read_query(db_path, query_avg)
    
    resp = {}
    resp[q.title()] = []
    for item in res:
        resp[q.title()].append({f"Date": item[3], f"Temperature": item[0], f"Pressure": item[1], f"Wind Speed": item[2]})
    for item in res_avg:
        resp["Average"] = {f"Temperature": item[0], f"Pressure": item[1], f"Wind Speed": item[2]}
    return resp


if __name__ == "__main__":
    uvicorn.run(app="main:app", host="127.0.0.1", port=8080, reload=False)