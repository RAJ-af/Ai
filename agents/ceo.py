from agents.base import BaseAgent
from agents.specialists import UIUXAgent, FrontendAgent, BackendAgent, QAAgent, DevOpsAgent
import re

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
            {"id": "uiux", "name": "UI/UX Design & Mockups", "status": "Pending", "agent": self.uiux},
            {"id": "backend", "name": "Backend API & Logic", "status": "Pending", "agent": self.backend},
            {"id": "frontend", "name": "Frontend Implementation", "status": "Pending", "agent": self.frontend},
            {"id": "qa", "name": "Quality Assurance & Testing", "status": "Pending", "agent": self.qa},
            {"id": "devops", "name": "DevOps & Deployment Setup", "status": "Pending", "agent": self.devops},
        ]

    def get_todo_list(self):
        todo = "### 📋 Project Roadmap\n"
        for t in self.tasks:
            icon = "⏳" if t["status"] == "Pending" else ("🚀" if t["status"] == "In Progress" else "✅")
            todo += f"- {icon} **{t['name']}** ({t['status']})\n"
        return todo

    def execute_project(self, approved_plan: str):
        context = approved_plan
        full_output = []

        # Reset task statuses
        for t in self.tasks: t["status"] = "Pending"

        for task in self.tasks:
            task["status"] = "In Progress"
            yield self.get_todo_list(), f"🔄 **{task['agent'].name}** is now working on {task['name']}...", ""

            prompt = (
                f"### PHASE: {task['name']}\n\n"
                f"Project Plan:\n{approved_plan}\n\n"
                f"Previous Context:\n{context[-1500:]}\n\n"
                f"Perform your duties. Use simulated tools if needed (e.g., [SEARCH: query], [WRITE_FILE: path])."
            )

            response = task["agent"].chat(prompt)
            task["status"] = "Completed"

            full_output.append(f"--- {task['agent'].name} Output ---\n{response}")
            context += f"\n\n{task['agent'].name} finished: {response[:300]}..."

            yield self.get_todo_list(), f"🏁 **{task['agent'].name}** has completed their task.", response

        final_result = "\n\n".join(full_output)
        yield self.get_todo_list(), "🎉 **Project fully completed!**", final_result
