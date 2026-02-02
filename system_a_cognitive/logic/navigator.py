import json
from termcolor import colored
import re

class ConceptNavigator:
    def __init__(self, kernel):
        self.blocks = kernel.blocks
        self.client = kernel.llm_client
        self.id_map = {}
        self._build_id_map()

    def _build_id_map(self):
        """Map 'G,I' strings to Block objects for fast lookup."""
        for b in self.blocks.values():
            if "id" in b:
                key = f"{b['id']['group']},{b['id']['item']}"
                self.id_map[key] = b

    def get_exits(self, block):
        """
        Finds all outbound links from the block.
        Returns list of dicts: {'dimension': str, 'target_id': str, 'target_name': str, 'link_confidence': float}
        """
        exits = []
        
        # 1. SCAN CLAIMS (New Schema)
        claims = block.get('claims', [])
        for claim in claims:
            # We look for claims where 'object' is a Concept Name or ID
            # This requires resolution, but for now we assume explicit IDs might appear or Names exist in map
            # To be robust, we rely on the fact that Ingestor might put IDs in objects
            
            # Simple Heuristic: If object string matches an ID pattern
            obj_str = str(claim.get('object', ''))
            matches = re.findall(r'\((\d+),\s*(\d+)\)', obj_str)
            
            # Or if object name exists in ID map (Name Resolution)
            # This is expensive, so we stick to explicit IDs for now or Regex
            
            link_conf = claim.get('epistemic', {}).get('confidence', 1.0)
            
            for g, i in matches:
                target_key = f"{g},{i}"
                if target_key in self.id_map:
                    target_name = self.id_map[target_key].get('name', 'Unknown')
                    exits.append({
                        'dimension': f"CLAIM:{claim.get('predicate','rel')}", 
                        'target_id': target_key,
                        'target_name': target_name,
                        'context': f"Claim: {claim.get('predicate')} -> {obj_str}",
                        'link_confidence': float(link_conf)
                    })

        # 2. SCAN FACETS (Legacy)
        facets = block.get('facets', {})
        for facet_name, content in facets.items():
            content_str = json.dumps(content)
            matches = re.findall(r'\((\d+),\s*(\d+)\)', content_str)
            for g, i in matches:
                target_key = f"{g},{i}"
                if target_key in self.id_map:
                    target_name = self.id_map[target_key].get('name', 'Unknown')
                    exits.append({
                        'dimension': facet_name,
                        'target_id': target_key,
                        'target_name': target_name,
                        'context': f"Found in {facet_name}",
                        'link_confidence': 0.9 # Default for legacy structure
                    })
        
        return exits

    def navigate(self, start_blocks, query, max_steps=1):
        """
        Agentic Loop to expand context with Confidence Math.
        """
        print(colored("Step 2.1 (Navigation): Activating Agentic Navigator...", "cyan"))
        
        current_context = list(start_blocks)
        visited_ids = set()
        
        # Map: BlockID -> Cumulative Confidence
        block_confidence = {} 
        
        # Init start blocks
        for b in start_blocks:
            if 'id' in b:
                key = f"{b['id']['group']},{b['id']['item']}"
                visited_ids.add(key)
                block_confidence[key] = 1.0 # Root is Truth

        if not start_blocks: return []
        focus_block = start_blocks[0]
        current_path_confidence = 1.0
        
        for step in range(max_steps):
            print(colored(f"  > [Nav Step {step+1}] Focused on: '{focus_block.get('name')}' (Conf: {current_path_confidence:.2f})", "yellow"))
            
            exits = self.get_exits(focus_block)
            if not exits:
                print(colored("    > No exits found. Stopping.", "white"))
                break

            # Deduplicate exits by target_id
            unique_exits = {e['target_id']: e for e in exits}.values()
            sorted_exits = sorted(unique_exits, key=lambda x: x['link_confidence'], reverse=True)[:10]

            # LLM Selection
            options_str = ""
            for i, ex in enumerate(sorted_exits):
                options_str += f"{i}. [{ex['dimension']}] -> '{ex['target_name']}' (Link Conf: {ex['link_confidence']:.2f})\n"
            
            prompt = f"""
            You are the Navigation Agent.
            Query: "{query}"
            Current: "{focus_block.get('name')}"
            Options:
            {options_str}
            Pick the most relevant link (0-9) or STOP.
            """
            
            response = self.client.completion("Pick number or STOP.", prompt).strip()
            
            if "STOP" in response.upper() or not response.isdigit():
                break
                
            choice_idx = int(response)
            if 0 <= choice_idx < len(sorted_exits):
                selected = list(sorted_exits)[choice_idx]
                t_id = selected['target_id']
                
                if t_id not in visited_ids:
                    new_block = self.id_map[t_id]
                    
                    # MATH: Propagate Confidence
                    new_conf = current_path_confidence * selected['link_confidence']
                    
                    # Attach metadata to block for the Logic Engine to see
                    # We inject it dynamically into the object in memory (safe for this session)
                    new_block['_computed_confidence'] = new_conf
                    
                    current_context.append(new_block)
                    visited_ids.add(t_id)
                    
                    focus_block = new_block
                    current_path_confidence = new_conf
                    
                    print(colored(f"    > Moving to: {new_block.get('name')} (New Cum. Conf: {new_conf:.2f})", "cyan"))
                else:
                    break
            else:
                break
                
        return current_context
