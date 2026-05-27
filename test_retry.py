import sys
sys.path.append('/app')
from agents.base import BaseAgent
from langchain_core.language_models.chat_models import BaseChatModel
from langchain_core.messages import BaseMessage, AIMessage
from langchain_core.outputs import ChatResult, ChatGeneration
from typing import Any, List, Optional
import time

class FailingLLM(BaseChatModel):
    fail_count: int = 2
    attempts: int = 0

    def _generate(self, messages: List[BaseMessage], stop: Optional[List[str]] = None, **kwargs: Any) -> ChatResult:
        self.attempts += 1
        if self.attempts <= self.fail_count:
            raise Exception("Rate limit exceeded (429)")
        return ChatResult(generations=[ChatGeneration(message=AIMessage(content="Success after retries"))])

    @property
    def _llm_type(self) -> str:
        return "failing"

def test_retry_logic():
    agent = BaseAgent("Test", "Tester", "Test Goal")
    agent.llm = FailingLLM()

    start_time = time.time()
    resp = agent.chat("hi")
    end_time = time.time()

    print(f"Response: {resp}")
    print(f"Attempts: {agent.llm.attempts}")

    assert "Success" in resp
    assert agent.llm.attempts == 3

if __name__ == "__main__":
    test_retry_logic()
    print("Retry test passed!")
