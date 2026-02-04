# Agentic AI Platform 🤖

A **multi-agent AI system** designed to autonomously plan, execute, supervise, and evaluate tasks using AI agents.  
This project demonstrates an **agentic AI pipeline** with Planner → Executor → Supervisor → Critic, all coordinated through a **Gradio web UI**.

---

## Features

- **Planner Agent**: Generates a plan of tasks based on a user-defined goal.  
- **Executor Agent**: Executes tasks and returns results.  
- **Task Supervisor**: Reviews task execution, decides retries, and ensures task reliability.  
- **Critic Agent**: Evaluates completed tasks for correctness and provides feedback/suggestions.  
- **Gradio UI**: Simple, interactive web interface to input goals, view execution logs, and see task summaries.  

---

## Architecture

User Goal
│
▼
Planner Agent ──► Task Plan ──► Executor Agent ──► Task Results
│ │
▼ ▼
Task Supervisor ◄───────────────────────── Critic Agent


- The pipeline **loops** until the supervisor decides the plan is complete.  
- Critic provides **quality checks** and recommendations for improving task results.

---

## Tech Stack

- **Python 3.10+**  
- **Gradio** for interactive web interface  
- **Transformers / Hugging Face models** for LLM-based agents  
- Modular architecture for **Planner, Executor, Supervisor, Critic** agents  

---

## Installation

1. Clone the repository:

```bash
git clone https://github.com/suryansh111000/agentic-ai-platform.git
cd agentic-ai-platform


Install dependencies:
pip install -r requirements.txt

For running the App
python app.py
Open the local web UI in your browser (usually http://127.0.0.1:7860)

Contributing

Contributions are welcome!
Fork the repo
Create a new branch (git checkout -b feature-name)
Commit your changes (git commit -m "Add feature")
Push to branch (git push origin feature-name)
Open a Pull Request
