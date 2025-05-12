from enum import Enum


class RateLimitingAlgoType(Enum):
    ALGO_TOKEN_BUCKET = 'token_bucket'
    ALGO_SLIDING_WINDOW = 'sliding_window'

    @classmethod
    def from_value(cls, value):
        for item in cls:
            if item.value == value:
                return item

        raise ValueError(f"Invalid algorithm name")
