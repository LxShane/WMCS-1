import sys
import os
from termcolor import colored

sys.path.append(os.getcwd())
from system_a_cognitive.meta.researcher import ResearchAgent
from main import WMCS_Kernel

def run_crispr_stress_test():
    print(colored("### STRESS TEST: AUTO-RESEARCH 'CRISPR-Cas9' ###", "magenta", attrs=['bold']))
    
    # 1. AUTONOMOUS RESEARCH
    print(colored("\nPHASE 1: RESEARCHING...", "yellow"))
    agent = ResearchAgent()
    # Topic specific enough to get mechanisms
    agent.conduct_research("Mechanism of CRISPR-Cas9 gene editing", max_steps=3)
    
    # 2. COGNITIVE VERIFICATION
    print(colored("\nPHASE 2: VERIFYING KNOWLEDGE...", "yellow"))
    wmcs = WMCS_Kernel()
    wmcs.load_data() # Reload to get new blocks
    
    query = "How does Cas9 know where to cut the DNA?"
    print(colored(f"Asking System: '{query}'", "cyan"))
    
    response = wmcs.process_query(query)
    
    print(colored("\n>>> SYSTEM RESPONSE:", "green"))
    print(response)

if __name__ == "__main__":
    run_crispr_stress_test()
