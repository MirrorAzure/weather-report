import sqlite3
from sqlite3 import Error
import logging

logging.basicConfig(filename="database.log",
                    filemode='w',
                    format='[%(asctime)s] [%(levelname)s] %(message)s',
                    datefmt='%H:%M:%S',
                    level=logging.DEBUG)

logger = logging.getLogger(__name__)

def create_connection(path):
    connection = None
    try:
        connection = sqlite3.connect(path)
        logger.info("Connection to SQLite DB successful")
    except Error as e:
        logger.error(f"The error '{e}' occurred")

    return connection


def execute_query(connection, query):
    # sqlite плохо работает с разными потоками, поэтому добавлена возможность создавать подключение "на месте"
    if type(connection) is str:
        connection = create_connection(connection)
        
    cursor = connection.cursor()
    try:
        cursor.execute(query)
        connection.commit()
        logger.info("Query executed successfully")
    except Error as e:
        logger.error(f"The error '{e}' occurred")


def execute_read_query(connection, query):
    
    if type(connection) is str:
        connection = create_connection(connection)
        
    cursor = connection.cursor()
    result = None
    try:
        cursor.execute(query)
        result = cursor.fetchall()
        logger.info("Query executed successfully")
        return result
    except Error as e:
        logger.error(f"The error '{e}' occurred")

def database_init(path):
    
    connection = create_connection(path)
    
    # создаём таблицу для хранения последней информации обо всех городах
    create_cities_table = """
    CREATE TABLE IF NOT EXISTS cities (
      id INTEGER PRIMARY KEY AUTOINCREMENT,
      city_name TEXT,
      last_temperature REAL,
      last_date TEXT
    );
    """
    execute_query(connection, create_cities_table)
    
    # создаём таблицу для поступающих с парсера данных
    create_data_table = """
    CREATE TABLE IF NOT EXISTS data (
      id INTEGER PRIMARY KEY AUTOINCREMENT,
      city_name TEXT,
      temperature REAL,
      pressure REAL,
      wind_speed REAL,
      date TEXT
    );
    """
    execute_query(connection, create_data_table)

