from database.postgres.db import get_db_connection

def create_thread_with_title(thread_id: str, title: str, user_id: int):
    conn = get_db_connection()
    try:
        with conn.cursor() as cur:
            cur.execute("""
                INSERT INTO threads (thread_id, title, user_id)
                VALUES (%s, %s, %s)
                ON CONFLICT (thread_id)
                DO UPDATE SET title = EXCLUDED.title
            """, (thread_id, title, user_id))
    finally:
        conn.close()