# agents/executor.py

from schemas.task import Task
from schemas.task_status import TaskStatus


class ExecutorAgent:
    """
    Executes a single Task safely and deterministically.

    Contract:
    - Input: Task (PENDING or FAILED)
    - Output: Task (COMPLETED or FAILED)
    - No retries
    - Never raises exceptions
    """

    def execute(self, task: Task) -> Task:
        # Defensive: clear stale data
        task.result = None
        task.error = None

        # Transition to IN_PROGRESS
        task.status = TaskStatus.IN_PROGRESS

        try:
            # Attempt execution exactly once
            task.attempts += 1

            # ---- EXECUTION LOGIC (placeholder) ----
            # For now, we simulate execution based on task description
            # This will later be replaced with real tool / LLM calls

            if "fail" in task.description.lower():
                raise RuntimeError("Simulated task failure")

            # Successful execution
            task.result = f"Task {task.id} executed successfully: {task.description}"
            task.status = TaskStatus.COMPLETED

        except Exception as e:
            # Failure path — NEVER crash
            task.error = str(e)
            task.status = TaskStatus.FAILED

        return task