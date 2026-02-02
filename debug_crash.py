
import sys
import os
sys.path.append(os.getcwd())
from termcolor import colored
import traceback

print(colored("--- STARTING CRASH DEBUGGER ---", "cyan"))

try:
    from main import WMCS_Kernel
    print("Initializing Kernel...")
    kernel = WMCS_Kernel()
    print("Kernel Initialized.")
    
    # We need to simulate the state where 'bird' needs research
    # But first, let's just see if a benign query works
    # print("Testing Benign Query...")
    # kernel.process_query("hello", allow_research=False)
    
    print("Testing RISKY Query ('Power bank')...")
    # This triggers:
    # 1. Navigation (finds nothing or something)
    # 2. If nothing -> Research -> load_data(force=True) -> ingest_all -> add_concept_block
    # 3. If something -> Secondary Reflex -> load_data(force=True) -> ...
    
    result = kernel.process_query("Power bank", allow_research=True)
    print("Result:", result)

except Exception as e:
    print(colored(f"--- CRASH DETECTED ---", "red"))
    print(colored(str(e), "red"))
    traceback.print_exc()
