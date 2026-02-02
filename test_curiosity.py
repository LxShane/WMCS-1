import sys
import os
from termcolor import colored

sys.path.append(os.getcwd())
from main import WMCS_Kernel

def run_curiosity_test():
    print(colored("### STRESS TEST: EPISTEMIC CURIOSITY (Auto-Research) ###", "magenta", attrs=['bold']))
    
    wmcs = WMCS_Kernel()
    wmcs.load_data()

    # Query about a topic we DEFINITELY don't have (Quantum Physics)
    # used unique words to avoid "mechanism" or "explain" matching irrelevant blocks.
    query = "Quantum Entanglement"
    
    print(colored(f"\nQuery: '{query}'", "cyan"))
    print(colored("Expectation: Gap Detection -> Auto-Research -> Successful Answer.", "white"))
    
    response = wmcs.process_query(query)
    
    print(colored("\n>>> SYSTEM RESPONSE:", "green"))
    print(response)

if __name__ == "__main__":
    run_curiosity_test()
