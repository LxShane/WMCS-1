"""
Composition Engine (v1.0)
Handles recursive part-whole relationships and component traversal.
"""
from typing import Dict, List, Optional, Set

class CompositionEngine:
    def __init__(self):
        pass

    def get_all_components(self, composition_data: Dict) -> List[str]:
        """Flattened list of all component names at all levels."""
        components = []
        
        # Method A: Semantic Levels (as in prototype)
        if "levels" in composition_data:
            for level in composition_data["levels"]:
                for comp in level.get("components", []):
                    components.append(comp.get("name"))
        
        # Method B: Recursive Dict (common)
        self._traverse_dict(composition_data, components)
        
        return list(set(components)) # dedup

    def _traverse_dict(self, data, collector):
        if isinstance(data, dict):
            for k, v in data.items():
                if k in ["organs", "limbs", "tissues", "components", "parts"]:
                    if isinstance(v, list):
                        for item in v:
                            if isinstance(item, str): collector.append(item)
                            elif isinstance(item, dict): 
                                if "name" in item: collector.append(item["name"])
                                self._traverse_dict(item, collector)
                    elif isinstance(v, dict):
                         self._traverse_dict(v, collector)
                else:
                    self._traverse_dict(v, collector)
        elif isinstance(data, list):
            for item in data:
                self._traverse_dict(item, collector)

    def is_part_of(self, part_name: str, composition_data: Dict) -> bool:
        """Checks if part_name exists anywhere in the composition tree."""
        all_parts = self.get_all_components(composition_data)
        part_clean = part_name.lower().replace(' ', '_')
        return any(p.lower().replace(' ', '_') == part_clean for p in all_parts)

    def get_structure_text(self, composition_data: Dict) -> str:
        """Returns a human-readable tree string."""
        # TODO: Implement fancy tree print
        # For now, just a summary
        parts = self.get_all_components(composition_data)
        return f"Contains {len(parts)} components: {', '.join(parts[:10])}..."

# Test
if __name__ == "__main__":
    eng = CompositionEngine()
    # Mock data
    mock_comp = {
        "body": {
            "organs": [
                {"name": "heart", "tissues": ["muscle", "nerve"]},
                {"name": "liver"}
            ]
        }
    }
    print(f"Components: {eng.get_all_components(mock_comp)}")
    print(f"Is Heart part? {eng.is_part_of('heart', mock_comp)}")
    print(f"Is Kidney part? {eng.is_part_of('kidney', mock_comp)}")
