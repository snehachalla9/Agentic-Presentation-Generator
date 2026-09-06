
import os
import time
from groq import Groq, RateLimitError
from dotenv import load_dotenv


class LLMService:

    def __init__(self):
        load_dotenv()

        self.client = Groq(
            api_key=os.getenv("GROQ_API_KEY")
        )

        self.model = os.getenv(
            "MODEL_NAME",
            "qwen/qwen3.8-27b"
        )

    def generate(
        self,
        system_prompt,
        user_prompt,
        temperature=0.3,
        max_tokens=1200,
        retries=5
    ):

        for attempt in range(retries):
            try:
                response = self.client.chat.completions.create(
                    model=self.model,
                    temperature=temperature,
                    max_tokens=max_tokens,
                    messages=[
                        {
                            "role": "system",
                            "content": system_prompt
                        },
                        {
                            "role": "user",
                            "content": user_prompt
                        }
                    ]
                )

                return response.choices[0].message.content

            except RateLimitError:
                wait = min(2 ** attempt, 10)
                print(f"⚠️ Rate limit reached. Retrying in {wait} seconds...")
                time.sleep(wait)

        raise Exception("Groq rate limit exceeded after multiple retries.")