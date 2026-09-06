from langgraph.graph import StateGraph, START, END

from .state import AgentState
from agents.planner_agent.src.agents.planner_agent_v4 import UniversalPlanner
from agents.researcher_agent.researcher import ResearcherAgent
from agents.content_gen.agent import SlideContentAgent
from agents.ppt_generator_v2.generator import PPTGeneratorV2
from pathlib import Path
from pptx import Presentation
from agents.supervisor.supervisor import Supervisor
from agents.researcher_agent.services.llm_service import LLMService

def planner_node(state: AgentState):

    print("\n🤖 Real Planner Agent is running...")
    print("Topic:", state["topic"])

    try:
        planner = UniversalPlanner()

        plan = planner.create_presentation(
            state["topic"]
        )

        return {
            "plan": plan,
            "current_agent": "planner"
        }

    except Exception as e:
         error_message = f"Planner failed: {str(e)}"
         print(f"❌ {error_message}")
         return {
            "current_agent": "planner",
            "errors": state.get("errors", []) + [error_message]
        }
def planner_validator_node(state: AgentState):

    print("\n🔎 Validating Planner output...")

    validation_errors = []

    plan = state.get("plan")

    # Check whether plan exists
    if not plan:
        validation_errors.append("Plan is missing")

    # Check whether plan has modules
    elif not plan.get("modules"):
        validation_errors.append("Plan contains no modules")

    is_valid = len(validation_errors) == 0

    if is_valid:
        print("✅ Planner validation passed")
    else:
        print("❌ Planner validation failed")
        for error in validation_errors:
            print(f"   - {error}")

    return {
        "validation_results": {
            "planner_valid": is_valid,
            "errors": validation_errors
        },
        "current_agent": "planner_validator"
    }


def route_after_planner_validation(state: AgentState):

    validation = state.get("validation_results", {})

    if validation.get("planner_valid"):
        return "research"

    return END
def research_node(state: AgentState):

    print("\n🔍 Research Agent is running...")

    try:
        researcher = ResearcherAgent()

        research_output = researcher.research_from_planner(
            state["plan"]
        )

        return {
            "research": research_output,
             "current_agent": "research"
        }

    except Exception as e:
        error_message = f"Research failed: {str(e)}"

        print(f"❌ {error_message}")

        return {
            "current_agent": "research",
            "errors": state.get("errors", []) + [error_message]
        }
def research_validator_node(state: AgentState):

    print("\n🔎 Validating Research output...")

    validation_errors = []

    research = state.get("research")

    if not research:
        validation_errors.append("Research output is missing")

    elif not isinstance(research, dict):
        validation_errors.append("Research output must be a dictionary")

    # Add your project-specific checks here
    elif len(research) == 0:
        validation_errors.append("Research output is empty")

    is_valid = len(validation_errors) == 0

    if is_valid:
        print("✅ Research validation passed")
    else:
        print("❌ Research validation failed")
        for error in validation_errors:
            print(f"   - {error}")

    return {
        "validation_results": {
            **state.get("validation_results", {}),
            "research_valid": is_valid,
            "research_errors": validation_errors
        },
        "current_agent": "research_validator"
    }
def route_after_research_validation(state: AgentState):

    validation = state.get("validation_results", {})

    if validation.get("research_valid"):
        return "content"

    return END
def content_node(state: AgentState):

    print("\n📝 Content Agent is running...")

    try:
        llm = LLMService()
        agent = SlideContentAgent(
            research_output=state["research"],
            llm=llm
        )

        content_output = agent.run()

        return {
            "content": content_output,
            "current_agent": "content"
        }

    except Exception as e:
        error_message = f"Content failed: {str(e)}"

        print(f"❌ {error_message}")

        return {
            "current_agent": "content",
            "errors": state.get("errors", []) + [error_message]
        }
def content_validator_node(state: AgentState):

    print("\n🔎 Validating Content output...")

    validation_errors = []

    content = state.get("content")

    # 1. Content must exist
    if not content:
        validation_errors.append("Content output is missing")

    # 2. Content must be a dictionary
    elif not isinstance(content, dict):
        validation_errors.append("Content output must be a dictionary")

    # 3. Content should contain slides
    elif not content.get("slides"):
        validation_errors.append("Content contains no slides")

    # 4. Check number of slides
    elif len(content["slides"]) == 0:
        validation_errors.append("Content contains zero slides")

    is_valid = len(validation_errors) == 0

    if is_valid:
        print("✅ Content validation passed")
    else:
        print("❌ Content validation failed")

        for error in validation_errors:
            print(f"   - {error}")

    return {
        "validation_results": {
            **state.get("validation_results", {}),
            "content_valid": is_valid,
            "content_errors": validation_errors
        },
        "current_agent": "content_validator"
    }
def route_after_content_validation(state: AgentState):

    validation = state.get("validation_results", {})

    if validation.get("content_valid"):
        return "ppt"

    return END
def ppt_node(state: AgentState):

    print("\n🎨 PPT Generator is running...")

    try:
        generator = PPTGeneratorV2()

        output_path = generator.generate(
            presentation_data=state["content"],
            output_path="output/final_v2.pptx"
        )

        return {
            "ppt": output_path,
            "current_agent": "ppt"
        }

    except Exception as e:
        error_message = f"PPT generation failed: {str(e)}"

        print(f"❌ {error_message}")

        return {
            "current_agent": "ppt",
            "errors": state.get("errors", []) + [error_message]
        }
def ppt_validator_node(state: AgentState):

    print("\n🔎 Validating PPT output...")

    validation_errors = []

    ppt_path = state.get("ppt")

    # 1. PPT output must exist
    if not ppt_path:
        validation_errors.append("PPT output is missing")

    else:
        path = Path(ppt_path)

        # 2. File must exist
        if not path.exists():
            validation_errors.append(
                f"PPT file does not exist: {ppt_path}"
            )

        # 3. Must be .pptx
        elif path.suffix.lower() != ".pptx":
            validation_errors.append(
                "PPT file must have .pptx extension"
            )

        else:
            try:
                # 4. PPT must be readable
                prs = Presentation(str(path))

                # 5. PPT must contain slides
                if len(prs.slides) == 0:
                    validation_errors.append(
                        "PPT contains no slides"
                    )

            except Exception as e:
                validation_errors.append(
                    f"PPT cannot be opened: {e}"
                )

    is_valid = len(validation_errors) == 0

    if is_valid:
        print("✅ PPT validation passed")
    else:
        print("❌ PPT validation failed")

        for error in validation_errors:
            print(f"   - {error}")

    return {
        "validation_results": {
            **state.get("validation_results", {}),
            "ppt_valid": is_valid,
            "ppt_errors": validation_errors
        },
        "current_agent": "ppt_validator"
    }
def supervisor_node(state: AgentState):

    print("\n🧠 Supervisor is deciding what to do next...")

    supervisor = Supervisor()

    next_agent = supervisor.decide(state)

    print(f"➡️ Next agent: {next_agent}")

    return {
        "next_agent": next_agent,
        "current_agent": "supervisor"
    }
def route_from_supervisor(state: AgentState):

    next_agent = state.get("next_agent")

    return next_agent

def build_graph():

    workflow = StateGraph(AgentState)

    workflow.add_node(
        "planner",
        planner_node
    )
    workflow.add_node(
        "planner_validator",
        planner_validator_node
    )

    workflow.add_node(
        "research",
        research_node
    )
    workflow.add_node(
    "research_validator",
    research_validator_node
)
    workflow.add_node(
    "content",
    content_node
)
    workflow.add_node(
    "content_validator",
    content_validator_node
)
    workflow.add_node(
    "ppt",
    ppt_node
)
    workflow.add_node(
    "ppt_validator",
    ppt_validator_node
)
    workflow.add_node(
    "supervisor",
    supervisor_node
    )
    workflow.add_edge(START, "supervisor")
    workflow.add_conditional_edges(
    "supervisor",
    route_from_supervisor,
    {
        "planner": "planner",
        "research": "research",
        "content": "content",
        "ppt": "ppt",
        "finish": END
    }
)
    workflow.add_edge(
        "planner",
        "planner_validator")
    workflow.add_edge(
    "planner_validator",
    "supervisor"
)
    workflow.add_edge("research", 
                       "research_validator")
    workflow.add_edge(
    "research_validator",
    "supervisor"
)
    workflow.add_edge(
    "content",
    "content_validator"
)
    workflow.add_edge(
    "content_validator",
    "supervisor"
)
    workflow.add_edge(
    "ppt",
    "ppt_validator"
)
    workflow.add_edge(
    "ppt_validator",
    "supervisor"
)
    
    return workflow.compile()