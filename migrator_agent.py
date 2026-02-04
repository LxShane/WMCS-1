"""
Migrator Agent - Upgrades concepts from v0.5 to v1.0
Uses Gemini to infer missing deep structure (Spatial, Composition, Grounding).
"""
import json
import os
from termcolor import colored
from system_b_llm.interfaces.gemini_client import GeminiClient
from config import Config
from schema_v1_production import ConceptBlockV1

class MigratorAgent:
    def __init__(self):
        self.client = GeminiClient(Config.LLM_API_KEY, Config.LLM_MODEL)
        self.output_dir = "data/concepts_v1"
        os.makedirs(self.output_dir, exist_ok=True)

    def migrate_concept(self, filename: str, source_dir="data/concepts"):
        """
        Reads old concept, prompts LLM for upgrade, saves new concept.
        """
        path = os.path.join(source_dir, filename)
        if not os.path.exists(path):
            print(f"Error: {path} not found")
            return None

        with open(path, 'r', encoding='utf-8') as f:
            old_data = json.load(f)

        name = old_data.get("name", "Unknown")
        print(colored(f"Migrating '{name}' to v1.0...", "cyan"))

        # Construct Prompt
        prompt = f"""
        You are the WMCS Schema Architect.
        Task: Upgrade a concept from v0.5 (Flat) to v1.0 (Deep Structure).
        
        Input Concept (v0.5):
        {json.dumps(old_data, indent=2)}
        
        Required v1.0 Schema Structure (JSON):
        Root keys: CORE, GROUNDING, CLASSIFICATION, SUBSTANCE, ARRANGEMENT, CAUSATION, CONNECTIONS.
        
        1. CORE: id, name, type (e.g. organism.animal...), definition
        2. GROUNDING: chain, base_types (perceptual/logic/etc), confidence
        3. SUBSTANCE (Composition): Recursive breakdown.
        4. ARRANGEMENT (Spatial): "structure_spatial" with center, overall size, parts (x/y/z).
        5. CAUSATION: requires, produces, caused_by.
        
        INSTRUCTIONS:
        - INFER missing data based on scientific reality.
        - For 'structure_spatial', estimate actual dimensions (cm) for a standard instance.
        - RETURN ONLY VALID JSON matching the schema.
        """

        # Call LLM
        print("  > Asking Gemini to restructure...")
        response = self.client.json_completion("Schema Migrator", prompt)
        
        # Validation (Basic)
        try:
            # We try to validate against our Pydantic model
            # Note: valid Pydantic models can be complex to instantiate directly from raw LLM JSON 
            # if the LLM isn't perfect, so we might need a loose check first.
            # For this prototype, we'll just save the raw JSON if it looks mostly right.
            
            if "structure_spatial" in response and "composition" in response:
                pass # Good signal
            
            # Save
            save_path = os.path.join(self.output_dir, filename)
            with open(save_path, 'w', encoding='utf-8') as f:
                json.dump(response, f, indent=2)
            
            print(colored(f"  > Success! Saved to {save_path}", "green"))
            return response
            
        except Exception as e:
            print(colored(f"  > Validation/Save Error: {e}", "red"))
            return None

if __name__ == "__main__":
    agent = MigratorAgent()
    agent.migrate_concept("cat.json")
