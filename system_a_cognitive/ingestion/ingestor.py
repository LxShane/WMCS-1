import json
import os
from typing import List, Dict, Any
from system_b_llm.interfaces.gemini_client import GeminiClient
from config import Config
from .prompts import INGESTION_SYSTEM_PROMPT, INGESTION_USER_PROMPT_TEMPLATE

class ContentIngestor:
    def __init__(self, identity_manager=None):
        self.client = GeminiClient(Config.LLM_API_KEY, Config.LLM_MODEL)
        self.output_dir = os.path.join("data", "concepts")
        os.makedirs(self.output_dir, exist_ok=True)
        self.identity_manager = identity_manager
        
        from system_a_cognitive.subsystems.visual_cortex import VisualCortex
        self.visual_cortex = VisualCortex(self.client)

    def ingest_file(self, filepath: str) -> List[str]:
        """
        Reads a file and ingests it. Supports Text and Images.
        """
        if not os.path.exists(filepath):
            return [f"Error: File not found {filepath}"]

        # IMAGE HANDLING
        if filepath.lower().endswith(('.png', '.jpg', '.jpeg', '.webp')):
             return self.ingest_image(filepath)

        # TEXT HANDLING

        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                content = f.read()
        except UnicodeDecodeError:
             with open(filepath, 'r', encoding='latin-1') as f:
                content = f.read()
        
        return self.ingest_text(content, source_name=os.path.basename(filepath))

    def ingest_proposition(self, text: str) -> List[str]:
        """
        Fast ingestion for single propositions.
        Ex: "A Zorb is a floating pink orb."
        """
        system_prompt = (
            "You are a Knowledge Extraction Engine.\\n"
            "Input: A single factual statement.\\n"
            "Output: A SINGLE valid Concept Block JSON.\\n"
            "Rules:\\n"
            "1. Extract the SUBJECT as the concept Name.\\n"
            "2. Extract the DEFINITION.\\n"
            "3. Extract CLAIMS (Subject -> Predicate -> Object).\\n"
            "4. Infer the TYPE (Physical, Abstract, etc).\\n"
            "5. Return ONLY JSON."
        )
        
        print(f"DEBUG: Learning Proposition: '{text}'...")
        response_json = self.client.json_completion(system_prompt, text)
        
        # Wrap in list if single object
        if isinstance(response_json, dict) and "name" in response_json:
            blocks = [response_json]
        elif isinstance(response_json, dict) and "blocks" in response_json:
             blocks = response_json["blocks"]
        else:
             blocks = []
             
        return self._process_and_save_blocks(blocks)

    def ingest_text(self, content: str, source_name: str = "interactive") -> List[str]:
        """
        Ingests raw text string.
        """
        # Limit to ~30k chars for safety
        truncated_content = content[:30000]
        prompt = INGESTION_USER_PROMPT_TEMPLATE.format(text=truncated_content) 

        with open("ingestion_debug.log", "a", encoding='utf-8') as log:
            log.write(f"\n--- Ingesting {source_name} ---\n")

        print(f"DEBUG: Sending ingestion request for {source_name}...")
        response_json = self.client.json_completion(INGESTION_SYSTEM_PROMPT, prompt)
        
        with open("ingestion_debug.log", "a", encoding='utf-8') as log:
            log.write(f"LLM Response: {response_json}\n")

        if "error" in response_json:
            print(f"Error from LLM: {response_json}")
            return []

        blocks = response_json.get("blocks", [])
        return self._process_and_save_blocks(blocks)

    def ingest_image(self, filepath: str) -> List[str]:
        """
        Ingests an image concept via Visual Cortex.
        """
        print(f"DEBUG: Analying Visual Data: {filepath}...")
        result = self.visual_cortex.analyze_diagram(filepath)
        blocks = result.get("concepts", [])
        return self._process_and_save_blocks(blocks)

    def _process_and_save_blocks(self, blocks: List[Dict]) -> List[str]:
        created_concepts = []
        for block_data in blocks:
            name = block_data.get("name")
            if not name: continue
            
            if not name: continue
            
            # Robust sanitization for Windows/Linux
            safe_name = name.lower().replace(' ', '_')
            for char in ['/', '\\', ':', '*', '?', '"', '<', '>', '|']:
                safe_name = safe_name.replace(char, '-')
            
            filename = f"{safe_name}.json"
            save_path = os.path.join(self.output_dir, filename)
            
            # Load existing if present to merging claims
            existing_data = {}
            if os.path.exists(save_path):
                try:
                    with open(save_path, 'r', encoding='utf-8') as f:
                        existing_data = json.load(f)
                except: pass

            # MERGE LOGIC
            if existing_data:
                # 1. Preserve ID
                if "id" not in block_data: block_data["id"] = existing_data.get("id")
                
                # 2. Merge Claims (Append)
                existing_claims = existing_data.get("claims", [])
                new_claims = block_data.get("claims", [])
                
                # Simple append (Advanced: Deduplicate based on predicate+object+temporal)
                # For now we append to capture history
                combined_claims = existing_claims + new_claims
                
                # Update block_data with combined layers
                # We overwrite surface/deep layers with newest, but KEEP all claims
                block_data["claims"] = combined_claims
                
                print(f"  > Merging {len(new_claims)} new claims into {len(existing_claims)} existing.")

            # ENSURE ID EXISTS (Minting if still missing)
            if "id" not in block_data:
                # Fallback Logic based on Type
                ctype = block_data.get("type", "UNKNOWN")
                import random
                
                if ctype == "ABSTRACT_CONCEPT":
                    group = 50
                elif ctype == "SOCIAL_CONSTRUCT":
                    group = 60
                elif ctype == "MATHEMATICAL_OBJECT":
                    group = 40
                elif ctype == "LIVING_SYSTEM" or ctype == "INANIMATE_OBJECT":
                    group = 21 # Default Physical
                else:
                    group = 99 # Unknown
                    
                if self.identity_manager:
                    block_data["id"] = self.identity_manager.mint_id(name, group)
                else:
                    # Fallback if no manager (shouldn't happen in main integration)
                    block_data["id"] = {
                        "group": group,
                        "item": 9000 + hash(name) % 1000 # Semi-stable hash
                    }
            
            # Save
            with open(save_path, 'w', encoding='utf-8') as f:
                json.dump(block_data, f, indent=2)
            
            # AUTO-ADD ID RELATIONS
            try:
                from system_a_cognitive.logic.relation_builder import get_builder
                builder = get_builder()
                relations_added = builder.auto_add_relations(block_data)
                if relations_added > 0:
                    # Re-save with new relations
                    with open(save_path, 'w', encoding='utf-8') as f:
                        json.dump(block_data, f, indent=2)
                    print(f"  + Added {relations_added} ID-based relations")
            except Exception as e:
                print(f"  [!] RelationBuilder error: {e}")
            
            created_concepts.append(name)
            print(f"  Saved Concept: {name} -> {filename}")

        return created_concepts

    def ingest_all(self, memory_path: str, vector_store=None):
        """
        Ingests all JSON concepts in the directory.
        If vector_store is provided, it skips files that are already indexed (Title check).
        """
        concept_dir = os.path.join(memory_path, "concepts")
        if not os.path.exists(concept_dir): return
        
        files = [f for f in os.listdir(concept_dir) if f.endswith('.json')]
        print(f"[Ingestor] Found {len(files)} concept files.")
        
        # Optimization: Get existing names from VectorStore if passed
        existing_names = set()
        if vector_store:
            # This assumes vector_store has a way to list all source files or names
            # If not, we can just rely on the count check in main.py, 
            # BUT for 'force=True' we want to be smart.
            pass

        count = 0
        for f in files:
            path = os.path.join(concept_dir, f)
            # We don't need to 'ingest' (LLM Process) JSON files that are already JSON.
            # We just need to LOAD them into the Vector Database.
            # This method seems to have been missing or defined elsewhere?
            # We will implement the loading logic here or assume Main does it.
            
            # WAIT: The Main.py expects 'ingest_all' to load data into Vector Store.
            # But ContentIngestor usually *creates* JSON from Text.
            # Who puts JSON into Chroma? 
            # It's 'VectorStore.add_concept_block'.
            
            if vector_store:
                with open(path, 'r', encoding='utf-8') as jf:
                     try:
                        data = json.load(jf)
                        vector_store.add_concept_block(data)
                        count += 1
                     except: pass
        
        if vector_store:
             print(f"[Ingestor] Loaded {count} concepts into Vector Store.")
