# image_planner.py

class ImagePlanner:
    def plan(self, selected: dict, slide_blueprint: dict) -> dict:
        plan = slide_blueprint["slide"]["presentation_plan"]
        audience = slide_blueprint.get("audience", "General")
        visual_type = plan.get("preferred_visuals", ["concept"])[0]
        cognitive_load = plan.get("cognitive_load", "medium")

        # Decide if image is needed
        needs_image, reason = self._decide_need(selected, visual_type, cognitive_load, audience)

        # Extract subject from research
        subject = self._extract_subject(selected, plan)

        spec = {
            "needs_image": needs_image,
            "reason": reason if not needs_image else None,
            "subject": subject,
            "style": {
                "type": "flat illustration",
                "complexity": "medium",
                "color_palette": "professional",
                "background": "transparent",
                "perspective": "isometric"
            },
            "priority": "primary" if visual_type in ["hero","concept","case_study"] else "secondary",
            "placement": {
                "layout": "sidebar" if visual_type=="comparison" else "main",
                "occupancy": 0.35,
                "crop": "contain",
                "aspect_ratio": "16:9",
                "alignment": "center"
            },
            "keywords": self._extract_keywords(selected),
            "icons": self._recommend_icons(selected),
            "safety": {
                "avoid_text": True,
                "avoid_watermark": True,
                "avoid_logos": True,
                "professional": True
            }
        }

        return spec

    def _decide_need(self, selected, visual_type, cognitive_load, audience):
        if cognitive_load == "low" and not selected.get("examples") and not selected.get("case_studies"):
            return False, "Slide is simple; text and visuals suffice."
        if visual_type in ["workflow","timeline","matrix"]:
            return False, "Diagram already provides clarity."
        return True, None

    def _extract_subject(self, selected, plan):
        if selected.get("concepts"):
            return selected["concepts"][0]
        if selected.get("case_studies"):
            return selected["case_studies"][0]
        if selected.get("examples"):
            return selected["examples"][0]
        return plan.get("slide_focus","concept")

    def _extract_keywords(self, selected):
        keywords = []
        for field in ["concepts","examples","case_studies","trends"]:
            for item in selected.get(field, []):
                for word in item.split():
                    if len(word) > 3:
                        keywords.append(word.lower())
        return list(set(keywords))[:6]

    def _recommend_icons(self, selected):
        icons = []
        if "data" in " ".join(selected.get("concepts", [])).lower():
            icons.append("database")
        if "network" in " ".join(selected.get("concepts", [])).lower():
            icons.append("network")
        if "learning" in " ".join(selected.get("concepts", [])).lower():
            icons.append("brain")
        return icons
