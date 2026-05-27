import os
from langchain_nvidia_ai_endpoints import ChatNVIDIA
from langchain_core.language_models.chat_models import BaseChatModel
from langchain_core.messages import BaseMessage, AIMessage, HumanMessage, SystemMessage
from langchain_core.outputs import ChatResult, ChatGeneration
from typing import Any, List, Optional, Union, Dict
from dotenv import load_dotenv

load_dotenv()

class MockLLM(BaseChatModel):
    """
    A mock LLM provider for testing the agent workflow without an NVIDIA API key.
    """
    def _generate(self, messages: List[BaseMessage], stop: Optional[List[str]] = None, **kwargs: Any) -> ChatResult:
        last_message = ""
        for m in reversed(messages):
            if isinstance(m, HumanMessage):
                last_message = m.content
                break

        response_content = f"[MOCK RESPONSE to: {last_message[:50]}...]"
        lower_msg = last_message.lower()

        # Scenario-based responses
        if "ecommerce" in lower_msg or "e-commerce" in lower_msg:
            response_content = "I understand you want to build an e-commerce platform. Should it include features like a shopping cart and payment gateway? READY_TO_PLAN"

        if "prd" in lower_msg or "plan" in lower_msg:
            response_content = """# Project PRD: E-commerce Website
## 1. Overview
A modern e-commerce platform.
## 2. Tech Stack
- **Frontend**: React
- **Backend**: Python FastAPI
- **Database**: PostgreSQL
## 3. Features
- User Auth
- Product Catalog
- Cart & Checkout"""

        if "backend development" in lower_msg:
            response_content = "Generated Backend Code. [CODE_START]backend/main.py\nfrom fastapi import FastAPI\napp = FastAPI()\n@app.get('/')\ndef read_root(): return {'status': 'online'}\n[CODE_END]"
        elif "frontend development" in lower_msg:
            response_content = "Generated Frontend Code. [CODE_START]frontend/App.js\nimport React from 'react';\nexport default function App() { return <div>AI E-commerce</div>; }\n[CODE_END]"
        elif "ui/ux design" in lower_msg:
            response_content = "Generated UI/UX Design. [CODE_START]design/theme.json\n{\"primary\": \"#007bff\", \"secondary\": \"#6c757d\"}\n[CODE_END]"

        message = AIMessage(content=response_content)
        generation = ChatGeneration(message=message)
        return ChatResult(generations=[generation])

    @property
    def _llm_type(self) -> str:
        return "mock"

def get_llm(model_name: str = "meta/llama-3.1-70b-instruct") -> Union[ChatNVIDIA, MockLLM]:
    api_key = os.getenv("NVIDIA_API_KEY")
    if not api_key or api_key == "mock":
        return MockLLM()
    return ChatNVIDIA(model=model_name, nvidia_api_key=api_key)

class BaseAgent:
    def __init__(self, name: str, role: str, goal: str, model_name: str = "meta/llama-3.1-70b-instruct"):
        self.name = name
        self.role = role
        self.goal = goal
        self.llm = get_llm(model_name)
        self.memory: List[BaseMessage] = []
        self.system_message = SystemMessage(content=f"You are {name}, the {role}. Your goal is: {goal}")

    def chat(self, user_input: str) -> str:
        messages = [self.system_message] + self.memory + [HumanMessage(content=user_input)]
        response = self.llm.invoke(messages)
        self.memory.append(HumanMessage(content=user_input))
        self.memory.append(response)
        return response.content

    def clear_memory(self):
        self.memory = []
