from pydantic import BaseModel
from typing import List
from schemas.task import Task


class TaskPlan(BaseModel):
    goal: str
    tasks: List[Task]
