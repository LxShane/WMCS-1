import os
import json
import re
from termcolor import colored

def analyze_relations():
    concepts_dir = "data/concepts"
    files = [f for f in os.listdir(concepts_dir) if f.endswith(".json")]
    
    # 1. Build Index: Name -> Data
    print(colored("Step 1: Indexing Concepts...", "cyan"))
    concept_map = {}
    
    for filename in files:
        with open(os.path.join(concepts_dir, filename), 'r', encoding='utf-8') as f:
            data = json.load(f)
            name = data.get("name")
            if name:
                concept_map[name.lower()] = {
                    "data": data,
                    "filename": filename,
                    "outgoing": [], # List of (RelationType, TargetName)
                    "incoming": []  # List of (RelationType, SourceName)
                }

    print(f"Indexed {len(concept_map)} concepts.\n")

    # 2. Extract Relations
    print(colored("Step 2: Extracting Relations...", "cyan"))
    
    # Regex to capture "Source RELATION Target"
    # Basic assumption: "Subject SENTENCE_CASE_RELATION Object"
    # e.g., "Dog IS_A Mammal"
    rel_pattern = re.compile(r"(.+?)\s+([A-Z_]+(?:_[A-Z]+)*)\s+(.+)")

    for source_name, entry in concept_map.items():
        data = entry["data"]
        facets = data.get("facets", [])
        
        # Handle list format (new) or dict format (old/legacy) just in case
        facet_list = []
        if isinstance(facets, list):
            facet_list = facets
        elif isinstance(facets, dict):
            for lens, content in facets.items():
                if isinstance(content, list): facet_list.extend(content) # unlikely based on dashboard
                
        for facet in facet_list:
            if not isinstance(facet, dict): continue
            
            val = facet.get("value", "")
            match = rel_pattern.match(val)
            if match:
                subj, rel, obj = match.groups()
                # Check if this concept is actually the subject (usually yes)
                if subj.lower() == source_name:
                    target_key = obj.lower()
                    entry["outgoing"].append( (rel, target_key) )
                    
                    # Register incoming on target if it exists
                    if target_key in concept_map:
                        concept_map[target_key]["incoming"].append( (rel, source_name) )
                else:
                    # sometimes "Mammal has subtype Dog" might reside in "Dog" block? 
                    # Prefer standard direction: Subject is the Block Name.
                    pass
    
    # 3. Analyze Reciprocity
    print(colored("Step 3: Analyzing Connectivity...\n", "cyan"))
    
    one_way_count = 0
    two_way_count = 0
    dangling_count = 0
    
    print(colored(f"{'CONCEPT':<30} | {'OUT' :<5} | {'IN':<5} | {'DANGLING (Target not found)'}", "white", attrs=['bold']))
    print("-" * 80)
    
    for name, entry in sorted(concept_map.items()):
        outgoing = entry["outgoing"]
        incoming = entry["incoming"]
        
        # Check dangling
        dangling = []
        for rel, target in outgoing:
            if target not in concept_map:
                dangling.append(target)
        
        dangling_str = ", ".join(dangling[:3]) 
        if len(dangling) > 3: dangling_str += "..."
        if dangling_str: dangling_str = colored(dangling_str, "red")
        
        # Count connectivity
        if len(outgoing) > 0 and len(incoming) == 0:
            one_way_count += 1
        elif len(outgoing) > 0 and len(incoming) > 0:
            two_way_count += 1
            
        dangling_count += len(dangling)
        
        print(f"{name:<30} | {len(outgoing):<5} | {len(incoming):<5} | {dangling_str}")

    print("-" * 80)
    print(colored("\nSUMMARY:", "yellow", attrs=['bold']))
    print(f"Total Concepts: {len(concept_map)}")
    print(f"One-Way Nodes (Sources Only): {one_way_count}")
    print(f"Two-Way Nodes (Connected):    {two_way_count}")
    print(f"Dangling Links (Broken Refs): {dangling_count}")
    
    if dangling_count > 0:
        print(colored("\nCONCLUSION: The graph is mostly One-Way and Fragmented.", "red"))
        print("Concepts point to things that don't exist yet (Dangling).")
        print("We need to run a 'Cross-Linking' job to generate reciprocal links.")
    else:
        print(colored("\nCONCLUSION: The graph is well connected.", "green"))

if __name__ == "__main__":
    analyze_relations()
