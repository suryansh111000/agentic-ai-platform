import gradio as gr
from run_pipeline import run_full_pipeline

def run_agentic_system(goal):
    logs, summary = run_full_pipeline(goal)

    summary_text = (
        f"📊 Summary\n"
        f"Total tasks: {summary['total_tasks']}\n"
        f"Completed: {summary['completed']}\n"
        f"Failed: {summary['failed']}\n"
        f"Failed permanent: {summary['failed_permanent']}"
    )

    return logs, summary_text

with gr.Blocks(title="Agentic AI System") as demo:
    gr.Markdown("## 🤖 Multi-Agent AI Pipeline (Planner → Executor → Supervisor → Critic)")

    goal_input = gr.Textbox(
        label="Goal",
        placeholder="Enter the goal for the agentic system",
        lines=2,
    )

    run_button = gr.Button("Run Agents 🚀")

    logs_output = gr.Textbox(
        label="Execution Logs",
        lines=25,
    )

    summary_output = gr.Textbox(
        label="Final Summary",
        lines=6,
    )

    run_button.click(
        fn=run_agentic_system,
        inputs=goal_input,
        outputs=[logs_output, summary_output],
    )

demo.launch()
