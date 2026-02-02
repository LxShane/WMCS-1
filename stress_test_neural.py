import sys
import os
from termcolor import colored

sys.path.append(os.getcwd())
from system_a_cognitive.meta.researcher import ResearchAgent
from main import WMCS_Kernel

def run_neural_stress_test():
    print(colored("### STRESS TEST: MULTI-DIMENSIONAL (NEURAL NETWORKS) ###", "magenta", attrs=['bold']))
    
    agent = ResearchAgent()
    
    # PHASE 1: DUAL-DOMAIN RESEARCH
    # We need both sides to allow Lateral Thinking
    print(colored("\nPHASE 1: RESEARCHING DOMAINS...", "yellow"))
    
    # 1. Artificial Domain
    agent.conduct_research("Mechanism of Artificial Neural Networks", max_steps=1)
    
    # 2. Biological Domain (for comparison)
    agent.conduct_research("Mechanism of Biological Signal Transmission in Synapses", max_steps=1)
    
    # PHASE 2: NAVIGATOR STRESS TEST
    print(colored("\nPHASE 2: DIMENSIONAL NAVIGATION...", "yellow"))
    wmcs = WMCS_Kernel()
    wmcs.load_data() 
    
    tests = [
        {
            "dim": "STRUCTURAL (The 'What')",
            "query": "What are the components of an Artificial Neural Network?",
            "expect": "Navigator should choose STRUCTURE dimension (Nodes, Layers, Weights)."
        },
        {
            "dim": "LATERAL (The 'Analogy')",
            "query": "What is the biological equivalent of a Weight in an Artificial Network?",
            "expect": "Navigator should choose LATERAL/EQUIVALENCE dimension (Synaptic Strength)."
        }
    ]

    for test in tests:
        print(colored("="*60, "cyan"))
        print(colored(f"TEST DIMENSION: {test['dim']}", "white", attrs=['bold']))
        print(f"Query: {test['query']}")
        print(f"Expectation: {test['expect']}")
        
        response = wmcs.process_query(test['query'])
        
        print(colored("\n>>> SYSTEM RESPONSE:", "green"))
        print(response)

if __name__ == "__main__":
    run_neural_stress_test()
