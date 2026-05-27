import gradio as gr
import os
import tempfile
import time
from agents.boss import BossAgent
from agents.planner import PlannerAgent
from agents.ceo import CEOAgent
from utils.file_manager import create_project_zip

def get_initial_state():
    return {
        "is_interview_complete": False,
        "project_summary": "",
        "plan": "",
        "boss_state": {},
        "planner_state": {},
        "ceo_state": {},
        "chat_history": [],
        "agent_outputs": {
            "UI/UX Agent": "Waiting...",
            "Backend Agent": "Waiting...",
            "Frontend Agent": "Waiting...",
            "QA Agent": "Waiting...",
            "DevOps Agent": "Waiting..."
        }
    }

def restore_agents(state):
    boss, planner, ceo = BossAgent(), PlannerAgent(), CEOAgent()
    if state.get("boss_state"): boss.load_state(state["boss_state"])
    if state.get("planner_state"): planner.load_state(state["planner_state"])
    if state.get("ceo_state"): ceo.load_state(state["ceo_state"])
    return boss, planner, ceo

def chat_with_boss_stream(message, history, state):
    if message.strip() == "/new":
        new_state = get_initial_state()
        return [], new_state, ""

    if not state: state = get_initial_state()
    boss, planner, ceo = restore_agents(state)

    history.append({"role": "user", "content": message})
    history.append({"role": "assistant", "content": ""})

    for partial_resp in boss.chat_stream(message):
        history[-1]["content"] = partial_resp
        yield history, state, ""

    state["boss_state"] = boss.get_state()
    state["chat_history"] = history

    if boss.is_ready(history[-1]["content"]):
        state['is_interview_complete'] = True
        history[-1]["content"] += "\n\n✅ **Ready!** Go to the Architecture tab."
        summary = ""
        for msg in history:
            role = "User" if msg["role"] == "user" else "AI"
            summary += f"{role}: {msg['content']}\n"
        state['project_summary'] = summary
        yield history, state, ""

def generate_plan_stream(state):
    if not state.get('is_interview_complete'):
        yield "⚠️ Finish interview first.", gr.update(visible=False), gr.update(visible=False), state
        return

    boss, planner, ceo = restore_agents(state)
    summary = state.get('project_summary', '')

    plan_content = ""
    for partial_plan in planner.chat_stream(f"Based on this summary: {summary}, generate PRD and architecture."):
        plan_content = partial_plan
        yield plan_content, gr.update(visible=False), gr.update(visible=False), state

    state['plan'] = plan_content
    state['planner_state'] = planner.get_state()
    yield plan_content, gr.update(value=plan_content, visible=True), gr.update(visible=True), state

def run_execution_stream(approved_plan, state):
    boss, planner, ceo = restore_agents(state)

    for todo, status, worker_output, zip_path, s_update in ceo.execute_project_with_dashboard(approved_plan, state):
        outputs = list(s_update["agent_outputs"].values())
        yield todo, status, worker_output, zip_path, s_update, *outputs

def on_load(state):
    if not state: state = get_initial_state()
    history = state.get("chat_history", [])
    plan_val = state.get('plan', '')
    outputs = list(state.get("agent_outputs", {}).values())
    return state, history, plan_val, gr.update(value=plan_val, visible=bool(plan_val)), gr.update(visible=bool(plan_val)), *outputs

with gr.Blocks(title="AI Dev Team") as demo:
    session_state = gr.BrowserState(get_initial_state())

    gr.Markdown("# 🚀 Professional AI Developer Team")

    with gr.Tab("1. Interview"):
        chatbot = gr.Chatbot(label="Boss AI", height=450)
        msg = gr.Textbox(placeholder="Talk to the Boss AI...", label="Input")
        msg.submit(chat_with_boss_stream, inputs=[msg, chatbot, session_state], outputs=[chatbot, session_state, msg])

    with gr.Tab("2. Architecture"):
        plan_btn = gr.Button("Draft Technical Architecture", variant="primary")
        plan_display = gr.Markdown("### Architectural Blueprint")
        plan_edit = gr.Textbox(label="Edit PRD", lines=15, visible=False)
        approve_btn = gr.Button("Approve & Deploy Team", variant="stop", visible=False)
        plan_btn.click(generate_plan_stream, inputs=[session_state], outputs=[plan_display, plan_edit, approve_btn, session_state])

    with gr.Tab("3. Dashboard"):
        with gr.Row():
            with gr.Column(scale=1):
                todo_board = gr.Markdown("### 📋 Roadmap")
                file_download = gr.File(label="Project Assets")
            with gr.Column(scale=3):
                status_box = gr.Markdown("### 🚀 System Health")
                with gr.Row():
                    uiux_box = gr.Textbox(label="UI/UX", lines=4, interactive=False)
                    backend_box = gr.Textbox(label="Backend", lines=4, interactive=False)
                with gr.Row():
                    frontend_box = gr.Textbox(label="Frontend", lines=4, interactive=False)
                    qa_box = gr.Textbox(label="QA", lines=4, interactive=False)
                with gr.Row():
                    devops_box = gr.Textbox(label="DevOps", lines=4, interactive=False)
                worker_console = gr.Markdown("### 🛠️ Agent Terminal")

        approve_btn.click(
            run_execution_stream,
            inputs=[plan_edit, session_state],
            outputs=[todo_board, status_box, worker_console, file_download, session_state,
                     uiux_box, backend_box, frontend_box, qa_box, devops_box]
        )

    demo.load(on_load, inputs=[session_state],
              outputs=[session_state, chatbot, plan_display, plan_edit, approve_btn,
                       uiux_box, backend_box, frontend_box, qa_box, devops_box])

if __name__ == "__main__":
    demo.launch(theme=gr.themes.Soft())
