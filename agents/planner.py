from agents.base import BaseAgent

class PlannerAgent(BaseAgent):
    def __init__(self, model_name: str = "meta/llama-3.1-70b-instruct"):
        super().__init__(
            name="Planner AI",
            role="Solution Architect",
            goal="Create a detailed PRD and Technical Design. Include tech stack, file structure, and a MERMAID diagram for the architecture.",
            model_name=model_name
        )

    def generate_plan(self, project_summary: str) -> str:
        prompt = (
            f"Project Summary: {project_summary}\n\n"
            "Generate a comprehensive PRD and Technical Plan in Markdown.\n"
            "CRITICAL: You MUST include a Mermaid diagram block (graph TD ...) to visualize the system architecture or database schema."
        )
        return self.chat(prompt)
