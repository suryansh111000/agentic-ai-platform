# test_planner.py

from agents.planner import PlannerAgent
from schemas import TaskPlan, Task, TaskStatus


def test_planner_basic():
    planner = PlannerAgent()

    goal = "Analyze customer complaints and suggest product improvements"

    plan = planner.plan(goal)

    # ---------- Assertions ----------
    assert isinstance(plan, TaskPlan), "Planner did not return TaskPlan"

    assert plan.goal == goal, "Goal mismatch"

    assert isinstance(plan.tasks, list), "Tasks is not a list"
    assert 3 <= len(plan.tasks) <= 6, "Planner returned invalid number of tasks"

    task_ids = set()

    for task in plan.tasks:
        assert isinstance(task, Task), "Task is not a Task model"
        assert isinstance(task.id, int), "Task id is not int"
        assert task.id not in task_ids, "Duplicate task id found"
        task_ids.add(task.id)

        assert isinstance(task.description, str)
        assert len(task.description.strip()) > 0

        assert task.status == TaskStatus.PENDING
        assert task.attempts == 0
        assert task.result is None
        assert task.error is None

    print("✅ PlannerAgent test passed")
    print(plan)


if __name__ == "__main__":
    test_planner_basic()
