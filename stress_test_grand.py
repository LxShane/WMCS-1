import sys
import os
from termcolor import colored

sys.path.append(os.getcwd())
from main import WMCS_Kernel

def run_grand_test():
    print(colored("### INITIATING GRAND SYSTEM STRESS TEST ###", "magenta", attrs=['bold']))
    print(colored("Verifying 3 Layers: Ontology, Memory, Depth\n", "magenta"))
    
    wmcs = WMCS_Kernel()
    wmcs.load_data()

    tests = [
        {
            "layer": "LAYER 1: ONTOLOGY (Logic Rules)",
            "query": "Can the concept of Justice be physically located in Paris?",
            "expected_logic": "Should detect Category Mismatch (Abstract vs Physical Location)."
        },
        {
            "layer": "LAYER 2: MEMORY (Research Verification)",
            "query": "What is the role of the Toroidal Field in a Tokamak?",
            "expected_logic": "Should access the specific 'Fusion' blocks ingested by the Research Agent."
        },
        {
            "layer": "LAYER 3: DEPTH (Recursive Traversal)",
            "query": "Does a Cat contain Collagen?",
            "expected_logic": "Should traverse: Cat -> Has Part (Paw) -> Has Part (Pads) -> Composition (Collagen)."
        }
    ]

    for i, test in enumerate(tests):
        print(colored("="*80, "cyan"))
        print(colored(f"{test['layer']}", "yellow", attrs=['bold']))
        print(f"Query: {test['query']}")
        print(f"Expectation: {test['expected_logic']}")
        print(colored("-" * 80, "cyan"))
        
        response = wmcs.process_query(test['query'])
        
        print(colored("\n>>> SYSTEM RESPONSE:", "green"))
        print(response)
        print("\n")

if __name__ == "__main__":
    run_grand_test()
