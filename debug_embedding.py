import sys
import os
from termcolor import colored

# Fix path
sys.path.append(os.getcwd())

from config import Config
from system_b_llm.interfaces.gemini_client import GeminiClient

def debug_embedding():
    print(colored("### DEBUG: GEMINI EMBEDDING ###", "magenta", attrs=['bold']))
    
    try:
        client = GeminiClient(Config.LLM_API_KEY, Config.LLM_MODEL)
        text = "Test string for embedding."
        print(colored(f"Target Text: '{text}'", "cyan"))
        
        print(colored("Attempting embed_content...", "yellow"))
        vector = client.embed_content(text)
        
        if vector:
            print(colored(f"SUCCESS. Vector Length: {len(vector)}", "green"))
            print(f"Sample: {vector[:5]}...")
        else:
            print(colored("FAIL. Vector is empty.", "red"))

    except Exception as e:
        print(colored(f"CRITICAL ERROR: {e}", "red"))
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    debug_embedding()
