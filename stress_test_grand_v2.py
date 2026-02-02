import sys
import os
from termcolor import colored
import time

# Ensure path availability
sys.path.append(os.getcwd())
from main import WMCS_Kernel

def print_header(text):
    print(colored(f"\n{'='*60}", "magenta"))
    print(colored(f"   {text}", "magenta", attrs=['bold']))
    print(colored(f"{'='*60}\n", "magenta"))

def run_grand_test():
    print_header("WMCS GRAND UNIFIED STRESS TEST v2")
    
    wmcs = WMCS_Kernel()
    wmcs.load_data()
    
    tests = [
        {
            "domain": "Physics / Deep Research",
            "query": "Explain the role of Control Rods in a Nuclear Reactor",
            "expect": "Gap Detection -> Research -> Absorption of Neutrons"
        },
        {
            "domain": "Ontology / Logic Gate",
            "query": "Can the concept of Justice (Group 65) physically kick a ball?",
            "expect": "Symbolic Rejection (Abstract cannot perform Physical Action)"
        },
        {
            "domain": "Biology / Semantic Search",
            "query": "The filtering organ of the blood",
            "expect": "Vector Search finds 'Kidney' (if present) or Research finds it."
        },
        {
            "domain": "Lateral Thinking / Analogy",
            "query": "What acts as the brain of a computer?",
            "expect": "Agentic Nav -> CPU (via Function)"
        }
    ]

    results = []

    for i, test in enumerate(tests):
        print(colored(f"\n>>> TEST {i+1}: {test['domain']}", "yellow", attrs=['bold']))
        print(colored(f"Query: '{test['query']}'", "cyan"))
        print(colored(f"Expected: {test['expect']}", "white"))
        
        start_time = time.time()
        try:
            # We enforce research allowed for these tests
            response = wmcs.process_query(test['query'], allow_research=True)
            duration = time.time() - start_time
            
            print(colored(f"\n[SYSTEM RESPONSE ({duration:.1f}s)]:", "green"))
            print(response)
            results.append({"test": test['domain'], "status": "COMPLETED", "response": response[:100] + "..."})
            
        except Exception as e:
            print(colored(f"CRITICAL ERROR: {e}", "red"))
            results.append({"test": test['domain'], "status": "FAILED", "response": str(e)})

    # Summary
    print_header("TEST SUMMARY")
    for r in results:
        status_color = "green" if r['status'] == "COMPLETED" else "red"
        print(f"{r['test']:<30} | {colored(r['status'], status_color)}")

if __name__ == "__main__":
    run_grand_test()
