class Supervisor:

    def decide(self, state):

        validation = state.get("validation_results", {})
        retry_count = state.get("retry_count", {})

        # -----------------------------------
        # Validation failures + retry policy
        # -----------------------------------

        # Planner failed validation
        if validation.get("planner_valid") is False:
            if retry_count.get("planner", 0) < 1:
                return "planner"
            return "finish"

        # Research failed validation
        if validation.get("research_valid") is False:
            if retry_count.get("research", 0) < 1:
                return "research"
            return "finish"

        # Content failed validation
        if validation.get("content_valid") is False:
            if retry_count.get("content", 0) < 1:
                return "content"
            return "finish"

        # PPT failed validation
        if validation.get("ppt_valid") is False:
            if retry_count.get("ppt", 0) < 1:
                return "ppt"
            return "finish"

        # -----------------------------------
        # Normal pipeline
        # -----------------------------------

        if not state.get("plan"):
            return "planner"

        if not state.get("research"):
            return "research"

        if not state.get("content"):
            return "content"

        if not state.get("ppt"):
            return "ppt"

        return "finish"