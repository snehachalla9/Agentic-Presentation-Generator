class Supervisor:

    def decide(self, state):

        validation = state.get("validation_results", {})

        # If planner validation failed, stop for now
        if validation.get("planner_valid") is False:
            return "finish"

        # If research validation failed, stop for now
        if validation.get("research_valid") is False:
            return "finish"

        # If content validation failed, stop for now
        if validation.get("content_valid") is False:
            return "finish"

        # If PPT validation failed, stop for now
        if validation.get("ppt_valid") is False:
            return "finish"

        # Normal pipeline
        if not state.get("plan"):
            return "planner"

        if not state.get("research"):
            return "research"

        if not state.get("content"):
            return "content"

        if not state.get("ppt"):
            return "ppt"

        return "finish"