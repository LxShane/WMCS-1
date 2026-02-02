import sys
import os
from termcolor import colored

sys.path.append(os.getcwd())
from main import WMCS_Kernel

def run_integration_test():
    print(colored("### INTEGRATION TEST: KERNEL + DEEP RESEARCHER ###", "magenta", attrs=['bold']))
    
    wmcs = WMCS_Kernel()
    wmcs.load_data()

    # New complex topic
    query = "Explain the mechanism of RNA Polymerase"
    
    print(colored(f"\nQuery: '{query}'", "cyan"))
    print(colored("Expectation: Gap -> DeepResearchAgent Triggered -> Hypothesis/Recursive Logs -> Answer.", "white"))
    
    response = wmcs.process_query(query)
    
    print(colored("\n>>> SYSTEM RESPONSE:", "green"))
    print(response)

if __name__ == "__main__":
    run_integration_test()
