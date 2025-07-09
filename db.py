import pymysql
import os

def get_db_connection():
    return pymysql.connect(
        host=os.getenv("DB_HOST", "localhost"),
        user=os.getenv("DB_USER", "root"),
        password=os.getenv("DB_PASSWORD", ""),
        database=os.getenv("DB_NAME", "ecommerce"),
        charset='utf8mb4',
        cursorclass=pymysql.cursors.DictCursor
    )
  