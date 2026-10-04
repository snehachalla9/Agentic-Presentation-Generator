from agents.orchestrator.graph import build_graph
from agents.llm_gateway import LLMGateway


def main():

    topic = input("Enter topic: ").strip()

    if not topic:
        topic = "overfitting in machine learning"

    # ONE shared gateway
    llm_gateway = LLMGateway()

    # Give the same gateway to the graph
    graph = build_graph(
        llm_gateway=llm_gateway
    )

    initial_state = {
        "topic": topic,
        "errors": [],
        "validation_results": {},
        "retry_count": {
        "planner": 0,
        "research": 0,
        "content": 0,
        "ppt": 0
    }
}

    print("\n🚀 Starting Agentic PPT Generation...\n")

    final_state = graph.invoke(initial_state)

    print("\n🎯 Pipeline completed!")

    print("\nFinal State:")
    print(final_state)


if __name__ == "__main__":
    main()