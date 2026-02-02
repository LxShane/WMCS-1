import sys
import os
sys.path.append(os.getcwd())

from system_a_cognitive.meta.deep_researcher import DeepResearchAgent
from termcolor import colored

print(colored("--- STARTING RESEARCH TEST ---", "cyan"))
try:
    agent = DeepResearchAgent()
    print("Agent initialized.")
    agent.conduct_deep_research("Zylophant", max_depth=1)
    print(colored("--- RESEARCH COMPLETE ---", "green"))
except Exception as e:
    print(colored(f"--- CRASH: {e} ---", "red"))
    import traceback
    traceback.print_exc()
