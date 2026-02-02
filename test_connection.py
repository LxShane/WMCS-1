from config import Config
from system_b_llm.interfaces.gemini_client import GeminiClient

print("Testing Gemini Connection...")
try:
    client = GeminiClient(Config.LLM_API_KEY, Config.LLM_MODEL)
    print(f"Client initialized with model: {Config.LLM_MODEL}")
    response = client.completion("System: You are a test bot.", "Say 'Hello World'")
    print(f"Response: {response}")
except Exception as e:
    print(f"FAILED: {e}")
