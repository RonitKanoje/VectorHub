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

def create_thread_with_title(thread_id: str, title: str):
    conn = get_db_connection()
    try:
        with conn.cursor() as cur:
            cur.execute("""
                INSERT INTO threads (thread_id, title)
                VALUES (%s, %s)
                ON CONFLICT (thread_id)
                DO UPDATE SET title = EXCLUDED.title
            """, (thread_id, title))
    finally:
        conn.close()