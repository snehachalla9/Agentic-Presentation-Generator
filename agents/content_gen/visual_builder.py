import re
from typing import Any, Dict, List


class VisualBuilder:
    """
    Semantic Visual Builder for Neurovia.

    Responsibilities:
    - Understand what kind of information the slide contains
    - Choose the most suitable visual representation
    - Extract structured data for the renderer
    - Provide layout and density hints
    - Avoid empty or meaningless visuals
    """

    def build(
        self,
        selected: dict,
        slide_blueprint: dict
    ) -> dict:

        if not isinstance(selected, dict):
            selected = {}

        if not isinstance(slide_blueprint, dict):
            slide_blueprint = {}

        slide = slide_blueprint.get(
            "slide",
            {}
        )

        if not isinstance(slide, dict):
            slide = {}

        plan = slide.get(
            "presentation_plan",
            {}
        )

        if not isinstance(plan, dict):
            plan = {}

        intent = plan.get(
            "presentation_intent",
            {}
        )

        if not isinstance(intent, dict):
            intent = {}

        preferred_visuals = self._ensure_list(
            plan.get(
                "preferred_visuals",
                []
            )
        )

        alternative_visuals = self._ensure_list(
            plan.get(
                "alternative_visuals",
                []
            )
        )

        # ------------------------------------------
        # Choose visual
        # ------------------------------------------

        visual_type = self._choose_visual_type(
            preferred_visuals=preferred_visuals,
            alternative_visuals=alternative_visuals,
            intent=intent,
            selected=selected,
            plan=plan
        )

        # ------------------------------------------
        # Extract semantic data
        # ------------------------------------------

        semantic_data = self._extract_semantic_data(
            visual_type=visual_type,
            selected=selected,
            plan=plan
        )

        # ------------------------------------------
        # Density
        # ------------------------------------------

        density = self._visual_density(
            selected
        )

        # ------------------------------------------
        # Renderer hints
        # ------------------------------------------

        renderer_hints = self._renderer_hints(
            visual_type=visual_type,
            intent=intent,
            selected=selected,
            density=density
        )

        # ------------------------------------------
        # Image requirements
        # ------------------------------------------

        image_requirements = self._image_requirements(
            visual_type=visual_type,
            plan=plan,
            selected=selected
        )

        # ------------------------------------------
        # Final visual specification
        # ------------------------------------------

        return {
            "visual_type": visual_type,

            "visual_intent": intent.get(
                "information_type",
                "explain"
            ),

            "semantic_data": semantic_data,

            "renderer_hints": renderer_hints,

            "image_requirements": image_requirements,

            "density": density,

            "visual_priority": self._visual_priority(
                visual_type,
                selected
            )
        }

    # ==========================================================
    # VISUAL TYPE SELECTION
    # ==========================================================

    def _choose_visual_type(
        self,
        preferred_visuals: List[str],
        alternative_visuals: List[str],
        intent: Dict[str, Any],
        selected: Dict[str, Any],
        plan: Dict[str, Any]
    ) -> str:

        available = self._available_visuals(
            selected
        )

        # ------------------------------------------
        # 1. Planner preference
        # ------------------------------------------

        for visual in preferred_visuals:

            visual = self._normalize_visual_type(
                visual
            )

            if available.get(
                visual,
                False
            ):
                return visual

        # ------------------------------------------
        # 2. Planner alternatives
        # ------------------------------------------

        for visual in alternative_visuals:

            visual = self._normalize_visual_type(
                visual
            )

            if available.get(
                visual,
                False
            ):
                return visual

        # ------------------------------------------
        # 3. Semantic priority
        # ------------------------------------------

        if self._has_items(
            selected.get("process")
        ):
            return "workflow"

        if self._has_items(
            selected.get("timeline")
        ):
            return "timeline"

        if self._has_items(
            selected.get("comparison")
        ):
            return "comparison"

        if (
            self._has_items(
                selected.get("relationships")
            )
            or
            self._has_items(
                selected.get("components")
            )
        ):
            return "architecture"

        if self._has_items(
            selected.get("statistics")
        ):
            return "chart"

        if self._has_items(
            selected.get("case_studies")
        ):
            return "case_study"

        if self._has_items(
            selected.get("faqs")
        ):
            return "cards"

        if self._has_items(
            selected.get("pros_cons")
        ):
            return "comparison"

        if self._has_items(
            selected.get("concepts")
        ):
            return "cards"

        # ------------------------------------------
        # 4. Intent based fallback
        # ------------------------------------------

        information_type = str(
            intent.get(
                "information_type",
                ""
            )
        ).lower()

        slide_type = str(
            plan.get(
                "slide_type",
                ""
            )
        ).lower()

        slide_focus = str(
            plan.get(
                "slide_focus",
                ""
            )
        ).lower()

        if any(
            word in information_type
            for word in [
                "compare",
                "comparison",
                "versus"
            ]
        ):
            return "comparison"

        if any(
            word in information_type
            for word in [
                "process",
                "workflow",
                "sequence"
            ]
        ):
            return "workflow"

        if any(
            word in information_type
            for word in [
                "timeline",
                "history",
                "evolution"
            ]
        ):
            return "timeline"

        if any(
            word in information_type
            for word in [
                "architecture",
                "structure",
                "system"
            ]
        ):
            return "architecture"

        if any(
            word in information_type
            for word in [
                "metric",
                "metrics",
                "statistics",
                "data"
            ]
        ):
            return "chart"

        if (
            "concept" in slide_type
            or
            "concept" in information_type
            or
            "concept" in slide_focus
        ):
            return "cards"

        # ------------------------------------------
        # Final safe fallback
        # ------------------------------------------

        if selected.get("summary"):
            return "focus"

        return "cards"

    # ==========================================================
    # AVAILABLE VISUALS
    # ==========================================================

    def _available_visuals(
        self,
        selected: Dict[str, Any]
    ) -> Dict[str, bool]:

        return {

            "hero": bool(
                selected.get("summary")
            ),

            "cards": self._has_items(
                selected.get("concepts")
            ),

            "comparison": self._has_items(
                selected.get("comparison")
            ),

            "workflow": self._has_items(
                selected.get("process")
            ),

            "timeline": self._has_items(
                selected.get("timeline")
            ),

            "chart": self._has_items(
                selected.get("statistics")
            ),

            "architecture": (
                self._has_items(
                    selected.get("relationships")
                )
                or
                self._has_items(
                    selected.get("components")
                )
            ),

            "case_study": self._has_items(
                selected.get("case_studies")
            ),

            "faq": self._has_items(
                selected.get("faqs")
            ),

            "pros_cons": self._has_items(
                selected.get("pros_cons")
            ),

            "focus": bool(
                selected.get("summary")
                or
                selected.get("concepts")
            )
        }

    # ==========================================================
    # SEMANTIC DATA
    # ==========================================================

    def _extract_semantic_data(
        self,
        visual_type: str,
        selected: Dict[str, Any],
        plan: Dict[str, Any]
    ) -> Dict[str, Any]:

        visual_type = self._normalize_visual_type(
            visual_type
        )

        # ------------------------------------------
        # Chart
        # ------------------------------------------

        if visual_type == "chart":

            return {
                "metrics": self._extract_metrics(
                    selected.get(
                        "statistics",
                        []
                    )
                )
            }

        # ------------------------------------------
        # Workflow
        # ------------------------------------------

        if visual_type == "workflow":

            return {
                "steps": self._extract_process_steps(
                    selected.get(
                        "process",
                        []
                    )
                )
            }

        # ------------------------------------------
        # Timeline
        # ------------------------------------------

        if visual_type == "timeline":

            return {
                "events": self._extract_events(
                    selected.get(
                        "timeline",
                        []
                    )
                )
            }

        # ------------------------------------------
        # Comparison
        # ------------------------------------------

        if visual_type == "comparison":

            return self._extract_comparison(
                selected.get(
                    "comparison",
                    []
                ),
                selected
            )

        # ------------------------------------------
        # Cards
        # ------------------------------------------

        if visual_type == "cards":

            return {
                "items": self._extract_cards(
                    selected.get(
                        "concepts",
                        []
                    ),
                    selected.get(
                        "examples",
                        []
                    )
                )
            }

        # ------------------------------------------
        # Architecture
        # ------------------------------------------

        if visual_type == "architecture":

            return {
                "components": self._extract_components(
                    selected
                ),

                "relationships": self._extract_relationships(
                    selected
                )
            }

        # ------------------------------------------
        # Case study
        # ------------------------------------------

        if visual_type == "case_study":

            return {
                "cases": self._extract_case_studies(
                    selected.get(
                        "case_studies",
                        []
                    )
                )
            }

        # ------------------------------------------
        # Focus
        # ------------------------------------------

        if visual_type in [
            "hero",
            "focus"
        ]:

            return {
                "headline": selected.get(
                    "summary",
                    ""
                ),

                "focus_points": self._extract_focus_points(
                    selected
                )
            }

        return {}

    # ==========================================================
    # METRICS
    # ==========================================================

    def _extract_metrics(
        self,
        stats: List[Any]
    ) -> List[Dict[str, str]]:

        metrics = []

        if not isinstance(
            stats,
            list
        ):
            return metrics

        for stat in stats:

            # --------------------------------------
            # Structured statistic
            # --------------------------------------

            if isinstance(
                stat,
                dict
            ):

                label = (
                    stat.get("label")
                    or
                    stat.get("name")
                    or
                    stat.get("metric")
                    or
                    ""
                )

                value = (
                    stat.get("value")
                    or
                    stat.get("number")
                    or
                    stat.get("percentage")
                    or
                    ""
                )

                if label or value:

                    metrics.append({
                        "label": str(
                            label
                        ).strip(),

                        "value": str(
                            value
                        ).strip()
                    })

                continue

            # --------------------------------------
            # String statistic
            # --------------------------------------

            text = str(
                stat
            ).strip()

            if not text:
                continue

            match = re.search(
                r"""
                (?:
                    [$€₹]\s*
                )?
                [-+]?
                \d+(?:,\d{3})*
                (?:\.\d+)?
                \s*
                (?:%|[KMB])?
                """,
                text,
                re.VERBOSE | re.IGNORECASE
            )

            if match:

                value = match.group(
                    0
                ).strip()

                label = (
                    text[:match.start()]
                    +
                    text[match.end():]
                ).strip(
                    " :-–—"
                )

            else:

                value = ""
                label = text

            metrics.append({
                "label": label,
                "value": value
            })

        return metrics[:6]

    # ==========================================================
    # PROCESS
    # ==========================================================

    def _extract_process_steps(
        self,
        process: List[Any]
    ) -> List[Dict[str, Any]]:

        steps = []

        if not isinstance(
            process,
            list
        ):
            return steps

        for index, item in enumerate(
            process,
            start=1
        ):

            if isinstance(
                item,
                dict
            ):

                title = (
                    item.get("title")
                    or
                    item.get("name")
                    or
                    item.get("step")
                    or
                    f"Step {index}"
                )

                description = (
                    item.get("description")
                    or
                    item.get("details")
                    or
                    item.get("explanation")
                    or
                    ""
                )

            else:

                title = str(
                    item
                )

                description = ""

            steps.append({
                "number": index,

                "title": str(
                    title
                ).strip(),

                "description": str(
                    description
                ).strip()
            })

        return steps[:6]

    # ==========================================================
    # TIMELINE
    # ==========================================================

    def _extract_events(
        self,
        timeline: List[Any]
    ) -> List[Dict[str, Any]]:

        events = []

        if not isinstance(
            timeline,
            list
        ):
            return events

        for item in timeline:

            if isinstance(
                item,
                dict
            ):

                year = (
                    item.get("year")
                    or
                    item.get("date")
                    or
                    item.get("period")
                )

                event = (
                    item.get("event")
                    or
                    item.get("title")
                    or
                    item.get("description")
                    or
                    ""
                )

            else:

                year = None
                event = str(
                    item
                )

            if event:

                events.append({
                    "year": year,
                    "event": str(
                        event
                    ).strip()
                })

        return events[:7]

    # ==========================================================
    # COMPARISON
    # ==========================================================

    def _extract_comparison(
        self,
        comparison: List[Any],
        selected: Dict[str, Any]
    ) -> Dict[str, Any]:

        result = {
            "left_title": "Option A",
            "right_title": "Option B",
            "criteria": []
        }

        if not isinstance(
            comparison,
            list
        ):
            return result

        for item in comparison:

            if isinstance(
                item,
                dict
            ):

                left = (
                    item.get("left")
                    or
                    item.get("option_a")
                    or
                    item.get("a")
                    or
                    item.get("value_a")
                    or
                    ""
                )

                right = (
                    item.get("right")
                    or
                    item.get("option_b")
                    or
                    item.get("b")
                    or
                    item.get("value_b")
                    or
                    ""
                )

                criterion = (
                    item.get("criterion")
                    or
                    item.get("criteria")
                    or
                    item.get("feature")
                    or
                    item.get("name")
                    or
                    ""
                )

                if criterion or left or right:

                    result["criteria"].append({
                        "criterion": str(
                            criterion
                        ).strip(),

                        "left": str(
                            left
                        ).strip(),

                        "right": str(
                            right
                        ).strip()
                    })

            else:

                text = str(
                    item
                ).strip()

                if text:

                    result["criteria"].append({
                        "criterion": text,
                        "left": "",
                        "right": ""
                    })

        # ------------------------------------------
        # Comparison titles
        # ------------------------------------------

        titles = selected.get(
            "comparison_titles"
        )

        if (
            isinstance(
                titles,
                list
            )
            and
            len(titles) >= 2
        ):

            result["left_title"] = str(
                titles[0]
            ).strip()

            result["right_title"] = str(
                titles[1]
            ).strip()

        return result

    # ==========================================================
    # CARDS
    # ==========================================================

    def _extract_cards(
        self,
        concepts: List[Any],
        examples: List[Any]
    ) -> List[Dict[str, Any]]:

        cards = []

        if not isinstance(
            concepts,
            list
        ):
            concepts = []

        # ------------------------------------------
        # Concepts
        # ------------------------------------------

        for concept in concepts[:6]:

            if isinstance(
                concept,
                dict
            ):

                title = (
                    concept.get("title")
                    or
                    concept.get("name")
                    or
                    concept.get("concept")
                    or
                    ""
                )

                description = (
                    concept.get("description")
                    or
                    concept.get("explanation")
                    or
                    concept.get("details")
                    or
                    ""
                )

                icon = (
                    concept.get("icon")
                    or
                    concept.get("symbol")
                )

            else:

                title = str(
                    concept
                )

                description = ""
                icon = None

            if title:

                cards.append({
                    "title": str(
                        title
                    ).strip(),

                    "description": str(
                        description
                    ).strip(),

                    "icon": icon
                })

        # ------------------------------------------
        # Examples fallback
        # ------------------------------------------

        if (
            len(cards) < 2
            and
            isinstance(
                examples,
                list
            )
        ):

            for example in examples[:6]:

                if isinstance(
                    example,
                    dict
                ):

                    title = (
                        example.get("title")
                        or
                        example.get("name")
                        or
                        "Example"
                    )

                    description = (
                        example.get("description")
                        or
                        example.get("details")
                        or
                        ""
                    )

                else:

                    title = "Example"
                    description = str(
                        example
                    )

                cards.append({
                    "title": str(
                        title
                    ).strip(),

                    "description": str(
                        description
                    ).strip(),

                    "icon": None
                })

        return cards[:6]

    # ==========================================================
    # ARCHITECTURE
    # ==========================================================

    def _extract_components(
        self,
        selected: Dict[str, Any]
    ) -> List[Dict[str, Any]]:

        components = selected.get(
            "components",
            []
        )

        if not components:

            components = selected.get(
                "concepts",
                []
            )

        result = []

        if not isinstance(
            components,
            list
        ):
            return result

        for index, component in enumerate(
            components[:8],
            start=1
        ):

            if isinstance(
                component,
                dict
            ):

                name = (
                    component.get("name")
                    or
                    component.get("title")
                    or
                    component.get("component")
                    or
                    f"Component {index}"
                )

                description = (
                    component.get("description")
                    or
                    component.get("details")
                    or
                    ""
                )

            else:

                name = str(
                    component
                )

                description = ""

            result.append({
                "id": index,

                "name": str(
                    name
                ).strip(),

                "description": str(
                    description
                ).strip()
            })

        return result

    # ==========================================================
    # RELATIONSHIPS
    # ==========================================================

    def _extract_relationships(
        self,
        selected: Dict[str, Any]
    ) -> List[Dict[str, Any]]:

        relationships = selected.get(
            "relationships",
            []
        )

        result = []

        if not isinstance(
            relationships,
            list
        ):
            return result

        for relationship in relationships[:8]:

            if isinstance(
                relationship,
                dict
            ):

                source = (
                    relationship.get("source")
                    or
                    relationship.get("from")
                    or
                    ""
                )

                target = (
                    relationship.get("target")
                    or
                    relationship.get("to")
                    or
                    ""
                )

                relation = (
                    relationship.get("relationship")
                    or
                    relationship.get("label")
                    or
                    relationship.get("type")
                    or
                    ""
                )

            else:

                source = ""
                target = ""
                relation = str(
                    relationship
                )

            result.append({
                "source": str(
                    source
                ).strip(),

                "target": str(
                    target
                ).strip(),

                "relationship": str(
                    relation
                ).strip()
            })

        return result

    # ==========================================================
    # CASE STUDIES
    # ==========================================================

    def _extract_case_studies(
        self,
        case_studies: List[Any]
    ) -> List[Dict[str, Any]]:

        result = []

        if not isinstance(
            case_studies,
            list
        ):
            return result

        for case in case_studies[:3]:

            if isinstance(
                case,
                dict
            ):

                title = (
                    case.get("title")
                    or
                    case.get("name")
                    or
                    "Case Study"
                )

                problem = (
                    case.get("problem")
                    or
                    case.get("challenge")
                    or
                    ""
                )

                solution = (
                    case.get("solution")
                    or
                    case.get("approach")
                    or
                    ""
                )

                outcome = (
                    case.get("result")
                    or
                    case.get("outcome")
                    or
                    ""
                )

            else:

                title = "Case Study"
                problem = str(
                    case
                )
                solution = ""
                outcome = ""

            result.append({
                "title": str(
                    title
                ).strip(),

                "problem": str(
                    problem
                ).strip(),

                "solution": str(
                    solution
                ).strip(),

                "result": str(
                    outcome
                ).strip()
            })

        return result

    # ==========================================================
    # FOCUS POINTS
    # ==========================================================

    def _extract_focus_points(
        self,
        selected: Dict[str, Any]
    ) -> List[str]:

        concepts = selected.get(
            "concepts",
            []
        )

        result = []

        if not isinstance(
            concepts,
            list
        ):
            return result

        for concept in concepts[:3]:

            if isinstance(
                concept,
                dict
            ):

                value = (
                    concept.get("title")
                    or
                    concept.get("name")
                    or
                    concept.get("concept")
                )

            else:

                value = str(
                    concept
                )

            if value:

                result.append(
                    str(
                        value
                    ).strip()
                )

        return result

    # ==========================================================
    # RENDERER HINTS
    # ==========================================================

    def _renderer_hints(
        self,
        visual_type: str,
        intent: Dict[str, Any],
        selected: Dict[str, Any],
        density: str
    ) -> Dict[str, Any]:

        visual_type = self._normalize_visual_type(
            visual_type
        )

        return {
            "layout_hint": self._get_layout_hint(
                visual_type
            ),

            "orientation": self._get_orientation(
                visual_type
            ),

            "priority": visual_type,

            "item_count": self._get_item_count(
                visual_type,
                selected
            ),

            "max_items": self._get_max_items(
                visual_type
            ),

            "density": density,

            "max_title_words": 10,

            "max_body_words": (
                45
                if density == "low"
                else
                35
                if density == "medium"
                else
                25
            ),

            "emphasis": intent.get(
                "emphasis",
                "balanced"
            ),

            "allow_image": visual_type in [
                "hero",
                "focus",
                "case_study"
            ],

            "prefer_visual": True
        }

    # ==========================================================
    # LAYOUT HINT
    # ==========================================================

    def _get_layout_hint(
        self,
        visual_type: str
    ) -> str:

        mapping = {

            "hero": "hero",

            "focus": "focus",

            "concept": "focus",

            "cards": "cards",

            "feature_cards": "cards",

            "smart_cards": "cards",

            "comparison": "comparison",

            "comparison_table": "comparison",

            "workflow": "process",

            "vertical_process": "steps",

            "horizontal_process": "process",

            "timeline": "timeline",

            "chart": "grid",

            "kpi": "grid",

            "matrix": "grid",

            "architecture": "split",

            "architecture_diagram": "split",

            "case_study": "split",

            "faq": "cards",

            "pros_cons": "comparison"
        }

        return mapping.get(
            visual_type,
            "content"
        )

    # ==========================================================
    # ORIENTATION
    # ==========================================================

    def _get_orientation(
        self,
        visual_type: str
    ) -> str:

        horizontal = {
            "chart",
            "kpi",
            "timeline",
            "horizontal_process",
            "comparison"
        }

        if visual_type in horizontal:
            return "horizontal"

        return "vertical"

    # ==========================================================
    # MAX ITEMS
    # ==========================================================

    def _get_max_items(
        self,
        visual_type: str
    ) -> int:

        limits = {

            "hero": 3,

            "focus": 3,

            "cards": 6,

            "feature_cards": 6,

            "comparison": 5,

            "workflow": 6,

            "vertical_process": 7,

            "horizontal_process": 5,

            "timeline": 7,

            "chart": 6,

            "kpi": 4,

            "matrix": 6,

            "architecture": 8,

            "case_study": 3,

            "faq": 6,

            "pros_cons": 6
        }

        return limits.get(
            visual_type,
            5
        )

    # ==========================================================
    # ITEM COUNT
    # ==========================================================

    def _get_item_count(
        self,
        visual_type: str,
        selected: Dict[str, Any]
    ) -> int:

        mapping = {

            "hero": "concepts",

            "focus": "concepts",

            "cards": "concepts",

            "feature_cards": "concepts",

            "comparison": "comparison",

            "workflow": "process",

            "vertical_process": "process",

            "horizontal_process": "process",

            "timeline": "timeline",

            "chart": "statistics",

            "kpi": "statistics",

            "matrix": "concepts",

            "architecture": "components",

            "case_study": "case_studies",

            "faq": "faqs",

            "pros_cons": "pros_cons"
        }

        key = mapping.get(
            visual_type,
            "concepts"
        )

        value = selected.get(
            key,
            []
        )

        if isinstance(
            value,
            list
        ):
            return len(value)

        return 0

    # ==========================================================
    # DENSITY
    # ==========================================================

    def _visual_density(
        self,
        selected: Dict[str, Any]
    ) -> str:

        fields = [
            "concepts",
            "statistics",
            "examples",
            "process",
            "timeline",
            "comparison",
            "case_studies",
            "industry_applications"
        ]

        total = 0

        for field in fields:

            value = selected.get(
                field,
                []
            )

            if isinstance(
                value,
                list
            ):
                total += len(value)

        if total <= 2:
            return "low"

        if total <= 6:
            return "medium"

        return "high"

    # ==========================================================
    # IMAGE REQUIREMENTS
    # ==========================================================

    def _image_requirements(
        self,
        visual_type: str,
        plan: Dict[str, Any],
        selected: Dict[str, Any]
    ) -> Dict[str, Any]:

        visual_type = self._normalize_visual_type(
            visual_type
        )

        needs_image = visual_type in [
            "hero",
            "case_study"
        ]

        if visual_type == "focus":

            concepts = selected.get(
                "concepts",
                []
            )

            needs_image = (
                len(concepts) <= 2
            )

        slide_focus = (
            plan.get("slide_focus")
            or
            plan.get("headline")
            or
            plan.get("title")
            or
            "concept"
        )

        return {
            "needs_image": needs_image,

            "image_type": (
                f"professional visualization "
                f"of {slide_focus}"
                if needs_image
                else None
            ),

            "image_position": (
                "right"
                if needs_image
                else None
            ),

            "purpose": (
                "support_the_main_message"
                if needs_image
                else None
            ),

            "avoid_text_in_image": True
        }

    # ==========================================================
    # VISUAL PRIORITY
    # ==========================================================

    def _visual_priority(
        self,
        visual_type: str,
        selected: Dict[str, Any]
    ) -> str:

        if visual_type in [
            "chart",
            "workflow",
            "timeline",
            "comparison",
            "architecture"
        ]:
            return "high"

        if visual_type in [
            "cards",
            "case_study",
            "hero"
        ]:
            return "medium"

        return "balanced"

    # ==========================================================
    # NORMALIZE
    # ==========================================================

    def _normalize_visual_type(
        self,
        visual_type: Any
    ) -> str:

        if not visual_type:
            return "focus"

        value = str(
            visual_type
        ).strip().lower()

        aliases = {

            "process": "workflow",

            "flow": "workflow",

            "flowchart": "workflow",

            "diagram": "architecture",

            "architecture_diagram": "architecture",

            "card": "cards",

            "features": "cards",

            "feature_cards": "cards",

            "smart_cards": "cards",

            "comparison_table": "comparison",

            "metric": "chart",

            "metrics": "chart",

            "kpi": "chart",

            "image": "hero",

            "concept": "focus",

            "faq": "cards",

            "pros_cons": "comparison",

            "matrix": "chart"
        }

        return aliases.get(
            value,
            value
        )

    # ==========================================================
    # HELPERS
    # ==========================================================

    def _ensure_list(
        self,
        value: Any
    ) -> List[Any]:

        if isinstance(
            value,
            list
        ):
            return value

        if value is None:
            return []

        return [value]

    def _has_items(
        self,
        value: Any
    ) -> bool:

        if isinstance(
            value,
            list
        ):
            return len(value) > 0

        if isinstance(
            value,
            dict
        ):
            return len(value) > 0

        return bool(value)

    def _get_dimension(
        self,
        plan: Dict[str, Any],
        key: str,
        default: str
    ) -> str:

        dimensions = plan.get(
            "dimensions",
            {}
        )

        if isinstance(
            dimensions,
            dict
        ):

            value = dimensions.get(
                key
            )

            if value:
                return str(
                    value
                )

        value = plan.get(
            key
        )

        if value:
            return str(
                value
            )

        return default