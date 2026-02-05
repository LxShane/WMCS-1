"""
Registry Sync Tool
Synchronizes all existing concept files with the registry.json
Ensures every concept has a proper ID tracked in the centralized registry.
"""
import os
import json
from termcolor import colored
from system_a_cognitive.logic.identity import IdentityManager

def sync_registry():
    """Sync all concept files to the registry."""
    identity = IdentityManager()
    concepts_dir = "data/concepts"
    
    synced = 0
    updated = 0
    
    print(colored("=== SYNCING CONCEPTS TO REGISTRY ===", "magenta", attrs=["bold"]))
    
    for fname in os.listdir(concepts_dir):
        if not fname.endswith(".json"):
            continue
            
        path = os.path.join(concepts_dir, fname)
        
        try:
            with open(path, 'r', encoding='utf-8') as f:
                concept = json.load(f)
            
            name = concept.get("CORE", {}).get("name", fname.replace(".json", ""))
            current_id = concept.get("CORE", {}).get("id")
            
            # Check if in registry
            registered_id = identity.get_id(name)
            
            if registered_id:
                # Already in registry
                synced += 1
            else:
                # Not in registry - add it
                concept_type = concept.get("CORE", {}).get("type", "")
                
                # Determine group
                if "organism" in concept_type:
                    group = 21
                elif "artifact" in concept_type:
                    group = 30
                elif "abstraction" in concept_type or "phenomenon" in concept_type:
                    group = 50
                else:
                    group = 20  # Default physical
                
                # If concept has an ID, use that group
                if current_id and isinstance(current_id, dict):
                    group = current_id.get("group", group)
                
                new_id = identity.mint_id(name, group)
                concept["CORE"]["id"] = new_id
                
                # Save updated concept
                with open(path, 'w', encoding='utf-8') as f:
                    json.dump(concept, f, indent=2)
                
                print(f"  + {name}: {new_id}")
                updated += 1
                
        except Exception as e:
            print(colored(f"  ! Error with {fname}: {e}", "red"))
    
    print(colored(f"\nSync Complete: {synced} already registered, {updated} newly added", "green"))
    print(f"Total in registry: {len(identity.registry)}")

if __name__ == "__main__":
    sync_registry()
