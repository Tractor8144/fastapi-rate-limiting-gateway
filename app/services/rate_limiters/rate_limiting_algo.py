from abc import ABC, abstractmethod
from app.services.status_enum import StatusType


class RateLimitingAlgorithm(ABC):
    @staticmethod
    @abstractmethod
    def check_request_allowed(key: str, rate_limt: int, refill_rate: int) -> StatusType:
        pass
