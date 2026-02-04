# agents/planner.py
from llm.hf_llama_client import call_llm
import json, re
from schemas import TaskPlan, Task, TaskStatus

class PlannerAgent:
    def __init__(self, prompt_file: str = "prompts/planner_prompt.txt"):
        self.prompt_file = prompt_file
        print("🧠 PlannerAgent started")

    def extract_json(self, text: str):
        """
        Extracts the first valid JSON object from a string, with:
        - Markdown code fences removed
        - Brace-balanced parsing
        - Common LLM JSON fixes applied
        """
        # Remove markdown code fences
        text = re.sub(r"```(?:json)?", "", text)

        # Find the first opening brace
        start = text.find("{")
        if start == -1:
            raise ValueError("No JSON object found in LLM output")

        # Brace-balanced extraction
        brace_count = 0
        for i in range(start, len(text)):
            if text[i] == "{":
                brace_count += 1
            elif text[i] == "}":
                brace_count -= 1
                if brace_count == 0:
                    json_str = text[start:i+1]
                    return self._safe_json_load(json_str)

        raise ValueError("Unbalanced JSON braces in LLM output")

    def _safe_json_load(self, json_str: str):
        """
        Tries to parse JSON, applies common LLM fixes if it fails:
        - Single quotes -> double quotes
        - Trailing commas removed
        - Python literals replaced
        """
        try:
            return json.loads(json_str)
        except json.JSONDecodeError:
            fixed = json_str

            # Replace single quotes with double quotes
            fixed = re.sub(r"'", '"', fixed)

            # Remove trailing commas before } or ]
            fixed = re.sub(r",\s*([}\]])", r"\1", fixed)

            # Replace Python literals
            fixed = fixed.replace("None", "null")
            fixed = fixed.replace("True", "true")
            fixed = fixed.replace("False", "false")

            return json.loads(fixed)

    def plan(self, goal: str) -> TaskPlan:
        print(f"📄 Reading prompt from: {self.prompt_file}")
        with open(self.prompt_file, "r", encoding="utf-8") as f:
            template = f.read()

        prompt = template.replace("{{GOAL}}", goal)
        print("📤 Sending prompt to LLM...")

        raw_output = call_llm(prompt)
        # Debug: uncomment to see raw LLM output
        # print("RAW LLM OUTPUT:\n", raw_output)

        # Parse JSON from LLM
        data = self.extract_json(raw_output)

        # Force defaults required by tests
        tasks = []
        for t in data.get("tasks", []):
            tasks.append(
                Task(
                    id=t.get("id"),
                    description=t.get("description"),
                    status=TaskStatus.PENDING,
                    attempts=0,
                    result=None,
                    error=None,
                )
            )

        return TaskPlan(goal=data.get("goal", goal), tasks=tasks)


# Example usage
if __name__ == "__main__":
    planner = PlannerAgent()
    goal_text = "Analyze customer complaints and suggest product improvements"
    plan = planner.plan(goal_text)
    print("Generated plan:\n", plan)
