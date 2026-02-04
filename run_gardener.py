"""
Script to Start the Active Gardener
This background process:
1. Audits concepts for missing info (Spatial, Physics)
2. Scans for missing relations (RELATIONS mode)
3. Rebuilds the registry
"""
from termcolor import colored
from system_a_cognitive.meta.active_gardener import ActiveGardener

if __name__ == "__main__":
    print(colored("=== WMCS ACTIVE GARDENER ===", "green"))
    print("Initializing background agent...")
    
    gardener = ActiveGardener()
    
    # Run a few cycles
    try:
        gardener.start_cycle(max_loops=10)
    except KeyboardInterrupt:
        print("\nStopping Gardener.")
