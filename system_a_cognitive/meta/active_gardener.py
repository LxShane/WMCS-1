import os
import json
import time
import random
from termcolor import colored
from system_b_llm.interfaces.gemini_client import GeminiClient
from system_a_cognitive.meta.deep_researcher import DeepResearchAgent
from config import Config

class ActiveGardener:
    """
    Background agent that:
    1. Audits existing concepts for 'Knowledge Decay' or 'Gaps'.
    2. Autonomously triggers Deep Research to fill those gaps.
    3. Ensures the Knowledge Graph remains 'Fresh' and 'Deep'.
    """
    def __init__(self, concepts_dir="data/concepts"):
        self.concepts_dir = concepts_dir
        self.researcher = DeepResearchAgent()
        self.client = GeminiClient(Config.LLM_API_KEY, Config.LLM_MODEL)
        
    def start_cycle(self, max_loops=1):
        """
        Runs the gardening cycle.
        """
        print(colored("\n🌱 [ACTIVE GARDENER] waking up...", "green"))
        
        for i in range(max_loops):
            self.audit_and_fix()
            
        print(colored("🌱 [ACTIVE GARDENER] returning to sleep.\n", "green"))

    def rebuild_registry(self):
        """
        Scans all concept files and rebuilds registry.json.
        """
        print(colored("  [Gardener] Rebuilding Registry from disk...", "magenta"))
        registry = {}
        files = [f for f in os.listdir(self.concepts_dir) if f.endswith(".json")]
        
        for fname in files:
            try:
                with open(os.path.join(self.concepts_dir, fname), 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    name = data.get("name", "").lower().replace(" ", "_")
                    gid = data.get("id", {}).get("group")
                    iid = data.get("id", {}).get("item")
                    
                    if name and gid and iid:
                        registry[name] = {"group": gid, "item": iid}
            except: continue
            
        reg_path = os.path.join(os.path.dirname(self.concepts_dir), "registry.json")
        with open(reg_path, 'w', encoding='utf-8') as f:
            json.dump(registry, f, indent=4)
        print(colored(f"  [Gardener] Registry Rebuilt. Indexed {len(registry)} concepts.", "green"))

    def audit_and_fix(self):
        """
        Scans for gaps. Randomly chooses between SPATIAL, PHYSICS, and REGISTRY audits.
        """
        audit_mode = random.choices(["SPATIAL", "PHYSICS", "REGISTRY"], weights=[40, 40, 20], k=1)[0]
        
        if audit_mode == "REGISTRY":
            self.rebuild_registry()
            return

        print(colored(f"  [Gardener] Running Audit Mode: {audit_mode}...", "cyan"))
        # ... logic continues ...

        files = [f for f in os.listdir(self.concepts_dir) if f.endswith(".json")]
        random.shuffle(files) # Randomize to avoid getting stuck
        
        target_file = None
        target_data = None
        gap_type = None
        
        # 1. Find a candidate
        for fname in files:
            try:
                with open(os.path.join(self.concepts_dir, fname), 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    
                ctype = data.get("type", "UNKNOWN")
                cid = data.get("id", {}).get("group", 99)
                is_physical = (20 <= cid <= 39) or ctype in ["INANIMATE_OBJECT", "LIVING_SYSTEM", "BODY_PART", "MECHANICAL_PART"]
                
                if not is_physical: continue

                facets = data.get("facets", {})
                
                if audit_mode == "SPATIAL":
                    spatial = facets.get("SPATIAL")
                    if not spatial or (not spatial.get("location") and not spatial.get("connected_to")):
                        target_file = fname
                        target_data = data
                        gap_type = "SPATIAL"
                        break
                        
                elif audit_mode == "PHYSICS":
                    structural = facets.get("STRUCTURAL", {})
                    # Check for missing material_properties
                    if "material_properties" not in structural:
                        target_file = fname
                        target_data = data
                        gap_type = "PHYSICS"
                        break
                        
            except:
                continue
                
        if target_file:
            self._apply_fix(target_data, gap_type)
        else:
            print(colored(f"  [Gardener] No {audit_mode} gaps found. The garden is lush.", "green"))

    def _apply_fix(self, concept_data, gap_type):
        name = concept_data.get("name")
        print(colored(f"  [Gardener] GAP DETECTED: '{name}' is missing {gap_type} Data.", "yellow"))
        
        if gap_type == "SPATIAL":
             print(colored(f"  [Gardener] TRIGGERING RESEARCH: 'Spatial anatomy of {name}'", "magenta"))
             query = f"Spatial anatomy and physical connections of {name}. What is it connected to? Where is it located?"
             self.researcher.conduct_deep_research(query, max_depth=1)
             self._patch_spatial_facet(name)
             
        elif gap_type == "PHYSICS":
             print(colored(f"  [Gardener] TRIGGERING RESEARCH: 'Material properties of {name}'", "magenta"))
             query = f"Physical material properties of {name}. Is it rigid? Conductive? Solid/Liquid?"
             self.researcher.conduct_deep_research(query, max_depth=1)
             self._patch_physics_facet(name)
        
    def _patch_spatial_facet(self, concept_name):
        # ... (Existing logic, simplified for brevity in this edit if needed, but I'll keep it)
        # Actually I need to keep the existing _patch_spatial_facet logic.
        # But for this Replace block I am REPLACING _apply_fix and everything below.
        # So I must include _patch_spatial_facet's body.
        
        print(colored(f"  [Gardener] Patching '{concept_name}' with Spatial data...", "cyan"))
        prompt = f"""Task: Generate strictly the SPATIAL facet for "{concept_name}". Schema: {{ "location": "...", "connected_to": [], "coordinates": [] }} Output JSON."""
        response = self.client.json_completion("Spatial Anatomist", prompt)
        if "location" in response: self._write_patch(concept_name, "SPATIAL", response)

    def _patch_physics_facet(self, concept_name):
        print(colored(f"  [Gardener] Patching '{concept_name}' with Physics data...", "cyan"))
        prompt = f"""
        Task: Generate strictly the MATERIAL PROPERTIES for "{concept_name}".
        Schema:
        {{
            "material_properties": {{
                "rigidity": "High/Medium/Low",
                "flexibility": "High/Medium/Low",
                "state": "Solid/Liquid/Gas",
                "conductivity": "None/Elec/Thermal"
             }}
        }}
        Output JSON.
        """
        response = self.client.json_completion("Physics Expert", prompt)
        
        if "material_properties" in response:
             # Structure adjustment: The schema expects facets.STRUCTURAL.material_properties
             # So we need to be careful with _write_patch
             self._write_patch(concept_name, "STRUCTURAL", response, merge=True)

    def _write_patch(self, concept_name, facet_key, facet_data, merge=False):
        """Helper to write to disk. Logic centralized."""
        for f in os.listdir(self.concepts_dir):
            if f.endswith(".json"):
                try:
                    path = os.path.join(self.concepts_dir, f)
                    with open(path, 'r', encoding='utf-8') as jf:
                        d = json.load(jf)
                        if d.get("name") == concept_name:
                            if "facets" not in d: d["facets"] = {}
                            
                            if merge and facet_key in d["facets"]:
                                d["facets"][facet_key].update(facet_data)
                            else:
                                d["facets"][facet_key] = facet_data
                                
                            d["autocorrected"] = True
                            with open(path, 'w', encoding='utf-8') as wf:
                                json.dump(d, wf, indent=2)
                            print(colored(f"  [Gardener] SUCCESS: '{concept_name}' updated.", "green"))
                            return
                except: pass
        print(colored(f"  [Gardener] Error: Could not file file for '{concept_name}'", "red"))

if __name__ == "__main__":
    gardener = ActiveGardener()
    gardener.start_cycle()
