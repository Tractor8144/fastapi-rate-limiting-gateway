import redis
import time
from app.services.status_enum import StatusType


redis_client = redis.Redis(host='localhost',
                           port=6379, decode_responses=True)


def get_token_bucket(key: str, limit: int, refill_rate: float):
    try:
        now = time.time()
        bucket = redis_client.hgetall(key)

        if bucket:
            tokens = float(bucket.get("tokens", limit))
            last_refill = float(bucket.get("last_refill", now))
            elapsed = now - last_refill
            refill = elapsed * refill_rate
            tokens = min(limit, tokens + refill)
        else:
            tokens = limit
            last_refill = now

        if tokens >= 1:
            tokens -= 1
            redis_client.hset(key, mapping={"tokens": tokens, "last_refill": now})
            redis_client.expire(key, int(limit / refill_rate))  # optional cleanup
            return StatusType.ALLOWED
        else:
            return StatusType.REFUSED
    except redis.RedisError as e:
        print(f"redis client error: {e}")
        return StatusType.REDIS_ERROR