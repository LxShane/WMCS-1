"""
Variance Engine (WMCS v1.0)
Handles "typical X" vs "specific X" variations.
Manages prototypes, inheritance, and variance ranges.
"""
import json
import os
from typing import Dict, List, Optional, Tuple, Any
from system_a_cognitive.logic.graph_engine import get_graph_engine


class VarianceEngine:
    def __init__(self, concepts_dir: str = "data/concepts"):
        self.concepts_dir = concepts_dir
        self.graph = get_graph_engine(concepts_dir)
        self._prototypes = {}  # {type: concept_data}
        self._build_prototypes()
    
    def _build_prototypes(self):
        """Build prototype index from concepts marked as prototypical."""
        for name, concept in self.graph._concept_cache.items():
            # Check if this is a prototype
            variation = concept.get("VARIATION", {})
            if variation.get("is_prototype", False):
                type_str = concept.get("CORE", {}).get("type", "")
                if type_str:
                    self._prototypes[type_str] = concept
            
            # Also use first instance of each type as default prototype
            type_str = concept.get("CORE", {}).get("type", "")
            if type_str and type_str not in self._prototypes:
                self._prototypes[type_str] = concept
    
    def get_prototype(self, type_string: str) -> Optional[Dict]:
        """
        Get the prototypical/default instance for a type.
        """
        return self._prototypes.get(type_string)
    
    def get_variance_range(self, concept: Dict, property_path: str) -> Dict:
        """
        Get the min/max/typical range for a property.
        property_path: e.g., "ARRANGEMENT.structure_spatial.overall.size.value"
        Returns {min, max, typical, unit}
        """
        result = {
            "min": None,
            "max": None,
            "typical": None,
            "unit": None,
            "variance": None
        }
        
        # Check VARIATION category
        variation = concept.get("VARIATION", {})
        variance_data = variation.get("variance", {})
        
        if property_path in variance_data:
            v = variance_data[property_path]
            if isinstance(v, dict):
                result.update(v)
            else:
                result["variance"] = v
        
        # Get current value as typical if not specified
        current = self._get_nested(concept, property_path)
        if current is not None and result["typical"] is None:
            result["typical"] = current
        
        return result
    
    def _get_nested(self, data: Dict, path: str) -> Any:
        """Get value from nested dict using dot-notation path."""
        parts = path.split(".")
        current = data
        
        for part in parts:
            if isinstance(current, dict):
                current = current.get(part)
            else:
                return None
        
        return current
    
    def inherit_from_parent(self, child: Dict, parent_type: str) -> Dict:
        """
        Copy missing fields from parent prototype to child.
        Returns updated child.
        """
        parent = self.get_prototype(parent_type)
        if not parent:
            return child
        
        # Deep merge: only fill missing fields
        return self._merge_missing(child, parent)
    
    def _merge_missing(self, target: Dict, source: Dict) -> Dict:
        """Recursively merge missing fields from source into target."""
        for key, value in source.items():
            if key not in target:
                target[key] = value
            elif isinstance(value, dict) and isinstance(target.get(key), dict):
                self._merge_missing(target[key], value)
        
        return target
    
    def get_variants(self, type_string: str) -> List[Dict]:
        """
        Get all variants/instances of a type.
        """
        variants = []
        
        for name, concept in self.graph._concept_cache.items():
            c_type = concept.get("CORE", {}).get("type", "")
            if c_type == type_string or c_type.startswith(type_string + "."):
                variants.append({
                    "name": name,
                    "type": c_type,
                    "is_prototype": concept.get("VARIATION", {}).get("is_prototype", False)
                })
        
        return variants
    
    def compare_to_prototype(self, instance: Dict) -> Dict:
        """
        Compare an instance to its prototype.
        Returns {matches: [], differs: [], missing_in_instance: []}
        """
        result = {
            "matches": [],
            "differs": [],
            "missing_in_instance": [],
            "deviation_score": 0.0
        }
        
        type_str = instance.get("CORE", {}).get("type", "")
        prototype = self.get_prototype(type_str)
        
        if not prototype:
            return result
        
        # Compare key fields
        key_fields = [
            "CORE.type",
            "ARRANGEMENT.structure_spatial.overall.shape",
            "SUBSTANCE.composition"
        ]
        
        for field in key_fields:
            proto_val = self._get_nested(prototype, field)
            inst_val = self._get_nested(instance, field)
            
            if proto_val is None:
                continue
            
            if inst_val is None:
                result["missing_in_instance"].append(field)
            elif proto_val == inst_val:
                result["matches"].append(field)
            else:
                result["differs"].append({
                    "field": field,
                    "prototype": str(proto_val)[:50],
                    "instance": str(inst_val)[:50]
                })
        
        # Calculate deviation score
        total = len(result["matches"]) + len(result["differs"]) + len(result["missing_in_instance"])
        if total > 0:
            deviations = len(result["differs"]) + len(result["missing_in_instance"])
            result["deviation_score"] = deviations / total
        
        return result
    
    def is_typical(self, instance: Dict) -> bool:
        """Check if instance is within typical variance of its prototype."""
        comparison = self.compare_to_prototype(instance)
        return comparison["deviation_score"] < 0.3  # 30% deviation threshold


# Singleton
_engine = None

def get_variance_engine(concepts_dir: str = "data/concepts") -> VarianceEngine:
    global _engine
    if _engine is None:
        _engine = VarianceEngine(concepts_dir)
    return _engine


if __name__ == "__main__":
    engine = VarianceEngine()
    
    print("Available prototypes:")
    for type_str in list(engine._prototypes.keys())[:5]:
        print(f"  {type_str}")
