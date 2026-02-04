# test_planner_executor_supervisor_critic_supervisor.py

from agents.planner import PlannerAgent
from agents.executor import ExecutorAgent
from agents.supervisor import TaskSupervisorAgent
from agents.critic import CriticAgent
from schemas.task_status import TaskStatus

def test_full_pipeline_with_retries():
    # ---------- Step 0: Setup ----------
    goal = "Complete the data analysis report with visualizations"
    max_attempts = 3

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

    # ---------- Step 2: Execution + Supervisor/Critic Loop ----------
    while True:
        # Execute only tasks eligible for execution
        for task in plan.tasks:
            if task.status in [TaskStatus.PENDING, TaskStatus.FAILED]:
                updated_task = executor.execute(task)
                print(f"\n➡️ Executed Task {updated_task.id} | status={updated_task.status}, attempts={updated_task.attempts}")

        # Supervisor reviews plan after execution
        decision = supervisor.review_plan(plan)
        print("\n⚡ SUPERVISOR OUTPUT (post-execution)")
        print(f"Decision: {decision.decision}, Tasks to retry: {decision.tasks_to_retry}, Reason: {decision.reason}")

        if decision.decision == "RETRY":
            continue  # retry eligible tasks
        else:
            # Critic evaluates all completed tasks
            critic_feedback = critic.evaluate(goal, plan.tasks)
            print("\n🧪 CRITIC OUTPUT")
            for fb in critic_feedback:
                print(f"Task {fb.task_id} | Verdict: {fb.verdict} | Suggestions: {fb.suggestions}")

            # Supervisor reviews post-critic for retryable feedback
            post_critic_decision = supervisor.review_after_critic(plan, critic_feedback)
            print("\n⚡ SUPERVISOR OUTPUT (post-critic)")
            print(f"Decision: {post_critic_decision.decision}, Tasks to retry: {post_critic_decision.tasks_to_retry}, Reason: {post_critic_decision.reason}")

            if post_critic_decision.decision == "RETRY":
                continue  # retry tasks suggested by critic
            else:
                break  # no more retries, finish

    # ---------- Step 3: Summary ----------
    completed = sum(1 for t in plan.tasks if t.status == TaskStatus.COMPLETED)
    failed = sum(1 for t in plan.tasks if t.status == TaskStatus.FAILED)
    failed_perm = sum(1 for t in plan.tasks if t.status == TaskStatus.FAILED_PERMANENT)
    total = len(plan.tasks)

    print("\n📊 Summary:")
    print(f"Total tasks: {total}")
    print(f"Completed: {completed}")
    print(f"Failed: {failed}")
    print(f"Failed permanent: {failed_perm}")

    assert completed + failed + failed_perm == total
    print("\n✅ Full Planner + Executor + Supervisor + Critic loop with retries passed")


if __name__ == "__main__":
    test_full_pipeline_with_retries()
