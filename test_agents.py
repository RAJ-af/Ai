import sys
sys.path.append('/app')
from agents.boss import BossAgent
from agents.planner import PlannerAgent
from agents.ceo import CEOAgent

def test_mock_agents():
    import os
    os.environ["NVIDIA_API_KEY"] = "mock"
    boss = BossAgent()
    gen = boss.chat_stream("I want an e-commerce site")
    resp = list(gen)[-1]
    assert "READY_TO_PLAN" in resp.upper()

    planner = PlannerAgent()
    plan_gen = planner.chat_stream("Summary")
    plan = list(plan_gen)[-1]
    assert "[MOCK RESPONSE" in plan

if __name__ == "__main__":
    test_mock_agents()
    print("Agent tests passed!")
