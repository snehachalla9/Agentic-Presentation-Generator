import json

def save_research(data):
    with open("research_output.json", "w", encoding="utf-8") as f:
        json.dump(data, f, indent=4)

    print("Research saved for:", data["topic"])