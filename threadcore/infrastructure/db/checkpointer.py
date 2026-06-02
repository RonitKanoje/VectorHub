from langgraph.checkpoint.postgres import PostgresSaver
from threadcore.infrastructure.db.session import get_db_connection


def get_checkpointer():
    connection = get_db_connection(autocommit=True)
    checkpointer = PostgresSaver(conn=connection)
    checkpointer.setup()
    return checkpointer

