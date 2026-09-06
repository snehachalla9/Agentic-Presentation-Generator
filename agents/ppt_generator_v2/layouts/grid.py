from pptx.enum.shapes import MSO_SHAPE
from pptx.enum.text import PP_ALIGN
from pptx.util import Inches

from ..components.text import add_header, add_text
from ..core.theme import Theme


def render_grid(prs, data):
    """
    Render concepts/categories/components in a responsive grid.

    Current version:
    - 1 item  -> single feature cell
    - 2 items -> 2 columns
    - 3 items -> 3 columns
    - 4 items -> 2 x 2
    - 5–6     -> 3 x 2

    Later the Layout Director will choose richer variants.
    """

    # --------------------------------------------------
    # 1. Create slide
    # --------------------------------------------------

    slide = prs.slides.add_slide(
        prs.slide_layouts[6]
    )

    # --------------------------------------------------
    # 2. Background
    # --------------------------------------------------

    background = slide.background.fill
    background.solid()
    background.fore_color.rgb = Theme.BACKGROUND

    # --------------------------------------------------
    # 3. Extract content
    # --------------------------------------------------

    content = data.get("content", {})

    title = content.get("title", "")
    subtitle = content.get("subtitle", "")
    bullets = content.get("bullets", [])
    takeaway = content.get("key_takeaway", "")

    bullets = [
        str(item).strip()
        for item in bullets
        if item is not None and str(item).strip()
    ]

    # Phase 1 maximum
    bullets = bullets[:6]

    # --------------------------------------------------
    # 4. Header
    # --------------------------------------------------

    add_header(
        slide=slide,
        title=title,
        subtitle=subtitle,
    )

    # --------------------------------------------------
    # 5. Empty fallback
    # --------------------------------------------------

    if not bullets:

        _render_empty_grid(
            slide=slide,
            takeaway=takeaway,
        )

        return slide

    # --------------------------------------------------
    # 6. Determine grid
    # --------------------------------------------------

    rows, columns = _get_grid_dimensions(
        len(bullets)
    )

    # --------------------------------------------------
    # 7. Render grid
    # --------------------------------------------------

    _render_grid_items(
        slide=slide,
        items=bullets,
        rows=rows,
        columns=columns,
    )

    # --------------------------------------------------
    # 8. Takeaway
    # --------------------------------------------------

    if takeaway:

        add_text(
            slide=slide,
            text=takeaway,
            x=1.0,
            y=6.80,
            w=11.3,
            h=0.30,
            font_size=12,
            bold=True,
            color=Theme.PRIMARY,
            align=PP_ALIGN.CENTER,
        )

    return slide


# ======================================================
# Determine grid dimensions
# ======================================================

def _get_grid_dimensions(count):
    """
    Decide rows and columns based on item count.
    """

    if count == 1:
        return 1, 1

    if count == 2:
        return 1, 2

    if count == 3:
        return 1, 3

    if count == 4:
        return 2, 2

    # 5 or 6
    return 2, 3


# ======================================================
# Render grid
# ======================================================

def _render_grid_items(
    slide,
    items,
    rows,
    columns,
):

    left = 0.70
    top = 1.75

    available_width = 11.93
    available_height = 4.75

    gap_x = 0.25
    gap_y = 0.25

    cell_width = (
        available_width
        - gap_x * (columns - 1)
    ) / columns

    cell_height = (
        available_height
        - gap_y * (rows - 1)
    ) / rows

    for index, item in enumerate(items):

        row = index // columns
        column = index % columns

        x = left + column * (
            cell_width + gap_x
        )

        y = top + row * (
            cell_height + gap_y
        )

        _add_grid_cell(
            slide=slide,
            text=item,
            number=index + 1,
            x=x,
            y=y,
            w=cell_width,
            h=cell_height,
        )


# ======================================================
# Individual grid cell
# ======================================================

def _add_grid_cell(
    slide,
    text,
    number,
    x,
    y,
    w,
    h,
):

    # --------------------------------------------------
    # Cell background
    # --------------------------------------------------

    cell = slide.shapes.add_shape(
        MSO_SHAPE.ROUNDED_RECTANGLE,
        Inches(x),
        Inches(y),
        Inches(w),
        Inches(h),
    )

    cell.fill.solid()
    cell.fill.fore_color.rgb = Theme.CARD

    cell.line.color.rgb = Theme.BORDER

    # --------------------------------------------------
    # Number badge
    # --------------------------------------------------

    badge = slide.shapes.add_shape(
        MSO_SHAPE.ROUNDED_RECTANGLE,
        Inches(x + 0.30),
        Inches(y + 0.30),
        Inches(0.55),
        Inches(0.38),
    )

    badge.fill.solid()
    badge.fill.fore_color.rgb = Theme.PRIMARY

    badge.line.fill.background()

    add_text(
        slide=slide,
        text=f"{number:02d}",
        x=x + 0.30,
        y=y + 0.30,
        w=0.55,
        h=0.38,
        font_size=9,
        bold=True,
        color=Theme.CARD,
        align=PP_ALIGN.CENTER,
    )

    # --------------------------------------------------
    # Split bullet into heading + description
    # --------------------------------------------------

    heading, description = _split_item(text)

    add_text(
        slide=slide,
        text=heading,
        x=x + 1.00,
        y=y + 0.28,
        w=w - 1.30,
        h=0.50,
        font_size=16,
        bold=True,
        color=Theme.TEXT,
    )

    if description:

        add_text(
            slide=slide,
            text=description,
            x=x + 0.30,
            y=y + 1.05,
            w=w - 0.60,
            h=h - 1.35,
            font_size=13,
            color=Theme.MUTED_TEXT,
        )


# ======================================================
# Extract heading from bullet
# ======================================================

def _split_item(text):
    """
    Temporary transformation of a bullet into:

        heading
        description

    Example:

    "Matrix operations are fundamental to neural networks."

    becomes approximately:

        Matrix operations
        are fundamental to neural networks.

    Later the content/director layer should provide
    structured grid items instead.
    """

    text = str(text).strip()

    if not text:
        return "", ""

    words = text.split()

    # Very short point: use entire text as heading
    if len(words) <= 5:
        return text, ""

    heading_words = words[:3]
    description_words = words[3:]

    heading = " ".join(heading_words)

    description = " ".join(
        description_words
    )

    return heading, description


# ======================================================
# Empty fallback
# ======================================================

def _render_empty_grid(
    slide,
    takeaway,
):

    message = (
        takeaway
        or "No concepts available."
    )

    add_text(
        slide=slide,
        text=message,
        x=2.0,
        y=3.0,
        w=9.3,
        h=1.0,
        font_size=22,
        bold=True,
        color=Theme.TEXT,
        align=PP_ALIGN.CENTER,
    )