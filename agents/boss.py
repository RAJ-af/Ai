from agents.base import BaseAgent

class BossAgent(BaseAgent):
    def __init__(self, model_name: str = "meta/llama-3.1-70b-instruct"):
        super().__init__(
            name="Boss AI",
            role="Project Manager and Interviewer",
            goal="Interview the user to get all necessary details for a software project. You need to understand core features, tech stack, and audience. Once requirements are clear, summarize the project and end with the EXACT keyword 'READY_TO_PLAN'.",
            model_name=model_name
        )
        self.system_message.content += (
            "\n\nCRITICAL INSTRUCTIONS:"
            "\n1. You MUST include 'READY_TO_PLAN' in your response once you have enough information to start building."
            "\n2. Do NOT get stuck in an endless loop of questions."
            "\n3. After summarizing the project, always add 'READY_TO_PLAN' on a new line."
        )

    def interview(self, user_message: str) -> str:
        return self.chat(user_message)

    def is_ready(self, last_response: str) -> bool:
        # Case insensitive and checks for presence
        return "READY_TO_PLAN" in last_response.upper()
