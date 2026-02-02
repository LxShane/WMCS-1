import sys
import os
import json
import shutil
from termcolor import colored

sys.path.append(os.getcwd())
from main import WMCS_Kernel

def print_header(text):
    print(colored(f"\n{'='*60}", "magenta"))
    print(colored(f"   {text}", "magenta", attrs=['bold']))
    print(colored(f"{'='*60}\n", "magenta"))

def run_reality_test():
    print_header("STRESS TEST: REALITY & RESILIENCE (PHASE 5)")
    
    # 0. Setup
    wmcs = WMCS_Kernel()
    
    # Clean slate for Pluto
    pluto_path = os.path.join("data", "concepts", "pluto.json")
    if os.path.exists(pluto_path):
        os.remove(pluto_path)
        print(colored("Deleted existing pluto.json for clean test.", "yellow"))

    # 1. Ingest Historical Fact
    print(colored("\nStep 1: Ingesting Historical Fact (1930)...", "cyan"))
    text_1930 = "In 1930, Clyde Tombaugh discovered Pluto, which was classified as the ninth planet of the solar system."
    wmcs.ingestor.ingest_text(text_1930, source_name="history_book")
    
    # 2. Ingest Modern Fact
    print(colored("\nStep 2: Ingesting Modern Fact (2006)...", "cyan"))
    text_2006 = "In 2006, the IAU issued a resolution reclassifying Pluto as a 'dwarf planet', stripping it of full planet status."
    wmcs.ingestor.ingest_text(text_2006, source_name="science_journal")
    
    # 3. Verify JSON Structure
    print(colored("\nStep 3: Verifying Knowledge Graph Structure...", "cyan"))
    
    if not os.path.exists(pluto_path):
        print(colored("FAIL: pluto.json not found.", "red"))
        return

    with open(pluto_path, 'r') as f:
        data = json.load(f)
        
    print(colored("JSON Content:", "white"))
    print(json.dumps(data, indent=2))
    
    claims = data.get("claims", [])
    if not claims:
        print(colored("FAIL: No 'claims' list found in JSON.", "red"))
        return

    # Check for Temporal Markers
    found_1930 = False
    found_2006 = False
    found_planet = False
    found_dwarf = False
    
    for c in claims:
        pred = c.get("predicate", "").lower()
        obj = c.get("object", "").lower()
        temp = c.get("temporal", {})
        
        if "planet" in obj and "dwarf" not in obj: found_planet = True
        if "dwarf" in obj: found_dwarf = True
        
        v_from = str(temp.get("valid_from", ""))
        v_until = str(temp.get("valid_until", ""))
        
        if "1930" in v_from: found_1930 = True
        if "2006" in v_from: found_2006 = True
        
        print(f"  - Claim: {pred} -> {obj} | Time: {v_from} to {v_until}")

    if found_planet and found_dwarf:
        print(colored("PASS: Contains both 'Planet' and 'Dwarf Planet' classifications.", "green"))
    else:
        print(colored("FAIL: Missing one of the conflicting classifications.", "red"))

    if found_1930 and found_2006:
        print(colored("PASS: Contains temporal markers (1930 and 2006).", "green"))
    else:
        print(colored("FAIL: Missing temporal metadata.", "red"))

if __name__ == "__main__":
    run_reality_test()
