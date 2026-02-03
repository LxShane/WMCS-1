from system_a_cognitive.meta.active_gardener import ActiveGardener
from termcolor import colored
import json
import os

def test_registry_rebuild():
    print(colored("╔═══ TEST: REG REBUILD ═══╗", "magenta", attrs=['bold']))
    
    gardener = ActiveGardener()
    
    # Check current size
    reg_path = "data/registry.json"
    with open(reg_path, 'r') as f:
        old_size = len(json.load(f))
    print(f"Old Registry Size: {old_size}")
    
    # Rebuild
    print(colored("Triggering Rebuild...", "yellow"))
    gardener.rebuild_registry()
    
    # Check new size
    with open(reg_path, 'r') as f:
        new_size = len(json.load(f))
    print(f"New Registry Size: {new_size}")
    
    if new_size > 1000:
        print(colored("[PASS] Registry Rebuilt Successfully.", "green"))
    else:
        print(colored(f"[FAIL] Registry size weirdly low ({new_size}).", "red"))

if __name__ == "__main__":
    test_registry_rebuild()
