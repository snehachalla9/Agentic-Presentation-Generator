# # # #!/usr/bin/env python3
# # # """
# # # Quick test for Planner Agent V4
# # # Run this to verify everything works
# # # """

# # # import json
# # # import os
# # # from agents.planner_agent import PlannerAgentV4, UniversalPlanner

# # # def main():
# # #     print("=" * 70)
# # #     print("🧪 TESTING PLANNER AGENT V4")
# # #     print("=" * 70)
    
# # #     # Test 1: New V4 Planner
# # #     print("\n📝 Test 1: Using PlannerAgentV4")
# # #     print("-" * 50)
    
# # #     planner = PlannerAgentV4()
# # #     plan = planner.generate_plan("Create a course on Transformer Architecture for NLP")
# # #     planner.display_plan(plan)
# # #     planner.save_plan(plan)
    
# # #     print("\n" + "=" * 70)
# # #     print("✅ TEST COMPLETE!")
# # #     print(f"📄 Plan saved to: {os.path.abspath('output/course_plan_v4.json')}")
# # #     print("=" * 70)

# # # if __name__ == "__main__":
# # #     main()
# # import json

# # from agents.ppt_generator_v2.generator import PPTGeneratorV2


# # INPUT_FILE = "output/merged_slide_plan.json"
# # OUTPUT_FILE = "output/test_v2.pptx"


# # def main():

# #     # ------------------------------------------
# #     # Load existing merged JSON
# #     # ------------------------------------------

# #     with open(
# #         INPUT_FILE,
# #         "r",
# #         encoding="utf-8",
# #     ) as file:
# #         merged_plan = json.load(file)

# #     print(
# #         f"📥 Loaded: {INPUT_FILE}"
# #     )

# #     # ------------------------------------------
# #     # Generate PPT
# #     # ------------------------------------------

# #     generator = PPTGeneratorV2()

# #     ppt_path = generator.generate(
# #         presentation_data=merged_plan,
# #         output_path=OUTPUT_FILE,
# #     )

# #     print(
# #         f"\n🎯 Created: {ppt_path}"
# #     )


# # if __name__ == "__main__":
# #     main()
# # from agents.orchestrator.graph import build_graph


# # # Build the LangGraph application
# # app = build_graph()


# # # Initial state
# # initial_state = {
# #     "topic": "Artificial Intelligence"
# # }


# # # Run the graph
# # result = app.invoke(initial_state)


# # # Print final result
# # print("\nFinal Result:")
# # print(result)
# # from agents.orchestrator.graph import build_graph


# # app = build_graph()


# # initial_state = {
# #     "topic": "Artificial Intelligence"
# # }


# # result = app.invoke(initial_state)


# # print("\n" + "=" * 50)
# # print("FINAL RESULT")
# # print("=" * 50)

# # print("Topic:", result["topic"])

# # print("\nPlan:")
# # print(result["plan"])
# from agents.orchestrator.graph import build_graph

# app = build_graph()

# result = app.invoke({
#     "topic": "Artificial Intelligence"
# })

# print("\nFINAL RESULT")
# print(result.keys())
# from groq import Groq
# import os
# from dotenv import load_dotenv

# load_dotenv()

# client = Groq(api_key=os.getenv("GROQ_API_KEY"))

# models = client.models.list()

# for model in models.data:
#     print(model.id)
from agents.orchestrator.graph import build_graph


def main():

    print("\n🚀 Starting Agentic Workflow...\n")

    app = build_graph()

    result = app.invoke({
        "topic": "Artificial Intelligence"
    })

    print("\n" + "=" * 60)
    print("FINAL RESULT")
    print("=" * 60)

    print("\nFinal state keys:")
    print(result.keys())

    print("\nCurrent agent:")
    print(result.get("current_agent"))

    print("\nErrors:")
    print(result.get("errors", []))

    print("\nPlan available:")
    print(bool(result.get("plan")))

    print("\nResearch available:")
    print(bool(result.get("research")))


if __name__ == "__main__":
    main()