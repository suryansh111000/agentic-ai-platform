from enum import Enum


class CriticVerdict(str, Enum):
    PASS = "PASS"
    FAIL_RETRYABLE = "FAIL_RETRYABLE"
    FAIL_FATAL = "FAIL_FATAL"