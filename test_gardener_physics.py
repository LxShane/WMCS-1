from system_a_cognitive.meta.active_gardener import ActiveGardener
from termcolor import colored
import json
import os
import time

def test_physics_gardener():
    print(colored("╔═══ TEST: PHYSICS GARDENER ═══╗", "magenta", attrs=['bold']))
    
    # 1. Setup
    gardener = ActiveGardener()
    dummy_path = "data/concepts/dummy_steel_beam.json"
    
    # Reload dummy to make sure it's clean
    with open(dummy_path, 'r') as f:
        original_data = json.load(f)
        
    print(colored("Step 1: Loaded Dummy Concept (Physics-Blind).", "cyan"))
    
    # 2. Force Fix
    # We simulate finding the gap
    print(colored("Step 2: Triggering Physics Fix...", "yellow"))
    gardener._apply_fix(original_data, gap_type="PHYSICS")
    
    # 3. Verify
    print(colored("Step 3: Checking File Update...", "cyan"))
    # Allow file I/O to settle
    time.sleep(1)
    
    with open(dummy_path, 'r') as f:
        new_data = json.load(f)
        
    facets = new_data.get("facets", {})
    structural = facets.get("STRUCTURAL", {})
    props = structural.get("material_properties", {})
    
    print(f"Material Properties Found: {props}")
    
    if props.get("rigidity") or props.get("state"):
        print(colored("[PASS] Gardener successfully injected Physics Data!", "green"))
    else:
        print(colored("[FAIL] Physics Data missing.", "red"))

if __name__ == "__main__":
    test_physics_gardener()
