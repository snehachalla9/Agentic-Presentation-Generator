import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

class Config:
    # Use GROQ_API_KEY instead of OPENAI_API_KEY
    GROQ_API_KEY = os.getenv("GROQ_API_KEY")
    MODEL_NAME = os.getenv("MODEL_NAME", "llama3-8b-8192")
    TEMPERATURE = 0.2
    MAX_TOKENS = 2000
    
    # Validate API key exists
    if not GROQ_API_KEY:
        raise ValueError("""
        ❌ GROQ_API_KEY not found in .env file!
        
        Please create .env file with:
        GROQ_API_KEY=your-groq-api-key-here
        MODEL_NAME=llama3-8b-8192
        """)