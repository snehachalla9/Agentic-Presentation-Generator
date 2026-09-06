import json
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.agents.planner_agent import PlannerAgent

def test_planner():
    planner = PlannerAgent()
    
    test_prompts = [
        "5 slides on climate change for students, simple tone",
        "15 slides about blockchain for investors, business tone",
        "8 slides on Python programming for beginners"
    ]
    
    for prompt in test_prompts:
        print(f"\n📝 Testing: {prompt}")
        plan = planner.parse_prompt(prompt)
        assert "outline" in plan
        assert plan["slide_count"] in [5, 15, 8]
        print(f"✅ Passed: {plan['objective'][:50]}...")
    
    print("\n🎉 All tests passed!")

if __name__ == "__main__":
    test_planner()