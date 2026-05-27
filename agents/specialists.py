from agents.base import BaseAgent

class SpecialistAgent(BaseAgent):
    def __init__(self, name: str, role: str, goal: str, model_name: str = "meta/llama-3.1-70b-instruct"):
        super().__init__(name, role, goal, model_name)
        self.system_message.content += (
            "\n\nAVAILABLE SIMULATED TOOLS:"
            "\n- [SEARCH: 'query']: Search the web for information."
            "\n- [READ_FILE: 'path']: Read contents of a file."
            "\n- [WRITE_FILE: 'path', 'content']: Write or update a file."
            "\n- [TERMINAL: 'command']: Run a shell command."
            "\n\nINSTRUCTIONS:"
            "\n1. Always show your reasoning and tool usage steps in your response."
            "\n2. When writing final code, use: [CODE_START]filename\ncode\n[CODE_END]"
            "\n3. Act like a real developer: search for best practices, write files, and 'test' them."
        )

class UIUXAgent(SpecialistAgent):
    def __init__(self, model_name: str = "meta/llama-3.1-70b-instruct"):
        super().__init__("UI/UX Agent", "Designer", "Design the layout and user experience.", model_name)

class FrontendAgent(SpecialistAgent):
    def __init__(self, model_name: str = "meta/llama-3.1-70b-instruct"):
        super().__init__("Frontend Agent", "Frontend Developer", "Implement the user interface.", model_name)

class BackendAgent(SpecialistAgent):
    def __init__(self, model_name: str = "meta/llama-3.1-70b-instruct"):
        super().__init__("Backend Agent", "Backend Developer", "Implement server-side logic.", model_name)

class QAAgent(SpecialistAgent):
    def __init__(self, model_name: str = "meta/llama-3.1-70b-instruct"):
        super().__init__("QA Agent", "Tester", "Test code and fix bugs.", model_name)

class DevOpsAgent(SpecialistAgent):
    def __init__(self, model_name: str = "meta/llama-3.1-70b-instruct"):
        super().__init__("DevOps Agent", "Cloud Engineer", "Handle deployment and CI/CD.", model_name)
