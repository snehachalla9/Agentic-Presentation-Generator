import os, requests
from dotenv import load_dotenv
load_dotenv()

key = os.getenv("GROQ_API_KEY")
print("Key loaded:", bool(key), "| starts with:", (key or "")[:6])

r = requests.post(
    "https://api.groq.com/openai/v1/chat/completions",
    headers={"Authorization": f"Bearer {key}"},
    json={
        "model": "llama-3.3-70b-versatile",
        "messages": [{"role": "user", "content": "Say hi"}],
        "max_tokens": 20,
    },
    timeout=30,
)
print(r.status_code)
print(r.text[:500])
