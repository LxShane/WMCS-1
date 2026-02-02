import requests
import json
import time
from termcolor import colored

API_URL = "http://127.0.0.1:8000/query"

# FRESH TOPICS that the system definitely doesn't know yet
TOPICS = [
    # "How does a mantis shrimp see colors?",
    "What caused the Bronze Age Collapse?",
    # "Explain the triple point of water.",
    # "What is the main function of the amygdala?",
    # "How do mangroves filter salt water?"
]

def test_topic(i, topic):
    print(colored(f"\n[{i}/{len(TOPICS)}] Testing: '{topic}'", "yellow"))
    start = time.time()
    try:
        # 1. Send Query (Timeout 120s for research)
        res = requests.post(API_URL, json={"text": topic, "allow_research": True}, timeout=150)
        
        duration = time.time() - start
        
        if res.status_code == 200:
            data = res.json()
            answer = data.get("text", "")
            
            # Check for failure keywords
            failures = ["do not have enough information", "cannot answer", "no internal knowledge", "I don't know"]
            is_failure = any(f in answer for f in failures)
            
            if is_failure:
                print(colored(f"  FAILED ({duration:.1f}s): {answer[:100]}...", "red"))
                return False
            else:
                print(colored(f"  SUCCESS ({duration:.1f}s): {answer[:100]}...", "green"))
                # print(f"  Answer: {answer[:200]}...")
                return True
        else:
            print(colored(f"  ERROR {res.status_code}: {res.text}", "red"))
            return False
            
    except Exception as e:
        print(colored(f"  CRASH: {e}", "red"))
        return False

def run_stress_test():
    score = 0
    print(colored(f"=== STARTING FRESH STRESS TEST ({len(TOPICS)} UNSEEN TOPICS) ===", "magenta", attrs=['bold']))
    
    for i, topic in enumerate(TOPICS):
        if test_topic(i+1, topic):
            score += 1
        time.sleep(3) # Cooldown to let system settle
        
    print(colored(f"\n=== FINAL RESULT: {score}/{len(TOPICS)} ===", "magenta", attrs=['bold']))

if __name__ == "__main__":
    run_stress_test()
