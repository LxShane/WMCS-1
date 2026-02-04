"""
WMCS v1.0 Demonstration
Shows off the new Cognitive Engines reasoning over the Solar System data.
"""
import json
import os
from termcolor import colored
from system_a_cognitive.logic.spatial import SpatialEngine
from system_a_cognitive.logic.composition import CompositionEngine
from system_a_cognitive.logic.grounding import GroundingEngine

def load_concept(name):
    path = f"data/concepts/{name}.json"
    if not os.path.exists(path): return None
    with open(path, 'r', encoding='utf-8') as f:
        return json.load(f)

def demo():
    print(colored("=== WMCS v1.0 COGNITIVE DEMO ===", "magenta", attrs=['bold']))
    
    spatial = SpatialEngine()
    comp = CompositionEngine()
    ground = GroundingEngine()
    
    # Load Concepts
    sun = load_concept("sun")
    earth = load_concept("earth")
    jupiter = load_concept("jupiter")
    moon = load_concept("the_moon")
    
    if not all([sun, earth, jupiter, moon]):
        print("Error: Missing concept files. Run output check.")
        return

    print(colored("\n1. SPATIAL REASONING (The 'Fit' Test)", "cyan"))
    # Q: Does Earth fit inside the Sun?
    sun_vol = spatial.calculate_volume_cm3(sun["ARRANGEMENT"]["structure_spatial"])
    earth_vol = spatial.calculate_volume_cm3(earth["ARRANGEMENT"]["structure_spatial"])
    
    print(f"Sun Volume:   {sun_vol:.2e} cm³")
    print(f"Earth Volume: {earth_vol:.2e} cm³")
    
    ratio = sun_vol / earth_vol
    print(f"You could fit {ratio:.1f} Earths inside the Sun.")
    
    # Q: Does the Moon fit inside Earth?
    fit = spatial.check_fit(
        moon["ARRANGEMENT"]["structure_spatial"], 
        earth["ARRANGEMENT"]["structure_spatial"]
    )
    print(f"Does Moon fit in Earth? {str(fit['fits']).upper()} ({fit['reason']})")

    print(colored("\n2. COMPOSITIONAL ANALYSIS (The 'X-Ray')", "cyan"))
    # Q: What is Earth made of?
    earth_parts = comp.get_all_components(earth["SUBSTANCE"]["composition"])
    print(f"Earth Components ({len(earth_parts)} found):")
    for p in earth_parts[:5]: print(f" - {p}")
    
    # Recursive search
    target = "Iron"
    has_iron = comp.is_part_of(target, earth["SUBSTANCE"]["composition"])
    print(f"Does Earth contain '{target}'? {str(has_iron).upper()}")

    print(colored("\n3. GROUNDING VERIFICATION (The 'Truth' Check)", "cyan"))
    # Q: How do we know about Jupiter?
    j_ground = ground.evaluate_grounding(jupiter["GROUNDING"])
    print(f"Jupiter Grounding: {j_ground['strength']} ({j_ground['status']})")
    print(f"Evidence Chain: {' -> '.join(jupiter['GROUNDING']['chain'])}")

if __name__ == "__main__":
    demo()
