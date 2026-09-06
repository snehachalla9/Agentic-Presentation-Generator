
from .hero import render_hero
from .cards import render_cards
from .comparison import render_comparison
from .grid import render_grid

from .split import render_split
from .process import render_process
from .timeline import render_timeline
from .focus import render_focus
from .steps import render_steps
from .content import render_content 


class LayoutRegistry:

    def __init__(self):

        self.layouts = {
            "hero": render_hero,
            "cards": render_cards,
            "comparison": render_comparison,
            "grid": render_grid,

            "split": render_split,
            "process": render_process,
            "timeline": render_timeline,
            "focus": render_focus,
            "steps": render_steps,
            "content": render_content,        
            "bullets": render_content,      
            "content_slide": render_content, 
        }

    def get(self, name: str):

        renderer = self.layouts.get(name)

        if renderer:
            return renderer

        print(
            f"⚠️ Unknown layout '{name}'. "
            "Falling back to hero."
        )

        return render_hero