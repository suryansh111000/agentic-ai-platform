from agents.executor import ExecutorAgent
from schemas.task import Task
from schemas.task_status import TaskStatus


def run_test(task_id, description):
    agent = ExecutorAgent()
    task = Task(
        id=task_id,
        description=description,
        status=TaskStatus.PENDING,
        attempts=0,
        result=None,
        error=None,
    )

    result_task = agent.execute(task)

    print("-" * 40)
    print(f"Task ID: {result_task.id}")
    print(f"Description: {result_task.description}")
    print(f"Status: {result_task.status}")
    print(f"Attempts: {result_task.attempts}")
    print(f"Result: {result_task.result}")
    print(f"Error: {result_task.error}")


if __name__ == "__main__":
    # Successful task
    run_test(1, "Generate a summary")

    # Failing task
    run_test(2, "This task should fail")
