import sys
import os
from termcolor import colored

sys.path.append(os.getcwd())
from system_a_cognitive.meta.deep_researcher import DeepResearchAgent

def run_deep_stress_test():
    print(colored("### STRESS TEST: RECURSIVE DEEP RESEARCH ###", "magenta", attrs=['bold']))
    
    # We choose a topic that implies sub-components
    topic = "How does a Lithium-Ion Battery work?"
    
    agent = DeepResearchAgent()
    
    print(colored(f"\nTarget Topic: {topic}", "cyan"))
    print(colored("Expectation: Agent should break it down (Anode, Cathode, Electrolyte) and critique results.", "white"))
    
    # Run with limited depth for the test
    agent.conduct_deep_research(topic, max_depth=1)

if __name__ == "__main__":
    run_deep_stress_test()
