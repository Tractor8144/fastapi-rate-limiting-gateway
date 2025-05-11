from rate_limiting_algo import RateLimitingAlgorithm
from status_enum import StatusType
from time import time
from redis_handler import redis_client
import redis


class TokenBucketAlgorithm(RateLimitingAlgorithm):
    def get_request_status(self, key: str, rate_limit: int, refill_rate: int) -> StatusType:
        try:
            now = time.time()
            bucket = redis_client.hgetall(key)

            if bucket:
                tokens = float(bucket["tokens"])
                last_refill = float(bucket["last_refill"])
                elapsed = now - last_refill
                refill = elapsed * refill_rate
                tokens = min(rate_limit, round(tokens + refill, 6))
            else:
                tokens = float(rate_limit)
                last_refill = now

            if round(tokens, 6) >= 1:
                redis_client.hset(key, mapping={
                    "tokens": tokens - 1,
                    "last_refill": now
                })
                redis_client.expire(key, int(rate_limit / refill_rate))
                print(f"[DEBUG] Allowed. Tokens left: {tokens - 1:.2f}")
                return StatusType.ALLOWED
            else:
                print(f"[DEBUG] BLOCKED. Tokens left: {tokens:.2f}")
                return StatusType.REFUSED
        except redis.RedisError as e:
            print(f"redis client error: {e}")
            return StatusType.REDIS_ERROR
