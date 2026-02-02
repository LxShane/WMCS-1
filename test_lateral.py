import sys
import os
from termcolor import colored

sys.path.append(os.getcwd())
from main import WMCS_Kernel

def run_lateral_test():
    print(colored("### STRESS TEST: LATERAL THINKING (Navigation) ###", "magenta", attrs=['bold']))
    
    wmcs = WMCS_Kernel()
    wmcs.load_data()

    # Query specifically triggers the "EQUIVALENCE" or "FUNCTION" dimension
    query = "What serves the same functional role as a Cat Paw in humans?"
    
    print(colored(f"\nQuery: '{query}'", "cyan"))
    print(colored("Expectation: Navigator should choose 'fills_role' or 'equivalent_to' link.", "white"))
    
    response = wmcs.process_query(query)
    
    print(colored("\n>>> SYSTEM RESPONSE:", "green"))
    print(response)

if __name__ == "__main__":
    run_lateral_test()
