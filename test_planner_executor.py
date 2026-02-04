# test_planner_executor.py

from agents.planner import PlannerAgent
from agents.executor import ExecutorAgent
from schemas import TaskPlan, Task, TaskStatus


def test_planner_executor_verbose():
    planner = PlannerAgent()
    executor = ExecutorAgent()

    goal = "Analyze customer complaints and suggest product improvements"

    # ================== PLANNER ==================
    print("\n🧠 PLANNER OUTPUT")
    print("=" * 80)

    plan = planner.plan(goal)

    # Print planner output exactly like a model repr
    print(plan)

    assert isinstance(plan, TaskPlan)
    assert plan.goal == goal
    assert len(plan.tasks) > 0

    # ================== EXECUTOR ==================
    print("\n⚙️  EXECUTOR OUTPUT")
    print("=" * 80)

    for task in plan.tasks:
        print(f"\n➡️  Executing Task {task.id}")
        print(f"Description: {task.description}")
        print(f"Initial State: status={task.status}, attempts={task.attempts}")

        executed_task = executor.execute(task)

        print("Final State:")
        print(
            f"  status={executed_task.status}, "
            f"attempts={executed_task.attempts}, "
            f"result={executed_task.result}, "
            f"error={executed_task.error}"
        )

        # Contract checks
        assert executed_task.attempts == 1
        assert executed_task.status in (
            TaskStatus.COMPLETED,
            TaskStatus.FAILED,
        )

    print("\n✅ Planner + Executor verbose integration test passed")


if __name__ == "__main__":
    test_planner_executor_verbose()
