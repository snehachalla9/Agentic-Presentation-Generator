# import json
# import os
# import re
# from groq import Groq
# from dotenv import load_dotenv
# from datetime import datetime

# load_dotenv()

# class UniversalPlanner:
#     def __init__(self):
#         api_key = os.getenv("GROQ_API_KEY")
#         if not api_key:
#             raise ValueError("❌ GROQ_API_KEY not found in .env file!")
        
#         self.model = os.getenv("MODEL_NAME", "llama-3.3-70b-versatile")
#         self.client = Groq(api_key=api_key)
        
#         # Create directories with proper permissions
#         self.setup_directories()
#         print("✅ Planner Agent Ready - Extracts topic and subtopics only!\n")
    
#     def setup_directories(self):
#         """Create necessary directories with permissions"""
#         try:
#             # Get current working directory
#             current_dir = os.getcwd()
            
#             # Create output and data directories
#             output_dir = os.path.join(current_dir, "output")
#             data_dir = os.path.join(current_dir, "data")
            
#             os.makedirs(output_dir, exist_ok=True)
#             os.makedirs(data_dir, exist_ok=True)
            
#             # Set permissions (755 for directories)
#             os.chmod(output_dir, 0o755)
#             os.chmod(data_dir, 0o755)
            
#             print(f"📁 Directories created: {output_dir}, {data_dir}")
#         except Exception as e:
#             print(f"⚠️ Could not create directories: {e}")
    
#     def extract_user_requirements(self, prompt):
#         """Simple extraction - just get topic and organize subtopics"""
#         # Just return basic info, no slide logic needed
#         return {
#             'has_slide_specification': False,  # Planner doesn't care about slides
#             'has_duration_specification': False  # Planner doesn't care about duration
#         }
    
#     def create_presentation(self, user_prompt):
#         """Create simple topic + subtopics structure for research agent"""
        
#         # Build system prompt for simple topic + subtopics extraction
#         system_prompt = f"""You are a Planner Agent. Extract the TOPIC and SUBTOPICS from user request.

# USER REQUEST: {user_prompt}

# YOUR TASK:
# 1. Identify the main TOPIC from user request
# 2. Break down the topic into logical SUBTOPICS (5-15 subtopics based on complexity)
# 3. Each subtopic MUST have a description explaining what to research
# 4. Return ONLY valid JSON - no other text

# CRITICAL RULES:
# - NO slide numbers
# - NO slide titles  
# - NO slide count
# - NO estimated duration
# - NO audience or tone (unless explicitly asked by user, then include in metadata)
# - Focus ONLY on topic and subtopics with descriptions

# Output JSON structure:
# {{
#     "topic": "Main topic from user request",
#     "subtopics": [
#         {{
#             "key": "Subtopic name 1",
#             "description": "What to research about this subtopic"
#         }},
#         {{
#             "key": "Subtopic name 2", 
#             "description": "What to research about this subtopic"
#         }}
#     ],
#     "user_request": "{user_prompt[:100]}",
#     "slide_count_specified": null,
#     "duration_specified": null,
#     "audience": "NA",
#     "tone": "NA"
# }}

# Example:
# Input: "Create presentation on diabetic retinopathy"
# Output:
# {{
#     "topic": "Diabetic Retinopathy",
#     "subtopics": [
#         {{"key": "Definition and Causes", "description": "What is diabetic retinopathy and what causes it"}},
#         {{"key": "Risk Factors", "description": "Factors that increase risk of developing diabetic retinopathy"}},
#         {{"key": "Symptoms", "description": "Early and advanced symptoms of diabetic retinopathy"}}
#     ]
# }}

# Remember: Keep it SIMPLE. Research agent only needs topic + subtopics with descriptions."""
        
#         try:
#             response = self.client.chat.completions.create(
#                 model=self.model,
#                 messages=[
#                     {"role": "system", "content": system_prompt},
#                     {"role": "user", "content": user_prompt}
#                 ],
#                 temperature=0.3,
#                 max_tokens=2000
#             )
            
#             result_text = response.choices[0].message.content.strip()
            
#             # Clean markdown
#             if result_text.startswith('```json'):
#                 result_text = result_text[7:]
#             if result_text.startswith('```'):
#                 result_text = result_text[3:]
#             if result_text.endswith('```'):
#                 result_text = result_text[:-3]
            
#             result_text = result_text.strip()
#             plan = json.loads(result_text)
            
#             # Ensure required fields exist
#             plan = self.ensure_required_fields(plan, user_prompt)
            
#             return plan
            
#         except Exception as e:
#             print(f"⚠️ API Error: {e}")
#             return self.smart_fallback(user_prompt)
    
#     def ensure_required_fields(self, plan, user_prompt):
#         """Ensure only minimal required fields exist"""
#         required_fields = {
#             "topic": "General Topic",
#             "subtopics": [],
#             "user_request": user_prompt[:100],
#             "slide_count_specified": None,
#             "duration_specified": None,
#             "audience": "NA",
#             "tone": "NA"
#         }
        
#         for field, default_value in required_fields.items():
#             if field not in plan:
#                 plan[field] = default_value
        
#         # Ensure subtopics have key and description
#         if not plan["subtopics"]:
#             # Generate default subtopics if none exist
#             plan["subtopics"] = [
#                 {"key": "Introduction", "description": f"Overview of {plan['topic']}"},
#                 {"key": "Key Concepts", "description": f"Main concepts related to {plan['topic']}"},
#                 {"key": "Applications", "description": f"Practical applications of {plan['topic']}"},
#                 {"key": "Conclusion", "description": f"Summary and key takeaways about {plan['topic']}"}
#             ]
#         else:
#             # Convert string subtopics to key-value pairs if needed
#             new_subtopics = []
#             for subtopic in plan["subtopics"]:
#                 if isinstance(subtopic, str):
#                     new_subtopics.append({
#                         "key": subtopic,
#                         "description": f"Research and gather information about {subtopic.lower()}"
#                     })
#                 elif isinstance(subtopic, dict):
#                     if "key" not in subtopic:
#                         subtopic["key"] = "Information"
#                     if "description" not in subtopic:
#                         subtopic["description"] = f"Details about {subtopic.get('key', 'this topic')}"
#                     new_subtopics.append(subtopic)
#             plan["subtopics"] = new_subtopics
        
#         return plan
    
#     def smart_fallback(self, user_prompt):
#         """Simple fallback with topic and subtopics only"""
#         # Extract topic from prompt
#         topic = user_prompt.strip()
#         if len(topic) > 50:
#             topic = topic[:50]
        
#         # Generate generic subtopics
#         subtopics = [
#             {"key": "Introduction and Overview", "description": f"Basic understanding of {topic}"},
#             {"key": "Key Concepts", "description": f"Fundamental principles of {topic}"},
#             {"key": "Importance and Relevance", "description": f"Why {topic} matters in current context"},
#             {"key": "Applications", "description": f"Practical uses and implementations of {topic}"},
#             {"key": "Future Directions", "description": f"Emerging trends and future developments in {topic}"},
#             {"key": "Conclusion", "description": f"Summary and key takeaways about {topic}"}
#         ]
        
#         return {
#             "topic": topic,
#             "subtopics": subtopics,
#             "user_request": user_prompt[:100],
#             "slide_count_specified": None,
#             "duration_specified": None,
#             "audience": "NA",
#             "tone": "NA"
#         }
    
#     def display_plan(self, plan):
#         """Display the simple topic + subtopics structure"""
#         print("\n" + "="*80)
#         print(f"📊 PLANNER AGENT OUTPUT")
#         print("="*80)
        
#         print(f"\n📌 TOPIC: {plan.get('topic', 'N/A')}")
#         print(f"👥 AUDIENCE: {plan.get('audience', 'NA')}")
#         print(f"🎨 TONE: {plan.get('tone', 'NA')}")
        
#         if plan.get('slide_count_specified'):
#             print(f"📄 SLIDES: {plan['slide_count_specified']} (user specified)")
#         else:
#             print(f"📄 SLIDES: Not specified (research agent + slide generator will decide)")
        
#         print("\n📋 SUBTOPICS FOR RESEARCH AGENT:")
#         print("-"*80)
        
#         for i, subtopic in enumerate(plan.get('subtopics', []), 1):
#             if isinstance(subtopic, dict):
#                 print(f"\n{i}. 🔑 {subtopic.get('key', 'Point')}")
#                 print(f"   📝 {subtopic.get('description', 'No description')}")
#             else:
#                 print(f"\n{i}. 🔑 {subtopic}")
#                 print(f"   📝 Research and gather information")
        
#         print("\n" + "="*80)
    
#     def save_output(self, plan):
#         """Save for research agent"""
#         try:
#             # Use absolute paths
#             current_dir = os.getcwd()
#             output_dir = os.path.join(current_dir, "output")
#             data_dir = os.path.join(current_dir, "data")
            
#             # Ensure directories exist with proper permissions
#             os.makedirs(output_dir, exist_ok=True)
#             os.makedirs(data_dir, exist_ok=True)
#             # Save JSON without timestamp
#             json_path = os.path.join(output_dir, "planner_output.json")
#             with open(json_path, "w") as f:
#                 json.dump(plan, f, indent=2)
#             fixed_path = os.path.join(data_dir, "planner_output.json")
            
#             print(f"\n💾 Saved output to:")
#             print(f"   • {json_path}")
#             print(f"   • {fixed_path}")
            
#             return json_path
            
#         except Exception as e:
#             print(f"❌ Error saving file: {e}")
#             # Try saving to current directory as fallback
#             fallback_path = "planner_output.json"
#             with open(fallback_path, "w") as f:
#                 json.dump(plan, f, indent=2)
#             print(f"💾 Saved to fallback location: {fallback_path}")
#             return fallback_path

# def main():
#     print("="*80)
#     print("🤖 PLANNER AGENT - Extracts Topic & Subtopics for Research Agent")
#     print("="*80)
#     print("\n✨ This agent ONLY extracts:")
#     print("   • Main TOPIC")
#     print("   • SUBTOPICS with descriptions")
#     print("   • NO slide numbers, NO slide titles, NO formatting logic")
#     print("\n📝 Examples:")
#     print("   • 'Diabetic retinopathy'")
#     print("   • 'AI in healthcare for doctors'")
#     print("   • 'Climate change effects on agriculture'\n")
    
#     user_prompt = input("🎤 Enter your presentation topic: ").strip()
    
#     if not user_prompt:
#         user_prompt = "Diabetic retinopathy causes, symptoms, and treatment"
#         print(f"\n📝 Demo: '{user_prompt}'")
    
#     planner = UniversalPlanner()
    
#     print(f"\n🔄 Processing: '{user_prompt}'")
#     print("📝 Extracting topic and subtopics...\n")
    
#     plan = planner.create_presentation(user_prompt)
#     planner.display_plan(plan)
#     json_path = planner.save_output(plan)
    
#     print("\n" + "="*80)
#     print("✅ PLANNER AGENT OUTPUT READY FOR RESEARCH AGENT!")
#     print("="*80)
#     print("\n📤 For Research Agent :")
#     print(f"   • Input file: data/planner_output.json")
#     print(f"   • Structure: topic + subtopics with descriptions")
#     print("   • Research agent will use this to gather content")
#     print("\n📋 Sample input for your research agent:")
    
#     # Show just the essential part for research agent
#     research_input = {
#         "topic": plan["topic"],
#         "subtopics": plan["subtopics"]
#     }
#     print(json.dumps(research_input, indent=2))

# if __name__ == "__main__":
#     main()
# main.py
from src.agents.planner_agent_v4 import PlannerAgentV4

def main():

    print("=" * 60)
    print("PLANNER AGENT")
    print("=" * 60)

    topic = input("\nEnter topic: ").strip()

    if not topic:
        print("Topic cannot be empty.")
        return

    planner = PlannerAgentV4()

    plan = planner.generate_plan(topic)

    planner.display_plan(plan)

    planner.save_plan(
        plan,
        filename="planner_output.json"
    )

    print("\n✅ Planner JSON saved successfully.")
    print("📄 output/planner_output.json")


if __name__ == "__main__":
    main()