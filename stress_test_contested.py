import sys
import os
import json
from termcolor import colored

sys.path.append(os.getcwd())
try:
    from main import WMCS_Kernel
except ImportError:
    # If running from tools/, fix path
    sys.path.append(os.path.join(os.getcwd(), '..'))
    from main import WMCS_Kernel

def run_contested_test():
    print(colored("STRESS TEST: CONTESTED KNOWLEDGE (PHASE 6)", "magenta", attrs=['bold']))
    
    wmcs = WMCS_Kernel()
    
    # 1. Clean previous
    coffee_path = "data/concepts/coffee.json"
    if os.path.exists(coffee_path): os.remove(coffee_path)

    # 2. Ingest Thesis (2010)
    print(colored("\nStep 1: Ingesting Thesis (Coffee is BAD)...", "cyan"))
    text_bad = "A 2010 study by Dr. Smith concluded that coffee consumption is linked to a higher risk of throat cancer."
    wmcs.ingestor.ingest_text(text_bad, source_name="study_2010")
    
    # 3. Ingest Antithesis (2020)
    print(colored("\nStep 2: Ingesting Antithesis (Coffee is GOOD)...", "cyan"))
    text_good = "A comprehensive 2020 review by the Health Institute found that coffee actually prevents liver cancer and has no link to throat cancer."
    wmcs.ingestor.ingest_text(text_good, source_name="study_2020")
    
    # RELOAD TO INDEX
    print(colored("Step 2.5: Reloading Knowledge Graph to index new facts...", "yellow"))
    wmcs.load_data()
    
    # 4. Query Logic
    print(colored("\nStep 3: Querying the Conflict...", "cyan"))
    query = "Does coffee cause cancer?"
    response = wmcs.process_query(query, allow_research=False) # Force internal lookup
    
    print(colored(f"\nWMCS Response:\n{response}", "white", attrs=['bold']))
    
    # 5. Verify Response Content
    start_checks = ["2010", "2020", "Smith", "Institute", "prevent", "link"]
    score = 0
    lower_resp = str(response).lower()
    
    for check in start_checks:
        if check.lower() in lower_resp:
            score += 1
            
    if score >= 3:
        print(colored("PASS: Response captured the conflict and citations.", "green"))
    else:
        print(colored(f"FAIL: Response was too simple. Score {score}/6.", "red"))

if __name__ == "__main__":
    run_contested_test()
