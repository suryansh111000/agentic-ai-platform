from agents.planner import PlannerAgent
from agents.executor import ExecutorAgent
from agents.supervisor import TaskSupervisorAgent
from agents.critic import CriticAgent
from schemas.task_status import TaskStatus

def run_full_pipeline(goal: str, max_attempts: int = 3):
    logs = []
    summary = {}

    planner = PlannerAgent()
    executor = ExecutorAgent()
    supervisor = TaskSupervisorAgent(max_attempts=max_attempts)
    critic = CriticAgent()

    logs.append("🧠 PlannerAgent started")

    # ---------- Planning ----------
    plan = planner.plan(goal)
    logs.append("\n🧠 PLANNER OUTPUT")
    logs.append(str(plan))

    # ---------- Execution loop ----------
    while True:
        for task in plan.tasks:
            if task.status in [TaskStatus.PENDING, TaskStatus.FAILED]:
                updated_task = executor.execute(task)
                logs.append(
                    f"➡️ Executed Task {updated_task.id} | "
                    f"status={updated_task.status}, attempts={updated_task.attempts}"
                )

        decision = supervisor.review_plan(plan)
        logs.append(
            f"\n⚡ SUPERVISOR (post-execution): {decision.decision} | "
            f"Retry: {decision.tasks_to_retry} | Reason: {decision.reason}"
        )

        if decision.decision == "RETRY":
            continue

        # ---------- Critic ----------
        critic_feedback = critic.evaluate(goal, plan.tasks)
        logs.append("\n🧪 CRITIC OUTPUT")

        for fb in critic_feedback:
            logs.append(
                f"Task {fb.task_id} | Verdict: {fb.verdict} | Suggestions: {fb.suggestions}"
            )

        post_decision = supervisor.review_after_critic(plan, critic_feedback)
        logs.append(
            f"\n⚡ SUPERVISOR (post-critic): {post_decision.decision} | "
            f"Retry: {post_decision.tasks_to_retry} | Reason: {post_decision.reason}"
        )

        if post_decision.decision == "RETRY":
            continue
        break

    # ---------- Summary ----------
    completed = sum(1 for t in plan.tasks if t.status == TaskStatus.COMPLETED)
    failed = sum(1 for t in plan.tasks if t.status == TaskStatus.FAILED)
    failed_perm = sum(1 for t in plan.tasks if t.status == TaskStatus.FAILED_PERMANENT)

    summary = {
        "total_tasks": len(plan.tasks),
        "completed": completed,
        "failed": failed,
        "failed_permanent": failed_perm,
    }

    return "\n".join(logs), summary
