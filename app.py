import gradio as gr
import os
from agents.boss import BossAgent
from agents.planner import PlannerAgent
from agents.ceo import CEOAgent
from utils.file_manager import create_project_zip
import tempfile

# State management
class GlobalState:
    def __init__(self):
        self.boss = BossAgent()
        self.planner = PlannerAgent()
        self.ceo = CEOAgent()
        self.project_summary = ""
        self.is_interview_complete = False

gs = GlobalState()

def chat_with_boss(message, history):
    response = gs.boss.interview(message)
    if gs.boss.is_ready(response):
        gs.is_interview_complete = True
        # history is a list of tuples in older gradio or different in newer
        summary_parts = []
        for h in history:
            # h might be a dict or a list depending on Gradio version
            if isinstance(h, dict):
                role = h.get("role")
                content = h.get("content")
                summary_parts.append(f"{role}: {content}")
            else:
                summary_parts.append(f"User: {h[0]}\nAI: {h[1]}")
        summary_parts.append(f"User: {message}\nAI: {response}")
        gs.project_summary = "\n".join(summary_parts)
        return response + "\n\n✅ **Interview Complete!** Go to the '2. Planning' tab."
    return response

def generate_plan_ui():
    if not gs.is_interview_complete:
        return "Please complete the Boss AI interview first.", gr.update(visible=False), gr.update(visible=False)
    plan = gs.planner.generate_plan(gs.project_summary)
    return plan, gr.update(value=plan, visible=True), gr.update(visible=True)

def run_execution_ui(approved_plan):
    yield "🚀 CEO is starting the project...", None
    output = gs.ceo.execute_project(approved_plan)

    # Create ZIP
    zip_buffer = create_project_zip([output])
    temp_dir = tempfile.gettempdir()
    zip_path = os.path.join(temp_dir, "project_source.zip")
    with open(zip_path, "wb") as f:
        f.write(zip_buffer.getbuffer())

    yield output, zip_path

with gr.Blocks() as demo:
    gr.Markdown("# 🤖 Team AI Developer")
    gr.Markdown("Build entire projects from scratch using an autonomous AI team.")

    with gr.Tab("1. Boss AI Interview"):
        gr.ChatInterface(chat_with_boss)

    with gr.Tab("2. Planning"):
        plan_btn = gr.Button("Generate PRD & Plan", variant="primary")
        plan_display = gr.Markdown("### Project Plan will appear here...")
        plan_edit = gr.Textbox(label="Edit Plan / PRD", lines=15, visible=False)
        approve_btn = gr.Button("Approve & Start Coding", variant="stop", visible=False)

        plan_btn.click(generate_plan_ui, outputs=[plan_display, plan_edit, approve_btn])

    with gr.Tab("3. Execution & Download"):
        exec_status = gr.Markdown("### Execution Results")
        file_download = gr.File(label="Download Generated Source Code (ZIP)")

        approve_btn.click(run_execution_ui, inputs=[plan_edit], outputs=[exec_status, file_download])

if __name__ == "__main__":
    demo.launch()
