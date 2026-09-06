#!/usr/bin/env python3
"""
Configuration for Researcher Agent
"""

import os
from dataclasses import dataclass
from dotenv import load_dotenv

# Load environment variables
load_dotenv()


@dataclass
class ResearchConfig:
    """Research Agent configuration"""
    
    # Search settings
    max_sources: int = 5 
    max_content_length: int = 500
    
    # LLM settings
    use_llm: bool = True
    llm_provider: str = "groq"
    llm_max_tokens: int = 500
    
    # Default planner file
    planner_file: str = "output/course_plan_v4.json"
    
    @classmethod
    def from_env(cls) -> 'ResearchConfig':
        """Load from environment variables"""
        return cls(
            max_sources_per_question=int(os.getenv("MAX_SOURCES", "5")),
            max_content_length=int(os.getenv("MAX_CONTENT_LENGTH", "500")),
            use_llm=os.getenv("USE_LLM", "true").lower() == "true",
            llm_provider=os.getenv("LLM_PROVIDER", "groq"),
            llm_max_tokens=int(os.getenv("LLM_MAX_TOKENS", "500")),
            planner_file=os.getenv("PLANNER_FILE", "output/course_plan_v4.json")
        )


# For backward compatibility with existing services
TAVILY_API_KEY = os.getenv("TAVILY_API_KEY", "")
GROQ_API_KEY = os.getenv("GROQ_API_KEY", "")
MODEL_NAME = os.getenv("MODEL_NAME", "llama-3.3-70b-versatile")


# Simple function to get config
def get_config():
    """Get configuration"""
    return ResearchConfig.from_env()