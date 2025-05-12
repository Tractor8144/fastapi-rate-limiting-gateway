from app.services.rate_limiters.rate_limiting_algo import RateLimitingAlgorithm
from app.services.status_enum import StatusType
from decimal import Decimal
import time
from app.services.redis_handler import redis_client
import redis


class TokenBucketAlgorithm(RateLimitingAlgorithm):
    @staticmethod
    def check_request_allowed(key: str, rate_limit: int, refill_rate: int) -> StatusType:
        try:
            now = Decimal(time.time())
            bucket = redis_client.hgetall(key)

            if bucket:
                tokens = Decimal(bucket.get("tokens", rate_limit))
                last_refill = Decimal(bucket.get("last_refill", now))
            else:
                tokens = Decimal(rate_limit)
                last_refill = now

            elapsed = now - last_refill
            refill = elapsed * Decimal(refill_rate)

            if refill >= 1:
                tokens = min(Decimal(rate_limit), tokens + refill)
                last_refill = now

            if tokens >= 1:
                tokens -= 1
                redis_client.hset(key, mapping={
                    "tokens": str(tokens),
                    "last_refill": str(last_refill)
                })
                redis_client.expire(key, int(rate_limit / refill_rate))
                print(f"[DEBUG] Allowed. Tokens left: {tokens:.6f}")
                return StatusType.ALLOWED
            else:
                print(f"[DEBUG] BLOCKED. Tokens left: {tokens:.6f}")
                return StatusType.REFUSED
        except redis.RedisError as e:
            print(f"Redis client error: {e}")
            return StatusType.REDIS_ERROR
