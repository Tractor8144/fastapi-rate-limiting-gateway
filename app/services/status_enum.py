from enum import Enum

class StatusType(Enum):
    REDIS_ERROR = -1
    REFUSED = 0
    ALLOWED = 1
