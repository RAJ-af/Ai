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
        "chat_history": [] # Now a list of {"role": "...", "content": "..."}
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

    state["chat_history"].append({"role": "user", "content": message})
    state["chat_history"].append({"role": "assistant", "content": response})

    if boss.is_ready(response):
        state['is_interview_complete'] = True
        summary = ""
        for msg in state["chat_history"]:
            role = "User" if msg["role"] == "user" else "AI"
            summary += f"{role}: {msg['content']}\n"
        state['project_summary'] = summary

    return state["chat_history"], state, ""

def generate_plan_ui(state):
    if not state.get('is_interview_complete'):
        return "Please complete the Boss AI interview first.", gr.update(visible=False), gr.update(visible=False), state

    try:
        boss, planner, ceo = restore_agents(state)
        summary = state.get('project_summary', '')
        plan = planner.generate_plan(summary)

        if "❌ Error" in plan:
            return plan, gr.update(visible=False), gr.update(visible=False), state

        state['plan'] = plan
        state['planner_state'] = planner.get_state()

        return plan, gr.update(value=plan, visible=True), gr.update(visible=True), state
    except Exception as e:
        return f"❌ UI Error: {str(e)}", gr.update(visible=False), gr.update(visible=False), state

def run_execution_ui(approved_plan, state):
    yield "🚀 CEO is assembling the team and starting development...", None, state

    try:
        boss, planner, ceo = restore_agents(state)
        output = ceo.execute_project(approved_plan)

        if "❌ Error" in output:
             yield output, None, state
             return

        state['ceo_state'] = ceo.get_state()

        # Create ZIP
        zip_buffer = create_project_zip([output])
        fd, zip_path = tempfile.mkstemp(suffix=".zip")
        with os.fdopen(fd, 'wb') as f:
            f.write(zip_buffer.getbuffer())

        yield output, zip_path, state
    except Exception as e:
        yield f"❌ Execution Error: {str(e)}", None, state

def on_load(state):
    if not state:
        state = get_initial_state()

    # Handle legacy chat_history format if it exists (for backward compatibility during migration)
    chat_history = state.get("chat_history", [])
    formatted_history = []
    for m in chat_history:
        if isinstance(m, (list, tuple)):
            formatted_history.append({"role": "user", "content": m[0]})
            formatted_history.append({"role": "assistant", "content": m[1]})
        else:
            formatted_history.append(m)
    state["chat_history"] = formatted_history

    plan_val = state.get('plan', '')
    plan_edit_vis = gr.update(value=plan_val, visible=bool(plan_val))
    approve_btn_vis = gr.update(visible=bool(plan_val))
    plan_display_val = plan_val if plan_val else "*Your plan will appear here after generation...*"

    return state, formatted_history, plan_display_val, plan_edit_vis, approve_btn_vis

with gr.Blocks() as demo:
    session_state = gr.BrowserState(get_initial_state())

    gr.Markdown("# 🤖 Autonomous AI Developer Team")
    gr.Markdown("Transform your ideas into code. Use **/new** to reset the session.")

    with gr.Tab("1. Interview (Boss AI)"):
        chatbot = gr.Chatbot(label="Boss AI Chat") # Explicitly set type to messages
        msg = gr.Textbox(label="Your Message (Type /new to reset)")

        msg.submit(chat_with_boss, inputs=[msg, chatbot, session_state], outputs=[chatbot, session_state, msg])

    with gr.Tab("2. Planning (Architect AI)"):
        plan_btn = gr.Button("Generate PRD & Plan", variant="primary")
        plan_display = gr.Markdown("*Your plan will appear here after generation...*")
        plan_edit = gr.Textbox(label="Review & Edit PRD/Plan", lines=15, visible=False)
        approve_btn = gr.Button("Approve & Start Execution", variant="stop", visible=False)

        plan_btn.click(
            generate_plan_ui,
            inputs=[session_state],
            outputs=[plan_display, plan_edit, approve_btn, session_state]
        )

    with gr.Tab("3. Execution & Code Delivery"):
        exec_status = gr.Markdown("Waiting for approval...")
        file_download = gr.File(label="Download Source Code (ZIP)")

        approve_btn.click(
            run_execution_ui,
            inputs=[plan_edit, session_state],
            outputs=[exec_status, file_download, session_state]
        )

    demo.load(on_load, inputs=[session_state], outputs=[session_state, chatbot, plan_display, plan_edit, approve_btn])

if __name__ == "__main__":
    demo.launch(theme=gr.themes.Soft())
