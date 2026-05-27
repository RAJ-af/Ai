import gradio as gr
import os
import tempfile
from agents.boss import BossAgent
from agents.planner import PlannerAgent
from agents.ceo import CEOAgent
from utils.file_manager import create_project_zip

def chat_with_boss(message, history, boss_agent, state):
    response = boss_agent.interview(message)

    if boss_agent.is_ready(response):
        state['is_interview_complete'] = True

        summary = ""
        for user_msg, ai_msg in history:
            summary += f"User: {user_msg}\nAI: {ai_msg}\n"
        summary += f"User: {message}\nAI: {response}"
        state['project_summary'] = summary

        return response + "\n\n✅ **Interview Complete!** Please move to the **2. Planning** tab."

    return response

def generate_plan_ui(state, planner_agent):
    if not state.get('is_interview_complete'):
        return "Please complete the Boss AI interview first.", gr.update(visible=False), gr.update(visible=False)

    summary = state.get('project_summary', '')
    plan = planner_agent.generate_plan(summary)
    state['plan'] = plan

    return plan, gr.update(value=plan, visible=True), gr.update(visible=True)

def run_execution_ui(approved_plan, state, ceo_agent):
    yield "🚀 CEO is assembling the team and starting development...", None

    output = ceo_agent.execute_project(approved_plan)

    # Create ZIP
    zip_buffer = create_project_zip([output])
    fd, zip_path = tempfile.mkstemp(suffix=".zip")
    with os.fdopen(fd, 'wb') as f:
        f.write(zip_buffer.getbuffer())

    yield output, zip_path

# Initialize agents in state
def init_session():
    return BossAgent(), PlannerAgent(), CEOAgent(), {}

with gr.Blocks() as demo:
    # Session-specific agents and state
    boss_agent = gr.State(BossAgent)
    planner_agent = gr.State(PlannerAgent)
    ceo_agent = gr.State(CEOAgent)
    session_state = gr.State({})

    gr.Markdown("# 🤖 Autonomous AI Developer Team")
    gr.Markdown("Transform your ideas into code using a specialized squad of AI agents.")

    with gr.Tab("1. Interview (Boss AI)"):
        gr.Markdown("### Phase 1: Requirements Gathering\nTalk to the Boss AI to define your project.")

        gr.ChatInterface(
            fn=chat_with_boss,
            additional_inputs=[boss_agent, session_state],
        )

    with gr.Tab("2. Planning (Architect AI)"):
        gr.Markdown("### Phase 2: PRD & Technical Design")
        plan_btn = gr.Button("Generate PRD & Plan", variant="primary")
        plan_display = gr.Markdown("*Your plan will appear here after generation...*")
        plan_edit = gr.Textbox(label="Review & Edit PRD/Plan", lines=15, visible=False)
        approve_btn = gr.Button("Approve & Start Execution", variant="stop", visible=False)

        plan_btn.click(
            generate_plan_ui,
            inputs=[session_state, planner_agent],
            outputs=[plan_display, plan_edit, approve_btn]
        )

    with gr.Tab("3. Execution & Code Delivery"):
        gr.Markdown("### Phase 3: Development & Packaging")
        exec_status = gr.Markdown("Waiting for approval...")
        file_download = gr.File(label="Download Source Code (ZIP)")

        approve_btn.click(
            run_execution_ui,
            inputs=[plan_edit, session_state, ceo_agent],
            outputs=[exec_status, file_download]
        )

    demo.load(init_session, outputs=[boss_agent, planner_agent, ceo_agent, session_state])

if __name__ == "__main__":
    demo.launch(theme=gr.themes.Soft())
