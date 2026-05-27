import gradio as gr
import os
import tempfile
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
    boss = BossAgent()
    planner = PlannerAgent()
    ceo = CEOAgent()
    if state.get("boss_state"): boss.load_state(state["boss_state"])
    if state.get("planner_state"): planner.load_state(state["planner_state"])
    if state.get("ceo_state"): ceo.load_state(state["ceo_state"])
    return boss, planner, ceo

def chat_with_boss(message, history, state):
    if message.strip() == "/new":
        new_state = get_initial_state()
        return [], new_state, ""
    if not state: state = get_initial_state()
    boss, planner, ceo = restore_agents(state)
    response = boss.interview(message)
    state["boss_state"] = boss.get_state()
    if boss.is_ready(response):
        state['is_interview_complete'] = True
        response += "\n\n✅ **Interview Complete!** Go to the **2. Architecture** tab."
    state["chat_history"].append({"role": "user", "content": message})
    state["chat_history"].append({"role": "assistant", "content": response})
    if state['is_interview_complete']:
        summary = ""
        for msg in state["chat_history"]:
            role = "User" if msg["role"] == "user" else "AI"
            summary += f"{role}: {msg['content']}\n"
        state['project_summary'] = summary
    return state["chat_history"], state, ""

def manual_complete(state):
    if not state: state = get_initial_state()
    state['is_interview_complete'] = True
    summary = ""
    for msg in state.get("chat_history", []):
        role = "User" if msg["role"] == "user" else "AI"
        summary += f"{role}: {msg['content']}\n"
    state['project_summary'] = summary
    state["chat_history"].append({"role": "assistant", "content": "✅ **Manual Override:** Ready for planning."})
    return state["chat_history"], state

def generate_plan_ui(state):
    if not state.get('is_interview_complete'):
        yield "⚠️ Please complete interview.", gr.update(visible=False), gr.update(visible=False), state
        return
    yield "🧠 **Architect AI** is drafting the Technical Architecture and PRD...", gr.update(visible=False), gr.update(visible=False), state
    boss, planner, ceo = restore_agents(state)
    plan = planner.generate_plan(state.get('project_summary', ''))
    state['plan'] = plan
    state['planner_state'] = planner.get_state()
    yield plan, gr.update(value=plan, visible=True), gr.update(visible=True), state

def run_execution_ui(approved_plan, state):
    boss, planner, ceo = restore_agents(state)
    for todo, status, worker_output, zip_path, s_update in ceo.execute_project_with_dashboard(approved_plan, state):
        outputs = list(s_update["agent_outputs"].values())
        yield todo, status, worker_output, zip_path, s_update, *outputs

def on_load(state):
    if not state: state = get_initial_state()
    chat_history = state.get("chat_history", [])
    # Migration
    formatted_history = []
    for m in chat_history:
        if isinstance(m, (list, tuple)):
            formatted_history.append({"role": "user", "content": m[0]})
            formatted_history.append({"role": "assistant", "content": m[1]})
        else: formatted_history.append(m)
    state["chat_history"] = formatted_history

    plan_val = state.get('plan', '')
    agent_outputs = list(state.get("agent_outputs", {}).values())
    return state, formatted_history, plan_val, gr.update(value=plan_val, visible=bool(plan_val)), gr.update(visible=bool(plan_val)), *agent_outputs

with gr.Blocks(title="Team AI Developer") as demo:
    session_state = gr.BrowserState(get_initial_state())

    gr.Markdown("# 🤖 Team AI Developer v3.0")
    gr.Markdown("Autonomous agent team for full-stack development.")

    with gr.Tab("1. Interview"):
        chatbot = gr.Chatbot(label="Conversation with Boss AI")
        with gr.Row():
            msg = gr.Textbox(label="Input", scale=4)
            finish_btn = gr.Button("Finish Interview", scale=1)
        msg.submit(chat_with_boss, inputs=[msg, chatbot, session_state], outputs=[chatbot, session_state, msg])
        finish_btn.click(manual_complete, inputs=[session_state], outputs=[chatbot, session_state])

    with gr.Tab("2. Architecture"):
        plan_btn = gr.Button("Generate Architecture & PRD", variant="primary")
        plan_display = gr.Markdown("Waiting for requirements...")
        plan_edit = gr.Textbox(label="Review Specification", lines=12, visible=False)
        approve_btn = gr.Button("Approve & Assemble Team", variant="stop", visible=False)
        plan_btn.click(generate_plan_ui, inputs=[session_state], outputs=[plan_display, plan_edit, approve_btn, session_state])

    with gr.Tab("3. Dashboard & Execution"):
        with gr.Row():
            with gr.Column(scale=1):
                todo_board = gr.Markdown("### 📋 Roadmap")
                file_download = gr.File(label="Generated Assets")
            with gr.Column(scale=3):
                status_box = gr.Markdown("### 🚀 System Status: Idle")
                with gr.Row():
                    uiux_box = gr.Textbox(label="UI/UX Specialist", lines=4, interactive=False)
                    backend_box = gr.Textbox(label="Backend Specialist", lines=4, interactive=False)
                with gr.Row():
                    frontend_box = gr.Textbox(label="Frontend Specialist", lines=4, interactive=False)
                    qa_box = gr.Textbox(label="QA Specialist", lines=4, interactive=False)
                with gr.Row():
                    devops_box = gr.Textbox(label="DevOps Specialist", lines=4, interactive=False)
                worker_console = gr.Markdown("### 🛠️ Live Agent Logs")

        approve_btn.click(
            run_execution_ui,
            inputs=[plan_edit, session_state],
            outputs=[todo_board, status_box, worker_console, file_download, session_state,
                     uiux_box, backend_box, frontend_box, qa_box, devops_box]
        )

    demo.load(on_load, inputs=[session_state],
              outputs=[session_state, chatbot, plan_display, plan_edit, approve_btn,
                       uiux_box, backend_box, frontend_box, qa_box, devops_box])

if __name__ == "__main__":
    demo.launch(theme=gr.themes.Soft())
