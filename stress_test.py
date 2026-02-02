import sys
import os
from termcolor import colored

# Ensure we can import system modules
sys.path.append(os.getcwd())
from main import WMCS_Kernel

def run_stress_test():
    print(colored("### INITIALIZING STRESS TEST ###", "magenta", attrs=['bold']))
    wmcs = WMCS_Kernel()
    wmcs.load_data()
    
    tests = [
        {
            "name": "Category Error (Logic Check)",
            "query": "Can the concept of Justice eat food?",
            "expectation": "Should identifying Type Mismatch (Abstract vs Living)."
        },
        {
            "name": "Compositional Property (Deep Recursion)",
            "query": "Is a Red Cat capable of silent walking?",
            "expectation": "Should traverse Cat -> Paw -> Adipose Pads -> Silent Walk. Should ignore 'Red'."
        },
        {
            "name": "Unknown Entity (Safety Check)",
            "query": "Is a Glorp dangerous to humans?",
            "expectation": "Should cite Ambiguity/Unknown status and refuse to guess."
        }
    ]
    
    for i, test in enumerate(tests):
        print("\n" + "="*60)
        print(colored(f"TEST {i+1}: {test['name']}", "yellow", attrs=['bold']))
        print(f"Query: {test['query']}")
        print(f"Expectation: {test['expectation']}")
        print("-" * 60)
        
        response = wmcs.process_query(test['query'])
        
        print(colored("\n>>> SYSTEM RESPONSE:", "green"))
        print(response)
        print("="*60 + "\n")

if __name__ == "__main__":
    run_stress_test()
