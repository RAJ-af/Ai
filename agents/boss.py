from agents.base import BaseAgent

class BossAgent(BaseAgent):
    def __init__(self, model_name: str = "meta/llama-3.1-70b-instruct"):
        super().__init__(
            name="Boss AI",
            role="Project Manager and Interviewer",
            goal="Interview the user to get all necessary details for a software project. You need to understand the core features, tech stack preferences (if any), and the target audience. Once you have enough details to form a solid PRD, summarize the project and end your message with 'READY_TO_PLAN'.",
            model_name=model_name
        )
        self.system_message.content += (
            "\n\nGuidelines:"
            "\n1. Be professional and helpful."
            "\n2. Ask one or two questions at a time to not overwhelm the user."
            "\n3. When you have sufficient info, provide a summary and the keyword READY_TO_PLAN."
        )

    def interview(self, user_message: str) -> str:
        return self.chat(user_message)

    def is_ready(self, last_response: str) -> bool:
        return "READY_TO_PLAN" in last_response
