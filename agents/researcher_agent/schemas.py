# from pydantic import BaseModel
# from typing import List


# class PlannerOutput(BaseModel):
#     topic: str
#     objective: str
#     audience: str
#     subtopics: List[str]


# class ResearchItem(BaseModel):
#     title: str
#     url: str
#     content: str
#     source: str


# class ResearchSummary(BaseModel):
#     subtopic: str
#     summary: List[str]


# class ResearcherOutput(BaseModel):
#     topic: str
#     research: List[ResearchSummary]
#!/usr/bin/env python3
"""
Schemas for Researcher Agent - Planner V4 Compatible
"""

from typing import List, Dict, Any, Optional
from dataclasses import dataclass, field, asdict
from datetime import datetime

# ============================================================================
# PLANNER V4 SCHEMAS (Read-only)
# ============================================================================

@dataclass
class ConceptNode:
    """Concept node from Planner V4"""
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
    """Module from Planner V4"""
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
    misconception_topics: List[str] = field(default_factory=list)
    needs_checkpoint: bool = False
    resource_needs: List[str] = field(default_factory=list)
    
    def to_dict(self):
        return asdict(self)

@dataclass
class ResearchCategory:
    """Research category from Planner V4"""
    questions: List[str]
    priority: str
    expected_output: str

@dataclass
class ResearchPlan:
    """Research plan from Planner V4"""
    categories: Dict[str, ResearchCategory]
    
    def to_dict(self):
        return {
            "categories": {
                key: {
                    "questions": value.questions,
                    "priority": value.priority,
                    "expected_output": value.expected_output
                }
                for key, value in self.categories.items()
            }
        }

@dataclass
class PlannerV4Output:
    """Complete Planner V4 output"""
    topic: str
    subtopic: Optional[str]
    course_title: str
    course_description: str
    course_type: str
    domain_template: str
    audience: Dict[str, Any]
    overall_difficulty: str
    learning_outcomes: List[str]
    modules: List[ModuleV4]
    concept_graph: Dict[str, Any]
    research_plan: ResearchPlan
    resource_requirements: Dict[str, Any]
    validation_results: Dict[str, Any]
    schema_version: str
    compatibility_version: str
    created_by: str
    created_at: str
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'PlannerV4Output':
        """Create PlannerV4Output from dictionary"""
        # Parse modules
        modules = []
        for m in data.get("modules", []):
            modules.append(ModuleV4(**m))
        
        # Parse research plan
        research_plan_data = data.get("research_plan", {})
        categories = {}
        for key, value in research_plan_data.get("categories", {}).items():
            categories[key] = ResearchCategory(
                questions=value.get("questions", []),
                priority=value.get("priority", "Normal"),
                expected_output=value.get("expected_output", "")
            )
        
        research_plan = ResearchPlan(categories=categories)
        
        return cls(
            topic=data.get("topic", ""),
            subtopic=data.get("subtopic"),
            course_title=data.get("course_title", ""),
            course_description=data.get("course_description", ""),
            course_type=data.get("course_type", ""),
            domain_template=data.get("domain_template", ""),
            audience=data.get("audience", {}),
            overall_difficulty=data.get("overall_difficulty", ""),
            learning_outcomes=data.get("learning_outcomes", []),
            modules=modules,
            concept_graph=data.get("concept_graph", {}),
            research_plan=research_plan,
            resource_requirements=data.get("resource_requirements", {}),
            validation_results=data.get("validation_results", {}),
            schema_version=data.get("schema_version", "4.0"),
            compatibility_version=data.get("compatibility_version", "4.0"),
            created_by=data.get("created_by", "PlannerAgentV4"),
            created_at=data.get("created_at", datetime.now().isoformat())
        )
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        return {
            "topic": self.topic,
            "subtopic": self.subtopic,
            "course_title": self.course_title,
            "course_description": self.course_description,
            "course_type": self.course_type,
            "domain_template": self.domain_template,
            "audience": self.audience,
            "overall_difficulty": self.overall_difficulty,
            "learning_outcomes": self.learning_outcomes,
            "modules": [m.to_dict() for m in self.modules],
            "concept_graph": self.concept_graph,
            "research_plan": self.research_plan.to_dict(),
            "resource_requirements": self.resource_requirements,
            "validation_results": self.validation_results,
            "schema_version": self.schema_version,
            "compatibility_version": self.compatibility_version,
            "created_by": self.created_by,
            "created_at": self.created_at
        }

# ============================================================================
# RESEARCHER OUTPUT SCHEMAS
# ============================================================================

@dataclass
class Source:
    """Source from search results"""
    title: str
    url: str
    snippet: str
    source_type: str  # "tavily" or "duckduckgo"
    
    def to_dict(self):
        return asdict(self)

@dataclass
class ResearchFinding:
    """Research finding for a single question"""
    question: str
    answer: str
    sources: List[Source]
    confidence: float
    researched_at: str = field(default_factory=lambda: datetime.now().isoformat())
    
    def to_dict(self):
        return {
            "question": self.question,
            "answer": self.answer,
            "sources": [s.to_dict() for s in self.sources],
            "confidence": self.confidence,
            "researched_at": self.researched_at
        }

@dataclass
class ResearchOutput:
    """Complete research output"""
    topic: str
    research: Dict[str, List[ResearchFinding]]
    metadata: Dict[str, Any] = field(default_factory=dict)
    created_at: str = field(default_factory=lambda: datetime.now().isoformat())
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for JSON output"""
        return {
            "research_output": {
                category: [f.to_dict() for f in findings]
                for category, findings in self.research.items()
            },
            "metadata": self.metadata,
            "created_at": self.created_at
        }