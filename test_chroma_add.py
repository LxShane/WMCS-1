
import sys
import os
sys.path.append(os.getcwd())
import json
from termcolor import colored

print(colored("--- TESTING CHROMA STORE ADD ---", "cyan"))

try:
    from system_a_cognitive.memory.chroma_store import ChromaStore
    store = ChromaStore()
    print("Store Initialized.")
    
    mock_block = {
        "name": "Test_Concept",
        "id": {"group": 99, "item": 123},
        "facets": {"definition": "A test entity", "type": "Mock"},
        "claims": [
            {"predicate": "is_a", "object": "test"},
            {"predicate": "has_part", "object": "mock_data"}
        ]
    }
    
    print("Adding Mock Block...")
    store.add_concept_block(mock_block)
    print("Add Complete.")
    
    print("Verifying Search...")
    results = store.search("Test_Concept")
    print(f"Search Results: {len(results)}")
    print(results)
    
    if len(results) > 0:
        print(colored("SUCCESS: Block added and retrieved.", "green"))
    else:
        print(colored("FAILURE: Block added but not found.", "red"))

except Exception as e:
    print(colored(f"CRASH: {e}", "red"))
    import traceback
    traceback.print_exc()
