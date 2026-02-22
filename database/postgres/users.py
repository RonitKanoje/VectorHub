from database.postgres.db import get_db_connection

def create_user(username: str, password_hash: bytes):
    conn = get_db_connection()
    try:
        with conn.cursor() as cur:
            cur.execute("""
                INSERT INTO users (username, password_hash)
                VALUES (%s, %s)
                RETURNING id
            """, (username, password_hash))

            result = cur.fetchone()
            return result  # Will be None if conflict occurs
    except Exception as e:
        raise
    finally:
        conn.close()

def get_user_by_username(username: str):
    conn = get_db_connection()
    try:
        with conn.cursor() as cur:
            cur.execute("""
                SELECT id, username, password_hash
                FROM users
                WHERE username = %s
            """, (username,))
            return cur.fetchone()
    finally:
        conn.close()