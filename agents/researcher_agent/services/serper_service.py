# services/serper_service.py
import requests

 # get this from serper.dev
import os
from dotenv import load_dotenv

load_dotenv()

SERPER_API_KEY = os.getenv("SERPER_API_KEY")

def serper_search(query: str, max_results: int = 3):
    """
    Call Serper API to fetch search results.
    Returns a list of dicts with title, url, snippet, and content.
    """
    url = "https://google.serper.dev/search"
    headers = {"X-API-KEY": SERPER_API_KEY, "Content-Type": "application/json"}
    payload = {"q": query, "num": max_results}

    try:
        response = requests.post(url, headers=headers, json=payload)
        response.raise_for_status()
        data = response.json()

        results = []
        for item in data.get("organic", [])[:max_results]:
            results.append({
                "title": item.get("title", "No Title"),
                "url": item.get("link", ""),
                "snippet": item.get("snippet", ""),
                "content": item.get("snippet", "")
            })
        return results

    except Exception as e:
        print(f"⚠️ Serper search failed: {e}")
        return []
