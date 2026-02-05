"""
Seed Generator (v1.0)
Batch generates 100 concepts for the 'System Reset' using LLM.
Target Topic: Solar System
"""
import os
import time
import json
from termcolor import colored
from system_b_llm.interfaces.gemini_client import GeminiClient
from system_a_cognitive.logic.identity import IdentityManager
from config import Config
from schema_v1_production import ConceptBlockV1  # Schema validation

TOPIC_CONCEPTS_100 = [
    # Stars
    "Sun",
    # Planets
    "Mercury", "Venus", "Earth", "Mars", "Jupiter", "Saturn", "Uranus", "Neptune",
    # Dwarf Planets
    "Pluto", "Ceres", "Eris", "Haumea", "Makemake",
    # Moons - Earth/Mars
    "The Moon", "Phobos", "Deimos",
    # Moons - Jupiter
    "Io", "Europa", "Ganymede", "Callisto",
    # Moons - Saturn
    "Titan", "Enceladus", "Mimas", "Rhea", "Iapetus",
    # Features - Sun
    "Photosphere", "Corona", "Solar Flare", "Sunspot", "Solar Wind",
    # Features - Earth
    "Atmosphere", "Magnetosphere", "Crust", "Mantle", "Core", "Ozone Layer",
    # Features - Mars
    "Olympus Mons", "Valles Marineris", "Polar Ice Caps",
    # Features - Gas Giants
    "Great Red Spot", "Saturn's Rings", "Metallic Hydrogen",
    # Small Bodies
    "Asteroid Belt", "Kuiper Belt", "Oort Cloud", "Halley's Comet", "Shoemaker-Levy 9",
    "Vesta", "Pallas", "Hygiea",
    # Spacecraft/Missions
    "Voyager 1", "Voyager 2", "Hubble Space Telescope", "James Webb Space Telescope",
    "Curiosity Rover", "Perseverance Rover", "Apollo 11", "ISS", "Sputnik 1",
    # Physics/Concepts
    "Gravity", "Orbit", "Escape Velocity", "Accretion Disk", "Tidal Force",
    "Heliosphere", "Lagrange Point", "Retrograde Motion", "Transit", "Eclipse",
    "Aurora", "Black Hole", "Nebula", "Supernova", "Galaxy", "Milky Way",
    # Composition
    "Hydrogen", "Helium", "Methane", "Ammonia", "Water Ice", "Silicate Rock", "Iron",
    # Measurement
    "Astronomical Unit", "Light Year", "Parsec", "Kelvin",
    # Phenomena
    "Greenhouse Effect", "Plate Tectonics", "Volcanism", "Impact Crater",
    # Biological Context
    "Habitable Zone", "Extremophile", "Panspermia", "Fermi Paradox", "Drake Equation"
]

class SeedGenerator:
    def __init__(self):
        self.client = GeminiClient(Config.LLM_API_KEY, Config.LLM_MODEL)
        self.output_dir = "data/concepts" # Direct to live folder after purge
        self.identity = IdentityManager()  # Centralized ID management
        
    def generate_all(self):
        print(colored("=== GENERATING 100 SOLAR SYSTEM CONCEPTS (v1.0) ===", "magenta", attrs=['bold']))
        
        for name in TOPIC_CONCEPTS_100:
            self._generate_one(name)
            time.sleep(1) # Rate limit hygiene

    def _generate_one(self, name):
        fname = f"{name.lower().replace(' ', '_')}.json"
        
        prompt = f"""
        You are the v1.0 Seed Generator.
        Create a rigorous v1.0 Concept Block for: '{name}'
        
        CRITICAL: You must Output JSON adhering EXACTLY to this structure. Do not flatten it.
        NOTE: Do NOT include the "id" field - it will be assigned by the system.
        
        {{
          "CORE": {{
            "name": "{name}",
            "type": "organism.animal... (or similar)",
            "definition": "..."
          }},
          "GROUNDING": {{
            "chain": ["step1", "step2"],
            "base_types": ["perceptual", "measurement"],
            "confidence": 0.95,
            "evidence_summary": "..."
          }},
          "CLASSIFICATION": {{
            "categorical_chain": ["..."],
            "siblings": ["..."]
          }},
          "SUBSTANCE": {{
            "composition": {{
                "levels": [
                    {{ "depth": 0, "name": "Major", "components": [ {{ "name": "...", "ref": "..." }} ] }}
                ]
            }}
          }},
          "ARRANGEMENT": {{
            "structure_spatial": {{
                "overall": {{ "shape": "sphere/irregular", "size": {{ "value": 123, "unit": "cm" }} }},
                "center": {{ "name": "core" }},
                "parts": [
                    {{ "name": "part1", "relative_to": "core", "position": {{ "x": 10, "y": 0, "z": 0 }} }}
                ]
            }}
          }},
          "CAUSATION": {{ "requires": [], "produces": [] }},
          "CONNECTIONS": {{ "relational": [] }},
          "TIME": {{ "lifecycle": [] }}
        }}
        
        INSTRUCTIONS:
        - Fill in the values for '{name}' based on scientific reality.
        - FOR "ARRANGEMENT": You MUST estimate actual 3D dimensions in cm.
        - RETURN ONLY JSON.
        """
        
        try:
            print(f"  > {name}...", end="", flush=True)
            res = self.client.json_completion("SeedGen", prompt)
            
            # Simple check
            if "CORE" in res and "ARRANGEMENT" in res:
                # ASSIGN ID VIA IDENTITY MANAGER (centralized)
                concept_type = res.get("CORE", {}).get("type", "")
                
                # Determine group based on type
                if "organism" in concept_type:
                    group = 21  # Living systems
                elif "artifact" in concept_type:
                    group = 30  # Artifacts
                elif "natural_object" in concept_type or "planet" in concept_type:
                    group = 20  # Physical natural
                elif "abstraction" in concept_type or "phenomenon" in concept_type:
                    group = 50  # Abstract
                else:
                    group = 20  # Default physical
                
                # Mint the ID through centralized system
                res["CORE"]["id"] = self.identity.mint_id(name, group)
                
                path = os.path.join(self.output_dir, fname)
                with open(path, 'w', encoding='utf-8') as f:
                    json.dump(res, f, indent=2)
                print(colored(f" DONE (ID: {res['CORE']['id']})", "green"))
            else:
                print(colored(f" FAIL (Structure mismatch). Keys: {list(res.keys())}", "red"))
                
        except Exception as e:
            print(colored(f" ERROR: {e}", "red"))

if __name__ == "__main__":
    # Ensure dir exists
    os.makedirs("data/concepts", exist_ok=True)
    gen = SeedGenerator()
    gen.generate_all()
