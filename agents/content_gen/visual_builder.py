# visual_builder.py

class VisualBuilder:
    def build(self, selected: dict, slide_blueprint: dict) -> dict:
        plan = slide_blueprint["slide"]["presentation_plan"]
        intent = plan.get("presentation_intent", {})
        preferred_visuals = plan.get("preferred_visuals", [])
        alternative_visuals = plan.get("alternative_visuals", [])

        # Choose visual type from planner preferences
        visual_type = preferred_visuals[0] if preferred_visuals else "chart"

        spec = {
            "visual_type": visual_type,
            "visual_intent": intent.get("information_type", "explain"),
            "semantic_data": self._extract_semantic_data(visual_type, selected),
            "renderer_hints": self._renderer_hints(visual_type, intent),
            "image_requirements": self._image_requirements(visual_type, plan)
        }

        return spec

    def _extract_semantic_data(self, visual_type: str, selected: dict):
        if visual_type == "chart":
            return {
                "metrics": self._extract_metrics(selected.get("statistics", []))
            }
        if visual_type == "workflow":
            return {
                "steps": selected.get("process", [])
            }
        if visual_type == "timeline":
            return {
                "events": self._extract_events(selected.get("timeline", []))
            }
        if visual_type == "comparison":
            return {
                "left_title": "Advantages",
                "right_title": "Disadvantages",
                "criteria": selected.get("comparison", [])
            }
        if visual_type == "matrix":
            return {
                "x_dimension": "Dimension X",
                "y_dimension": "Dimension Y",
                "items": selected.get("concepts", [])
            }
        return {}

    def _extract_metrics(self, stats: list):
        metrics = []
        for s in stats:
            words = s.split()
            label = " ".join(words[:-1]) if len(words) > 1 else s
            value = "".join([w for w in words if any(c.isdigit() for c in w)])
            metrics.append({"label": label.strip(), "value": value})
        return metrics

    def _extract_events(self, timeline: list):
        events = []
        for t in timeline:
            if isinstance(t, dict):
                events.append({"year": t.get("year"), "event": t.get("event")})
            else:
                events.append({"event": t})
        return events

    def _renderer_hints(self, visual_type: str, intent: dict):
        return {
            "layout_hint": "two_column" if visual_type=="comparison" else "single_column",
            "orientation": "horizontal" if visual_type in ["timeline","chart"] else "vertical",
            "priority": visual_type
        }

    def _image_requirements(self, visual_type: str, plan: dict):
        # Only certain slide types need images
        needs_image = visual_type in ["hero","concept","case_study","quote"]
        return {
            "needs_image": needs_image,
            "image_type": f"illustration of {plan.get('slide_focus','concept')}" if needs_image else None,
            "image_position": "right" if needs_image else None
        }
