# validator.py

class SlideValidator:
    def validate(self, slide_content: dict, slide_blueprint: dict, research: dict) -> dict:
        plan = slide_blueprint["slide"]["presentation_plan"]

        report = {
            "status": "PASS",
            "validation": {
                "content_quality": {},
                "semantic_quality": {},
                "visual_quality": {},
                "render_quality": {},
                "research_quality": {},
                "speaker_quality": {},
                "accessibility": {},
                "warnings": [],
                "errors": [],
                "repair_actions": []
            }
        }

        # 1. Mandatory fields
        mandatory = ["headline","main_message","bullets","visual_spec","speaker_notes"]
        for field in mandatory:
            if not slide_content.get(field):
                report["validation"]["errors"].append(f"Missing mandatory field: {field}")
                report["status"] = "FAIL"

        # 2. Planner alignment
        if plan.get("slide_type") == "chart":
            if not slide_content.get("visual_spec", {}).get("semantic_data", {}).get("metrics"):
                report["validation"]["errors"].append("Chart slide missing metrics.")
                report["status"] = "FAIL"

        # 3. Content mapping validation
        mapping = plan.get("content_mapping", {})
        for slot, source in mapping.items():
            if source not in research or not research[source]:
                report["validation"]["warnings"].append(f"Content slot {slot} expects {source}, but research missing.")
                report["status"] = "WARN"

        # 4. Research coverage
        total_facts = len(research.get("key_facts", []))
        used_facts = sum(1 for f in research.get("key_facts", []) if f in str(slide_content))
        coverage = (used_facts/total_facts)*100 if total_facts else 100
        report["validation"]["research_quality"]["coverage_score"] = coverage
        if coverage < 30:
            report["validation"]["warnings"].append("Low research coverage (<30%).")

        # 5. Semantic preservation
        preserved = sum(1 for c in research.get("concepts", []) if c in str(slide_content))
        total_concepts = len(research.get("concepts", []))
        preservation = (preserved/total_concepts)*100 if total_concepts else 100
        report["validation"]["semantic_quality"]["preservation_score"] = preservation

        # 6. Duplicate detection
        seen = set()
        duplicates = []
        for field in ["headline","main_message"] + slide_content.get("bullets", []):
            if field in seen:
                duplicates.append(field)
            seen.add(field)
        if duplicates:
            report["validation"]["warnings"].append(f"Duplicate content detected: {duplicates}")
            report["validation"]["semantic_quality"]["duplicate_score"] = 5
        else:
            report["validation"]["semantic_quality"]["duplicate_score"] = 10

        # 7. Visual alignment
        vtype = slide_content.get("visual_spec", {}).get("visual_type")
        if vtype == "timeline" and not slide_content.get("visual_spec", {}).get("semantic_data", {}).get("events"):
            report["validation"]["errors"].append("Timeline missing events.")
            report["status"] = "FAIL"

        # 8. Image alignment
        image_plan = slide_content.get("image_plan", {})
        if image_plan.get("needs_image") and not image_plan.get("subject"):
            report["validation"]["errors"].append("Image subject missing.")
            report["status"] = "FAIL"

        # 9. Speaker notes validation
        notes = slide_content.get("speaker_notes", {})
        required_sections = ["opening","explanation","transition","timing"]
        for sec in required_sections:
            if not notes.get(sec):
                report["validation"]["warnings"].append(f"Speaker notes missing {sec}.")
                report["status"] = "WARN"

        # 10. Renderer readiness
        if vtype == "workflow" and not slide_content.get("visual_spec", {}).get("semantic_data", {}).get("steps"):
            report["validation"]["errors"].append("Workflow missing steps.")
            report["status"] = "FAIL"

        # Repair suggestions
        if len(slide_content.get("bullets", [])) > plan.get("bullet_limit", 5):
            report["validation"]["repair_actions"].append("Remove extra bullets beyond limit.")

        if len(slide_content.get("headline","").split()) > 8:
            report["validation"]["repair_actions"].append("Shorten headline to <=8 words.")

        return report
