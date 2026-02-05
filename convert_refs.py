"""
Ref-to-ID Converter
Scans all concept files and converts string refs to proper block ID references.
This ensures full compliance with WMCS v1.0 spec for ID-based relations.
"""
import os
import json
from termcolor import colored
from system_a_cognitive.logic.identity import IdentityManager

def convert_refs_to_ids():
    """Convert all string refs in concept files to ID references."""
    identity = IdentityManager()
    concepts_dir = "data/concepts"
    
    converted = 0
    total_refs_fixed = 0
    
    print(colored("=== CONVERTING STRING REFS TO ID REFS ===", "magenta", attrs=["bold"]))
    
    for fname in os.listdir(concepts_dir):
        if not fname.endswith(".json"):
            continue
            
        path = os.path.join(concepts_dir, fname)
        modified = False
        refs_in_file = 0
        
        try:
            with open(path, 'r', encoding='utf-8') as f:
                concept = json.load(f)
            
            # Process SUBSTANCE.composition.levels[].components[].ref
            substance = concept.get("SUBSTANCE", {})
            composition = substance.get("composition", {})
            levels = composition.get("levels", [])
            
            for level in levels:
                components = level.get("components", [])
                for comp in components:
                    ref = comp.get("ref")
                    if ref and isinstance(ref, str):
                        # It's a string ref, try to resolve to ID
                        ref_id = identity.get_id(ref.lower().replace(' ', '_'))
                        if ref_id:
                            comp["ref"] = ref_id
                            modified = True
                            refs_in_file += 1
                        else:
                            # Try to find in registry by name similarity
                            comp_name = comp.get("name", "").lower().replace(' ', '_')
                            comp_id = identity.get_id(comp_name)
                            if comp_id:
                                comp["ref"] = comp_id
                                modified = True
                                refs_in_file += 1
            
            # Process CONNECTIONS.relational[].target
            connections = concept.get("CONNECTIONS", {})
            relational = connections.get("relational", [])
            
            for rel in relational:
                target = rel.get("target")
                if target and isinstance(target, str):
                    target_id = identity.get_id(target.lower().replace(' ', '_'))
                    if target_id:
                        rel["target"] = target_id
                        modified = True
                        refs_in_file += 1
            
            # Process ARRANGEMENT.structure_spatial.parts[].ref
            arrangement = concept.get("ARRANGEMENT", {})
            spatial = arrangement.get("structure_spatial", {})
            parts = spatial.get("parts", [])
            
            for part in parts:
                ref = part.get("ref")
                if ref and isinstance(ref, str):
                    ref_id = identity.get_id(ref.lower().replace(' ', '_'))
                    if ref_id:
                        part["ref"] = ref_id
                        modified = True
                        refs_in_file += 1
            
            # Process CAUSATION.requires[] and produces[]
            causation = concept.get("CAUSATION", {})
            for key in ["requires", "produces"]:
                items = causation.get(key, [])
                for i, item in enumerate(items):
                    if isinstance(item, str):
                        item_id = identity.get_id(item.lower().replace(' ', '_'))
                        if item_id:
                            causation[key][i] = item_id
                            modified = True
                            refs_in_file += 1
                    elif isinstance(item, dict) and "ref" in item and isinstance(item["ref"], str):
                        ref_id = identity.get_id(item["ref"].lower().replace(' ', '_'))
                        if ref_id:
                            item["ref"] = ref_id
                            modified = True
                            refs_in_file += 1
            
            if modified:
                with open(path, 'w', encoding='utf-8') as f:
                    json.dump(concept, f, indent=2)
                print(f"  + {fname}: {refs_in_file} refs converted")
                converted += 1
                total_refs_fixed += refs_in_file
                
        except Exception as e:
            print(colored(f"  ! Error with {fname}: {e}", "red"))
    
    print(colored(f"\nConversion Complete: {converted} files updated, {total_refs_fixed} refs fixed", "green"))

if __name__ == "__main__":
    convert_refs_to_ids()
