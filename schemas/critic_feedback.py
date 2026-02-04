from pydantic import BaseModel
from typing import List
from schemas.critic_verdict import CriticVerdict


class CriticFeedback(BaseModel):
    task_id: int
    verdict: CriticVerdict
    issues: List[str]
    suggestions: List[str]