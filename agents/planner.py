from agents.base import BaseAgent

class PlannerAgent(BaseAgent):
    def __init__(self, model_name: str = "meta/llama-3.1-405b-instruct"):
        super().__init__(
            name="Planner AI",
            role="Solution Architect",
            goal="Create a detailed PRD (Product Requirements Document) and Technical Design for the project. Include tech stack, file structure, and feature list in Markdown format.",
            model_name=model_name
        )

    def generate_plan(self, project_summary: str) -> str:
        prompt = f"Based on this project summary: {project_summary}\n\nGenerate a comprehensive PRD and Technical Plan in Markdown format."
        return self.chat(prompt)
