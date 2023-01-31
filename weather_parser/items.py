# Define here the models for your scraped items
#
# See documentation in:
# https://docs.scrapy.org/en/latest/topics/items.html

import scrapy


class WeatherParserItem(scrapy.Item):
    name = scrapy.Field()
    temperature = scrapy.Field()
    pressure = scrapy.Field()
    wind_speed = scrapy.Field()
    date = scrapy.Field()
