"""
Batch Enrichment - Add ID-based relations to ALL existing concepts
"""
import os
import json
from termcolor import colored
from system_a_cognitive.logic.relation_builder import RelationBuilder

print(colored("=== BATCH ENRICHMENT: Adding ID Relations ===", "magenta", attrs=['bold']))

concept_dir = "data/concepts"
rb = RelationBuilder()
print(f"RelationBuilder loaded with {len(rb._name_cache)} concept names")

files = [f for f in os.listdir(concept_dir) if f.endswith('.json')]
print(f"Processing {len(files)} concept files...\n")

total_relations_added = 0
concepts_enriched = 0
errors = 0

for i, fname in enumerate(files):
    path = os.path.join(concept_dir, fname)
    try:
        with open(path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        added = rb.auto_add_relations(data)
        
        if added > 0:
            with open(path, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2)
            total_relations_added += added
            concepts_enriched += 1
        
        # Progress every 1000
        if (i + 1) % 1000 == 0:
            print(f"  Progress: {i+1}/{len(files)} ({100*(i+1)//len(files)}%) - {total_relations_added} relations added")
            
    except Exception as e:
        errors += 1
        if errors <= 5:
            print(colored(f"  Error with {fname}: {e}", "red"))

print(colored(f"\n=== BATCH ENRICHMENT COMPLETE ===", "green", attrs=['bold']))
print(f"Concepts enriched: {concepts_enriched}")
print(f"Total relations added: {total_relations_added}")
print(f"Errors: {errors}")
