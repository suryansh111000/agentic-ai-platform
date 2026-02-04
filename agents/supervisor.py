from schemas.task_status import TaskStatus
from schemas.supervisor_decision import SupervisorDecision, SupervisorDecisionType
from typing import List
from schemas.critic_feedback import CriticFeedback
from schemas.critic_verdict import CriticVerdict
from schemas.task_plan import TaskPlan

class TaskSupervisorAgent:
    """
    Inspects a TaskPlan after execution and decides next steps.

    Contract:
    - Input: TaskPlan (post execution)
    - Output: SupervisorDecision
        - RETRY with list of task IDs
        - PROCEED_TO_CRITIC
    """

    def __init__(self, max_attempts: int = 3):
        self.max_attempts = max_attempts

    def review_plan(self, plan: TaskPlan) -> SupervisorDecision:
        retry_tasks = []

        for task in plan.tasks:
            if task.status == TaskStatus.FAILED:
                if task.attempts < self.max_attempts:
                    retry_tasks.append(task.id)
                else:
                    task.status = TaskStatus.FAILED_PERMANENT

        if retry_tasks:
            return SupervisorDecision(
                decision=SupervisorDecisionType.RETRY,
                tasks_to_retry=retry_tasks,
                reason=f"{len(retry_tasks)} task(s) eligible for retry"
            )

        # No retryable tasks left → proceed
        return SupervisorDecision(
            decision=SupervisorDecisionType.PROCEED_TO_CRITIC,
            tasks_to_retry=[],
            reason="All tasks completed or permanently failed"
        )
    
    def review_after_critic(
        self,
        plan: TaskPlan,
        feedbacks: List[CriticFeedback],
    ) -> SupervisorDecision:
        """
        Post-critic review.
        Decides whether tasks should be retried based on critic verdicts
        and remaining attempts.
        """
        retry_tasks = []

        feedback_by_task_id = {fb.task_id: fb for fb in feedbacks}

        for task in plan.tasks:
            fb = feedback_by_task_id.get(task.id)

            if not fb:
                continue

            if fb.verdict == CriticVerdict.FAIL_RETRYABLE:
                if task.attempts < self.max_attempts:
                    task.status = TaskStatus.PENDING
                    retry_tasks.append(task.id)
                else:
                    task.status = TaskStatus.FAILED_PERMANENT

        if retry_tasks:
            return SupervisorDecision(
                decision=SupervisorDecisionType.RETRY,
                tasks_to_retry=retry_tasks,
                reason="Retrying tasks based on critic feedback"
            )

        return SupervisorDecision(
            decision=SupervisorDecisionType.PROCEED_TO_CRITIC,
            tasks_to_retry=[],
            reason="No retryable critic failures"
        )