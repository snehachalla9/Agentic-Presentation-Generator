# from ddgs import DDGS

# def ddg_search(query):

#     results = []

#     with DDGS() as ddgs:

#         data = ddgs.text(query, max_results=5)

#         for item in data:

#             results.append({
#                 "title": item["title"],
#                 "url": item["href"],
#                 "content": item["body"],
#                 "source": "DuckDuckGo"
#             })

#     return results
#!/usr/bin/env python3
"""
DuckDuckGo Search Service
"""

from typing import List, Dict, Any

try:
    from duckduckgo_search import DDGS
    DDGS_AVAILABLE = True
except ImportError:
    DDGS_AVAILABLE = False
    print("⚠️ duckduckgo-search not installed. Install with: pip install duckduckgo-search")


def duckduckgo_search(query: str, max_results: int = 5) -> List[Dict[str, Any]]:
    """
    Search using DuckDuckGo
    
    Args:
        query: Search query
        max_results: Maximum number of results
        
    Returns:
        List of search results
    """
    if not DDGS_AVAILABLE:
        print(f"⚠️ DuckDuckGo not available. Query: {query[:50]}...")
        return []
    
    try:
        with DDGS() as ddgs:
            results = []
            for r in ddgs.text(query, max_results=max_results):
                results.append({
                    "title": r.get("title", "No Title"),
                    "url": r.get("href", r.get("url", "")),
                    "content": r.get("body", r.get("snippet", "")),
                    "score": 0.5  # DuckDuckGo doesn't provide scores
                })
            return results
    except Exception as e:
        print(f"⚠️ DuckDuckGo search failed: {e}")
        return []


# Alias for backward compatibility
def duckduckgo_search_sync(query: str, max_results: int = 5) -> List[Dict[str, Any]]:
    """Alias for duckduckgo_search"""
    return duckduckgo_search(query, max_results)