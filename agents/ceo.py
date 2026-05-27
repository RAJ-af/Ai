from agents.base import BaseAgent
from agents.specialists import UIUXAgent, FrontendAgent, BackendAgent, QAAgent, DevOpsAgent
import re

class CEOAgent(BaseAgent):
    def __init__(self, model_name: str = "meta/llama-3.1-70b-instruct"):
        super().__init__(
            name="CEO AI",
            role="Chief Executive Officer",
            goal="Oversee the entire development process, assign tasks to specialized agents, and ensure the project is completed correctly based on the PRD.",
            model_name=model_name
        )
        self.uiux = UIUXAgent(model_name)
        self.frontend = FrontendAgent(model_name)
        self.backend = BackendAgent(model_name)
        self.qa = QAAgent(model_name)
        self.devops = DevOpsAgent(model_name)

    def execute_project(self, approved_plan: str):
        steps = [
            ("UI/UX Design & Theming", self.uiux),
            ("Backend Logic & API", self.backend),
            ("Frontend Implementation", self.frontend),
            ("Quality Assurance & Bug Fixes", self.qa),
            ("DevOps & Deployment Configuration", self.devops)
        ]

        full_output = []
        context = approved_plan

        for step_name, agent in steps:
            prompt = f"### TASK: {step_name}\n\nProject PRD & Plan:\n{approved_plan}\n\nPrevious Progress/Context:\n{context[-2000:] if len(context) > 2000 else context}\n\nPlease generate the necessary files and code for this phase."
            response = agent.chat(prompt)
            full_output.append(f"--- {agent.name} Output ---\n{response}")
            # Add to context for next agent
            context += f"\n\n{agent.name} implemented: {response[:500]}..."

        return "\n\n".join(full_output)
