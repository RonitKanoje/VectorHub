from langgraph.checkpoint.postgres.aio import AsyncPostgresSaver
from threadcore.infrastructure.db.session import get_async_db_pool

async def get_checkpointer():
    pool = get_async_db_pool()
    checkpointer = AsyncPostgresSaver(conn=pool)

    await checkpointer.setup()

    return checkpointer, pool