"""
Researcher Agent - Planner V4 Integration (v4.2)
Production-ready: enriches Planner sections with structured research blocks
"""

import json
import os
import re
from typing import Dict, Any, List, Optional
from datetime import datetime

try:
    from .config import ResearchConfig
except ImportError:
    class ResearchConfig:
        def __init__(self):
            self.use_llm = False
            self.llm_provider = "groq"
            self.max_sources = 3
            self.max_categories = 6


class ResearcherAgent:
    """Researcher Agent: enriches Planner sections with structured research blocks"""

    def __init__(self, config: Optional[ResearchConfig] = None, llm_gateway=None):
        self.config = config or ResearchConfig()
        self.llm = llm_gateway

        if self.config.use_llm and self.llm is None:
            try:
                from agents.llm_gateway import LLMGateway
                self.llm = LLMGateway()
            except Exception as e:
                print(f"⚠️ Shared gateway fallback failed: {e}")
    def research_from_planner(self, planner_json: Dict[str, Any]) -> Dict[str, Any]:
        topic = planner_json.get("topic", "Unknown")
        modules = planner_json.get("modules", [])

        enriched_modules = []
        for module in modules:
            enriched_sections = []
            for section in module.get("sections", []):
                query_context = self._build_query_context(topic, module, section)
                results = self._search_topic(query_context)
                research_block = self._synthesize_research(topic, module, section, results)
                enriched_sections.append({**section, "research": research_block})
            enriched_modules.append({**module, "sections": enriched_sections})

        planner_json["modules"] = enriched_modules
        planner_json["research_metadata"] = {
            "version": "1.2",
            "status": "complete",
            "total_modules": len(enriched_modules),
            "researched_at": datetime.now().isoformat(),
            "format": "research_blocks"
        }

        os.makedirs("output", exist_ok=True)
        with open("output/research_output.json", "w", encoding="utf-8") as f:
            json.dump(planner_json, f, indent=4)

        print(f"✅ Enriched {len(enriched_modules)} modules with research")
        return planner_json

    def _build_query_context(self, topic: str, module: Dict, section: Dict) -> str:
        parts = [
            topic,
            module.get("title", ""),
            section.get("heading", ""),
            "definition",
            "examples",
            "applications",
            "statistics",
            "case study",
            "latest trends",
            "best practices",
            "workflow",
            " ".join(section.get("concepts", [])),
            " ".join(section.get("questions", []))
        ]
        return " ".join([p for p in parts if p]).strip()

    def _search_topic(self, query: str) -> List[Dict]:
        results = []
        try:
            from .services.tavily_service import tavily_search
            results += tavily_search(query, max_results=self.config.max_sources)
            for r in results: r['source_type'] = 'tavily'
        except Exception:
            pass

        try:
            from .services.serper_service import serper_search
            serper_results = serper_search(query, max_results=self.config.max_sources)
            for r in serper_results: r['source_type'] = 'serper'
            results += serper_results
        except Exception:
            pass

        try:
            from .services.duckduckgo_service import duckduckgo_search
            ddg_results = duckduckgo_search(query, max_results=self.config.max_sources)
            for r in ddg_results: r['source_type'] = 'duckduckgo'
            results += ddg_results
        except Exception:
            pass

        # Deduplicate by URL
        seen = set()
        deduped = []
        for r in results:
            url = r.get("url", "")
            if url not in seen:
                deduped.append(r)
                seen.add(url)

        PRIORITY = [
            "nature.com","science.org","ieee.org","acm.org","arxiv.org",
            "springer.com","sciencedirect.com","nih.gov",".gov",".edu",
            "docs.","openai.com","huggingface.co","tensorflow.org","pytorch.org","wikipedia.org"
        ]
        ranked = sorted(deduped, key=lambda r: self._rank_source(r.get("url", ""), PRIORITY))
        return ranked[:5]

    def _rank_source(self, url: str, priority_list: List[str]) -> int:
        for i, domain in enumerate(priority_list):
            if domain in url:
                return i
        return len(priority_list)

    def _synthesize_research(self, topic: str, module: Dict, section: Dict, results: List[Dict]) -> Dict[str, Any]:
        MAX_CHARS_PER_SOURCE = 600
        MAX_INPUT = 4000

        snippets = [(r.get("content") or r.get("snippet") or "")[:MAX_CHARS_PER_SOURCE] for r in results]
        combined_text = "\n\n".join(snippets)[:MAX_INPUT]

        raw_sources = [{
            "title": r.get("title", "No Title"),
            "url": r.get("url", ""),
            "snippet": (r.get("content", r.get("snippet", "")) or "")[:300],
            "source_type": r.get("source_type", "unknown")
        } for r in results]

        research = {
            "summary": "",
            "problem": "",
            "background": "",
            "solution": "",
            "key_facts": [],
            "concepts": [],
            "examples": [],
            "case_studies": [],
            "statistics": [],
            "trends": [],
            "industry_applications": [],
            "misconceptions": [],
            "workflow": [],
            "analogy": "",
            "key_takeaway": "",
            "references": [],
            "confidence": 0.5 if results else 0.0,
            "raw_sources": raw_sources
        }

        if self.llm and combined_text:
            system_prompt = """
You are an expert Research Scientist and Technical Educator.

Generate accurate, structured research using only the provided sources.

Never invent facts.

Merge duplicate information.

Keep explanations concise and presentation-ready.

Return valid JSON only.
"""
            user_prompt = f"""
Generate structured research.

Requirements:
- concise
- technically accurate
- educational
- no repetition
- practical examples
- statistics when available
- return JSON only

Schema:
{{
  "summary":"",
  "problem":"",
  "background":"",
  "solution":"",
  "key_facts":[],
  "concepts":[],
  "examples":[],
  "case_studies":[],
  "statistics":[],
  "trends":[],
  "industry_applications":[],
  "misconceptions":[],
  "workflow":[],
  "analogy":"",
  "key_takeaway":"",
  "references":[],
  "confidence":0.0
}}

Sources:
{combined_text}
"""
            try:
                structured_json = self.llm.generate(
                    system_prompt=system_prompt,
                    user_prompt=user_prompt,
                    temperature=0.2,
                    max_tokens=1200,
                )
                data = self._safe_json_loads(structured_json)
                if isinstance(data, dict):
                    # Validation
                    if not isinstance(data.get("key_facts"), list):
                        data["key_facts"] = []
                    if not isinstance(data.get("examples"), list):
                        data["examples"] = []
                    if not data.get("summary"):
                        data["summary"] = "Summary unavailable."
                    if len(data["summary"]) < 40:
                        print("⚠️ Summary too short")

                    research.update(data)
                    research["raw_sources"] = raw_sources

                    # Smarter confidence
                    confidence = 0.5
                    if len(results) >= 3: confidence += 0.2
                    if data.get("statistics"): confidence += 0.1
                    if data.get("case_studies"): confidence += 0.1
                    if data.get("references"): confidence += 0.1
                    research["confidence"] = min(confidence, 0.95)
            except Exception as e:
                print(f"⚠️ LLM synthesis failed: {e}")

        return research

    def _safe_json_loads(self, text: str) -> Dict[str, Any]:
        """Clean and parse JSON safely"""
        try:
            cleaned = text.strip()
            match = re.search(r"(\{[\s\S]*\}|\[[\s\S]*\])", cleaned)



            if match:
                return json.loads(match.group())
            return {}
        except Exception:
            return {}

    def _get_fallback_categories(self, topic: str) -> Dict:
        return {
            "Definition": {"questions": [f"What is {topic}?"]},
            "Applications": {"questions": [f"How is {topic} applied?"]},
            "Theory": {"questions": [f"What are the key principles of {topic}?"]},
            "Challenges": {"questions": [f"What are the main challenges in {topic}?"]},
            "Solutions": {"questions": [f"How can these challenges be addressed?"]},
            "Best Practices": {"questions": [f"What are best practices for {topic}?"]},
            "Trends": {"questions": [f"What are the latest trends in {topic}?"]}
        }


# Convenience functions
def research_from_planner(planner_json: Dict[str, Any]) -> Dict[str, Any]:
    agent = ResearcherAgent()
    return agent.research_from_planner(planner_json)


def research_optimized(planner_json: Dict[str, Any]) -> Dict[str, Any]:
    return research_from_planner(planner_json)


if __name__ == "__main__":
    test_planner = {
        "topic": "overfitting in machine learning",
        "modules": [
            {
                "module_id": "M1",
                "title": "Foundations",
                "sections": [
                    {
                        "section_id": "S1",
                        "heading": "Definition",
                        "concepts": ["Overfitting"],
                        "objectives": ["Explain overfitting"],
                        "questions": ["What is overfitting?"]
                    }
                ]
            }
        ]
    }

    agent = ResearcherAgent()
    enriched = agent.research_from_planner(test_planner)

    print(json.dumps(enriched, indent=4))
