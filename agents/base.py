import os
import time
import logging
from langchain_nvidia_ai_endpoints import ChatNVIDIA
from langchain_core.language_models.chat_models import BaseChatModel
from langchain_core.messages import BaseMessage, AIMessage, HumanMessage, SystemMessage
from langchain_core.outputs import ChatResult, ChatGeneration
from typing import Any, List, Optional, Union, Dict
from dotenv import load_dotenv

load_dotenv()

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class MockLLM(BaseChatModel):
    def _generate(self, messages: List[BaseMessage], stop: Optional[List[str]] = None, **kwargs: Any) -> ChatResult:
        last_message = ""
        for m in reversed(messages):
            if isinstance(m, HumanMessage):
                last_message = m.content
                break

        response_content = f"[MOCK RESPONSE to: {last_message[:50]}...]"
        lower_msg = last_message.lower()
        if "ecommerce" in lower_msg or "e-commerce" in lower_msg:
            response_content = "I understand you want to build an e-commerce platform. READY_TO_PLAN"

        message = AIMessage(content=response_content)
        generation = ChatGeneration(message=message)
        return ChatResult(generations=[generation])

    def stream(self, input: Any, config: Optional[Any] = None, **kwargs: Any):
        content = self._generate(input).generations[0].message.content
        for word in content.split():
            yield AIMessage(content=word + " ")
            time.sleep(0.01)

    @property
    def _llm_type(self) -> str:
        return "mock"

def get_llm(model_name: str = "meta/llama-3.1-70b-instruct"):
    api_key = os.getenv("NVIDIA_API_KEY")
    if not api_key or api_key == "mock":
        return MockLLM()
    return ChatNVIDIA(model=model_name, nvidia_api_key=api_key, temperature=0.2)

class BaseAgent:
    def __init__(self, name: str, role: str, goal: str, model_name: str = "meta/llama-3.1-70b-instruct"):
        self.name = name
        self.role = role
        self.goal = goal
        self.model_name = model_name
        self.llm = get_llm(model_name)
        self.memory: List[BaseMessage] = []
        self.system_message = SystemMessage(content=f"You are {name}, the {role}. Goal: {goal}")

    def chat_stream(self, user_input: str):
        messages = [self.system_message] + self.memory + [HumanMessage(content=user_input)]
        full_response = ""
        try:
            for chunk in self.llm.stream(messages):
                full_response += chunk.content
                yield full_response

            self.memory.append(HumanMessage(content=user_input))
            self.memory.append(AIMessage(content=full_response))
        except Exception as e:
            logger.error(f"Stream error in {self.name}: {e}")
            yield f"❌ Error: {str(e)}"

    def get_state(self) -> Dict:
        return {"memory": [{"type": m.type, "content": m.content} for m in self.memory]}

    def load_state(self, state: Dict):
        self.memory = []
        for m in state.get("memory", []):
            if m["type"] == "human": self.memory.append(HumanMessage(content=m["content"]))
            elif m["type"] == "ai": self.memory.append(AIMessage(content=m["content"]))
