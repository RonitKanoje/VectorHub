from langgraph.checkpoint.postgres.aio import AsyncPostgresSaver # Asynchronous Version
from threadcore.infrastructure.db.session import get_async_db_pool

async def get_checkpointer():
    try:
        pool = get_async_db_pool()
        checkpointer = AsyncPostgresSaver(conn=pool)
        await checkpointer.setup()
        return checkpointer, pool
    except Exception as exc:
        print("Failed to initialize async checkpointer, continuing without it:", repr(exc))
        return None, None