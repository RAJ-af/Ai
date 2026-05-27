from agents.base import BaseAgent

class BossAgent(BaseAgent):
    def __init__(self, model_name: str = "meta/llama-3.1-405b-instruct"):
        super().__init__(
            name="Boss AI",
            role="Project Manager and Interviewer",
            goal="Interview the user to get all necessary details for a software project. Once you have enough details, summarize the project.",
            model_name=model_name
        )
        self.system_message.content += "\nIf you have enough information to start the project, end your message with 'READY_TO_PLAN'."

    def interview(self, user_message: str) -> str:
        return self.chat(user_message)

    def is_ready(self, last_response: str) -> bool:
        return "READY_TO_PLAN" in last_response
