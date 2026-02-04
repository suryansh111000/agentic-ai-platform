# test_supervisor.py

from agents.supervisor import TaskSupervisorAgent
from schemas.task import Task
from schemas.task_status import TaskStatus
from schemas.task_plan import TaskPlan  # assuming this exists
from schemas.supervisor_decision import SupervisorDecisionType


def test_supervisor_agent():
    max_attempts = 2
    supervisor = TaskSupervisorAgent(max_attempts=max_attempts)

    # ------------------ Test 1: All tasks completed ------------------
    plan1 = TaskPlan(
        goal="Test Goal 1",
        tasks=[
            Task(id=1, description="Task 1", status=TaskStatus.COMPLETED, attempts=1),
            Task(id=2, description="Task 2", status=TaskStatus.COMPLETED, attempts=1),
        ]
    )

    decision1 = supervisor.review_plan(plan1)
    assert decision1.decision == SupervisorDecisionType.PROCEED_TO_CRITIC
    assert decision1.tasks_to_retry == []
    print("✅ Test 1 passed: All tasks completed → proceed to critic")

    # ------------------ Test 2: Some tasks failed, retryable ------------------
    plan2 = TaskPlan(
        goal="Test Goal 2",
        tasks=[
            Task(id=1, description="Task 1", status=TaskStatus.COMPLETED, attempts=1),
            Task(id=2, description="Task 2", status=TaskStatus.FAILED, attempts=1),
            Task(id=3, description="Task 3", status=TaskStatus.FAILED, attempts=0),
        ]
    )

    decision2 = supervisor.review_plan(plan2)
    assert decision2.decision == SupervisorDecisionType.RETRY
    assert set(decision2.tasks_to_retry) == {2, 3}
    print("✅ Test 2 passed: Retryable failed tasks identified correctly")

    # ------------------ Test 3: Some tasks failed, exceeded max attempts ------------------
    plan3 = TaskPlan(
        goal="Test Goal 3",
        tasks=[
            Task(id=1, description="Task 1", status=TaskStatus.FAILED, attempts=2),
            Task(id=2, description="Task 2", status=TaskStatus.FAILED, attempts=3),
            Task(id=3, description="Task 3", status=TaskStatus.COMPLETED, attempts=1),
        ]
    )

    decision3 = supervisor.review_plan(plan3)
    # Task 1: attempts == max_attempts → retryable? Let's check our supervisor logic:
    # In our implementation, retryable = attempts < max_attempts
    # So task.attempts == max_attempts → should be FAILED_PERMANENT
    # Task 2: attempts > max_attempts → FAILED_PERMANENT

    failed_permanent_ids = [t.id for t in plan3.tasks if t.status == TaskStatus.FAILED_PERMANENT]
    assert set(failed_permanent_ids) == {1, 2}
    assert decision3.decision == SupervisorDecisionType.PROCEED_TO_CRITIC
    assert decision3.tasks_to_retry == []
    print("✅ Test 3 passed: Exceeded attempts → tasks marked FAILED_PERMANENT and proceed to critic")


if __name__ == "__main__":
    test_supervisor_agent()