import sys
sys.path.append('/app')
from agents.boss import BossAgent
from agents.planner import PlannerAgent
from agents.ceo import CEOAgent

def test_mock_agents():
    # Set mock key if not present
    import os
    os.environ["NVIDIA_API_KEY"] = "mock"

    boss = BossAgent()
    resp = boss.chat("I want an e-commerce site")
    print(f"Boss response: {resp}")
    assert "READY_TO_PLAN" in resp or "[MOCK RESPONSE" in resp

    planner = PlannerAgent()
    plan = planner.generate_plan("User wants e-commerce")
    print(f"Plan: {plan[:50]}...")
    assert "Project PRD" in plan or "[MOCK RESPONSE" in plan

    ceo = CEOAgent()
    # Mock execute_project (it calls other agents)
    # Since they all use get_llm which returns MockLLM when key is mock, it should work
    output = ceo.execute_project("My Plan")
    print(f"CEO Output sample: {output[:100]}...")
    assert "Output" in output

if __name__ == "__main__":
    test_mock_agents()
    print("Agent tests passed!")
