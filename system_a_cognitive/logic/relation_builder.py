"""
RelationBuilder - Centralized utility for creating ID-based relations between concepts.
Used by Ingestor, Gardener, and other components to maintain navigable connections.
"""
import json
import os
import re
from typing import List, Dict, Optional, Set
from system_a_cognitive.logic.identity import IdentityManager


class RelationBuilder:
    """
    Utility for adding ID-based relations to concept blocks.
    Scans text for mentioned concepts and adds proper (group, item) references.
    """
    
    def __init__(self, identity_manager: IdentityManager = None, concepts_dir: str = "data/concepts"):
        self.identity_manager = identity_manager or IdentityManager()
        self.concepts_dir = concepts_dir
        self._name_cache = {}  # Cache of lowercased names for fast lookup
        self._build_name_cache()
    
    def _build_name_cache(self):
        """Build cache of all concept names for matching."""
        for name, id_data in self.identity_manager.registry.items():
            self._name_cache[name.lower()] = id_data
    
    def get_id_str(self, name: str) -> Optional[str]:
        """Get (group, item) string for a concept name."""
        key = name.lower().replace(' ', '_')
        id_data = self._name_cache.get(key)
        if id_data:
            return f"({id_data['group']}, {id_data['item']})"
        return None
    
    def find_mentioned_concepts(self, text: str, exclude_names: Set[str] = None) -> List[str]:
        """
        Find concept names mentioned in text.
        Returns list of names that exist in the registry.
        """
        exclude_names = exclude_names or set()
        found = []
        
        # Simple approach: check each registered name against text
        text_lower = text.lower()
        
        for name in self._name_cache.keys():
            # Skip very short names (too many false positives)
            if len(name) < 3:
                continue
            # Skip excluded names (e.g., the concept itself)
            if name in exclude_names:
                continue
            # Check if name appears in text (word boundary)
            if re.search(rf'\b{re.escape(name)}\b', text_lower):
                found.append(name)
        
        return found
    
    def add_relation(self, block: Dict, predicate: str, target_name: str) -> bool:
        """
        Add an ID-based relation claim to a block.
        Returns True if relation was added, False if already exists or target not found.
        """
        target_id = self.get_id_str(target_name)
        if not target_id:
            return False
        
        if "claims" not in block:
            block["claims"] = []
        
        # Check if relation already exists
        for claim in block["claims"]:
            obj = str(claim.get("object", ""))
            if claim.get("predicate") == predicate and target_id in obj:
                return False  # Already exists
        
        block["claims"].append({
            "predicate": predicate,
            "object": f"{target_name} {target_id}",
            "epistemic": {
                "confidence": 0.9,
                "status": "AUTO_GENERATED",
                "source_type": "RELATION_BUILDER"
            }
        })
        return True
    
    def auto_add_relations(self, block: Dict, infer_types: bool = True) -> int:
        """
        Automatically scan block content and add relations to mentioned concepts.
        Returns count of relations added.
        """
        block_name = block.get("name", "").lower()
        exclude = {block_name, block_name.replace(' ', '_')}
        added = 0
        
        # Scan definition
        definition = block.get("surface_layer", {}).get("definition", "")
        mentioned = self.find_mentioned_concepts(definition, exclude)
        
        for name in mentioned:
            if self.add_relation(block, "RELATED_TO", name):
                added += 1
        
        # Scan claims for potential targets
        for claim in block.get("claims", []):
            obj = str(claim.get("object", ""))
            # Skip if already has ID reference
            if re.search(r'\(\d+,\s*\d+\)', obj):
                continue
            
            # Check if object matches a concept name
            obj_clean = obj.lower().replace(' ', '_')
            if obj_clean in self._name_cache:
                # Add ID to existing claim
                target_id = self.get_id_str(obj_clean)
                if target_id and target_id not in obj:
                    claim["object"] = f"{obj} {target_id}"
                    added += 1
        
        return added
    
    def enrich_and_save(self, block: Dict, filepath: str = None) -> int:
        """
        Add relations to block and save to disk.
        Returns count of relations added.
        """
        added = self.auto_add_relations(block)
        
        if added > 0 and filepath:
            with open(filepath, 'w', encoding='utf-8') as f:
                json.dump(block, f, indent=2)
        
        return added


# Singleton instance for easy access
_default_builder = None

def get_builder() -> RelationBuilder:
    """Get the default RelationBuilder instance."""
    global _default_builder
    if _default_builder is None:
        _default_builder = RelationBuilder()
    return _default_builder
