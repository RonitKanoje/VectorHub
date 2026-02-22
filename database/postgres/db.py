import psycopg
import os

def get_db_connection():
    return psycopg.connect(
        host="localhost",
        port=5432,
        dbname=os.getenv("DB_NAME"),
        user=os.getenv("DB_USER"),
        password=os.getenv("DB_PASSWORD"),
        autocommit=True
    )