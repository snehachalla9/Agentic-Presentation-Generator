
import json
from typing import Any, Dict, List, Optional


class ContentSelector:
    """
    Selects the most relevant research content for each slide.
    """

    def __init__(self, research_output: Dict):
        self.research_index = {}
        self._build_index(research_output)

    def _build_index(self, research_output: Dict):
        """Build research index from various formats"""
        # Case 1: Direct sections format
        if "sections" in research_output:
            for section in research_output.get("sections", []):
                module_id = section.get("module_id", "default_module")
                section_id = section.get("section_id", "default_section")
                research = section.get("research", {})
                self.research_index[(module_id, section_id)] = research
                # Also store under default key for fallback
                if not self.research_index.get(("default_module", "default_section")):
                    self.research_index[("default_module", "default_section")] = research

        # Case 2: Modules format
        modules = research_output.get("modules", [])
        for module in modules:
            module_id = (
                module.get("id")
                or module.get("module_id")
                or "default_module"
            )
            
            for section in module.get("sections", []):
                section_id = section.get("section_id", "default_section")
                research = section.get("research", {})
                self.research_index[(module_id, section_id)] = research
                # Also store under default key for fallback
                if not self.research_index.get(("default_module", "default_section")):
                    self.research_index[("default_module", "default_section")] = research

        # Case 3: If no structured data, store the whole thing
        if not self.research_index:
            self.research_index[("default_module", "default_section")] = research_output

    # ----------------------------------------------------
    # Main Selection Entry
    # ----------------------------------------------------
    def select(self, slide_blueprint: Dict) -> Dict:
        slide = slide_blueprint.get("slide", {})
        identity = slide.get("identity", {})
        plan = slide.get("presentation_plan", {})

        # FIXED: Safe access with fallbacks
        module_id = identity.get("module_id", "default_module")
        section_id = identity.get("section_id", "default_section")

        # Try to get research from index
        research = self.research_index.get((module_id, section_id))
        
        # If not found, try default key
        if not research:
            research = self.research_index.get(("default_module", "default_section"), {})
        
        # If still no research, try from slide_blueprint directly
        if not research:
            research = slide_blueprint.get("research", {})

        if not isinstance(research, dict):
            research = {}

        objective = (
            plan.get("learning_objective")
            or plan.get("headline")
            or plan.get("slide_focus")
            or plan.get("objective")
            or ""
        )

        importance = plan.get("importance", "Medium")
        communication_goal = plan.get("communication_goal", {})
        visual_intent = plan.get("presentation_intent", {})

        selected = {
            "summary": self._normalize_text(research.get("summary", "")),
            "concepts": self._rank_items(
                research.get("concepts", []),
                objective,
                importance
            )[:3],
            "key_facts": self._rank_items(
                research.get("key_facts", []),
                objective,
                importance
            )[:5],
            "examples": self._rank_items(
                research.get("examples", []),
                objective,
                importance
            )[:3],
            "statistics": self._rank_items(
                research.get("statistics", []),
                objective,
                importance,
                quantitative=True
            )[:3],
            "case_studies": self._rank_items(
                research.get("case_studies", []),
                objective,
                importance
            )[:2],
            "industry_applications": self._rank_items(
                research.get("industry_applications", []),
                objective,
                importance
            )[:3],
            "trends": self._rank_items(
                research.get("trends", []),
                objective,
                importance
            )[:2],
            "misconceptions": self._rank_items(
                research.get("misconceptions", []),
                objective,
                importance
            )[:2],
            "references": self._rank_sources(
                research.get("references", [])
            )[:3],
            "sources": self._rank_sources(
                research.get("sources", [])
            )[:3],
            "communication_goal": communication_goal,
            "visual_intent": visual_intent
        }

        return self._validate_selected(selected)

    # ----------------------------------------------------
    # Normalize text safely
    # ----------------------------------------------------
    def _normalize_text(self, value: Any) -> str:
        if value is None:
            return ""

        if isinstance(value, str):
            return value.strip()

        if isinstance(value, list):
            return "\n".join(str(v) for v in value if v)

        if isinstance(value, dict):
            return (
                value.get("text")
                or value.get("summary")
                or value.get("description")
                or json.dumps(value, ensure_ascii=False)
            )

        return str(value)

    # ----------------------------------------------------
    # Rank research items
    # ----------------------------------------------------
    def _rank_items(
        self,
        items: List[Any],
        objective: str,
        importance: str,
        quantitative: bool = False
    ) -> List[str]:
        if not items:
            return []

        objective = str(objective or "")
        importance = str(importance or "")

        objective_words = {
            word.casefold()
            for word in objective.split()
            if len(word) > 2
        }

        ranked = []
        seen = set()

        for item in items:
            text = self._extract_text(item)

            if not text:
                continue

            key = text.casefold()
            if key in seen:
                continue

            seen.add(key)
            score = 0.0
            lower = text.casefold()

            # Objective keyword relevance
            if objective_words:
                matches = sum(1 for word in objective_words if word in lower)
                score += (matches / len(objective_words)) * 0.40

            # Importance weighting
            importance_lower = importance.casefold()
            if importance_lower == "high":
                score += 0.25
            elif importance_lower == "medium":
                score += 0.18
            else:
                score += 0.10

            # Prefer quantitative evidence
            if quantitative:
                if any(ch.isdigit() for ch in text):
                    score += 0.20
                if "%" in text:
                    score += 0.08
                if any(
                    unit in lower
                    for unit in [
                        "million", "billion", "accuracy", "precision",
                        "recall", "f1", "auc", "score", "rate"
                    ]
                ):
                    score += 0.08

            # Informative content bonus
            words = text.split()
            if 8 <= len(words) <= 25:
                score += 0.10
            elif len(words) > 25:
                score += 0.05

            # Research quality bonus
            if any(
                token in lower
                for token in [
                    "study", "paper", "research", "journal", "ieee",
                    "nature", "acm", "arxiv", "science", "report"
                ]
            ):
                score += 0.10

            # Example bonus
            if any(
                token in lower
                for token in [
                    "example", "case study", "application",
                    "used in", "for instance", "e.g."
                ]
            ):
                score += 0.05

            ranked.append((round(score, 4), text))

        ranked.sort(key=lambda x: x[0], reverse=True)
        return [item for _, item in ranked]

    # ----------------------------------------------------
    # Convert any research item to readable text
    # ----------------------------------------------------
    def _extract_text(self, item: Any) -> str:
        if item is None:
            return ""

        if isinstance(item, str):
            return item.strip()

        if isinstance(item, (int, float)):
            return str(item)

        if isinstance(item, dict):
            for field in [
                "text", "value", "summary", "description",
                "title", "statement", "fact", "content", "name"
            ]:
                value = item.get(field)
                if value:
                    return str(value)
            return json.dumps(item, ensure_ascii=False)

        if isinstance(item, list):
            return " ".join(str(x) for x in item if x)

        return str(item)

    # ----------------------------------------------------
    # Rank References / Sources
    # ----------------------------------------------------
    def _rank_sources(self, sources: List[Any]) -> List[str]:
        if not sources:
            return []

        priority_domains = {
            "ieee": 1.0,
            "acm": 1.0,
            "nature": 1.0,
            "science": 0.9,
            "springer": 0.9,
            "arxiv": 0.8,
            "gov": 0.8,
            "edu": 0.8,
            "nih": 0.8,
            "who": 0.8,
            "microsoft": 0.6,
            "google": 0.6,
            "openai": 0.6,
            "ibm": 0.6,
            "docs": 0.5
        }

        ranked = []
        seen = set()

        for src in sources:
            src_text = self._normalize_source(src)

            if not src_text:
                continue

            key = src_text.casefold()
            if key in seen:
                continue

            seen.add(key)
            score = 0.0
            lower = src_text.casefold()

            for domain, weight in priority_domains.items():
                if domain in lower:
                    score += weight

            if "http" in lower:
                score += 0.15

            if "doi" in lower:
                score += 0.25

            if len(src_text) > 40:
                score += 0.05

            ranked.append((score, src_text))

        ranked.sort(key=lambda x: x[0], reverse=True)
        return [source for _, source in ranked]

    # ----------------------------------------------------
    # Normalize Source
    # ----------------------------------------------------
    def _normalize_source(self, source: Any) -> str:
        if source is None:
            return ""

        if isinstance(source, str):
            return source.strip()

        if isinstance(source, dict):
            return (
                source.get("citation")
                or source.get("title")
                or source.get("url")
                or source.get("source")
                or source.get("name")
                or json.dumps(source, ensure_ascii=False)
            )

        return str(source)

    # ----------------------------------------------------
    # Validate Selected Content
    # ----------------------------------------------------
    def _validate_selected(self, selected: Dict) -> Dict:
        required = [
            "summary", "concepts", "key_facts", "examples",
            "statistics", "case_studies", "industry_applications",
            "trends", "misconceptions", "references", "sources",
            "communication_goal", "visual_intent"
        ]

        for key in required:
            if key not in selected:
                if key == "summary":
                    selected[key] = ""
                else:
                    selected[key] = []

        return selected