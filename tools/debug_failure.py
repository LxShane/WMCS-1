import requests
import json
import time
from termcolor import colored

API_URL = "http://127.0.0.1:8000/query"

def run_debug():
    topic = "What is the purpose of a narwhal tusk?"
    print(colored(f"DEBUG: Testing '{topic}'...", "yellow"))
    
    try:
        # 1. Send Query
        res = requests.post(API_URL, json={"text": topic, "allow_research": True}, timeout=120)
        
        if res.status_code == 200:
            data = res.json()
            print(colored("\n=== RESPONSE ===", "cyan"))
            print(data.get("text", "No Text"))
            print(colored("\n=== VISITED NODES ===", "cyan"))
            print(data.get("visited_nodes", []))
            
            # Check if research actually happened by checking response text
            # We can't see server logs here easily, but we can infer from visited nodes
            # If visited nodes are empty, then injection failed.
        else:
            print(colored(f"ERROR: {res.text}", "red"))
            
    except Exception as e:
        print(colored(f"CRASH: {e}", "red"))

if __name__ == "__main__":
    run_debug()
