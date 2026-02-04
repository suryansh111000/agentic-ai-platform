from typing import List
from schemas.task import Task
from schemas.critic_feedback import CriticFeedback
from schemas.critic_verdict import CriticVerdict
from schemas.task_status import TaskStatus
from llm.hf_llama_client import call_llm
import json


class CriticAgent:
    """
    Evaluates completed tasks for quality and correctness.

    Contract:
    - Input: goal + list of completed Tasks
    - Output: List[CriticFeedback]
    - Read-only (never mutates tasks)
    """

    def __init__(self):
        self.prompt_path = "prompts/critic_prompt.txt"

    def _ensure_list(self, value):
        if value is None:
            return []
        if isinstance(value, list):
            return value
        if isinstance(value, str):
            return [] if value.strip() == "" else [value.strip()]
        return []

    def evaluate(self, goal: str, tasks: List[Task]) -> List[CriticFeedback]:
        feedbacks: List[CriticFeedback] = []

        for task in tasks:
            if task.status != TaskStatus.COMPLETED:
                continue

            prompt = self._build_prompt(goal, task)
            raw_output = call_llm(prompt)

            parsed = json.loads(raw_output)

            feedbacks.append(
                CriticFeedback(
                    task_id=task.id,
                    verdict=CriticVerdict(parsed["verdict"]),
                    issues=self._ensure_list(parsed.get("issues")),
                    suggestions=self._ensure_list(parsed.get("suggestions"))
                )
            )

        return feedbacks

    def _build_prompt(self, goal: str, task: Task) -> str:
        with open(self.prompt_path, "r", encoding="utf-8") as f:
            template = f.read()

        return (
            template
            .replace("{{GOAL}}", goal)
            .replace("{{TASK_DESCRIPTION}}", task.description)
            .replace("{{TASK_RESULT}}", task.result or "")
        )
