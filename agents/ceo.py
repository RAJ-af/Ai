from agents.base import BaseAgent
from agents.specialists import UIUXAgent, FrontendAgent, BackendAgent, QAAgent, DevOpsAgent
import re
import tempfile
import os
from utils.file_manager import create_project_zip

class CEOAgent(BaseAgent):
    def __init__(self, model_name: str = "meta/llama-3.1-70b-instruct"):
        super().__init__(
            name="CEO AI",
            role="Chief Executive Officer",
            goal="Oversee the entire development process, assign tasks, and monitor progress.",
            model_name=model_name
        )
        self.uiux = UIUXAgent(model_name)
        self.frontend = FrontendAgent(model_name)
        self.backend = BackendAgent(model_name)
        self.qa = QAAgent(model_name)
        self.devops = DevOpsAgent(model_name)

        self.tasks = [
            {"id": "uiux", "name": "UI/UX Design", "agent": self.uiux},
            {"id": "backend", "name": "Backend API", "agent": self.backend},
            {"id": "frontend", "name": "Frontend Web", "agent": self.frontend},
            {"id": "qa", "name": "Quality Testing", "agent": self.qa},
            {"id": "devops", "name": "Deployment", "agent": self.devops},
        ]
        self.statuses = {t["id"]: "Pending" for t in self.tasks}

    def get_todo_list(self):
        todo = "### 📋 Project Roadmap\n"
        for t in self.tasks:
            s = self.statuses[t["id"]]
            icon = "⏳" if s == "Pending" else ("🚀" if s == "In Progress" else "✅")
            todo += f"- {icon} **{t['name']}** ({s})\n"
        return todo

    def execute_project_with_dashboard(self, approved_plan: str, state: dict):
        context = approved_plan
        full_output = []
        for t in self.tasks: self.statuses[t["id"]] = "Pending"

        for task in self.tasks:
            self.statuses[task["id"]] = "In Progress"
            agent_name = task["agent"].name
            state["agent_outputs"][agent_name] = "Informing agent..."

            yield self.get_todo_list(), f"🔄 **{agent_name}** is building {task['name']}...", "", None, state

            prompt = (
                f"PHASE: {task['name']}\nPlan:\n{approved_plan}\n"
                f"Previous:\n{context[-1000:]}\nPerform your duties. Show reasoning."
            )

            # Streaming worker output
            current_response = ""
            for partial in task["agent"].chat_stream(prompt):
                current_response = partial
                state["agent_outputs"][agent_name] = current_response
                # Update dashboard with partial output
                yield self.get_todo_list(), f"🔄 **{agent_name}** is building {task['name']}...", current_response, None, state

            self.statuses[task["id"]] = "Completed"
            full_output.append(f"--- {agent_name} Output ---\n{current_response}")
            context += f"\n\n{agent_name} finished: {current_response[:300]}..."

            yield self.get_todo_list(), f"✅ **{agent_name}** done.", current_response, None, state

        final_result = "\n\n".join(full_output)
        zip_buffer = create_project_zip([final_result])
        fd, zip_path = tempfile.mkstemp(suffix=".zip")
        with os.fdopen(fd, 'wb') as f:
            f.write(zip_buffer.getbuffer())

        yield self.get_todo_list(), "🎉 **Mission Accomplished!**", final_result, zip_path, state
