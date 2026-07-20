import redis
from redis.exceptions import RedisError
from ai.core.config import settings


redis_client = redis.Redis(
    host=settings.redis_host,
    port=settings.redis_port,
    decode_responses=True,
    socket_connect_timeout=2,
    socket_timeout=2,
)

_fallback_thread_status: dict[str, str] = {}   ## Temporary backup if Redis is crashed


def is_redis_available() -> bool:
    try:
        return bool(redis_client.ping())
    except RedisError:
        return False


def set_thread_status(thread_id: str, status: str) -> None:
    _fallback_thread_status[thread_id] = status
    try:
        redis_client.set(thread_id, status)
    except RedisError:
        pass


def get_thread_status(thread_id: str) -> str | None:
    try:
        status = redis_client.get(thread_id)
        if status is not None:
            _fallback_thread_status[thread_id] = status
        return status
    except RedisError:
        return _fallback_thread_status.get(thread_id)
