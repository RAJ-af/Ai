from agents.base import BaseAgent

class SpecialistAgent(BaseAgent):
    def __init__(self, name: str, role: str, goal: str, model_name: str = "meta/llama-3.1-405b-instruct"):
        super().__init__(name, role, goal, model_name)
        self.system_message.content += "\nWhen writing code, always use the format:\n[CODE_START]filename\ncode here\n[CODE_END]"

class UIUXAgent(SpecialistAgent):
    def __init__(self, model_name: str = "meta/llama-3.1-405b-instruct"):
        super().__init__("UI/UX Agent", "Designer", "Design the layout and user experience.", model_name)

class FrontendAgent(SpecialistAgent):
    def __init__(self, model_name: str = "meta/llama-3.1-405b-instruct"):
        super().__init__("Frontend Agent", "Frontend Developer", "Implement the user interface using the chosen tech stack.", model_name)

class BackendAgent(SpecialistAgent):
    def __init__(self, model_name: str = "meta/llama-3.1-405b-instruct"):
        super().__init__("Backend Agent", "Backend Developer", "Implement the server-side logic and database integration.", model_name)

class QAAgent(SpecialistAgent):
    def __init__(self, model_name: str = "meta/llama-3.1-405b-instruct"):
        super().__init__("QA Agent", "Tester", "Test the generated code and suggest fixes.", model_name)

class DevOpsAgent(SpecialistAgent):
    def __init__(self, model_name: str = "meta/llama-3.1-405b-instruct"):
        super().__init__("DevOps Agent", "Cloud Engineer", "Handle deployment configurations and CI/CD setup.", model_name)
