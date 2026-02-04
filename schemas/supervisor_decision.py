from dataclasses import dataclass
from typing import List
from enum import Enum


class SupervisorDecisionType(str, Enum):
    RETRY = "RETRY"
    PROCEED_TO_CRITIC = "PROCEED_TO_CRITIC"


@dataclass
class SupervisorDecision:
    decision: SupervisorDecisionType
    tasks_to_retry: List[int]
    reason: str = ""
