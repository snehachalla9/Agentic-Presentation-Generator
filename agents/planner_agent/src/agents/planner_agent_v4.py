"""
Planner Agent V4 - FIXED VERSION (No 413 Error)
- Reduced prompt sizes
- Split curriculum generation into 2 calls
- Lower max_tokens to 2500
- Simplified schemas
- Enhanced intent extraction with topic/scope/technology separation
"""

import json
import os
import re
from datetime import datetime
from typing import List, Dict, Any, Optional, Tuple
from dataclasses import dataclass, field, asdict
from enum import Enum
from groq import Groq
from dotenv import load_dotenv

# ============================================================================
# PROMPTS - SIMPLIFIED (Reduced by 70%)
# ============================================================================

INTENT_ANALYSIS_PROMPT = """You are an expert curriculum planning assistant.

Analyze the user's request and extract the educational intent.

Return ONLY valid JSON.

{{
  "scope": "",
  "technology_or_context": "",
  "domain": "",
  "audience_type": "",
  "duration": 60,
  "difficulty": "",
  "purpose": "",
  "constraints": []
}}

Rules:

1. topic = the actual subject being taught.
2. scope = the specific focus or sub-area.
3. technology_or_context = language, framework, platform, disease, country, etc.
4. Never replace the topic with the technology.
5. If the request already contains a specific topic, preserve it.

Examples

Input:
OOPs in Java

Output:
{{
 "topic":"Object-Oriented Programming",
 "scope":"Classes, Objects, Inheritance, Polymorphism, Encapsulation, Abstraction",
 "technology_or_context":"Java",
 "domain":"Programming"
}}

Input:
CNN for Medical Imaging

Output:
{{
 "topic":"Convolutional Neural Networks",
 "scope":"Medical Image Classification",
 "technology_or_context":"Medical Imaging",
 "domain":"AI_ML"
}}

Input:
Diabetes

Output:
{{
 "topic":"Diabetes",
 "scope":"Complete Disease Overview",
 "technology_or_context":"",
 "domain":"Medicine"
}}

Input:
Sorting Algorithms in Python

Output:
{{
 "topic":"Sorting Algorithms",
 "scope":"Implementation and Analysis",
 "technology_or_context":"Python",
 "domain":"Programming"
}}

Input:
French Revolution

Output:
{{
 "topic":"French Revolution",
 "scope":"Historical Events",
 "technology_or_context":"",
 "domain":"History"
}}

Request: {user_input}"""

CURRICULUM_PLANNING_PROMPT = """Create a detailed curriculum for:
Topic: {topic}
Scope: {scope}
Technology/Context: {technology}
Domain: {domain}
Audience: {audience_type}
Difficulty: {difficulty}

Generate ONLY modules relevant to the topic and scope.
Do NOT expand into unrelated areas.
Do NOT generate a complete course on the technology unless explicitly requested.

Generate 5 modules in this sequence. Each module must have:
- id (string)
- title (string)
- learning_objectives (array of 2-3 strings)
- concepts (array of 1-2 strings)

Return valid JSON:
{{"modules":[{{"id":"","title":"","learning_objectives":[],"concepts":[]}}]}}"""

RESEARCH_PLAN_PROMPT = """Generate research objectives for:
Topic: {topic}
Modules: {module_titles}

Categories: Definition, Applications, Best Practices, Limitations

Return JSON: {{"categories":{{"Definition":{{"questions":[],"priority":"Critical"}}}}}}"""

# ============================================================================
# ENUMS (Keep existing enums here)
# ============================================================================

class TeachingMethod(str, Enum):
    LECTURE = "Lecture"
    DISCUSSION = "Discussion"
    DEMONSTRATION = "Demonstration"
    HANDS_ON_LAB = "Hands-on Lab"
    CASE_STUDY = "Case Study"
    INTERACTIVE = "Interactive"
    PROBLEM_SOLVING = "Problem Solving"
    PEER_LEARNING = "Peer Learning"
    SELF_STUDY = "Self Study"
    QUIZ = "Quiz"
    REFLECTION = "Reflection"

class CognitiveLoad(str, Enum):
    LOW = "Low"
    MEDIUM = "Medium"
    HIGH = "High"
    VERY_HIGH = "Very High"

class ModuleType(str, Enum):
    THEORY = "Theory"
    PRACTICAL = "Practical"
    DISCUSSION = "Discussion"
    CASE_STUDY = "Case Study"
    LAB = "Lab"
    ASSESSMENT = "Assessment"
    REVIEW = "Review"
    INTRODUCTION = "Introduction"
    SUMMARY = "Summary"

class DifficultyLevel(str, Enum):
    BEGINNER = "Beginner"
    INTERMEDIATE = "Intermediate"
    ADVANCED = "Advanced"
    EXPERT = "Expert"

class ConceptType(str, Enum):
    FOUNDATIONAL = "Foundational"
    CORE = "Core"
    ADVANCED = "Advanced"
    SPECIALIZED = "Specialized"
    EMERGING = "Emerging"

class DomainTemplate(str, Enum):
    PROGRAMMING = "Programming"
    AI_ML = "AI_ML"
    MEDICINE = "Medicine"
    FINANCE = "Finance"
    HISTORY = "History"
    BUSINESS = "Business"
    SCIENCE = "Science"
    GENERAL = "General"

# ============================================================================
# DOMAIN TEMPLATES (Keep existing)
# ============================================================================

class DomainTemplateConfig:
    def __init__(self, name: str, module_pattern: List[str], concept_types: List[str], 
                 resource_types: List[str], default_audience: str = "General"):
        self.name = name
        self.module_pattern = module_pattern
        self.concept_types = concept_types
        self.resource_types = resource_types
        self.default_audience = default_audience

DOMAIN_TEMPLATES = {
    DomainTemplate.PROGRAMMING: DomainTemplateConfig(
        name="Programming",
        module_pattern=[
            "Setup and Environment", "Core Syntax", "Data Structures",
            "Control Flow", "Functions", "Error Handling",
            "Libraries", "Best Practices", "Testing", "Performance"
        ],
        concept_types=["Syntax", "Architecture", "Design Pattern", "Implementation", "Optimization"],
        resource_types=["Code Example", "Architecture Diagram", "Performance Graph"],
        default_audience="University Lecture"
    ),
    DomainTemplate.AI_ML: DomainTemplateConfig(
        name="AI_ML",
        module_pattern=[
            "Mathematical Foundations", "Core Algorithms", "Model Architecture",
            "Training", "Evaluation", "Applications", "Limitations"
        ],
        concept_types=["Mathematics", "Algorithm", "Architecture", "Implementation", "Application"],
        resource_types=["Formula", "Architecture Diagram", "Code Example", "Performance Graph"],
        default_audience="University Lecture"
    ),
    DomainTemplate.MEDICINE: DomainTemplateConfig(
        name="Medicine",
        module_pattern=[
            "Overview", "Anatomy", "Pathophysiology", "Clinical Presentation",
            "Diagnosis", "Treatment", "Case Studies", "Recent Advances"
        ],
        concept_types=["Anatomy", "Pathology", "Clinical", "Treatment", "Case Study"],
        resource_types=["Diagram", "Case Study", "Statistics"],
        default_audience="University Lecture"
    ),
    DomainTemplate.FINANCE: DomainTemplateConfig(
        name="Finance",
        module_pattern=[
            "Fundamentals", "Markets", "Valuation", "Risk Management",
            "Trading", "Regulation", "Advanced Strategies", "Case Studies"
        ],
        concept_types=["Fundamental", "Instrument", "Analysis", "Risk", "Strategy"],
        resource_types=["Formula", "Chart", "Case Study"],
        default_audience="Corporate Training"
    ),
    DomainTemplate.GENERAL: DomainTemplateConfig(
        name="General",
        module_pattern=[
            "Introduction", "Core Concepts", "Key Principles",
            "Applications", "Advanced Topics", "Summary"
        ],
        concept_types=["Concept", "Principle", "Application", "Advanced"],
        resource_types=["Diagram", "Example"],
        default_audience="General"
    )
}

# ============================================================================
# DATA CLASSES (Keep existing)
# ============================================================================

@dataclass
class ConceptNode:
    id: str
    name: str
    description: str
    concept_type: str
    difficulty: str
    prerequisites: List[str]
    estimated_time: int
    resources_needed: List[str]
    module_id: Optional[str] = None
    
    def to_dict(self):
        return asdict(self)

@dataclass
class ModuleV4:
    id: str
    title: str
    learning_objectives: List[str]
    concepts: List[str]
    pedagogical_goal: str
    difficulty: str
    estimated_duration: int
    prerequisites_modules: List[str]
    module_type: str
    teaching_method: str
    cognitive_load: str
    cognitive_load_reason: str
    transition_reason: Optional[str] = None
    sections: List[Dict[str, Any]] = field(default_factory=list)
    misconception_topics: List[str] = field(default_factory=list)
    needs_checkpoint: bool = False
    resource_needs: List[str] = field(default_factory=list)
    
    def to_dict(self):
        return asdict(self)

@dataclass
class AudienceV4:
    type: str
    experience_level: str
    learning_goal: str
    domain: str
    age_range: Optional[str] = None
    background: Optional[str] = None
    preferred_style: Optional[str] = None
    language: Optional[str] = None
    time_availability: Optional[str] = None
    motivation: Optional[str] = None
    
    def __post_init__(self):
        if not self.age_range:
            self.age_range = "25-40" if self.type == "Corporate Training" else "18-35"
        if not self.background:
            self.background = "Professional" if self.type == "Corporate Training" else "Academic"
        if not self.preferred_style:
            self.preferred_style = "Mixed"
        if not self.language:
            self.language = "English"
        if not self.motivation:
            self.motivation = "Career advancement" if self.type == "Corporate Training" else "Knowledge acquisition"
    
    def to_dict(self):
        return asdict(self)

@dataclass
class CoursePlanV4:
    topic: str
    course_title: str
    course_description: str
    course_type: str
    domain_template: str
    audience: AudienceV4
    overall_difficulty: str
    learning_outcomes: List[str]
    modules: List[ModuleV4]
    subtopic: Optional[str] = None
    concept_graph: Dict[str, Any] = field(default_factory=dict)
    research_plan: Dict[str, Any] = field(default_factory=dict)
    resource_requirements: Dict[str, Any] = field(default_factory=dict)
    validation_results: Dict[str, Any] = field(default_factory=dict)
    schema_version: str = "4.0"
    compatibility_version: str = "4.0"
    created_by: str = "PlannerAgentV4"
    created_at: str = field(default_factory=lambda: datetime.now().isoformat())
    
    def to_dict(self):
        return {
            "schema_version": self.schema_version,
            "compatibility_version": self.compatibility_version,
            "created_by": self.created_by,
            "created_at": self.created_at,
            "topic": self.topic,
            "subtopic": self.subtopic,
            "course_title": self.course_title,
            "course_description": self.course_description,
            "course_type": self.course_type,
            "domain_template": self.domain_template,
            "audience": self.audience.to_dict() if self.audience else {},
            "overall_difficulty": self.overall_difficulty,
            "learning_outcomes": self.learning_outcomes,
            "modules": [m.to_dict() for m in self.modules],
            "concept_graph": self.concept_graph,
            "research_plan": self.research_plan,
            "resource_requirements": self.resource_requirements,
            "validation_results": self.validation_results
        }

# ============================================================================
# LLM SERVICE - REDUCED MAX_TOKENS
# ============================================================================

class LLMService:
    def __init__(self, provider: str = "groq"):
        load_dotenv()
        self.provider = provider
        
        if provider == "groq":
            api_key = os.getenv("GROQ_API_KEY")
            if not api_key:
                raise ValueError("❌ GROQ_API_KEY not found! Please create .env file")
            self.client = Groq(api_key=api_key)
            self.model = os.getenv("MODEL_NAME", "qwen/qwen3.6-27b")
        else:
            raise ValueError(f"Provider {provider} not supported yet")
    
    def generate(self, system_prompt: str, user_prompt: str, temperature: float = 0.1, max_tokens: int = 2500) -> str:
        """Generate response from LLM with reduced token limit"""
        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt}
                ],
                temperature=temperature,
                max_tokens=max_tokens
            )
            return response.choices[0].message.content.strip()
        except Exception as e:
            raise Exception(f"LLM Service error: {e}")

# ============================================================================
# PLANNER AGENT - FIXED VERSION
# ============================================================================

class PlannerAgentV4:
    def __init__(self):
        self.llm = LLMService(provider="groq")
        self.setup_directories()
        print("✅ Planner Agent V4 Ready (Fixed - No 413 Error)")
        print("   ⚙️  Temperature: 0.1")
        print("   📦 Max Tokens: 2500 (reduced)")
        print("   📋 Split Generation: 5+5 modules")
        print("   🎯 Enhanced Intent Extraction: Topic/Scope/Technology separated")
    
    def setup_directories(self):
        try:
            os.makedirs("output", exist_ok=True)
            os.makedirs("data", exist_ok=True)
        except Exception as e:
            print(f"⚠️ Could not create directories: {e}")
    
    def generate_plan(self, user_input: str) -> CoursePlanV4:
        print("\n" + "=" * 60)
        print("📝 Generating Curriculum Plan")
        print("=" * 60)
        
        print("\n🔍 Analyzing Intent...")
        intent = self._analyze_intent(user_input)
        print(f"   Topic: {intent['topic']}")
        print(f"   Scope: {intent.get('scope', '')}")
        print(f"   Technology/Context: {intent.get('technology', '')}")
        print(f"   Domain: {intent.get('domain', 'General')}")
        print(f"   Audience: {intent['audience_type']}")
        
        print("\n📚 Building Curriculum (Split Generation)...")
        modules, learning_outcomes, concepts = self._build_curriculum_split(intent)
        print(f"   Total Modules: {len(modules)}")
        print(f"   Concepts: {len(concepts)}")
        
        print("\n🧩 Building Concept Graph...")
        concept_graph = self._build_concept_graph(concepts, modules, intent['topic'])
        
        print("\n🔬 Planning Research...")
        research_plan = self._plan_research(intent['topic'], modules, concepts)
        
        # domain_config = DOMAIN_TEMPLATES.get(
        #     DomainTemplate(intent.get('domain', 'General')),
        #     DOMAIN_TEMPLATES[DomainTemplate.GENERAL]
        # )
        domain_value = intent.get("domain") or DomainTemplate.GENERAL.value
        try:
             domain_template_enum = DomainTemplate(domain_value)
        except ValueError:
             print(
                  f"⚠️ Invalid domain '{domain_value}'. "
                  "Using GENERAL."
             )
             domain_template_enum = DomainTemplate.GENERAL
        domain_config = DOMAIN_TEMPLATES.get(
            domain_template_enum,
            DOMAIN_TEMPLATES[DomainTemplate.GENERAL]
            )
        
        audience = AudienceV4(
            type=intent.get('audience_type', domain_config.default_audience),
            experience_level=intent.get('difficulty', 'Intermediate'),
            learning_goal=intent.get('purpose', 'Knowledge acquisition'),
            domain=intent.get('domain', 'General')
        )
        
        resource_counts = {}
        for m in modules:
            for r in m.resource_needs:
                resource_counts[r] = resource_counts.get(r, 0) + 1
        
        resource_requirements = {
            "must_have": list(resource_counts.keys()),
            "nice_to_have": [],
            "resource_types": list(resource_counts.keys()),
            "resource_counts": resource_counts
        }
        
        plan = CoursePlanV4(
            topic=intent['topic'],
            course_title=f"Comprehensive Course on {intent['topic']}",
            course_description=f"Complete coverage of {intent['topic']} for {intent['audience_type']}",
            course_type=intent['audience_type'],
            domain_template=intent.get('domain', 'General'),
            audience=audience,
            overall_difficulty=intent['difficulty'],
            learning_outcomes=learning_outcomes,
            modules=modules,
            concept_graph=concept_graph,
            research_plan=research_plan,
            resource_requirements=resource_requirements,
            validation_results={}
        )
        
        print("\n✅ Plan Generation Complete!")
        return plan
    
    def _analyze_intent(self, user_input: str) -> Dict[str, Any]:
        prompt = INTENT_ANALYSIS_PROMPT.format(user_input=user_input)
        
        try:
            response = self.llm.generate(
                system_prompt="You are a course intent analyzer. Extract structured data. Return ONLY valid JSON.",
                user_prompt=prompt,
                temperature=0.1,
                max_tokens=500
            )
            response = self._clean_json_robust(response)
            data = json.loads(response)
            
            return {
                "topic": user_input.strip(),          # <-- Preserve exactly what the user typed
                "scope": data.get("scope", ""),
                "technology": data.get("technology_or_context", ""),
                "domain": data.get("domain", "General"),
                "audience_type": data.get("audience_type", "University Lecture"),
                "duration": data.get("duration", 60),
                "difficulty": data.get("difficulty", "Intermediate"),
                "purpose": data.get("purpose", "Knowledge acquisition"),
                "constraints": data.get("constraints", [])
                }
                # "topic": data.get("topic", user_input),
                # "scope": data.get("scope", ""),
                # "technology": data.get("technology_or_context", ""),
                # "domain": data.get("domain", "General"),
                # "audience_type": data.get("audience_type", "University Lecture"),
                # "duration": data.get("duration", 60),
                # "difficulty": data.get("difficulty", "Intermediate"),
                # "purpose": data.get("purpose", "Knowledge acquisition"),
                # "constraints": data.get("constraints", [])
            
        except Exception as e:
            print(f"⚠️ Intent analysis failed: {e}")
            return {
                "topic": user_input,
                "scope": "",
                "technology": "",
                "domain": "General",
                "audience_type": "University Lecture",
                "duration": 60,
                "difficulty": "Intermediate",
                "purpose": "Knowledge acquisition",
                "constraints": []
            }
    
    def _build_curriculum_split(self, intent: Dict[str, Any]) -> Tuple[List[ModuleV4], List[str], List[ConceptNode]]:
        """Split curriculum generation into 2 calls to avoid 413"""
        topic = intent['topic']
        scope = intent.get('scope', '')
        technology = intent.get('technology', '')
        domain = intent.get('domain', 'General')
        audience = intent['audience_type']
        difficulty = intent['difficulty']
        
        # Generate first 5 modules
        print("   🔄 Generating modules 1-5...")
        modules_1 = self._generate_module_batch(topic, scope, technology, domain, audience, difficulty, batch=1, total_batches=2)
        
        # Generate next 5 modules
        print("   🔄 Generating modules 6-10...")
        modules_2 = self._generate_module_batch(topic, scope, technology, domain, audience, difficulty, batch=2, total_batches=2)
        
        # Combine
        all_modules = modules_1 + modules_2
        
        # If we got fewer than 10 modules, use fallback
        if len(all_modules) < 10:
            print(f"\n   ⚠️ Only {len(all_modules)} modules generated. Using fallback...")
            return self._fallback_curriculum(intent)
        
        # Generate learning outcomes and concepts from modules
        learning_outcomes = self._generate_learning_outcomes(topic, all_modules)
        concepts = self._generate_concepts(topic, all_modules)
        
        print(f"\n   ✅ Generated {len(all_modules)} modules total")
        return all_modules, learning_outcomes, concepts
    
    def _generate_module_batch(self, topic: str, scope: str, technology: str, 
                                domain: str, audience: str, difficulty: str, 
                                batch: int, total_batches: int) -> List[ModuleV4]:
        """Generate a batch of 5 modules"""
        
        # Determine module sequence for this batch
        if batch == 1:
            sequence = "first 5 modules covering foundational concepts, prerequisites, and core principles"
        else:
            sequence = "last 5 modules covering advanced topics, applications, and summary"
        
        prompt = f"""Topic: {topic}
Scope: {scope}
Technology/Context: {technology}
Domain: {domain}
Audience: {audience}
Difficulty: {difficulty}

Generate the {sequence}. Provide exactly 5 modules.
Generate ONLY modules relevant to the topic and scope.
Do NOT expand into unrelated areas.
Do NOT generate a complete course on the technology unless explicitly requested.

Return JSON: {{"modules":[{{"id":"m1","title":"Module Title","learning_objectives":["obj1","obj2"],"concepts":["concept1"]}}]}}

Only return the JSON. No other text."""

        try:
            response = self.llm.generate(
                system_prompt="You are a curriculum designer. Generate 5 modules. Return valid JSON only.",
                user_prompt=prompt,
                temperature=0.1,
                max_tokens=480
            )
            
            cleaned = self._clean_json_robust(response)
            data = json.loads(cleaned)
            if isinstance(data, list):
                module_data = data

            elif isinstance(data, dict):
                module_data = data.get("modules", [])
            else:
                raise ValueError(
                    f"Unexpected response type: {type(data)}"
                    )
            modules = []
            for m in module_data:
                if not isinstance(m, dict):
                    print(f"⚠️ Skipping invalid module: {m}")
                    continue
                module = ModuleV4(
                    id=m.get("id", f"m_{len(modules)+1}"),
                    title=m.get("title", f"Module {len(modules)+1}"),
                    learning_objectives=m.get(
                        "learning_objectives",
                        [f"Understand {topic}"]
                        ),
                        concepts=m.get(
                            "concepts",
                            [f"{topic} Concept"]
                            ),
                        sections=[
                            {
                                "section_id": f"{m.get('id', f'm{len(modules)+1}')}_S01",
                                "heading": m.get(
                                    "title",
                                    f"Module {len(modules)+1}"
                                    ),
                                    "concepts": m.get("concepts", []),
                                    "questions": []
                                    }
                                    ],
                                    pedagogical_goal=f"Build understanding of {topic}",
                                    difficulty=difficulty,
                                    estimated_duration=15,
                                    prerequisites_modules=[],
                                    module_type="Theory" if batch == 1 else "Practical",
                                    teaching_method="Lecture",
                                    cognitive_load="Medium",
                                    cognitive_load_reason="Standard module content",
                                    transition_reason="Sequential module",
                                    misconception_topics=[],
                                    needs_checkpoint=False,
                                    resource_needs=["Diagram"])
                modules.append(module)
            return modules
            # data = json.loads(cleaned)
            # modules = []
            # if isinstance(data, list):
            #      module_data = data
            # elif isinstance(data, dict):
            #      module_data = data.get("modules", [])
            # else:
            #     raise ValueError(
            #          f"Unexpected JSON structure: {type(data).__name__}")
            # for m in module_data:
            #     # Fill in default values for required fields
            #     module = ModuleV4(
            #         id=m.get("id", f"m_{len(modules)+1}"),
            #         title=m.get("title", f"Module {len(modules)+1}"),
            #         learning_objectives=m.get("learning_objectives", [f"Understand {topic}"]),
            #         concepts=m.get("concepts", [f"{topic} Concept"]),
            #         sections=[
            #             {
            #                 "section_id": f"{m.get('id', f'm{len(modules)+1}')}_S01",
            #                 "heading": m.get("title", f"Module {len(modules)+1}"),
            #                 "concepts": m.get("concepts", []),
            #                 "questions": []
            #                 }
            #                 ],
            #         pedagogical_goal=f"Build understanding of {topic}",
            #         difficulty=difficulty,
            #         estimated_duration=15,
            #         prerequisites_modules=[],
            #         module_type="Theory" if batch == 1 else "Practical",
            #         teaching_method="Lecture",
            #         cognitive_load="Medium",
            #         cognitive_load_reason="Standard module content",
            #         transition_reason="Sequential module",
            #         misconception_topics=[],
            #         needs_checkpoint=False,
            #         resource_needs=["Diagram"]
            #     )
            #     modules.append(module)
            
            # return modules
            
        except Exception as e:
            print(f"   ⚠️ Batch {batch} generation failed: {e}")
            return []
    
    def _generate_learning_outcomes(self, topic: str, modules: List[ModuleV4]) -> List[str]:
        """Generate learning outcomes from modules"""
        outcomes = [
            f"Define and explain the fundamentals of {topic}",
            f"Apply {topic} concepts to practical problems",
            f"Analyze and evaluate {topic} implementations",
            f"Design solutions using {topic} best practices",
            f"Evaluate emerging trends in {topic}"
        ]
        return outcomes
    
    def _generate_concepts(self, topic: str, modules: List[ModuleV4]) -> List[ConceptNode]:
        """Generate concepts from modules"""
        concepts = []
        for i, module in enumerate(modules[:8]):  # Max 8 concepts
            concept = ConceptNode(
                id=f"concept_{i+1}",
                name=f"{topic} Concept {i+1}",
                description=f"Key concept from {module.title}",
                concept_type="Core",
                difficulty="Intermediate",
                prerequisites=[],
                estimated_time=10,
                resources_needed=["Diagram"],
                module_id=module.id
            )
            concepts.append(concept)
        return concepts
    def _clean_json_robust(self, text: str) -> str:
        """Extract and repair the first valid JSON object from LLM output."""
        text = text.strip()
        text = re.sub(r"^```json\s*", "", text, flags=re.IGNORECASE)
        text = re.sub(r"^```\s*", "", text)
        text = re.sub(r"\s*```$", "", text)
        start = text.find("{")
        if start == -1:
            raise ValueError("No JSON object found in response")
        decoder = json.JSONDecoder()
        try:
            obj, end = decoder.raw_decode(text[start:])
            return json.dumps(obj)
        except json.JSONDecodeError:
            try:
                from json_repair import repair_json
                repaired = repair_json(text[start:])
                obj, end = decoder.raw_decode(repaired)
                return json.dumps(obj)

            except ImportError:
                raise ValueError("Invalid JSON and json_repair is not installed")
    
    def _fallback_curriculum(self, intent: Dict[str, Any]) -> Tuple[List[ModuleV4], List[str], List[ConceptNode]]:
        """Comprehensive fallback with 10 modules"""
        topic = intent["topic"]
        scope = intent.get('scope', '')
        technology = intent.get('technology', '')
        difficulty = intent.get("difficulty", "Intermediate")
        
        # Create 10 modules with scope and technology context
        title_prefix = topic
        if scope:
            title_prefix = f"{topic}: {scope}"
        if technology:
            title_prefix = f"{title_prefix} (with {technology})"
        
        module_titles = [
            f"Introduction to {title_prefix}",
            f"Fundamentals of {title_prefix}",
            f"Core Concepts in {title_prefix}",
            f"Key Principles of {title_prefix}",
            f"Applications of {title_prefix}",
            f"Advanced {title_prefix} Techniques",
            f"{title_prefix} in Practice",
            f"Best Practices for {title_prefix}",
            f"Future Trends in {title_prefix}",
            f"Summary and Key Takeaways"
        ]
        
        modules = []
        for i, title in enumerate(module_titles, 1):
            module = ModuleV4(
                id=f"m_{i}",
                title=title,
                learning_objectives=[f"Understand {title}", f"Apply {title} concepts"],
                concepts=[f"{topic} Concept"],
                sections=[
                    {
                        "section_id": f"m_{i}_S01",
                        "heading": title,
                        "concepts": [f"{topic} Concept"],
                        "questions": []
                        }
                        ],
                pedagogical_goal=f"Build understanding of {title}",
                difficulty=difficulty,
                estimated_duration=15,
                prerequisites_modules=[],
                module_type="Theory" if i <= 5 else "Practical",
                teaching_method="Lecture",
                cognitive_load="Medium",
                cognitive_load_reason="Standard content",
                transition_reason="Sequential"
            )
            modules.append(module)
        
        learning_outcomes = [
            f"Define and explain the fundamentals of {topic}",
            f"Apply {topic} concepts to practical problems",
            f"Analyze and evaluate {topic} implementations",
            f"Design solutions using {topic} best practices",
            f"Evaluate emerging trends in {topic}"
        ]
        
        concepts = []
        for i in range(1, 9):
            concepts.append(ConceptNode(
                id=f"c_{i}",
                name=f"{topic} Concept {i}",
                description=f"Key concept in {topic}",
                concept_type="Core",
                difficulty=difficulty,
                prerequisites=[],
                estimated_time=10,
                resources_needed=["Diagram"]
            ))
        
        print(f"\n   ✅ Using comprehensive fallback with {len(modules)} modules")
        return modules, learning_outcomes, concepts
    
    def _build_concept_graph(self, concepts: List[ConceptNode], modules: List[ModuleV4], topic: str) -> Dict[str, Any]:
        nodes = []
        edges = []
        
        for concept in concepts:
            nodes.append(concept.to_dict())
        
        # Create simple edges between consecutive modules
        for i in range(len(modules) - 1):
            if i < len(concepts) - 1:
                edges.append({
                    "source": concepts[i].id if i < len(concepts) else "c_1",
                    "target": concepts[i+1].id if i+1 < len(concepts) else "c_1",
                    "relationship": "prerequisite",
                    "reason": f"Building on previous knowledge"
                })
        
        return {"nodes": nodes, "edges": edges}
    
    def _plan_research(self, topic: str, modules: List[ModuleV4], concepts: List[ConceptNode]) -> Dict[str, Any]:
        """Simplified research planning with reduced data"""
        # Only send first 5 module titles
        module_titles = ", ".join(m.title for m in modules[:5])
        
        prompt = RESEARCH_PLAN_PROMPT.format(
            topic=topic,
            module_titles=module_titles
        )
        
        try:
            response = self.llm.generate(
                system_prompt="You are a research planner. Return ONLY valid JSON.",
                user_prompt=prompt,
                temperature=0.1,
                max_tokens=500
            )
            response = self._clean_json_robust(response)
            data = json.loads(response)
            return data
        except Exception as e:
            print(f"⚠️ Research planning failed: {e}")
            return {
                "categories": {
                    "Definition": {
                        "questions": [f"What is {topic}?", f"Why is {topic} important?"],
                        "priority": "Critical"
                    },
                    "Applications": {
                        "questions": [f"How is {topic} applied in practice?"],
                        "priority": "Important"
                    }
                }
            }
    
    def save_plan(self, plan: CoursePlanV4, filename: str = "course_plan_v4.json"):
        filepath = os.path.join("output", filename)
        with open(filepath, "w") as f:
            json.dump(plan.to_dict(), f, indent=2)
        print(f"💾 Plan saved to: {filepath}")
        return filepath
    
    def display_plan(self, plan: CoursePlanV4):
        print("\n" + "=" * 70)
        print("📚 COURSE PLAN")
        print("=" * 70)
        print(f"\n📌 Topic: {plan.topic}")
        print(f"📖 Title: {plan.course_title}")
        print(f"🎯 Type: {plan.course_type}")
        print(f"👥 Audience: {plan.audience.type}")
        print(f"📊 Difficulty: {plan.overall_difficulty}")
        print(f"📋 Modules: {len(plan.modules)}")
        print(f"🧩 Concepts: {len(plan.concept_graph.get('nodes', []))}")
        
        print("\n🎯 LEARNING OUTCOMES:")
        for outcome in plan.learning_outcomes[:5]:
            print(f"  • {outcome}")
        
        print(f"\n📋 MODULE DETAILS:")
        for i, module in enumerate(plan.modules, 1):
            print(f"\n{i}. {module.title} [{module.id}]")
            print(f"   Type: {module.module_type}")
            print(f"   Method: {module.teaching_method}")
            print(f"   Load: {module.cognitive_load}")
            print(f"   Duration: {module.estimated_duration} min")
            if module.misconception_topics:
                print(f"   Misconceptions: {', '.join(module.misconception_topics)}")
        
        print("\n" + "=" * 70)

# ============================================================================
# UniversalPlanner - Backward Compatible
# ============================================================================

class UniversalPlanner(PlannerAgentV4):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        print("✅ UniversalPlanner (V4) - Backward compatible")
    
    def extract_user_requirements(self, prompt):
        return self._analyze_intent(prompt)
    
    def create_presentation(self, user_prompt):
        plan = self.generate_plan(user_prompt)
        return plan.to_dict()
    
    def smart_fallback(self, user_prompt):
        try:
            plan = self.generate_plan(user_prompt)
            return plan.to_dict()
        except Exception as e:
            print(f"⚠️ Fallback triggered: {e}")
            return {
                "topic": user_prompt[:50],
                "subtopics": [
                    {"key": "Introduction", "description": "Overview"},
                    {"key": "Core Concepts", "description": "Main concepts"},
                    {"key": "Applications", "description": "Practical uses"}
                ]
            }
    
    def ensure_required_fields(self, plan, user_prompt):
        if not plan.get("topic"):
            plan["topic"] = user_prompt[:50]
        if not plan.get("subtopics"):
            plan["subtopics"] = [
                {"key": "Introduction", "description": "Overview"},
                {"key": "Core Concepts", "description": "Main concepts"},
                {"key": "Applications", "description": "Practical uses"}
            ]
        return plan

# ============================================================================
# MAIN
# ============================================================================

if __name__ == "__main__":
    print("=" * 70)
    print("🤖 PLANNER AGENT V4 - FIXED (No 413 Error)")
    print("=" * 70)
    print("\n⚙️  Key fixes:")
    print("   • Split curriculum: 2 calls (5 modules each)")
    print("   • Reduced max_tokens: 6000 → 2500")
    print("   • Simplified prompts (70% smaller)")
    print("   • Reduced research input (only 5 modules)")
    print("   • Enhanced Intent Extraction: Topic/Scope/Technology separated")
    
    user_input = input("\n📝 Enter your topic: ").strip()
    if not user_input:
        user_input = "overfitting in machine learning"
        print(f"📝 Using demo: {user_input}")
    
    planner = PlannerAgentV4()
    plan = planner.generate_plan(user_input)
    planner.display_plan(plan)
    planner.save_plan(plan)
    
    print("\n✅ Done! No 413 error.")