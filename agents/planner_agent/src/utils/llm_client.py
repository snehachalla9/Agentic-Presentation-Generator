from groq import Groq
from config.settings import Config

class LLMClient:
    def __init__(self):
        self.client = Groq(api_key=Config.GROQ_API_KEY)
        self.model = Config.MODEL_NAME
        print(f"✅ LLM Client initialized with Groq: {self.model}")
    
    def get_completion(self, messages, temperature=Config.TEMPERATURE):
        # Ensure messages are properly formatted for Groq
        groq_messages = []
        for msg in messages:
            # Make sure content is a string, not None
            content = msg.get("content", "")
            if content is None:
                content = ""
            groq_messages.append({
                "role": msg["role"],
                "content": str(content)  # Convert to string to be safe
            })
        
        # Remove any empty messages
        groq_messages = [m for m in groq_messages if m["content"] and m["content"].strip()]
        
        # Make request to Groq
        response = self.client.chat.completions.create(
            model=self.model,
            messages=groq_messages,
            temperature=temperature,
            max_tokens=2000
        )
        
        return response.choices[0].message.content