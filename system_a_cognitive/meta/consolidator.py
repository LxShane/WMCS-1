import os
import json
from termcolor import colored
import re

class KnowledgeConsolidator:
    """
    Scans the Knowledge Base and creates reciprocal links.
    Example: If A -> IS_A -> B, then B -> INCLUDES -> A.
    """
    def __init__(self, concepts_dir="data/concepts"):
        self.concepts_dir = concepts_dir
        self.inverse_map = {
            "IS_A": "INCLUDES_SUBTYPE",
            "HAS_PART": "PART_OF",
            "PART_OF": "HAS_PART",
            "CAPABLE_OF": "PERFORMED_BY",
            "PERFORMED_BY": "CAPABLE_OF",
            "CAUSED_BY": "CAUSES",
            "CAUSES": "CAUSED_BY",
            "LOCATED_AT": "CONTAINS",
            "CONTAINS": "LOCATED_AT"
        }

    def consolidate(self):
        print(colored("SYSTEM: Running Knowledge Consolidation Cycle...", "cyan"))
        
        # 1. Load All
        files = [f for f in os.listdir(self.concepts_dir) if f.endswith(".json")]
        concept_map = {} # name -> filepath
        data_map = {}    # filename -> json_data
        
        for f in files:
            path = os.path.join(self.concepts_dir, f)
            with open(path, 'r', encoding='utf-8') as file:
                d = json.load(file)
                concept_map[d['name'].lower()] = f
                data_map[f] = d
                
        updates = {} # filename -> list of new facets

        # 2. Scan outgoing relations
        rel_pattern = re.compile(r"(.+?)\s+([A-Z_]+(?:_[A-Z]+)*)\s+(.+)")
        
        for filename, data in data_map.items():
            facets = data.get("facets", [])
            # Normalize to list
            facet_list = []
            if isinstance(facets, list): facet_list = facets
            elif isinstance(facets, dict):
                for v in facets.values():
                    if isinstance(v, list): facet_list.extend(v)

            for facet in facet_list:
                val = facet.get('value', '')
                match = rel_pattern.match(val)
                if match:
                    subj, rel, obj = match.groups()
                    target_key = obj.lower()
                    
                    # If target exists in our DB
                    if target_key in concept_map:
                        target_file = concept_map[target_key]
                        
                        # Calculate Inverse
                        inv_rel = self.inverse_map.get(rel)
                        if inv_rel:
                            # Create the Reciprocal Fact
                            # e.g. "Mammal INCLUDES_SUBTYPE Dog"
                            inv_fact = f"{obj} {inv_rel} {subj}"
                            
                            # Check if target already has this fact
                            target_data = data_map[target_file]
                            exists = False
                            
                            # quick check in target facets
                            t_facets = target_data.get("facets", [])
                            t_list = []
                            if isinstance(t_facets, list): t_list = t_facets
                            elif isinstance(t_facets, dict):
                                for v in t_facets.values():
                                    if isinstance(v, list): t_list.extend(v)
                                    
                            for tf in t_list:
                                if tf.get('value') == inv_fact:
                                    exists = True
                                    break
                            
                            if not exists:
                                if target_file not in updates: updates[target_file] = []
                                updates[target_file].append({
                                    "type": "STRUCTURAL",
                                    "value": inv_fact,
                                    "auto_generated": True
                                })

        # 3. Apply Updates
        if not updates:
             print(colored("SYSTEM: Structure is stable. No new links needed.", "green"))
             return 0

        print(colored(f"SYSTEM: Found missing reciprocal links for {len(updates)} concepts.", "yellow"))
        
        count = 0
        for fname, new_facets in updates.items():
            path = os.path.join(self.concepts_dir, fname)
            original = data_map[fname]
            
            # Append new facets
            # Handle schema (list vs dict) - defaulting to list for now as per V2
            if isinstance(original['facets'], list):
                original['facets'].extend(new_facets)
            elif isinstance(original['facets'], dict):
                # Fallback to STRUCTURAL bucket
                if "STRUCTURAL" not in original['facets']: original['facets']["STRUCTURAL"] = []
                original['facets']["STRUCTURAL"].extend(new_facets)
                
            with open(path, 'w', encoding='utf-8') as f:
                json.dump(original, f, indent=2)
            
            print(f"  > Updated {original['name']} with {len(new_facets)} links (e.g., {new_facets[0]['value']})")
            count += len(new_facets)

        print(colored(f"SYSTEM: Consolidation Complete. Added {count} new connections.", "green"))
        return count
