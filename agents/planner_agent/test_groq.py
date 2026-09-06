from groq import Groq
import os
from dotenv import load_dotenv

load_dotenv()

print("="*50)
print("Testing Groq Connection")
print("="*50)

api_key = os.getenv("GROQ_API_KEY")
# Read model from .env file, NOT hardcoded
model = os.getenv("MODEL_NAME", "llama-3.3-70b-versatile")

if not api_key:
    print("❌ GROQ_API_KEY not found in .env file!")
    exit(1)

print(f"✅ API Key found: {api_key[:10]}...{api_key[-5:]}")
print(f"✅ Using model: {model}")

try:
    print("🔄 Connecting to Groq API...")
    client = Groq(api_key=api_key)
    
    print("🔄 Sending test request...")
    response = client.chat.completions.create(
        model=model,  # Now using model from .env
        messages=[{"role": "user", "content": "Say 'Groq API is working perfectly!'"}],
        temperature=0.1,
        max_tokens=50
    )
    
    print(f"✅ Success! Response: {response.choices[0].message.content}")
    print("\n🎉 Groq API is ready!")
    print("Now run: python main.py")
    
except Exception as e:
    print(f"❌ Error: {e}")
    print("\n📝 Troubleshooting:")
    print("1. Check your .env file has MODEL_NAME=llama-3.3-70b-versatile")
    print("2. Run: cat .env to verify")
