from pydantic import BaseModel
from typing import Optional
from schemas.task_status import TaskStatus


class Task(BaseModel):
    id: int
    description: str
    status: TaskStatus = TaskStatus.PENDING
    attempts: int = 0
    result: Optional[str] = None
    error: Optional[str] = None
