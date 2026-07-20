import logging

from langgraph.checkpoint.postgres.aio import AsyncPostgresSaver # Asynchronous Version
from ai.infrastructure.db.session import get_async_db_pool

logger = logging.getLogger(__name__)

async def get_checkpointer():
    try:
        pool = get_async_db_pool()
        checkpointer = AsyncPostgresSaver(conn=pool)
        await checkpointer.setup()
        return checkpointer, pool
    except Exception as exc:
        logger.exception("Failed to initialize async checkpointer, continuing without it")
        return None, None
