from pptx.dml.color import RGBColor


class Theme:

    # Background
    BACKGROUND = RGBColor(248, 250, 252)

    # Text
    TEXT = RGBColor(15, 23, 42)
    MUTED_TEXT = RGBColor(71, 85, 105)

    # Accent
    PRIMARY = RGBColor(79, 70, 229)
    SECONDARY = RGBColor(14, 165, 233)

    # Surfaces
    CARD = RGBColor(255, 255, 255)
    BORDER = RGBColor(226, 232, 240)

    # Typography
    FONT = "Aptos"

    TITLE_SIZE = 28
    SUBTITLE_SIZE = 14
    BODY_SIZE = 16
    CARD_TITLE_SIZE = 17

    # Geometry
    LEFT_MARGIN = 0.65
    RIGHT_MARGIN = 0.65

    TOP_MARGIN = 0.45
    BOTTOM_MARGIN = 0.40