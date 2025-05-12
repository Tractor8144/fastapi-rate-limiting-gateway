from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import JSONResponse
from app.services.redis_handler import check_request_allowed, get_rule_key
from app.services.status_enum import StatusType
from app.services.request_parser import RequestParser
from app.routes.admin import IdentifierType
from app.services.redis_handler import redis_client
import logging

logging.basicConfig(level=logging.INFO,
                    format='%(asctime)s - %(levelname)s - %(message)s')


class RateLimiterMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request, call_next) -> JSONResponse:
        logging.info(
            f"Incoming request: {request.method} {request.url} from {request.client.host}")

        if request.url.path.startswith('/admin/'):
            logging.info(
                f"Skipping rate limiting for admin route: {request.url.path}")
            return await call_next(request)

        identifiers = RequestParser.extract_identifiers(request)
        logging.info(f"Extracted identifiers: {identifiers}")

        default_rate_limit = 5
        default_refill_rate = 1
        rule_applied = False

        logging.info("Checking rate limit for extracted identifiers...")

        for identifier_type, identifier_name in identifiers.items():
            limit, refill_rate, algorithm_name = self.get_rate_limit_rule(
                identifier_name)
            logging.info(
                f"Rate limit for {identifier_name}: {limit} requests/min, refill rate: {refill_rate}")

            if limit > 0:
                rule_applied = True
                status = check_request_allowed(
                    identifier_name, limit, refill_rate, algorithm_name)

                if status == StatusType.REFUSED:
                    logging.warning(
                        f"Rate limit exceeded for {identifier_name}")
                    return JSONResponse(
                        status_code=429,
                        content={'detail': 'Too many requests'}
                    )
                elif status == StatusType.REDIS_ERROR:
                    logging.error(
                        "Redis server error while checking rate limit")
                    return JSONResponse(
                        status_code=503,
                        content={'detail': 'Redis server error'}
                    )
                logging.info(
                    f"Rate limiting applied for {identifier_name}, proceeding with request")
                break

        if not rule_applied:
            logging.info(
                "No specific rate limit rule applied, using default rate limit")
            default_limit, default_refill_rate, default_algo_name = self.get_rate_limit_rule(
                'default')
            if default_limit == 0:
                logging.info(
                    "Default rate limit not found in Redis, using hardcoded values")
                default_limit = 5
                default_refill_rate = 1
                default_algo_name = 'token_bucket'
            status = check_request_allowed(
                'default', default_limit, default_refill_rate, default_algo_name)

            if status == StatusType.REFUSED:
                logging.warning("Default rate limit exceeded")
                return JSONResponse(
                    status_code=429,
                    content={'detail': 'Too many requests (default)'}
                )

        logging.info(
            f"Request from {request.client.host} allowed, forwarding to next middleware")
        response = await call_next(request)
        logging.info(f"Response status: {response.status_code}")
        return response

    def get_rate_limit_rule(self, identifier_name):
        key = get_rule_key(identifier=identifier_name)
        logging.debug(f"Fetching rate limit rule from Redis for key: {key}")

        data = redis_client.hgetall(key)

        if not data:
            logging.info(f"No rate limit rule found for {identifier_name}")
            return (0, 0.0, '')
        try:
            rate_limit = int(data['rate_limit'])
            refill_rate = float(data['refill_rate'])
            algorithm_name = data['algorithm']
            logging.info(
                f"Rate limit rule found for {identifier_name}: {rate_limit} requests/sec, refill rate: {refill_rate}, algorithm name: {algorithm_name}")
            return (rate_limit, refill_rate, algorithm_name)
        except (KeyError, ValueError) as e:
            logging.error(
                f"Error parsing rate limit rule for {identifier_name}: {e}")
            return (0, 0.0, '')
