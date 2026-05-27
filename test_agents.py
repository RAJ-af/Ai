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
    assert "READY_TO_PLAN" in resp.upper()

    planner = PlannerAgent()
    plan = planner.generate_plan("Summary")
    assert "MERMAID" in plan.upper() or "[MOCK RESPONSE" in plan

    ceo = CEOAgent()
    state = {"agent_outputs": {}}
    gen = ceo.execute_project_with_dashboard("Plan", state)
    todo, status, worker_out, zip_path, s = next(gen)
    assert "UI/UX Agent" in status

if __name__ == "__main__":
    test_mock_agents()
    print("Agent tests passed!")
