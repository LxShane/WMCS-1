import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

class Config:
    # LLM Settings
    LLM_API_KEY = os.getenv("LLM_API_KEY", "your-gemini-key") 
    LLM_MODEL = os.getenv("LLM_MODEL", "gemini-2.0-flash")
    SERPAPI_KEY = os.getenv("SERPAPI_KEY", None)
    
    # System Settings
    DEBUG_MODE = True
