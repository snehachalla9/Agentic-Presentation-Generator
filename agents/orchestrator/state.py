from typing import TypedDict, Dict, Any, List


class AgentState(TypedDict, total=False):
    topic: str
    plan: Dict[str, Any]
    research: Dict[str, Any]
    current_agent: str
    next_agent: str
    content: Dict[str, Any]
    ppt: str

    # Error handling
    errors: List[str]

    # Validation
    validation_results: Dict[str, Any]

    # Retry tracking
    retry_count: Dict[str, int]