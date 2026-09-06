import json
import re
from typing import Dict, Any, List, Optional


class ContentSynthesizer:
    """
    Synthesizes research into presentation content.
    Works with or without an LLM.
    """

    def __init__(self, llm=None):
        self.llm = llm
        self.last_quality_score = None

    def synthesize(self, selected: Dict, slide_blueprint: Dict) -> Dict:
        """
        Generate presentation content from selected research.
        If LLM is available, use it. Otherwise, use rule-based synthesis.
        """
        # Extract slide context
        slide = slide_blueprint.get("slide", {})
        plan = slide.get("presentation_plan", {})
        
        # Get constraints
        slide_focus = plan.get("slide_focus", "Untitled")
        bullet_limit = plan.get("bullet_limit", 5)
        
        # If LLM is available, use it
        if self.llm is not None:
            try:
                return self._synthesize_with_llm(selected, slide_blueprint)
            except Exception as e:
                print(f"LLM synthesis failed: {e}")
                # Fall through to rule-based
        
        # Rule-based synthesis (works without LLM)
        return self._synthesize_rule_based(selected, slide_focus, bullet_limit)

    def _synthesize_with_llm(self, selected: Dict, slide_blueprint: Dict) -> Dict:
        """Synthesize using LLM"""
        slide = slide_blueprint.get("slide", {})
        plan = slide.get("presentation_plan", {})
        slide_focus = plan.get("slide_focus", "Untitled")
        bullet_limit = plan.get("bullet_limit", 5)
        
        prompt = self._build_prompt(selected, slide_blueprint)
        
        response = self.llm.generate(
            system_prompt="You are a presentation content expert.",
            user_prompt=prompt,
            temperature=0.3,
            max_tokens=1200
        )
        
        raw = response.content if hasattr(response, "content") else str(response)
        
        content = self._safe_json(raw)
        content = self._normalize(content)
        content = self._repair(content, slide_blueprint)
        content = self._ensure_bullets(content, slide_focus, bullet_limit)
        
        return content

    def _synthesize_rule_based(self, selected: Dict, slide_focus: str, bullet_limit: int) -> Dict:
        """Rule-based synthesis with improved data extraction"""
        
        # ============================================================
        # IMPROVED DATA EXTRACTION - Get data from multiple sources
        # ============================================================
        
        summary = ""
        key_facts = []
        concepts = []
        examples = []
        statistics = []
        
        # Debug - see what we're getting
        print(f"\n📝 Synthesizing: {slide_focus}")
        
        # Method 1: Direct from selected
        if isinstance(selected, dict):
            summary = selected.get("summary", "")
            key_facts = selected.get("key_facts", [])
            concepts = selected.get("concepts", [])
            examples = selected.get("examples", [])
            statistics = selected.get("statistics", [])
            
            # Also check for these fields
            if not key_facts and "facts" in selected:
                key_facts = selected.get("facts", [])
            if not key_facts and "key_points" in selected:
                key_facts = selected.get("key_points", [])
        
        # Method 2: From research nested in selected
        if not key_facts and "research" in selected:
            research = selected.get("research", {})
            if isinstance(research, dict):
                if not summary:
                    summary = research.get("summary", "")
                key_facts = research.get("key_facts", []) or research.get("facts", [])
                concepts = research.get("concepts", [])
                statistics = research.get("statistics", [])
                examples = research.get("examples", [])
        
        # Method 3: From slide_blueprint's section
        if not key_facts and "section" in selected:
            section = selected.get("section", {})
            if isinstance(section, dict):
                research = section.get("research", {})
                if isinstance(research, dict):
                    if not summary:
                        summary = research.get("summary", "")
                    key_facts = research.get("key_facts", []) or research.get("facts", [])
                    concepts = research.get("concepts", [])
                    statistics = research.get("statistics", [])
                    examples = research.get("examples", [])
        
        # Method 4: If still empty, extract from any string values
        if not key_facts and not concepts:
            for key, value in selected.items():
                if isinstance(value, str) and len(value) > 20 and key not in ["summary", "section"]:
                    key_facts.append(value[:200])
                elif isinstance(value, list) and value:
                    for item in value[:3]:
                        if isinstance(item, str) and len(item) > 10:
                            key_facts.append(item[:200])
        
        # Method 5: ULTIMATE FALLBACK - Generate from slide_focus
        if not key_facts and not concepts and not statistics:
            print(f"   ⚠️ No data found! Generating from slide_focus: {slide_focus}")
            key_facts = [
                f"{slide_focus} is a key concept in this domain",
                f"Understanding {slide_focus} enables better outcomes",
                f"{slide_focus} has important practical applications",
                f"Mastering {slide_focus} requires systematic approach"
            ]
            summary = f"This slide covers key aspects of {slide_focus}."
            concepts = [slide_focus, "Core Concepts", "Applications"]
        
        print(f"   📊 Found: {len(key_facts)} facts, {len(concepts)} concepts, {len(statistics)} stats")
        
        # ============================================================
        # BUILD HEADLINE
        # ============================================================
        headline = slide_focus if slide_focus else "Key Insights"
        if len(headline.split()) > 8:
            headline = " ".join(headline.split()[:8])
        
        # ============================================================
        # BUILD MAIN MESSAGE
        # ============================================================
        if summary:
            main_message = summary.split(".")[0][:150]
        elif key_facts:
            main_message = str(key_facts[0])[:150]
        else:
            main_message = f"Understanding {headline} is essential for success in this area."
        
        # ============================================================
        # BUILD BULLETS - ALWAYS GENERATE!
        # ============================================================
        bullets = []
        
        # Add key facts as bullets
        for fact in key_facts[:bullet_limit]:
            if fact and str(fact).strip():
                cleaned = self._clean_bullet(str(fact))
                if cleaned and len(cleaned) > 5:
                    bullets.append(cleaned)
        
        # Add statistics as bullets
        if len(bullets) < bullet_limit and statistics:
            for stat in statistics[:bullet_limit - len(bullets)]:
                if stat and str(stat).strip():
                    cleaned = self._clean_bullet(str(stat))
                    if cleaned and len(cleaned) > 5:
                        bullets.append(cleaned)
        
        # Add concepts as bullets
        if len(bullets) < bullet_limit and concepts:
            for concept in concepts[:bullet_limit - len(bullets)]:
                if concept and str(concept).strip():
                    cleaned = self._clean_bullet(str(concept))
                    if cleaned and len(cleaned) > 5:
                        bullets.append(cleaned)
        
        # Add examples as bullets
        if len(bullets) < bullet_limit and examples:
            for example in examples[:bullet_limit - len(bullets)]:
                if example and str(example).strip():
                    cleaned = self._clean_bullet(f"Example: {example}")
                    if cleaned and len(cleaned) > 5:
                        bullets.append(cleaned)
        
        # FINAL FALLBACK - Ensure we have bullets
        while len(bullets) < min(bullet_limit, 4):
            fallbacks = [
                f"Key insight about {headline}",
                f"Understanding {headline} drives innovation",
                f"Practical applications of {headline} are significant",
                f"Mastering {headline} requires systematic approach"
            ]
            for fb in fallbacks:
                if len(bullets) < min(bullet_limit, 4):
                    bullets.append(fb)
                else:
                    break
        
        # Limit bullets
        bullets = bullets[:bullet_limit]
        
        print(f"   ✅ Generated {len(bullets)} bullets")
        
        # ============================================================
        # BUILD KEY TAKEAWAY
        # ============================================================
        if key_facts:
            takeaway = str(key_facts[0])[:100]
        elif statistics:
            takeaway = str(statistics[0])[:100]
        else:
            takeaway = f"The key takeaway is understanding {headline}"
        
        # ============================================================
        # BUILD CALLOUT
        # ============================================================
        if statistics:
            callout = str(statistics[0])[:80]
        elif examples:
            callout = f"Example: {str(examples[0])[:80]}"
        elif key_facts:
            callout = str(key_facts[0])[:80]
        else:
            callout = f"Consider the implications of {headline}"
        
        # ============================================================
        # BUILD SUPPORTING EVIDENCE
        # ============================================================
        if statistics:
            evidence = str(statistics[0])
        elif examples:
            evidence = str(examples[0])
        elif key_facts:
            evidence = str(key_facts[0])
        else:
            evidence = f"Research supports the importance of {headline}"
        
        # ============================================================
        # BUILD SPEAKER NOTES
        # ============================================================
        speaker_notes = {
            "opening": f"Let's explore {headline}.",
            "explanation": f"This topic covers important aspects of {headline}.",
            "visual_walkthrough": "Notice the key elements in this visualization.",
            "audience_question": "How does this relate to your experience?",
            "common_mistake": "A common misunderstanding is to overlook these implications.",
            "transition": "Now let's explore what this means in practice.",
            "timing": "60-90 seconds",
            "emphasis": takeaway
        }
        
        return {
            "headline": headline,
            "subtitle": "",
            "main_message": main_message,
            "bullets": bullets,
            "key_takeaway": takeaway,
            "callout": callout,
            "supporting_evidence": evidence,
            "visual_description": f"Visualization illustrating {headline}",
            "recommended_visuals": {
                "type": "concept",
                "layout": "single",
                "icon": "",
                "image_prompt": f"Professional visualization of {headline}"
            },
            "speaker_notes": speaker_notes
        }

    def _clean_bullet(self, text: str) -> str:
        """Clean bullet text - remove markdown and trim"""
        if not text:
            return ""
        
        text = str(text).strip()
        
        # Remove bullet symbols
        for char in ["•", "-", "*", "–", "—", "·", "●", "○"]:
            if text.startswith(char):
                text = text[1:].strip()
        
        # Remove common prefixes
        for prefix in ["Key Fact:", "Fact:", "Concept:", "Example:", "Statistic:", "Key Insight:"]:
            if text.startswith(prefix):
                text = text[len(prefix):].strip()
        
        # Remove quotes if present
        if text.startswith('"') and text.endswith('"'):
            text = text[1:-1]
        
        # Capitalize first letter
        if text and len(text) > 0:
            text = text[0].upper() + text[1:]
        
        # Ensure minimum length
        if len(text) < 3:
            return ""
        
        return text

    def _generate_fallback_bullets(self, headline: str, key_facts: list, concepts: list, 
                                   statistics: list, examples: list, limit: int) -> List[str]:
        """Generate smart fallback bullets"""
        bullets = []
        
        # Use key facts
        for fact in key_facts[:limit]:
            if fact and str(fact).strip():
                cleaned = self._clean_bullet(str(fact))
                if cleaned:
                    bullets.append(cleaned)
        
        # Use statistics
        for stat in statistics[:limit - len(bullets)]:
            if stat and str(stat).strip():
                cleaned = self._clean_bullet(str(stat))
                if cleaned:
                    bullets.append(cleaned)
        
        # Use concepts
        for concept in concepts[:limit - len(bullets)]:
            if concept and str(concept).strip():
                cleaned = self._clean_bullet(str(concept))
                if cleaned:
                    bullets.append(cleaned)
        
        # Use examples
        for example in examples[:limit - len(bullets)]:
            if example and str(example).strip():
                cleaned = self._clean_bullet(f"Example: {example}")
                if cleaned:
                    bullets.append(cleaned)
        
        # Final fallback
        while len(bullets) < limit:
            default_bullets = [
                f"Understanding {headline} is crucial for success",
                f"Key principles of {headline} drive innovation",
                f"Real-world applications of {headline} are transformative",
                f"Mastering {headline} requires practice and insight",
                f"The future of {headline} depends on adaptation"
            ]
            for bullet in default_bullets:
                if len(bullets) < limit:
                    bullets.append(bullet)
                else:
                    break
        
        return bullets[:limit]

    def _ensure_bullets(self, content: Dict, slide_focus: str, bullet_limit: int) -> Dict:
        """Ensure bullets exist even if LLM didn't generate them"""
        bullets = content.get("bullets", [])
        
        if not bullets or len(bullets) == 0:
            new_bullets = []
            
            # Use main message
            main_msg = content.get("main_message", "")
            if main_msg and len(main_msg) > 20:
                new_bullets.append(main_msg[:100])
            
            # Use key takeaway
            takeaway = content.get("key_takeaway", "")
            if takeaway and len(takeaway) > 10:
                new_bullets.append(takeaway[:100])
            
            # Use callout
            callout = content.get("callout", "")
            if callout and len(callout) > 10:
                new_bullets.append(callout[:100])
            
            # Fallback
            if not new_bullets:
                new_bullets = [
                    f"Key insight about {slide_focus}",
                    f"Important aspect of {slide_focus}",
                    f"Practical application of {slide_focus}",
                    f"Understanding {slide_focus} drives results"
                ]
            
            content["bullets"] = new_bullets[:bullet_limit]
        
        # Ensure main_message exists
        if not content.get("main_message"):
            if content.get("key_takeaway"):
                content["main_message"] = content["key_takeaway"]
            elif content.get("bullets"):
                content["main_message"] = content["bullets"][0]
            else:
                content["main_message"] = f"Understanding {slide_focus}"
        
        return content

    def _build_prompt(self, selected: Dict, slide_blueprint: Dict) -> str:
        """Build prompt for LLM"""
        slide = slide_blueprint.get("slide", {})
        plan = slide.get("presentation_plan", {})
        
        bullet_limit = plan.get("bullet_limit", 5)
        slide_focus = plan.get("slide_focus", "")
        
        research_text = json.dumps(selected, indent=2)
        
        return f"""
Slide Topic: {slide_focus}
Bullet Limit: {bullet_limit}

Research Data:
{research_text}

Generate presentation content in JSON format with:
- headline (max 8 words)
- subtitle (max 15 words)
- main_message (one sentence)
- bullets (list of {bullet_limit} bullet points)
- key_takeaway (max 12 words)
- callout (surprising insight)
- supporting_evidence (statistic or example)
- visual_description
- speaker_notes (opening, explanation, visual_walkthrough, audience_question, common_mistake, transition)
"""

    def _safe_json(self, text: str) -> Dict:
        """Parse JSON safely"""
        text = text.strip()
        
        text = re.sub(r"```json", "", text, flags=re.IGNORECASE)
        text = re.sub(r"```", "", text)
        
        start = text.find("{")
        end = text.rfind("}")
        
        if start != -1 and end != -1:
            text = text[start:end + 1]
        
        try:
            return json.loads(text)
        except Exception:
            return {}

    def _normalize(self, content: Dict) -> Dict:
        """Normalize content fields"""
        default = {
            "headline": "",
            "subtitle": "",
            "main_message": "",
            "bullets": [],
            "key_takeaway": "",
            "callout": "",
            "supporting_evidence": "",
            "visual_description": "",
            "recommended_visuals": {"type": "concept", "layout": "single", "icon": "", "image_prompt": ""},
            "speaker_notes": {
                "opening": "",
                "explanation": "",
                "visual_walkthrough": "",
                "audience_question": "",
                "common_mistake": "",
                "transition": "",
                "timing": "60 sec",
                "emphasis": ""
            }
        }
        
        for key, value in default.items():
            if key not in content:
                content[key] = value
        
        return content

    def _repair(self, content: Dict, slide_blueprint: Dict) -> Dict:
        """Repair and validate content"""
        plan = slide_blueprint.get("slide", {}).get("presentation_plan", {})
        bullet_limit = plan.get("bullet_limit", 5)
        slide_focus = plan.get("slide_focus", "Untitled")
        
        if not isinstance(content.get("bullets"), list):
            content["bullets"] = []
        
        content["bullets"] = content["bullets"][:bullet_limit]
        
        if not content.get("headline"):
            content["headline"] = slide_focus
        
        if not content.get("main_message"):
            if content.get("key_takeaway"):
                content["main_message"] = content["key_takeaway"]
            elif content.get("bullets"):
                content["main_message"] = content["bullets"][0]
            else:
                content["main_message"] = f"Understanding {slide_focus}"
        
        if not content.get("key_takeaway"):
            if content.get("main_message"):
                content["key_takeaway"] = content["main_message"]
            elif content.get("bullets"):
                content["key_takeaway"] = content["bullets"][0]
            else:
                content["key_takeaway"] = f"The key takeaway is {slide_focus}"
        
        return content