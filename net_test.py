import os, time, requests
from dotenv import load_dotenv
load_dotenv()

tests = {
    "google": "https://www.google.com",
    "tavily": "https://api.tavily.com",
    "serper": "https://google.serper.dev",
    "llm": "https://api.groq.com",  # change to your LLM provider URL
}
for name, url in tests.items():
    t = time.time()
    try:
        r = requests.get(url, timeout=10)
        print(name, r.status_code, f"{time.time()-t:.1f}s")
    except Exception as e:
        print(name, "FAILED:", type(e).__name__, e)
