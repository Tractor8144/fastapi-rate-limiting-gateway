import redis
import time
from app.services.status_enum import StatusType
from app.services.rate_limiters.algo_types import RateLimitingAlgoType

redis_client = redis.Redis(host='localhost', port=6379, decode_responses=True)


def check_request_allowed(key: str, limit: int, refill_rate: float, algorithm_name: str):
    try:
        algo_type = RateLimitingAlgoType.from_value(algorithm_name)
    except:
        raise ValueError({'detail': 'Invalid rate limiting algorithm'})
    if algo_type == RateLimitingAlgoType.ALGO_TOKEN_BUCKET:
        from app.services.rate_limiters.token_bucket import TokenBucketAlgorithm
        return TokenBucketAlgorithm.check_request_allowed(
            key, limit, refill_rate)


def get_rule_key(identifier: str) -> str:
    return f'rate_limiy_rule:{identifier}'
