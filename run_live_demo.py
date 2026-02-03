
import sys
import os
from termcolor import colored
from main import WMCS_Kernel

def run_live():
    print(colored("### INITIALIZING WMCS LIVE DEMO ###", "magenta", attrs=['bold']))
    
    # Initialize Kernel
    kernel = WMCS_Kernel()
    kernel.load_data()
    
    # Force a novel query
    query = "Explain the mechanism of CRISPR Prime Editing compared to Cas9."
    
    print(colored(f"\n### PROCESSING QUERY: '{query}' ###", "cyan", attrs=['bold']))
    
    # Run the full pipeline
    result = kernel.process_query(query, allow_research=True)
    
    print("\n" + "="*50)
    print(colored("FINAL RESPONSE:", "green"))
    print(result['text'])
    print("="*50)
    
    print(colored("\nVISITED NODES:", "yellow"))
    print(result['visited_nodes'])

if __name__ == "__main__":
    run_live()
