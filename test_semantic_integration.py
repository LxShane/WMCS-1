import sys
import os
from termcolor import colored

sys.path.append(os.getcwd())
from main import WMCS_Kernel

def run_semantic_test():
    print(colored("### INTEGRATION TEST: SEMANTIC KERNEL ###", "magenta", attrs=['bold']))
    
    wmcs = WMCS_Kernel()
    wmcs.load_data()
    
    # Query with NO keyword overlap, but strong semantic overlap
    query = "the sharp tool of a feline" 
    
    print(colored(f"\nQuery: '{query}'", "cyan"))
    print(colored("Expectation: Should find 'Cat Paw' or 'Claws' via Vector Search.", "white"))
    
    response = wmcs.process_query(query)

if __name__ == "__main__":
    run_semantic_test()
