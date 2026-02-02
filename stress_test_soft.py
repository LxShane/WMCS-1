import sys
import os
from termcolor import colored

sys.path.append(os.getcwd())
from system_a_cognitive.meta.deep_researcher import DeepResearchAgent

def run_soft_stress_test():
    print(colored("### STRESS TEST: CRITIQUE LENIENCY ###", "magenta", attrs=['bold']))
    
    # Topic that is easily "Good Enough" without deep physics
    topic = "How do Piano Keys generate sound?"
    
    agent = DeepResearchAgent()
    
    print(colored(f"\nTopic: {topic}", "cyan"))
    print(colored("Expectation: Agent should accept 'Hammers strike Strings' without demanding 'Harmonic Series Math'.", "white"))
    
    # We want to see [OK]
    agent.conduct_deep_research(topic, max_depth=1)

if __name__ == "__main__":
    run_soft_stress_test()
