"""
Verification Script for v1.0 Engines
Tests Spatial and Composition engines using the migrated cat.json.
"""
import json
import os
from system_a_cognitive.logic.spatial import SpatialEngine
from system_a_cognitive.logic.composition import CompositionEngine
from termcolor import colored

print(colored("=== v1.0 Engine Verification ===", "magenta", attrs=['bold']))

# Load Data
path = "data/concepts_v1/cat.json"
if not os.path.exists(path):
    print(colored("Error: data/concepts_v1/cat.json not found. Run Migrator first.", "red"))
    exit(1)

with open(path, 'r') as f:
    cat = json.load(f)

print(colored(f"Loaded v1.0 Concept: {cat['CORE']['name']}", "green"))

# Test Spatial
print("\n--- Testing Spatial Engine ---")
spatial = SpatialEngine()
sp_data = cat.get("SPATIAL", {})
if not sp_data:
    print(colored("No SPATIAL data found.", "yellow"))
else:
    vol = spatial.calculate_volume_cm3(sp_data.get("structure_spatial", {}))
    print(f"Calculated Volume: {vol} cm3")
    
    head_pos = spatial.get_part_position(sp_data, "head")
    print(f"Head Position: {head_pos}")
    
    # Check Fit
    box = {
        "overall": {"size": {"width": 30, "height": 30, "depth": 30}}
    }
    fit = spatial.check_fit(sp_data.get("structure_spatial", {}), box)
    print(f"Fits in 30cm box? {fit['fits']} ({fit['reason']})")

# Test Composition
print("\n--- Testing Composition Engine ---")
comp = CompositionEngine()
comp_data = cat.get("COMPOSITION", {})
if not comp_data:
    print(colored("No COMPOSITION data found.", "yellow"))
else:
    parts = comp.get_all_components(comp_data)
    print(f"Found {len(parts)} parts in hierarchy.")
    print(f"First 10 parts: {parts[:10]}")
    
    check_parts = ["heart", "kidney", "cat_paw", "wings"]
    for p in check_parts:
        has = comp.is_part_of(p, comp_data)
        res = "YES" if has else "NO"
        print(f"  Has {p}? {res}")

print("\n=== Verification Complete ===")
