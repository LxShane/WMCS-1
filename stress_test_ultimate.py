import sys
import os
import random
import time
from termcolor import colored

sys.path.append(os.getcwd())
from main import WMCS_Kernel

def print_header(text):
    print(colored(f"\n{'#'*70}", "magenta"))
    print(colored(f"   {text}", "magenta", attrs=['bold']))
    print(colored(f"{'#'*70}\n", "magenta"))

def run_ultimate_test():
    print_header("WMCS ULTIMATE STRESS TEST (MULTI-ITERATION)")
    
    wmcs = WMCS_Kernel()
    wmcs.load_data()
    
    # DATASET
    test_suite = {
        "DEEP RESEARCH (Physics/Science)": [
            {"q": "How does a Tokamak fusion reactor work?", "k": ["plasma", "magnetic", "confinement"]},
            {"q": "Mechanism of photosynthesis light reaction", "k": ["chlorophyll", "photon", "ATP"]},
            {"q": "How works a Stirling Engine?", "k": ["heat", "piston", "gas"]}
        ],
        "SYMBOLIC LOGIC (Ontology/Boolean)": [
            {"q": "Can the concept of Democracy eat a burger?", "k": ["CANNOT_CONCLUDE", "Abstract", "Physical"]},
            {"q": "Does a rock have intentions?", "k": ["CANNOT_CONCLUDE", "Inanimate", "Mental"]},
            {"q": "Can a triangle run a marathon?", "k": ["CANNOT_CONCLUDE", "Abstract", "Action"]}
        ],
        "SEMANTIC RETRIEVAL (Vector Memory)": [
            {"q": "The powerhouse of the cell", "k": ["block", "mitochondria"]}, # Assuming it finds or researches it
            {"q": "The sharp tools of a feline", "k": ["cat", "paw", "claws"]},
            {"q": "The thinking rock of a computer", "k": ["cpu", "processor"]}
        ]
    }
    
    # CONFIG
    ITERATIONS = 2 # Run 2 FULL rounds of random picks
    
    score = 0
    total = 0
    
    for round_idx in range(ITERATIONS):
        print_header(f"ROUND {round_idx + 1} / {ITERATIONS}")
        
        # Pick 1 random question from EACH domain per round
        for domain, questions in test_suite.items():
            case = random.choice(questions)
            query = case["q"]
            keywords = case["k"]
            
            print(colored(f"DOMAIN: {domain}", "yellow"))
            print(colored(f"QUERY:  '{query}'", "cyan"))
            
            start = time.time()
            try:
                # Force research enabled
                response = wmcs.process_query(query, allow_research=True)
                elapsed = time.time() - start
                
                # Check keywords (Case insensitive)
                response_lower = str(response).lower()
                results_logs = str(wmcs.vector_store.vectors) # simplistic peek if needed but response is better
                
                # For specific logic checks, we look at the contract output in stdout usually, 
                # but here we check the text response or internal logs if captured.
                # Since we capture stdout in the tool, checking the returned response string is best.
                
                passed = False
                matches = [k for k in keywords if k.lower() in response_lower]
                
                if len(matches) > 0:
                    passed = True
                
                # Special handling for Logic which might output "CANNOT_CONCLUDE"
                if "SYMBOLIC" in domain and ("cannot_conclude" in response_lower or "reject" in response_lower):
                    passed = True
                    
                status = "PASS" if passed else "FAIL"
                color = "green" if passed else "red"
                
                print(colored(f"RESULT: {status} (Matches: {matches}) [{elapsed:.1f}s]", color, attrs=['bold']))
                if not passed:
                    print(colored(f"  [DEBUG] Response was: {str(response)[:200]}...", "white"))

                if passed: score += 1
                total += 1
                
            except Exception as e:
                print(colored(f"ERROR: {e}", "red"))
                total += 1

            print("-" * 50)

    print_header("FINAL REPORT")
    print(f"Total Tests: {total}")
    print(f"Passed:      {score}")
    print(f"Score:       {int((score/total)*100)}%")

if __name__ == "__main__":
    run_ultimate_test()
