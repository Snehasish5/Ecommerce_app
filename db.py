import pymysql
import config

def get_db_connection():
    return pymysql.connect(
        host=config.DB_HOST,
        user=config.DB_USER,
        password=config.DB_PASSWORD,
        database=config.DB_NAME,
        port=3306,
        charset='utf8mb4',
        cursorclass=pymysql.cursors.DictCursor
    )
  