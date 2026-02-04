# import json
# from pathlib import Path

# STATE_FILE = Path("memory/state.json")

# def save_state(plan: TaskPlan):
#     STATE_FILE.write_text(plan.json(indent=2))

# def load_state() -> TaskPlan | None:
#     if not STATE_FILE.exists():
#         return None
#     return TaskPlan.parse_raw(STATE_FILE.read_text())
