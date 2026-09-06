# PLANNER_SYSTEM_PROMPT = """
# You are a Presentation Planner Agent.

# Rules:
# 1. Extract values only if explicitly provided by the user.
# 2. Never infer or assume slide count, audience, tone, duration, etc.
# 3. If a field is not mentioned, set it to "NA".
# 4. Always return all fields.
# 5. Generate outline based on topic.
# 6. Subtopics must be key-value pairs with descriptions.
# 7. Return ONLY valid JSON.

# Output Format:

# {
#   "topic": "string",
#   "slide_count": "number or NA",
#   "audience": "string or NA",
#   "tone": "string or NA",
#   "duration": "string or NA",
#   "outline": [
#     {
#       "slide_number": 1,
#       "title": "string",
#       "subtopics": {
#         "key1": "description",
#         "key2": "description"
#       }
#     }
#   ]
# }
# """
# utils/prompt_templates.py

# Add these to your existing file

INTENT_ANALYSIS_PROMPT = """Analyze this request and extract structured intent:

Request: {user_input}

Extract:
1. Topic (main subject)
2. Domain (AI_ML, Programming, Medicine, Finance, History, Business, Science, General)
3. Audience Type (University Lecture, Corporate Training, Certification, Workshop, Bootcamp, Seminar)
4. Duration (in minutes)
5. Difficulty (Beginner, Intermediate, Advanced, Expert)
6. Purpose (what should learners achieve)
7. Constraints (any limitations)

Return ONLY valid JSON with these fields."""

CURRICULUM_PLANNING_PROMPT = """Create a curriculum plan with educational intelligence for:
Topic: {topic}
Domain: {domain}
Audience: {audience_type}
Difficulty: {difficulty}
Duration: {duration} minutes

Use this module pattern (adapt as needed):
{module_pattern}

For EACH module, include EDUCATIONAL PLANNING (not content details):
1. Module Type: Theory, Practical, Discussion, Case Study, Lab, Assessment, Review, Introduction, Summary
2. Teaching Method: Lecture, Discussion, Demonstration, Hands-on Lab, Case Study, Interactive, Quiz, Reflection
3. Cognitive Load: Low, Medium, High, Very High - Why?
4. Misconception Topics: What do students usually misunderstand? (topics only, not explanations)
5. Checkpoint: Should there be an assessment after this module? (Yes/No)
6. Resource Needs: What resources are needed? (Diagram, Code Example, etc.)

Return ONLY valid JSON with this structure:

{{
  "modules": [
    {{
      "id": "semantic_id",
      "title": "Module Title",
      "learning_objectives": ["obj1", "obj2"],
      "concepts": ["concept_id1", "concept_id2"],
      "pedagogical_goal": "What this module achieves educationally",
      "difficulty": "Beginner|Intermediate|Advanced|Expert",
      "estimated_duration": 15,
      "prerequisites_modules": [],
      "transition_reason": "Why this follows the previous module",
      "module_type": "Theory|Practical|Discussion|Case Study|Lab|Assessment|Review|Introduction|Summary",
      "teaching_method": "Lecture|Discussion|Demonstration|Hands-on Lab|Case Study|Interactive|Quiz|Reflection",
      "cognitive_load": "Low|Medium|High|Very High",
      "cognitive_load_reason": "Brief reason for cognitive load estimate",
      "misconception_topics": ["topic1", "topic2"],
      "needs_checkpoint": true,
      "resource_needs": ["Diagram", "Code Example"]
    }}
  ],
  "learning_outcomes": ["outcome1", "outcome2"],
  "concepts": [
    {{
      "id": "concept_id1",
      "name": "Concept Name",
      "description": "Brief concept description",
      "concept_type": "Foundational|Core|Advanced|Specialized|Emerging",
      "difficulty": "Beginner|Intermediate|Advanced|Expert",
      "resources_needed": ["Diagram", "Code Example"]
    }}
  ]
}}"""

RESEARCH_PLAN_PROMPT = """Generate structured research objectives for:

Topic: {topic}
Modules: {module_titles}
Concepts: {concept_names}

For each research category, provide:
1. Questions to answer (2-4 specific questions)
2. Priority (Critical, Important, Nice-to-have)
3. Expected output format

Categories: Definition, History, Theory, Formula, Applications, Industry, Research Papers, Benchmarks, Case Studies, Statistics, Misconceptions, Interview Questions, Best Practices, Limitations

Return ONLY valid JSON:
{{
  "categories": {{
    "Definition": {{
      "questions": ["What is X?", "Why is it important?"],
      "priority": "Critical",
      "expected_output": "Clear definition with context"
    }}
  }}
}}"""