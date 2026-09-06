# from tavily import TavilyClient
# from agents.researcher_agent.config import TAVILY_API_KEY

# client = TavilyClient(api_key=TAVILY_API_KEY)


# def tavily_search(query):

#     response = client.search(
#         query=query,
#         max_results=5
#     )

#     return response["results"]
#!/usr/bin/env python3
"""
Tavily Search Service
"""

import os
from typing import List, Dict, Any

# Try to import Tavily
try:
    from tavily import TavilyClient
    TAVILY_AVAILABLE = True
except ImportError:
    TAVILY_AVAILABLE = False
    print("⚠️ Tavily not installed. Install with: pip install tavily-python")

from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Get API key from environment
TAVILY_API_KEY = os.getenv("TAVILY_API_KEY", "")


def tavily_search(query: str, max_results: int = 5) -> List[Dict[str, Any]]:
    """
    Search using Tavily API
    
    Args:
        query: Search query
        max_results: Maximum number of results
        
    Returns:
        List of search results
    """
    if not TAVILY_AVAILABLE:
        print(f"⚠️ Tavily not available. Query: {query[:50]}...")
        return []
    
    if not TAVILY_API_KEY:
        print(f"⚠️ TAVILY_API_KEY not set. Query: {query[:50]}...")
        return []
    
    try:
        client = TavilyClient(api_key=TAVILY_API_KEY)
        
        response = client.search(
            query=query,
            search_depth="advanced",
            max_results=max_results,
            include_raw_content=True
        )
        
        results = []
        if response and "results" in response:
            for result in response["results"]:
                results.append({
                    "title": result.get("title", "No Title"),
                    "url": result.get("url", ""),
                    "content": result.get("content", ""),
                    "score": result.get("score", 0.0)
                })
        
        return results
        
    except Exception as e:
        print(f"⚠️ Tavily search failed: {e}")
        return []


# Alias for backward compatibility
def tavily_search_sync(query: str, max_results: int = 5) -> List[Dict[str, Any]]:
    """Alias for tavily_search"""
    return tavily_search(query, max_results)