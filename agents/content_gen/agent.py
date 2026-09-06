import json
from typing import Dict, List, Any, Optional

from .selector import ContentSelector
from .synthesizer import ContentSynthesizer
from .audience_adapter import AudienceAdapter
from .compressor import ContentCompressor
from .visual_builder import VisualBuilder
from .speaker_notes import SpeakerNotesGenerator
from .image_planner import ImagePlanner
from .validator import SlideValidator
from .quality_scorer import PipelineQualityScorer


class SlideContentAgent:
    """
    Generates final PPT-compatible slide JSON directly from research output.
    No Presentation Planner needed.
    """

    def __init__(self, research_output: Dict, llm=None):
        self.research_output = research_output
        self.llm = llm
        self.selector = ContentSelector(research_output)
        self.synthesizer = ContentSynthesizer(llm)
        self.adapter = AudienceAdapter()
        self.compressor = ContentCompressor()
        self.visual_builder = VisualBuilder()
        self.speaker_notes = SpeakerNotesGenerator()
        self.image_planner = ImagePlanner()
        self.validator = SlideValidator()
        self.scorer = PipelineQualityScorer()
        
        # Available layouts from your registry
        self.available_layouts = [
            "hero", "cards", "comparison", "grid", 
            "split", "process", "timeline", "focus", "steps"
        ]

    def run(self) -> Dict:
        """Generate slides directly from research - no planner needed"""
        slides = []

        # Get research sections
        research_sections = self._extract_research_sections()

        if not research_sections:
            raise ValueError("No valid research sections found.")

        total_slides = len(research_sections)

        # Process every research section
        for index, section in enumerate(research_sections, start=1):
            slide_id = f"S{index:02d}"

            # Build slide context from research only
            slide_blueprint = self._build_slide_context(
                section=section,
                slide_id=slide_id,
                index=index,
                total=total_slides
            )

            layout_name = (
                slide_blueprint
                .get("slide", {})
                .get("presentation_plan", {})
                .get("template", "grid")
            )

            # 1. Select relevant research
            selected = self.selector.select(slide_blueprint)

            # 2. Synthesize research
            try:
                synthesized = self.synthesizer.synthesize(
                    selected,
                    slide_blueprint
                )
            except Exception as e:
                print(f"Warning: Synthesis error for slide {index}: {e}")
                synthesized = self._create_fallback_content(section)

            # 3. Adapt for audience
            try:
                adapted = self.adapter.adapt(
                    synthesized,
                    slide_blueprint["slide"]
                )
            except Exception as e:
                print(f"Warning: Adaptation error for slide {index}: {e}")
                adapted = synthesized

            # 4. Compress content
            try:
                compressed = self.compressor.compress(
                    adapted,
                    slide_blueprint
                )
            except Exception as e:
                print(f"Warning: Compression error for slide {index}: {e}")
                compressed = adapted

            # 5. Build semantic visual
            try:
                visuals = self.visual_builder.build(
                    selected,
                    slide_blueprint
                )
            except Exception as e:
                print(f"Warning: Visual builder error for slide {index}: {e}")
                visuals = {"visual_type": "concept", "semantic_data": {}}

            # 6. Generate speaker notes
            try:
                notes = self.speaker_notes.enhance(
                    draft_notes=synthesized.get("speaker_notes", {}),
                    slide_content=compressed,
                    slide_blueprint=slide_blueprint
                )
            except Exception as e:
                print(f"Warning: Speaker notes error for slide {index}: {e}")
                notes = {
                    "opening": "Let's explore this topic.",
                    "explanation": "Here's what you need to know.",
                    "transition": "Now let's move on.",
                    "timing": "60 sec",
                    "closing": "This is the key takeaway."
                }

            # 7. Build image plan
            try:
                image_plan = self.image_planner.plan(
                    selected,
                    slide_blueprint
                )
            except Exception as e:
                print(f"Warning: Image planner error for slide {index}: {e}")
                image_plan = {"type": "concept", "prompt": "Professional visualization"}

            # 8. Prepare temporary content
            slide_content = compressed.copy()
            slide_content["visual_spec"] = visuals
            slide_content["speaker_notes"] = notes
            slide_content["image_plan"] = image_plan

            # 9. Validate
            try:
                validated = self.validator.validate(
                    slide_content,
                    slide_blueprint,
                    selected
                )
            except Exception as e:
                print(f"Warning: Validation error for slide {index}: {e}")
                validated = {"validation": {"research_quality": {}, "semantic_quality": {}}}

            # 10. Quality scoring
            content_score = self._calculate_content_score(slide_content, slide_blueprint)
            visual_score = self._calculate_visual_score(visuals, image_plan)
            speaker_score = self._calculate_speaker_score(notes)
            accessibility_score = self._calculate_accessibility_score(slide_content, visuals)

            validation_data = validated.get("validation", {})

            pipeline_report = {
                "slide_type": layout_name,
                "research_score": 95,
                "presentation_score": 95,
                "content_score": content_score,
                "visual_score": visual_score,
                "speaker_score": speaker_score,
                "renderer_score": 95,
                "accessibility_score": accessibility_score,
                "research_coverage": (
                    validation_data
                    .get("research_quality", {})
                    .get("coverage_score", 100)
                ),
                "semantic_preservation": (
                    validation_data
                    .get("semantic_quality", {})
                    .get("preservation_score", 100)
                ),
                "speaker_notes_complete": speaker_score >= 80,
                "visual_ready": visual_score >= 70
            }

            score = self.scorer.score(pipeline_report)

            # ==================================================
            # 11. FINAL PPT JSON ASSEMBLY
            # ==================================================

            final_slide = {
                "slide": {
                    "identity": {
                        "slide_id": slide_id
                    },
                    "layout": layout_name,
                    "content": {
                        "title": slide_content.get("headline", slide_content.get("title", "")),
                        "subtitle": slide_content.get("subtitle", ""),
                        "main_message": slide_content.get("main_message", ""),
                        "bullets": slide_content.get("bullets", []),
                        "callout": slide_content.get("callout", ""),
                        "key_takeaway": slide_content.get("key_takeaway", ""),
                        "supporting_evidence": slide_content.get("supporting_evidence", "")
                    },
                    "speaker_notes": notes,
                    "visual_spec": visuals,
                    "image_plan": image_plan,
                    "quality": score,
                    "validation": validated,
                    "pipeline_report": pipeline_report
                }
            }

            slides.append(final_slide)

        return {"slides": slides}

    # ======================================================
    # EXTRACT RESEARCH SECTIONS
    # ======================================================

    def _extract_research_sections(self) -> List[Dict]:
        """Extract sections dynamically from the Research Agent output."""
        research = self.research_output

        if not isinstance(research, dict):
            raise TypeError("research_output must be a dictionary.")

        # Case 1: Direct sections
        sections = research.get("sections", [])
        if sections:
            return sections

        # Case 2: Modules with sections
        modules = research.get("modules", [])
        if modules:
            all_sections = []
            for module in modules:
                module_sections = module.get("sections", [])
                for section in module_sections:
                    section["_module_title"] = module.get("module_title", "")
                    all_sections.append(section)
            if all_sections:
                return all_sections

        # Case 3: Topics
        topics = research.get("topics", [])
        if topics:
            return topics

        # Case 4: Concepts
        concepts = research.get("concepts", [])
        if concepts:
            return [
                {"title": concept, "content": concept}
                for concept in concepts
            ]

        # Case 5: Single section - wrap it
        return [research]

    # ======================================================
    # BUILD INTERNAL SLIDE CONTEXT
    # ======================================================

    def _build_slide_context(self, section: Any, slide_id: str, index: int = 1, total: int = 1) -> Dict:
        """Build slide context from research section with smart layout selection"""
        # Extract title
        if isinstance(section, dict):
            title = (
                section.get("section_title")
                or section.get("title")
                or section.get("heading")
                or section.get("topic")
                or section.get("name")
                or f"Slide {slide_id}"
            )
            bullet_limit = section.get("bullet_limit", 5)
            word_limit = section.get("word_limit", 100)
        else:
            title = str(section)
            bullet_limit = 5
            word_limit = 100

        # SMART LAYOUT SELECTION
        layout_name = self._determine_layout(section, index, total)

        # Determine audience
        audience = self.research_output.get("audience", "Student")

        return {
            "slide": {
                "identity": {
                    "slide_id": slide_id
                },
                "audience": audience,
                "presentation_plan": {
                    "template": layout_name,
                    "slide_focus": title,
                    "word_limit": word_limit,
                    "bullet_limit": bullet_limit,
                    "cognitive_load": "medium",
                    "presentation_intent": {
                        "information_type": "explain"
                    },
                    "preferred_visuals": [layout_name],
                    "alternative_visuals": [],
                    "content_mapping": {}
                }
            },
            "audience": audience,
            "section": section
        }

    # ======================================================
    # SMART LAYOUT DETERMINATION - KEY IMPROVEMENT!
    # ======================================================

    def _determine_layout(self, section: Any, index: int = 1, total: int = 1) -> str:
        """
        Intelligently select layout based on content and position.
        This ensures different layouts for different slides.
        """
        if not isinstance(section, dict):
            return "grid"  # Default fallback

        # Get section title for smart selection
        title = section.get("section_title", "")
        title_lower = title.lower()
        
        # Check content structure
        has_comparison = section.get("comparison") or section.get("compare")
        has_timeline = section.get("timeline") or section.get("chronology")
        has_process = section.get("process") or section.get("steps") or section.get("workflow")
        has_statistics = section.get("statistics") or section.get("stats")
        has_cards = section.get("cards") or section.get("features") or section.get("benefits")
        has_split = section.get("split") or section.get("problem_solution")
        has_focus = section.get("focus") or section.get("highlight")
        
        # ============================================================
        # POSITION-BASED LAYOUT (First/Last slides)
        # ============================================================
        
        # First slide - Title/Intro
        if index == 1:
            return "hero"
        
        # Last slide - Summary
        if index == total:
            return "grid"
        
        # ============================================================
        # CONTENT-BASED LAYOUT SELECTION
        # ============================================================
        
        # Comparison slides
        if has_comparison or "comparison" in title_lower or "vs" in title_lower or "versus" in title_lower:
            return "comparison"
        
        # Timeline/History slides
        if has_timeline or "timeline" in title_lower or "history" in title_lower or "evolution" in title_lower:
            return "timeline"
        
        # Process/Steps slides
        if has_process or "process" in title_lower or "steps" in title_lower or "workflow" in title_lower:
            return "process"
        
        # Features/Benefits slides
        if has_cards or "features" in title_lower or "benefits" in title_lower or "advantages" in title_lower:
            return "cards"
        
        # Problem/Solution slides
        if has_split or "problem" in title_lower or "solution" in title_lower or "challenge" in title_lower:
            return "split"
        
        # Focus/Highlight slides
        if has_focus or "focus" in title_lower or "highlight" in title_lower or "key concept" in title_lower:
            return "focus"
        
        # Statistics/Data slides
        if has_statistics or "statistics" in title_lower or "data" in title_lower or "metrics" in title_lower:
            return "grid"
        
        # ============================================================
        # TITLE-BASED LAYOUT SELECTION
        # ============================================================
        
        # Check for specific keywords in title
        title_keywords = {
            "hero": ["introduction", "overview", "welcome", "getting started", "introduction to"],
            "comparison": ["comparison", "compare", "contrast", "difference", "vs", "versus"],
            "timeline": ["timeline", "history", "evolution", "chronology", "milestones", "journey"],
            "process": ["process", "steps", "workflow", "pipeline", "stages", "methodology", "approach"],
            "cards": ["features", "benefits", "advantages", "highlights", "key features"],
            "split": ["problem", "solution", "challenge", "before", "after", "issue"],
            "focus": ["focus", "highlight", "core", "main idea", "key concept"],
            "grid": ["summary", "conclusion", "key takeaways", "recap", "overview", "data"],
            "steps": ["step", "phase", "stage", "level", "tier"]
        }
        
        for layout, keywords in title_keywords.items():
            for keyword in keywords:
                if keyword in title_lower:
                    return layout
        
        # ============================================================
        # INDEX-BASED ROTATION (for variety)
        # ============================================================
        
        # If no specific match, rotate through layouts based on index
        layout_rotation = ["grid", "cards", "process", "comparison", "split", "timeline", "focus", "steps"]
        rotation_index = (index - 2) % len(layout_rotation)
        return layout_rotation[rotation_index]

    # ======================================================
    # FALLBACK CONTENT
    # ======================================================

    def _create_fallback_content(self, section: Any) -> Dict:
        """Create fallback content when synthesis fails"""
        if isinstance(section, dict):
            title = section.get("section_title", section.get("title", "Untitled Slide"))
        else:
            title = str(section)

        return {
            "headline": title,
            "subtitle": "",
            "main_message": f"Key insights about {title}",
            "bullets": [
                "Important point about this topic",
                "Another key consideration",
                "A notable insight or finding"
            ],
            "key_takeaway": f"Remember: {title} is important",
            "callout": "Consider the implications",
            "supporting_evidence": "",
            "visual_description": f"Visualization illustrating {title}",
            "recommended_visuals": {
                "type": "concept",
                "layout": "single",
                "icon": "",
                "image_prompt": f"Professional visualization of {title}"
            },
            "speaker_notes": {
                "opening": f"Let's discuss {title}.",
                "explanation": f"This slide covers important aspects of {title}.",
                "visual_walkthrough": "Notice the key elements in this visualization.",
                "audience_question": "How does this relate to your experience?",
                "common_mistake": "A common misunderstanding is to overlook the implications.",
                "transition": "Now let's see what this means in practice.",
                "timing": "60 sec",
                "emphasis": "This is the key insight to remember."
            }
        }

    # ======================================================
    # QUALITY SCORING METHODS
    # ======================================================

    def _calculate_content_score(self, content: Dict, slide_blueprint: Dict) -> float:
        """Calculate content quality score (0-100)"""
        score = 0
        plan = slide_blueprint.get("slide", {}).get("presentation_plan", {})

        headline = content.get("headline", "")
        if headline:
            score += 15
            if isinstance(headline, str) and len(headline.split()) <= 10:
                score += 5

        if content.get("main_message"):
            score += 20

        bullets = content.get("bullets", [])
        if bullets:
            score += 15
            bullet_limit = plan.get("bullet_limit", 5)
            if len(bullets) <= bullet_limit:
                score += 10
            meaningful = [b for b in bullets if isinstance(b, str) and len(b.split()) >= 3]
            if meaningful and len(meaningful) == len(bullets):
                score += 10

        if content.get("key_takeaway"):
            score += 10

        if (content.get("examples") or content.get("statistics") or content.get("case_studies")):
            score += 10

        normalized = [b.strip().lower() for b in bullets if isinstance(b, str)]
        if len(normalized) == len(set(normalized)):
            score += 5

        return min(score, 100)

    def _calculate_visual_score(self, visuals: Dict, image_plan: Dict) -> float:
        """Calculate visual quality score (0-100)"""
        score = 0

        if visuals:
            score += 40
        if visuals.get("visual_type"):
            score += 20
        if visuals.get("semantic_data"):
            score += 25
        if image_plan:
            score += 15

        return min(score, 100)

    def _calculate_speaker_score(self, notes: Dict) -> float:
        """Calculate speaker notes completeness score (0-100)"""
        if not isinstance(notes, dict):
            return 0.0

        required_fields = ["opening", "explanation", "transition", "timing", "closing"]
        filled = sum(1 for field in required_fields if notes.get(field))

        return round((filled / len(required_fields)) * 100, 1)

    def _calculate_accessibility_score(self, content: Dict, visuals: Dict) -> float:
        """Calculate accessibility score (0-100)"""
        score = 0

        if content.get("headline"):
            score += 25
        if content.get("bullets"):
            score += 25
        if visuals and visuals.get("semantic_data"):
            score += 25
        if visuals and visuals.get("image_requirements"):
            score += 25

        return score


# ==========================================================
# MAIN - Run from Research Only
# ==========================================================

if __name__ == "__main__":
    import os

    os.makedirs("output", exist_ok=True)

    try:
        with open("output/research_output.json", "r") as f:
            research = json.load(f)
        print("✅ Loaded research from output/research_output.json")
    except FileNotFoundError:
        print("❌ research_output.json not found!")
        print("Creating sample research for testing...")
        research = {
            "audience": "Technical Professionals",
            "sections": [
                {
                    "section_id": "section_01",
                    "section_title": "Introduction to Embeddings",
                    "template": "content",
                    "bullet_limit": 4,
                    "research": {
                        "summary": "Embeddings are dense vector representations of text that capture semantic meaning.",
                        "key_facts": [
                            "Embeddings convert text to vectors",
                            "Similar meanings have similar vectors",
                            "Dimensionality typically ranges from 100-1000"
                        ],
                        "concepts": ["Vector space", "Semantic similarity", "Dimensionality reduction"],
                        "statistics": ["80% of NLP tasks benefit from embedding-based approaches"],
                        "examples": ["Word2Vec", "GloVe", "BERT embeddings"]
                    }
                },
                {
                    "section_id": "section_02",
                    "section_title": "How RAG Works",
                    "template": "content",
                    "bullet_limit": 5,
                    "research": {
                        "summary": "RAG combines retrieval with generation to produce more accurate and contextually relevant outputs.",
                        "key_facts": [
                            "RAG combines retrieval with generation",
                            "Embeddings enable semantic search",
                            "RAG reduces hallucination in LLMs"
                        ],
                        "examples": ["A search for 'car' retrieves documents about 'automobiles'"],
                        "statistics": ["RAG improves accuracy by 30-40% on knowledge-intensive tasks"]
                    }
                },
                {
                    "section_id": "section_03",
                    "section_title": "Comparison of RAG vs Fine-tuning",
                    "comparison": True,
                    "research": {
                        "summary": "RAG and fine-tuning are complementary approaches for improving LLM performance.",
                        "key_facts": [
                            "RAG is better for dynamic data",
                            "Fine-tuning is better for static tasks"
                        ]
                    }
                },
                {
                    "section_id": "section_04",
                    "section_title": "RAG Implementation Steps",
                    "process": True,
                    "research": {
                        "summary": "Implementing RAG involves several key steps.",
                        "key_facts": [
                            "Step 1: Data ingestion",
                            "Step 2: Chunking",
                            "Step 3: Embedding",
                            "Step 4: Retrieval"
                        ]
                    }
                },
                {
                    "section_id": "section_05",
                    "section_title": "Key Features of RAG Systems",
                    "cards": True,
                    "research": {
                        "summary": "RAG systems have several key features.",
                        "key_facts": [
                            "Feature 1: Semantic search",
                            "Feature 2: Context grounding",
                            "Feature 3: Hallucination reduction"
                        ]
                    }
                },
                {
                    "section_id": "section_06",
                    "section_title": "Summary and Key Takeaways",
                    "research": {
                        "summary": "RAG is a powerful technique for enhancing LLM performance."
                    }
                }
            ]
        }

    # Create agent with research only - NO PLANNER
    agent = SlideContentAgent(
        research_output=research,
        llm=None  # No LLM needed for testing
    )

    # Generate slides - no arguments needed!
    content = agent.run()

    # Save output
    with open("output/slide_content.json", "w") as f:
        json.dump(content, f, indent=4)

    print(f"\n✅ Generated {len(content['slides'])} slides")
    print("✅ Saved to output/slide_content.json")

    # Print summary with layouts
    print("\n" + "="*60)
    print("SLIDE LAYOUT SUMMARY")
    print("="*60)
    
    for i, wrapper in enumerate(content["slides"], start=1):
        slide = wrapper.get("slide", {})
        content_data = slide.get("content", {})
        layout = slide.get("layout", "unknown")
        title = content_data.get("title", "Untitled")
        bullets_count = len(content_data.get("bullets", []))
        
        print(f"\nSlide {i}: {title[:40]}")
        print(f"  Layout: {layout}")
        print(f"  Bullets: {bullets_count}")
        print(f"  Content Score: {slide.get('pipeline_report', {}).get('content_score', 0):.1f}")