"""
Add Relations to Key Concepts
Adds ID-based relations to enable navigation between related concepts
"""
import json
import os
from system_a_cognitive.logic.identity import IdentityManager

print("=== ADDING CONCEPT RELATIONS ===\n")

im = IdentityManager()
concept_dir = "data/concepts"

def get_id_str(name):
    """Get (group, item) ID string for a concept name"""
    id_data = im.get_id(name.lower())
    if id_data:
        return f"({id_data['group']}, {id_data['item']})"
    return None

def add_relation(block, predicate, target_name):
    """Add a relation claim with ID reference"""
    target_id = get_id_str(target_name)
    if not target_id:
        print(f"  [!] Could not find ID for: {target_name}")
        return False
    
    if "claims" not in block:
        block["claims"] = []
    
    # Check if relation already exists
    for c in block["claims"]:
        if c.get("predicate") == predicate and target_id in str(c.get("object", "")):
            return False  # Already exists
    
    block["claims"].append({
        "predicate": predicate,
        "object": f"{target_name} {target_id}",
        "epistemic": {
            "confidence": 0.95,
            "status": "AUTO_GENERATED",
            "source_type": "RELATION_BUILDER"
        }
    })
    return True

def update_concept(filename, relations):
    """Update a concept file with new relations"""
    path = os.path.join(concept_dir, filename)
    if not os.path.exists(path):
        print(f"  [!] File not found: {filename}")
        return 0
    
    with open(path, 'r', encoding='utf-8') as f:
        block = json.load(f)
    
    added = 0
    for predicate, target in relations:
        if add_relation(block, predicate, target):
            added += 1
            print(f"  Added: {predicate} -> {target}")
    
    if added > 0:
        with open(path, 'w', encoding='utf-8') as f:
            json.dump(block, f, indent=2)
        print(f"  Saved {filename} with {added} new relations")
    
    return added

# Define key concepts and their relations
# Format: (filename, [(predicate, target_name), ...])
key_relations = [
    ("cat.json", [
        ("HAS_PART", "cat_paw"),
        ("HAS_PART", "feline_claw"),
        ("HAS_PART", "whiskers"),
        ("IS_A", "mammal"),
        ("IS_A", "predator"),
        ("IS_A", "domestic_cat"),
    ]),
    ("dog.json", [
        ("HAS_PART", "paw"),
        ("IS_A", "mammal"),
        ("IS_A", "predator"),
        ("RELATED_TO", "wolf"),
    ]),
    ("human.json", [
        ("HAS_PART", "hand"),
        ("HAS_PART", "foot"),
        ("HAS_PART", "brain"),
        ("IS_A", "mammal"),
        ("IS_A", "primate"),
    ]),
    ("brain.json", [
        ("PART_OF", "human"),
        ("HAS_PART", "neuron"),
        ("HAS_PART", "synapse"),
        ("ENABLES", "cognition"),
    ]),
    ("cell.json", [
        ("HAS_PART", "nucleus"),
        ("HAS_PART", "mitochondria"),
        ("HAS_PART", "membrane"),
    ]),
]

total_added = 0
for filename, relations in key_relations:
    print(f"\n{filename}:")
    total_added += update_concept(filename, relations)

print(f"\n=== COMPLETE: Added {total_added} relations ===")

# Verify navigation can now find exits
print("\n=== TESTING NAVIGATION ===")
with open(os.path.join(concept_dir, "cat.json"), 'r', encoding='utf-8') as f:
    cat_block = json.load(f)

print(f"Cat claims: {len(cat_block.get('claims', []))}")
import re
pattern = r'\(\d+,\s*\d+\)'
for claim in cat_block.get('claims', []):
    obj = str(claim.get('object', ''))
    if re.search(pattern, obj):
        print(f"  ✓ {claim['predicate']}: {obj}")
