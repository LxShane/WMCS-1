import sys
import os
from termcolor import colored

sys.path.append(os.getcwd())
from system_a_cognitive.meta.researcher import ResearchAgent

def run_demo():
    print(colored("### RUNNING DEEP RESEARCH DEMO ###", "magenta", attrs=['bold']))
    print("Subject: Nuclear Fusion Tokamak")
    print("Goal: Autonomous Multi-Step Learning\n")
    
    agent = ResearchAgent()
    agent.conduct_research("Nuclear Fusion Tokamak (Magnetic Confinement)", max_steps=3)

if __name__ == "__main__":
    run_demo()
