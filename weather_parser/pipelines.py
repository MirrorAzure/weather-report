# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://docs.scrapy.org/en/latest/topics/item-pipeline.html

# useful for handling different item types with a single interface
from itemadapter import ItemAdapter

import os
import sqlite3

db_path = os.getenv("DB_PATH")

class WeatherParserPipeline:

    def __init__(self):
        self.connection = sqlite3.connect(db_path)
    
    def process_item(self, item, spider):
        # вносим полученные данные в таблицу data
        query = f"""
                            INSERT INTO
                            data (city_name, temperature, pressure, wind_speed, date)
                            VALUES
                            (\"{item['name']}\", {item['temperature']}, {item['pressure']}, {item['wind_speed']}, \"{item['date']}\");
                """
        cursor = self.connection.cursor()
        cursor.execute(query)
        self.connection.commit()
        
        # актуализируем данные в таблице cities
        query = f"""
                            UPDATE
                            cities
                            SET
                            last_temperature = {item['temperature']},
                            last_date = \"{item['date']}\"
                            WHERE
                            cities.city_name = \"{item['name']}\"
                """
        cursor = self.connection.cursor()
        cursor.execute(query)
        self.connection.commit()
        return item
