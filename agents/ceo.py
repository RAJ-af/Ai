from agents.base import BaseAgent
from agents.specialists import UIUXAgent, FrontendAgent, BackendAgent, QAAgent, DevOpsAgent
import re

class CEOAgent(BaseAgent):
    def __init__(self, model_name: str = "meta/llama-3.1-405b-instruct"):
        super().__init__(
            name="CEO AI",
            role="Chief Executive Officer",
            goal="Oversee the entire development process, assign tasks to specialized agents, and ensure the project is completed correctly.",
            model_name=model_name
        )
        self.uiux = UIUXAgent(model_name)
        self.frontend = FrontendAgent(model_name)
        self.backend = BackendAgent(model_name)
        self.qa = QAAgent(model_name)
        self.devops = DevOpsAgent(model_name)

    def execute_project(self, approved_plan: str):
        steps = [
            ("UI/UX Design", self.uiux),
            ("Backend Development", self.backend),
            ("Frontend Development", self.frontend),
            ("Testing & QA", self.qa),
            ("Deployment Setup", self.devops)
        ]

        full_output = []
        for step_name, agent in steps:
            prompt = f"Based on the following PRD, perform your tasks for: {step_name}\n\nPlan:\n{approved_plan}"
            response = agent.chat(prompt)
            full_output.append(f"--- {agent.name} Output ---\n{response}")

        return "\n\n".join(full_output)
