from agents.orchestrator.graph import build_graph


def main():

    topic = input("Enter topic: ").strip()

    if not topic:
        topic = "overfitting in machine learning"

    graph = build_graph()

    initial_state = {
        "topic": topic,
        "errors": [],
        "validation_results": {}
    }

    print("\n🚀 Starting Agentic PPT Generation...\n")

    final_state = graph.invoke(initial_state)

    print("\n🎯 Pipeline completed!")

    print("\nFinal State:")
    print(final_state)


if __name__ == "__main__":
    main()