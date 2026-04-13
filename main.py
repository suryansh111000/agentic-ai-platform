from fastapi import FastAPI,HTTPException
from pydantic import BaseModel
from typing import List

from agents.planner import PlannerAgent
from agents.executor import ExecutorAgent
from agents.supervisor import TaskSupervisorAgent
from agents.critic import CriticAgent
from schemas.task_status import TaskStatus

# ---------- DTOs for Java ↔ Python ----------
class MessageDto(BaseModel):
    role: str
    content: str

class AIRequest(BaseModel):
    goal: str
    conversationHistory: List[MessageDto] = []

class TasksSummary(BaseModel):
    total: int
    completed: int
    failed: int

class AIResponse(BaseModel):
    finalResponse: str
    status: str
    tasksSummary: TasksSummary

# ---------- FastAPI ----------
app = FastAPI()

@app.post("/run-agent", response_model=AIResponse)
async def run_agent(request: AIRequest):

    goal = request.goal
    max_attempts = 3

    planner = PlannerAgent()
    executor = ExecutorAgent()
    supervisor = TaskSupervisorAgent(max_attempts=max_attempts)
    critic = CriticAgent()

    try:
        plan = planner.plan(goal)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail="Unexpected AI failure")

    # ---------- Executor + Supervisor + Critic loop ----------
    max_loops = 3
    loop_count = 0

    while loop_count < max_loops:
        loop_count += 1
        print(f"🔁 Loop iteration: {loop_count}")

        for task in plan.tasks:
            if task.status in [TaskStatus.PENDING, TaskStatus.FAILED]:
                executor.execute(task)

        decision = supervisor.review_plan(plan)

        if decision.decision == "RETRY":
            continue
        else:
            feedback = critic.evaluate(goal, plan.tasks)
            post_critic_decision = supervisor.review_after_critic(plan, feedback)

            if post_critic_decision.decision == "RETRY":
                continue
            else:
                break

    print("✅ Exiting loop")

    total = len(plan.tasks)
    completed = sum(1 for t in plan.tasks if t.status == TaskStatus.COMPLETED)
    failed = sum(1 for t in plan.tasks if t.status == TaskStatus.FAILED)

    return AIResponse(
        finalResponse="Simulation complete",  # you can replace with actual combined output
        status="SUCCESS",
        tasksSummary=TasksSummary(total=total, completed=completed, failed=failed)
    )
@app.post("/plan")
async def plan_only(request: AIRequest):
    planner = PlannerAgent()

    try:
        plan = planner.plan(request.goal)

        return {
            "tasks": [
                {
                    "id": t.id,
                    "description": t.description,
                    "status": t.status
                }
                for t in plan.tasks
            ]
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
class ExecuteRequest(BaseModel):
    description: str


@app.post("/execute")
async def execute_only(request: ExecuteRequest):
    executor = ExecutorAgent()

    # creating a dummy task object (since executor expects it)
    class DummyTask:
        def __init__(self, description):
            self.description = description
            self.status = TaskStatus.PENDING

    task = DummyTask(request.description)

    try:
        executor.execute(task)

        return {
            "description": task.description,
            "status": task.status
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
class CriticRequest(BaseModel):
    goal: str
    outputs: List[str]


@app.post("/critic")
async def critic_only(request: CriticRequest):
    critic = CriticAgent()

    # convert outputs into dummy tasks
    class DummyTask:
        def __init__(self, idx, output):
            self.id = idx                      # 👈 REQUIRED
            self.description = output          # 👈 REQUIRED
            self.result = output               # 👈 REQUIRED
            self.status = TaskStatus.COMPLETED # 👈 REQUIRED

    tasks = [
        DummyTask(idx=i+1, output=o)
        for i, o in enumerate(request.outputs)
    ]

    try:
        feedback = critic.evaluate(request.goal, tasks)

        return {
            "feedback": feedback
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))