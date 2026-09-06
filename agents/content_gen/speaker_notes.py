
from typing import Dict, Any


class SpeakerNotesGenerator:
    """
    Production-ready Speaker Notes Generator

    Supports:
    - LLM returning string speaker notes
    - LLM returning structured speaker notes
    - Audience adaptation
    - Visual walkthrough generation
    - Timing estimation
    - Safe defaults
    """

    def enhance(
        self,
        draft_notes: Any,
        slide_content: Dict,
        slide_blueprint: Dict
    ) -> Dict:

        # --------------------------------------------------
        # Normalize LLM output
        # --------------------------------------------------
        draft_notes = self._normalize_notes(draft_notes)

        # --------------------------------------------------
        # Audience profile
        # --------------------------------------------------
        profile = slide_content.get(
            "presentation_profile",
            {}
        )

        tone = profile.get("tone", "neutral")

        # --------------------------------------------------
        # Visual information
        # --------------------------------------------------
        visual = slide_content.get("visual_spec", {})

        visual_type = (
            visual.get("visual_type")
            or visual.get("type")
            or visual.get("layout")
        )

        # --------------------------------------------------
        # Base Notes
        # --------------------------------------------------
        notes = {
            "opening": draft_notes.get("opening", ""),
            "explanation": draft_notes.get("explanation", ""),
            "visual_walkthrough": draft_notes.get(
                "visual_walkthrough",
                ""
            ),
            "audience_question": draft_notes.get(
                "audience_question",
                ""
            ),
            "common_mistake": draft_notes.get(
                "common_mistake",
                ""
            ),
            "transition": draft_notes.get(
                "transition",
                ""
            ),
            "timing": draft_notes.get(
                "timing",
                "75 sec"
            ),
            "emphasis": draft_notes.get(
                "emphasis",
                ""
            ),
            "closing": draft_notes.get(
                "closing",
                ""
            )
        }

        # --------------------------------------------------
        # Audience Adaptation
        # --------------------------------------------------

        if tone == "strategic":

            notes["opening"] = (
                notes["opening"]
                or "Let's focus on the business value."
            )

            notes["emphasis"] = (
                "Highlight business impact, ROI, and decision making."
            )

        elif tone == "educational":

            notes["audience_question"] = (
                "Ask students why this concept matters."
            )

            notes["emphasis"] = (
                "Explain slowly using simple examples."
            )

        elif tone == "engineering":

            notes["emphasis"] = (
                "Explain implementation details and architecture."
            )

        elif tone == "academic":

            notes["emphasis"] = (
                "Discuss supporting evidence, citations and limitations."
            )

        elif tone == "practical":

            notes["opening"] = (
                "Relate this concept to a real-world scenario."
            )

            notes["emphasis"] = (
                "Focus on practical applications."
            )

        # --------------------------------------------------
        # Visual Walkthrough
        # --------------------------------------------------

        if visual_type == "chart":

            notes["visual_walkthrough"] = (
                "Walk through the chart from left to right. Explain important trends and highlight the key insight."
            )

        elif visual_type == "workflow":

            notes["visual_walkthrough"] = (
                "Explain each workflow step sequentially and describe how information flows."
            )

        elif visual_type == "timeline":

            notes["visual_walkthrough"] = (
                "Describe the evolution across the timeline and explain major milestones."
            )

        elif visual_type == "comparison":

            notes["visual_walkthrough"] = (
                "Compare both sides feature-by-feature before summarizing."
            )

        elif visual_type == "matrix":

            notes["visual_walkthrough"] = (
                "Explain each quadrant and discuss the trade-offs."
            )

        elif visual_type == "architecture":

            notes["visual_walkthrough"] = (
                "Describe the architecture from input to output while explaining each component."
            )

        elif visual_type == "pipeline":

            notes["visual_walkthrough"] = (
                "Explain the complete pipeline step-by-step."
            )

        elif visual_type == "diagram":

            notes["visual_walkthrough"] = (
                "Introduce the diagram first and then explain every connected component."
            )

        # --------------------------------------------------
        # Generate missing fields
        # --------------------------------------------------

        if not notes["opening"]:

            title = slide_content.get("headline") \
                or slide_content.get("title") \
                or "this topic"

            notes["opening"] = (
                f"Let's begin by understanding {title}."
            )

        if not notes["transition"]:

            notes["transition"] = (
                "Now let's move to the next concept."
            )

        if not notes["closing"]:

            takeaway = slide_content.get(
                "key_takeaway",
                ""
            )

            if takeaway:

                notes["closing"] = (
                    f"Remember: {takeaway}"
                )

            else:

                notes["closing"] = (
                    "Keep this concept in mind as we continue."
                )

        return notes

    # --------------------------------------------------
    # Normalize different LLM formats
    # --------------------------------------------------

    def _normalize_notes(self, draft_notes):

        if draft_notes is None:

            return {
                "opening": "",
                "explanation": "",
                "visual_walkthrough": "",
                "audience_question": "",
                "common_mistake": "",
                "transition": "",
                "timing": "75 sec",
                "emphasis": "",
                "closing": ""
            }

        if isinstance(draft_notes, str):

            return {
                "opening": "",
                "explanation": draft_notes,
                "visual_walkthrough": "",
                "audience_question": "",
                "common_mistake": "",
                "transition": "",
                "timing": "75 sec",
                "emphasis": "",
                "closing": ""
            }

        if isinstance(draft_notes, dict):

            return draft_notes

        return {
            "opening": "",
            "explanation": str(draft_notes),
            "visual_walkthrough": "",
            "audience_question": "",
            "common_mistake": "",
            "transition": "",
            "timing": "75 sec",
            "emphasis": "",
            "closing": ""
        }