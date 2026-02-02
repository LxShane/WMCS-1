import sys
import os
import json
from termcolor import colored

sys.path.append(os.getcwd())
try:
    from main import WMCS_Kernel
except ImportError:
    sys.path.append(os.path.join(os.getcwd(), '..'))
    from main import WMCS_Kernel

def run_theseus_test():
    print(colored("STRESS TEST: THE SHIP OF THESEUS (ONTOLOGICAL IDENTITY)", "magenta", attrs=['bold']))
    
    wmcs = WMCS_Kernel()
    
    # 1. Clean previous
    path = "data/concepts/ship_of_theseus.json"
    if os.path.exists(path): os.remove(path)

    # 2. Ingest Phase 1 (Antiquity)
    print(colored("\nStep 1: Ingesting Original State (500 BC)...", "cyan"))
    text_origin = "In 500 BC, the Ship of Theseus was constructed entirely of Oak Wood planks according to historical records."
    wmcs.ingestor.ingest_text(text_origin, source_name="history_500bc")
    
    # 3. Ingest Phase 2 (Maintenance)
    print(colored("\nStep 2: Ingesting Replacement State (2000 AD)...", "cyan"))
    text_modern = "By 2000 AD, every single wooden part of the Ship of Theseus had been replaced with Aluminum for preservation."
    wmcs.ingestor.ingest_text(text_modern, source_name="maintenance_log_2000")
    
    # 4. Check the JSON directly (Whitebox Test)
    print(colored("\nStep 3: Examining the Concept Block...", "cyan"))
    
    # Reload from disk to be sure
    with open(path, 'r', encoding='utf-8') as f:
        data = json.load(f)
        
    claims = data.get('claims', [])
    found_oak = False
    found_aluminum = False
    
    print(colored("Claims Found:", "yellow"))
    for c in claims:
        pred = c.get('predicate')
        obj = c.get('object')
        temp = c.get('temporal', {})
        print(f"  - {pred}: {obj} (Time: {temp})")
        
        if "Oak" in str(obj) or "Wood" in str(obj): found_oak = True
        if "Aluminum" in str(obj): found_aluminum = True
        
    if found_oak and found_aluminum:
        print(colored("PASS: System holds both identities (Wood & Aluminum) simultaneously.", "green"))
    else:
        print(colored("FAIL: System overwrote the history.", "red"))

    # 5. Query Logic
    print(colored("\nStep 4: Asking the Hard Question...", "cyan"))
    wmcs.load_data() # Refresh Index
    response = wmcs.process_query("What is the Ship of Theseus made of today?", allow_research=False)
    
    print(colored(f"\nFinal Answer:\n{response}", "white", attrs=['bold']))

if __name__ == "__main__":
    run_theseus_test()
