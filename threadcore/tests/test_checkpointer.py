import pytest
from unittest.mock import AsyncMock, patch

from threadcore.infrastructure.db import checkpointer


@pytest.mark.asyncio
async def test_get_checkpointer_returns_none_when_setup_fails():
    class DummyPool:
        pass

    with patch("threadcore.infrastructure.db.checkpointer.get_async_db_pool", return_value=DummyPool()):
        with patch("threadcore.infrastructure.db.checkpointer.AsyncPostgresSaver") as saver_cls:
            saver = saver_cls.return_value
            saver.setup = AsyncMock(side_effect=RuntimeError("boom"))

            result = await checkpointer.get_checkpointer()

    assert result == (None, None)
