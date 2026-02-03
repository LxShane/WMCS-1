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

    def audit_and_fix(self):
        """
        Scans for a specific type of gap (currently: SPATIAL data in Physical Objects).
        """
        files = [f for f in os.listdir(self.concepts_dir) if f.endswith(".json")]
        random.shuffle(files) # Randomize to avoid getting stuck
        
        target_file = None
        target_data = None
        
        print(colored("  [Gardener] Scanning for spatial gaps...", "cyan"))
        
        # 1. Find a candidate
        for fname in files:
            try:
                with open(os.path.join(self.concepts_dir, fname), 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    
                # Filter: Must be Physical (Group 20-39) or explicitly typed
                # And missing SPATIAL facet
                ctype = data.get("type", "UNKNOWN")
                cid = data.get("id", {}).get("group", 99)
                
                is_physical = (20 <= cid <= 39) or ctype in ["INANIMATE_OBJECT", "LIVING_SYSTEM", "BODY_PART"]
                
                if is_physical:
                    facets = data.get("facets", {})
                    spatial = facets.get("SPATIAL")
                    
                    # Gap Detected if SPATIAL is missing or empty
                    if not spatial or (not spatial.get("location") and not spatial.get("connected_to")):
                        target_file = fname
                        target_data = data
                        break
            except:
                continue
                
        if target_file:
            self._apply_fix(target_data)
        else:
            print(colored("  [Gardener] No gaps found. The garden is lush.", "green"))

    def _apply_fix(self, concept_data):
        name = concept_data.get("name")
        print(colored(f"  [Gardener] GAP DETECTED: '{name}' is missing Spatial Data.", "yellow"))
        print(colored(f"  [Gardener] TRIGGERING AUTONOMOUS RESEARCH: 'Spatial anatomy of {name}'", "magenta", attrs=['bold']))
        
        # 1. Trigger Research
        # We ask specifically for spatial details
        query = f"Spatial anatomy and physical connections of {name}. What is it connected to? Where is it located?"
        self.researcher.conduct_deep_research(query, max_depth=1)
        
        # 2. Patch the original file (Heuristic)
        # The researcher creates NEW files (nodes), but might not update the original file's facet.
        # So we do a quick specific patch here.
        self._patch_spatial_facet(name)
        
    def _patch_spatial_facet(self, concept_name):
        """
        Uses LLM to generate the SPATIAL facet specifically for the target concept, 
        now that research (might have) happened or just based on trained knowledge,
        and updates the file.
        """
        print(colored(f"  [Gardener] Patching '{concept_name}' with new spatial data...", "cyan"))
        
        prompt = f"""
        Task: Generate strictly the SPATIAL facet for the concept "{concept_name}".
        
        Schema:
        {{
            "location": "Relative position (e.g. Anterior, Distal)",
            "connected_to": ["List of parts it physically attaches to"],
            "coordinates": []
        }}
        
        Output ONLY valid JSON.
        """
        
        response = self.client.json_completion("You are a Spatial Anatomist.", prompt)
        
        if "location" in response:
            # Load and Update
            safe_name = concept_name.lower().replace(' ', '_') # Simplified
            # Better to find file by ID/Name loop? We know files are usually snake_case.
            # But the 'audit' loop gives us the filename. 
            # I'll just re-scan for the specific file matching name to be safe.
             
            target_path = None
            for f in os.listdir(self.concepts_dir):
                if f.endswith(".json"):
                    try:
                        with open(os.path.join(self.concepts_dir, f), 'r') as jf:
                            d = json.load(jf)
                            if d.get("name") == concept_name:
                                target_path = os.path.join(self.concepts_dir, f)
                                break
                    except: pass
            
            if target_path:
                with open(target_path, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                
                if "facets" not in data: data["facets"] = {}
                data["facets"]["SPATIAL"] = response
                data["autocorrected"] = True
                
                with open(target_path, 'w', encoding='utf-8') as f:
                    json.dump(data, f, indent=2)
                    
                print(colored(f"  [Gardener] SUCCESS: '{concept_name}' updated with spatial data.", "green"))
            else:
                 print(colored(f"  [Gardener] Error: Could not find file for '{concept_name}' to patch.", "red"))

if __name__ == "__main__":
    gardener = ActiveGardener()
    gardener.start_cycle()
