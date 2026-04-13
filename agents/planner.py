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

    def _parse_numbered_tasks(self, text: str):
        """
        Fallback parser for numbered task lists like:
        1. Task one
        2. Task two
        """
        tasks = []
        lines = text.strip().split("\n")
        task_id = 1

        for line in lines:
            line = line.strip()
            match = re.match(r"^\d+\.\s*(.+)", line)
            if match:
                description = match.group(1).strip()
                # 🔥 CLEANUP
                description = description.strip('"').strip("'")
                description = description.rstrip(",")
                description = description.rstrip("]")
                tasks.append(
                    Task(
                        id=task_id,
                        description=description,
                        status=TaskStatus.PENDING,
                        attempts=0,
                        result=None,
                        error=None,
                    )
                )
                task_id += 1

        return tasks

    def plan(self, goal: str) -> TaskPlan:
        print("🧠 Generating plan using LLM...")

        # Load prompt
        with open(self.prompt_file, "r", encoding="utf-8") as f:
            template = f.read()

        prompt = template.replace("{{GOAL}}", goal)

        # Call LLM
        raw_output = call_llm(prompt)

        print("🧾 RAW LLM OUTPUT:\n", raw_output)

        # Try JSON parsing
        try:
            parsed = self.extract_json(raw_output)

            tasks_data = parsed.get("tasks", [])

            tasks = []
            for i, t in enumerate(tasks_data, start=1):
                if isinstance(t, str):
                    description = t
                else:
                    description = t.get("description", "")

                tasks.append(
                    Task(
                        id=i,
                        description=description,
                        status=TaskStatus.PENDING,
                        attempts=0,
                        result=None,
                        error=None,
                    )
                )

            return TaskPlan(goal=goal, tasks=tasks)

        except Exception as e:
            print("❌ JSON parsing failed, using fallback:", e)

            # Fallback: numbered list parsing
            tasks = self._parse_numbered_tasks(raw_output)

            if not tasks:
                raise ValueError("Planner failed to generate valid tasks")

            return TaskPlan(goal=goal, tasks=tasks)

# Example usage
if __name__ == "__main__":
    planner = PlannerAgent()
    goal_text = "Analyze customer complaints and suggest product improvements"
    plan = planner.plan(goal_text)
    print("Generated plan:\n", plan)