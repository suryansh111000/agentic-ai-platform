from typing import List
from schemas.task import Task
from schemas.critic_feedback import CriticFeedback
from schemas.critic_verdict import CriticVerdict
from schemas.task_status import TaskStatus
from llm.hf_llama_client import call_llm
import json
import re


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

    def _extract_json(self, text: str):
        # Remove markdown code fences
        text = re.sub(r"```(?:json)?", "", text)

        start = text.find("{")
        if start == -1:
            raise ValueError("No JSON object found in LLM output")

        brace_count = 0
        for i in range(start, len(text)):
            if text[i] == "{":
                brace_count += 1
            elif text[i] == "}":
                brace_count -= 1
                if brace_count == 0:
                    json_str = text[start:i+1]
                    return self._safe_json_load(json_str)

        raise ValueError("Unbalanced JSON braces")


    def _safe_json_load(self, json_str: str):
        try:
            return json.loads(json_str)
        except json.JSONDecodeError:
            fixed = json_str

            fixed = re.sub(r"'", '"', fixed)
            fixed = re.sub(r",\s*([}\]])", r"\1", fixed)
            fixed = fixed.replace("None", "null")
            fixed = fixed.replace("True", "true")
            fixed = fixed.replace("False", "false")

            return json.loads(fixed)

    def evaluate(self, goal: str, tasks: List[Task]) -> List[CriticFeedback]:
        feedbacks: List[CriticFeedback] = []

        for task in tasks:
            if task.status != TaskStatus.COMPLETED:
                continue

            prompt = self._build_prompt(goal, task)
            raw_output = call_llm(prompt)

            # parsed = json.loads(raw_output)
            try:
                parsed = self._extract_json(raw_output)
            except Exception as e:
                print("❌ Critic JSON parsing failed:", e)
                print("🧾 RAW OUTPUT:\n", raw_output)

                # fallback so API doesn't crash
                parsed = {
                    "verdict": "FAIL",
                    "issues": ["Invalid JSON from LLM"],
                    "suggestions": ["Retry or improve prompt"]
                }

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
