# test_planner_executor_supervisor_critic.py

from agents.planner import PlannerAgent
from agents.executor import ExecutorAgent
from agents.supervisor import TaskSupervisorAgent
from agents.critic import CriticAgent
from schemas.task_status import TaskStatus

def test_full_pipeline():
    # ---------- Step 0: Setup ----------
    goal = "Summarize the key features of Python"
    max_attempts = 2

    planner = PlannerAgent()
    executor = ExecutorAgent()
    supervisor = TaskSupervisorAgent(max_attempts=max_attempts)
    critic = CriticAgent()

    print("🧠 PlannerAgent started")

    # ---------- Step 1: Planning ----------
    plan = planner.plan(goal)

    print("\n🧠 PLANNER OUTPUT")
    print("="*80)
    print(plan)

    # ---------- Step 2: Executor executes each task ----------
    print("\n⚙️  EXECUTOR OUTPUT")
    print("="*80)

    for task in plan.tasks:
        print(f"\n➡️  Executing Task {task.id}")
        print(f"Description: {task.description}")
        print(f"Initial State: status={task.status}, attempts={task.attempts}")

        updated_task = executor.execute(task)

        print("Final State:")
        print(f"  status={updated_task.status}, attempts={updated_task.attempts}, "
              f"result={updated_task.result}, error={updated_task.error}")

    # ---------- Step 3: Supervisor reviews plan ----------
    print("\n⚡ SUPERVISOR OUTPUT")
    print("="*80)
    decision = supervisor.review_plan(plan)
    print(f"Decision: {decision.decision}")
    print(f"Tasks to retry: {decision.tasks_to_retry}")
    print(f"Reason: {decision.reason}")

    # ---------- Step 4: Critic evaluates completed tasks ----------
    print("\n🧪 CRITIC OUTPUT")
    print("=" * 80)
    critic_feedback = critic.evaluate(goal, plan.tasks)

    for fb in critic_feedback:
        print(f"Task {fb.task_id}")
        print(f"  Verdict: {fb.verdict}")
        print(f"  Issues: {fb.issues}")
        print(f"  Suggestions: {fb.suggestions}")

    # ---------- Step 5: Summary ----------
    completed = sum(1 for t in plan.tasks if t.status == TaskStatus.COMPLETED)
    failed = sum(1 for t in plan.tasks if t.status == TaskStatus.FAILED)
    failed_perm = sum(1 for t in plan.tasks if t.status == TaskStatus.FAILED_PERMANENT)
    total = len(plan.tasks)

    print("\n📊 Summary:")
    print(f"Total tasks: {total}")
    print(f"Completed: {completed}")
    print(f"Failed: {failed}")
    print(f"Failed permanent: {failed_perm}")

    # ---------- Step 6: Assertion (Optional sanity check) ----------
    assert completed + failed + failed_perm == total
    print("\n✅ Full Planner + Executor + Supervisor + Critic integration test passed")


if __name__ == "__main__":
    test_full_pipeline()