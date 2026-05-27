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
        "chat_history": []
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
        response += "\n\n✅ **Interview Complete!** Ready for planning."

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
    state["chat_history"].append({"role": "assistant", "content": "✅ **Manual Override:** Ready for planning."})
    return state["chat_history"], state

def generate_plan_ui(state):
    if not state.get('is_interview_complete'):
        return "⚠️ Please complete interview.", gr.update(visible=False), gr.update(visible=False), state

    boss, planner, ceo = restore_agents(state)
    plan = planner.generate_plan(state.get('project_summary', ''))
    state['plan'] = plan
    state['planner_state'] = planner.get_state()

    return plan, gr.update(value=plan, visible=True), gr.update(visible=True), state

def run_execution_ui(approved_plan, state):
    boss, planner, ceo = restore_agents(state)

    for todo, status, worker_output in ceo.execute_project(approved_plan):
        zip_path = None
        if "Project fully completed" in status:
            zip_buffer = create_project_zip([worker_output])
            fd, zip_path = tempfile.mkstemp(suffix=".zip")
            with os.fdopen(fd, 'wb') as f:
                f.write(zip_buffer.getbuffer())

        yield todo, status, worker_output, zip_path, state

def on_load(state):
    if not state: state = get_initial_state()
    plan_val = state.get('plan', '')
    return state, state.get("chat_history", []), plan_val, gr.update(value=plan_val, visible=bool(plan_val)), gr.update(visible=bool(plan_val))

with gr.Blocks() as demo:
    session_state = gr.BrowserState(get_initial_state())

    gr.Markdown("# 🤖 Team AI Developer (Advanced)")

    with gr.Tab("1. Interview"):
        chatbot = gr.Chatbot(label="Boss AI Chat")
        msg = gr.Textbox(label="Message")
        finish_btn = gr.Button("Finish Interview", variant="secondary")
        msg.submit(chat_with_boss, inputs=[msg, chatbot, session_state], outputs=[chatbot, session_state, msg])
        finish_btn.click(manual_complete, inputs=[session_state], outputs=[chatbot, session_state])

    with gr.Tab("2. Planning"):
        plan_btn = gr.Button("Create Plan", variant="primary")
        plan_display = gr.Markdown()
        plan_edit = gr.Textbox(label="Edit Plan", lines=15, visible=False)
        approve_btn = gr.Button("Approve", variant="stop", visible=False)
        plan_btn.click(generate_plan_ui, inputs=[session_state], outputs=[plan_display, plan_edit, approve_btn, session_state])

    with gr.Tab("3. Monitoring & Execution"):
        with gr.Row():
            with gr.Column(scale=1):
                todo_board = gr.Markdown("### 📋 Roadmap\n*Pending approval...*")
            with gr.Column(scale=2):
                status_box = gr.Markdown("### 🚀 Status\nIdle")
                worker_console = gr.Markdown("### 🛠️ Worker Console\n*Waiting for logs...*")

        file_download = gr.File(label="Project Artifacts (ZIP)")

        approve_btn.click(
            run_execution_ui,
            inputs=[plan_edit, session_state],
            outputs=[todo_board, status_box, worker_console, file_download, session_state]
        )

    demo.load(on_load, inputs=[session_state], outputs=[session_state, chatbot, plan_display, plan_edit, approve_btn])

if __name__ == "__main__":
    demo.launch(theme=gr.themes.Soft())
