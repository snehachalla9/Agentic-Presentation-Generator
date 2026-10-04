from pathlib import Path
from typing import Optional

from pptx import Presentation
from pptx.util import Inches

from .layouts.registry import LayoutRegistry


class PPTGeneratorV2:
    """
    Main orchestrator for PPT Generator V2.

    Responsibilities:
    - receive merged presentation JSON
    - create PowerPoint presentation
    - iterate through slides
    - determine layout
    - pass visual specification to renderer
    - save final .pptx

    It should NOT contain layout/design logic.
    """

    def __init__(self):
        self.registry = LayoutRegistry()

    def generate(
        self,
        presentation_data: dict,
        output_path: str = "output/final_v2.pptx",
    ) -> str:

        if not isinstance(
            presentation_data,
            dict
        ):
            raise TypeError(
                "presentation_data must be a dictionary."
            )

        slides = presentation_data.get(
            "slides",
            []
        )

        if not slides:
            raise ValueError(
                "No slides found in presentation data."
            )

        # ------------------------------------------
        # Create presentation
        # ------------------------------------------

        prs = Presentation()

        prs.slide_width = Inches(13.333)
        prs.slide_height = Inches(7.5)

        print("\n🚀 PPT Generator V2")
        print(
            f"📑 Slides received: {len(slides)}"
        )

        rendered_count = 0
        failed_count = 0

        # ------------------------------------------
        # Render slides
        # ------------------------------------------

        for index, wrapper in enumerate(
            slides,
            start=1
        ):

            try:

                self._render_slide(
                    prs=prs,
                    wrapper=wrapper,
                    index=index
                )

                rendered_count += 1

            except Exception as exc:

                failed_count += 1

                print(
                    f"❌ Slide {index} failed: "
                    f"{type(exc).__name__}: {exc}"
                )

        # ------------------------------------------
        # Check rendering
        # ------------------------------------------

        if rendered_count == 0:

            raise RuntimeError(
                "PPT generation failed: "
                "no slides were rendered."
            )

        # ------------------------------------------
        # Save
        # ------------------------------------------

        output = Path(
            output_path
        )

        output.parent.mkdir(
            parents=True,
            exist_ok=True
        )

        prs.save(
            str(output)
        )

        print("\n✅ PPT generation complete")

        print(
            f"   Rendered: {rendered_count}"
        )

        print(
            f"   Failed:   {failed_count}"
        )

        print(
            f"   Output:   {output}"
        )

        return str(output)

    # ==========================================================
    # RENDER SLIDE
    # ==========================================================

    def _render_slide(
        self,
        prs,
        wrapper: dict,
        index: int,
    ):

        if not isinstance(
            wrapper,
            dict
        ):
            raise TypeError(
                "Slide wrapper must be a dictionary."
            )

        # ------------------------------------------
        # Extract slide
        # ------------------------------------------

        data = wrapper.get(
            "slide"
        )

        if not isinstance(
            data,
            dict
        ):
            raise ValueError(
                f"Slide {index} has invalid slide data."
            )

        # ------------------------------------------
        # Identity
        # ------------------------------------------

        identity = data.get(
            "identity",
            {}
        )

        if not isinstance(
            identity,
            dict
        ):
            identity = {}

        slide_id = identity.get(
            "slide_id",
            f"S{index:02d}"
        )

        # ------------------------------------------
        # Presentation plan
        # ------------------------------------------

        presentation_plan = data.get(
            "presentation_plan",
            {}
        )

        if not isinstance(
            presentation_plan,
            dict
        ):
            presentation_plan = {}

        # ------------------------------------------
        # Existing planner layout
        # ------------------------------------------

        layout_name = data.get(
            "layout"
        )

        if not layout_name:

            layout_name = presentation_plan.get(
                "template"
            )

        if not layout_name:

            layout_name = presentation_plan.get(
                "layout"
            )

        if not layout_name:

            layout_name = "content"

        layout_name = str(
            layout_name
        ).strip().lower()

        # ------------------------------------------
        # Visual specification
        # ------------------------------------------

        visual_spec = data.get(
            "visual_spec",
            {}
        )

        if not isinstance(
            visual_spec,
            dict
        ):
            visual_spec = {}

        visual_type = visual_spec.get(
            "visual_type"
        )

        # ------------------------------------------
        # Use VisualBuilder decision
        # ------------------------------------------

        if visual_type:

            mapped_layout = (
                self._map_visual_to_layout(
                    visual_type
                )
            )

            if mapped_layout:

                layout_name = mapped_layout

        # ------------------------------------------
        # Logging
        # ------------------------------------------

        print(
            f"\n🎨 {slide_id}"
        )

        print(
            f"   Layout: {layout_name}"
        )

        if visual_type:

            print(
                f"   Visual: {visual_type}"
            )

        # ------------------------------------------
        # Get renderer
        # ------------------------------------------

        renderer = self.registry.get(
            layout_name
        )

        if renderer is None:

            raise ValueError(
                f"No renderer found for layout: "
                f"{layout_name}"
            )

        # ------------------------------------------
        # Pass visual specification
        # ------------------------------------------

        render_data = dict(
            data
        )

        render_data["_visual_spec"] = (
            visual_spec
        )

        # ------------------------------------------
        # Render
        # ------------------------------------------

        renderer(
            prs=prs,
            data=render_data
        )

    # ==========================================================
    # VISUAL → EXISTING LAYOUT
    # ==========================================================

    def _map_visual_to_layout(
        self,
        visual_type: str
    ) -> Optional[str]:

        visual_type = str(
            visual_type
        ).strip().lower()

        mapping = {

            # --------------------------------------
            # Main visual types
            # --------------------------------------

            "hero": "hero",

            "focus": "focus",

            "concept": "focus",

            "cards": "cards",

            "feature_cards": "cards",

            "smart_cards": "cards",

            # --------------------------------------
            # Process
            # --------------------------------------

            "workflow": "process",

            "process": "process",

            "vertical_process": "steps",

            "horizontal_process": "process",

            # --------------------------------------
            # Timeline
            # --------------------------------------

            "timeline": "timeline",

            # --------------------------------------
            # Comparison
            # --------------------------------------

            "comparison": "comparison",

            "comparison_table": "comparison",

            "pros_cons": "comparison",

            # --------------------------------------
            # Data
            # --------------------------------------

            "chart": "grid",

            "kpi": "grid",

            # --------------------------------------
            # Architecture
            # --------------------------------------

            "architecture": "split",

            "architecture_diagram": "split",

            # --------------------------------------
            # Case study
            # --------------------------------------

            "case_study": "split",

            # --------------------------------------
            # Matrix
            # --------------------------------------

            "matrix": "grid",

            # --------------------------------------
            # FAQ
            # --------------------------------------

            "faq": "cards",
        }

        return mapping.get(
            visual_type
        )