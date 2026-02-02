import sys
import os
from termcolor import colored

sys.path.append(os.getcwd())
from main import WMCS_Kernel

def run_final_exam():
    print(colored("╔══════════════════════════════════════════╗", "magenta"))
    print(colored("║       WMCS FINAL EXAM (STRESS TEST)      ║", "magenta"))
    print(colored("╚══════════════════════════════════════════╝", "magenta"))
    
    wmcs = WMCS_Kernel()
    wmcs.load_data()

    tests = [
        {
            "name": "TEST 1: AMBIGUITY & DISAMBIGUATION",
            "query": "Why does a bank have branches but no leaves?",
            "goal": "Must distinguish Financial Institution (61) vs Plant (22).",
            "hard_pass": "Must NOT talk about photosynthesis."
        },
        {
            "name": "TEST 2: LATERAL THINKING (Analogy)",
            "query": "What is the nervous system of a car?",
            "goal": "Must map 'Communication Role' to 'Electrical Wiring/ECU'.",
            "hard_pass": "Must NOT look for biological neurons in a car."
        },
        {
            "name": "TEST 3: EPISTEMIC CURIOSITY (Unknown)",
            "query": "What is the key difficulty in the P versus NP problem?",
            "goal": "Trigger Auto-Research -> Learn -> Answer.",
            "hard_pass": "Must NOT passive fail ('I don't know')."
        },
        {
            "name": "TEST 4: ONTOLOGICAL VALIDITY (Impossible)",
            "query": "Can the number 5 eat a sandwich?",
            "goal": "Reject: Category Error (Mathematical Objects cannot perform Biological Actions).",
            "hard_pass": "Must NOT try to simulate eating."
        }
    ]

    score = 0
    
    for i, test in enumerate(tests):
        print(colored(f"\n\n{test['name']}", "yellow", attrs=['bold']))
        print(f"Q: {test['query']}")
        print(f"Goal: {test['goal']}")
        
        try:
            response = wmcs.process_query(test['query'])
            print(colored(f"\n>>> SYSTEM RESPONSE:\n{response}", "cyan"))
            
            # Simple keyword checks for automated preliminary scoring
            # (Real scoring requires human/agent review of the logic trace)
            
        except Exception as e:
            print(colored(f"CRITICAL FAILURE: {e}", "red"))

    print(colored("\n\n═══ EXAM COMPLETE ═══", "magenta"))
    print("Review the logs above to assign the Final Grade.")

if __name__ == "__main__":
    run_final_exam()
