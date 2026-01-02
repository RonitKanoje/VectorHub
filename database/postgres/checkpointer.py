from langgraph.checkpoint.postgres import PostgresSaver
import psycopg
import os

def get_checkpointer():
    conn = psycopg.connect(
        host="localhost",
        port=5432,
        dbname=os.getenv("DB_NAME"),
        user=os.getenv("DB_USER"),
        password=os.getenv("DB_PASSWORD"),
        autocommit=True
    )

    cp = PostgresSaver(conn=conn)
    cp.setup()
    return cp
