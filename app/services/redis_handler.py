import redis
import time


redis_client = redis.Redis(host='localhost',
                           port=6379, decode_responses=True)


def get_token_bucket(key: str, limit: int, refill_rate: float):
    now = int(time.time())
    bucket = redis_client.hgetall(key)

    if bucket:
        tokens = float(bucket.get("tokens", limit))
        last_refill = int(bucket.get("last_refill", now))
        elapsed = now - last_refill
        refill = elapsed * refill_rate
        tokens = min(limit, tokens + refill)
    else:
        tokens = limit
        last_refill = now

    if tokens >= 1:
        tokens -= 1
        redis_client.hmset(key, {"tokens": tokens, "last_refill": now})
        redis_client.expire(key, int(limit / refill_rate))  # optional cleanup
        return True
    else:
        return False