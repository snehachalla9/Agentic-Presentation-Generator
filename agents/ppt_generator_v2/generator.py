from pathlib import Path
from typing import Dict, Optional
from pptx import Presentation
from pptx.util import Inches, Pt
from pptx.enum.text import PP_ALIGN, MSO_ANCHOR
from pptx.dml.color import RGBColor

from .layouts.registry import LayoutRegistry


class PPTGeneratorV2:
    """
    Main orchestrator for PPT Generator V2.

    Responsibilities:
    - receive merged presentation JSON
    - create PowerPoint presentation
    - iterate through slides
    - select layout renderer
    - render each slide
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
        # ------------------------------------------
        # 1. Validate input
        # ------------------------------------------
        if not isinstance(presentation_data, dict):
            raise TypeError("presentation_data must be a dictionary.")

        slides = presentation_data.get("slides", [])

        if not slides:
            raise ValueError("No slides found in presentation data.")

        # ------------------------------------------
        # 2. Create fresh presentation
        # ------------------------------------------
        prs = Presentation()

        # 16:9 widescreen
        prs.slide_width = Inches(13.333)
        prs.slide_height = Inches(7.5)

        print("\n🚀 PPT Generator V2")
        print(f"📑 Slides received: {len(slides)}")

        # ------------------------------------------
        # 3. Render slides
        # ------------------------------------------
        rendered_count = 0
        failed_count = 0

        for index, wrapper in enumerate(slides, start=1):
            try:
                self._render_slide(
                    prs=prs,
                    wrapper=wrapper,
                    index=index,
                )
                rendered_count += 1
            except Exception as exc:
                failed_count += 1
                print(f"❌ Slide {index} failed: {type(exc).__name__}: {exc}")

        # ------------------------------------------
        # 4. Make sure something rendered
        # ------------------------------------------
        if rendered_count == 0:
            raise RuntimeError(
                "PPT generation failed: no slides were rendered."
            )

        # ------------------------------------------
        # 5. Save presentation
        # ------------------------------------------
        output = Path(output_path)
        output.parent.mkdir(parents=True, exist_ok=True)
        prs.save(str(output))

        # ------------------------------------------
        # 6. Summary
        # ------------------------------------------
        print("\n✅ PPT generation complete")
        print(f"   Rendered: {rendered_count}")
        print(f"   Failed:   {failed_count}")
        print(f"   Output:   {output}")

        return str(output)

    def _render_slide(
        self,
        prs,
        wrapper: dict,
        index: int,
    ):
        """Extract slide data and delegate rendering to the appropriate layout renderer."""
        if not isinstance(wrapper, dict):
            raise TypeError("Slide wrapper must be a dictionary.")

        # Your merged JSON structure: {"slide": {...}}
        data = wrapper.get("slide")

        if not isinstance(data, dict):
            raise ValueError(f"Slide {index} has invalid slide data.")

        # ------------------------------------------
        # Extract identity
        # ------------------------------------------
        identity = data.get("identity", {})
        slide_id = identity.get("slide_id", f"S{index:02d}")

        # ------------------------------------------
        # Determine layout
        # ------------------------------------------
        layout_name = data.get("layout")

        if not layout_name:
            presentation_plan = data.get("presentation_plan", {})
            layout_name = presentation_plan.get("template", "content")

        layout_name = str(layout_name).strip().lower()

        print(f"🎨 {slide_id} → {layout_name}")

        # ------------------------------------------
        # Resolve renderer
        # ------------------------------------------
        renderer = self.registry.get(layout_name)

        if renderer is None:
            # Fallback to content renderer
            renderer = self.registry.get("content")
            if renderer is None:
                raise ValueError(f"No renderer found for layout: {layout_name}")

        # ------------------------------------------
        # Render
        # ------------------------------------------
        renderer(prs=prs, data=data)