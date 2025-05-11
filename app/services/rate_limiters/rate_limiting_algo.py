from abc import ABC, abstractmethod
from status_enum import StatusType


class RateLimitingAlgorithm(ABC):
    @abstractmethod
    def check_request_allowed(self, key: str, rate_limt: int, refill_rate: int) -> StatusType:
        pass
