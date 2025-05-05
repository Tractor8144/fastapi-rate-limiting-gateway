import redis
import time
from app.services.status_enum import StatusType

redis_client = redis.Redis(host='localhost', port=6379, decode_responses=True)


def get_token_bucket(key: str, limit: int, refill_rate: float):
    try:
        now = time.time()
        bucket = redis_client.hgetall(key)

        if bucket:
            tokens = float(bucket["tokens"])
            last_refill = float(bucket["last_refill"])
            elapsed = now - last_refill
            refill = elapsed * refill_rate
            tokens = min(limit, round(tokens + refill, 6))
        else:
            tokens = float(limit)
            last_refill = now

        if round(tokens, 6) >= 1e-6:
            redis_client.hset(key, mapping={
                "tokens": tokens - 1,
                "last_refill": now
            })
            redis_client.expire(key, int(limit / refill_rate))
            print(f"[DEBUG] Allowed. Tokens left: {tokens - 1:.2f}")
            return StatusType.ALLOWED
        else:
            print(f"[DEBUG] BLOCKED. Tokens left: {tokens:.2f}")
            return StatusType.REFUSED

    except redis.RedisError as e:
        print(f"redis client error: {e}")
        return StatusType.REDIS_ERROR
