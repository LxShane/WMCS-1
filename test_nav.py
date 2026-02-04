"""Test Navigator Exits"""
import os
import json
from system_a_cognitive.logic.navigator import ConceptNavigator

class MockKernel:
    def __init__(self):
        self.file_map = {}
        self.block_cache = {}
        self.llm_client = None  # Not needed for get_exits test
        
        for fn in os.listdir('data/concepts'):
            if fn.endswith('.json'):
                self.file_map[fn.replace('.json', '')] = os.path.join('data/concepts', fn)
    
    @property
    def blocks(self):
        return self
    
    def values(self):
        for key in list(self.file_map.keys())[:200]:  # Limit for speed
            yield self.get(key)
    
    def get(self, key, default=None):
        key = key.lower().replace(' ', '_')
        if key in self.block_cache:
            return self.block_cache[key]
        if key in self.file_map:
            try:
                with open(self.file_map[key], 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    self.block_cache[key] = data
                    return data
            except:
                return default
        return default

print("=== TESTING NAVIGATOR EXITS ===\n")

k = MockKernel()
print(f"Mapped {len(k.file_map)} concept files")

# Load cat
cat = k.get('cat')
print(f"Cat loaded: {cat['name']} with {len(cat.get('claims',[]))} claims")

# Show ID-based claims
print("\nID-based claims in CAT:")
import re
pattern = r'\((\d+),\s*(\d+)\)'
for claim in cat.get('claims', []):
    obj = str(claim.get('object', ''))
    if re.search(pattern, obj):
        print(f"  {claim['predicate']}: {obj}")

# Test navigator
print("\nBuilding Navigator ID map...")
nav = ConceptNavigator(k)
print(f"ID map has {len(nav.id_map)} entries")

# Get exits
exits = nav.get_exits(cat)
print(f"\nNavigator found {len(exits)} exits from CAT:")
for e in exits:
    print(f"  {e['dimension']} -> {e['target_name']} (ID: {e['target_id']})")

if exits:
    print("\n✓ Navigation is working!")
else:
    print("\n✗ No exits found - check if target IDs exist in id_map")
