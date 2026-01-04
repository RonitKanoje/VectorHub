import redis

redis_client = redis.Redis(
    host="127.0.0.1",          # ✅ IMPORTANT
    port=6379,
    decode_responses=True,
    socket_connect_timeout=2,
    socket_timeout=2
)

