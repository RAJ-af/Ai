import sys
sys.path.append('/app')
from agents.boss import BossAgent
from agents.planner import PlannerAgent
from agents.ceo import CEOAgent

def test_mock_agents():
    import os
    os.environ["NVIDIA_API_KEY"] = "mock"

    boss = BossAgent()
    resp = boss.chat("I want an e-commerce site")
    print(f"Boss response: {resp}")
    assert "READY_TO_PLAN" in resp.upper()

    planner = PlannerAgent()
    plan = planner.generate_plan("User wants e-commerce")
    print(f"Plan summary: {plan[:50]}...")

    ceo = CEOAgent()
    # execute_project is now a generator
    gen = ceo.execute_project("My Plan")
    todo, status, worker_out = next(gen)
    print(f"CEO Status: {status}")
    assert "working on" in status

if __name__ == "__main__":
    test_mock_agents()
    print("Agent tests passed!")
