from langgraph.checkpoint.postgres import PostgresSaver
from database.postgres.db import get_db_connection

def get_checkpointer():
    conn = get_db_connection()
    cp = PostgresSaver(conn=conn)
    cp.setup()
    return cp