"""
Analogy Engine (WMCS v1.0)
Structural comparison between concepts.
"How is X like Y?" with deep structural mapping.
Implements Gentner's Structure Mapping Theory.
"""
import json
from typing import Dict, List, Optional, Tuple
from system_a_cognitive.logic.graph_engine import get_graph_engine


class AnalogyEngine:
    def __init__(self):
        self.graph = get_graph_engine()
    
    def compare_structure(self, concept_a: Dict, concept_b: Dict) -> Dict:
        """
        Compare structural similarity between two concepts.
        Returns {
            overlap_score: 0-1,
            shared_categories: [],
            shared_relations: [],
            differences: [],
            mappings: [{a_part: ..., b_part: ..., similarity: ...}]
        }
        """
        result = {
            "overlap_score": 0.0,
            "shared_categories": [],
            "relation_overlap": [],
            "structural_mappings": [],
            "differences": []
        }
        
        # 1. Compare top-level categories
        cats_a = set(concept_a.keys())
        cats_b = set(concept_b.keys())
        shared_cats = cats_a & cats_b
        result["shared_categories"] = list(shared_cats)
        
        # 2. Compare SUBSTANCE (composition)
        if "SUBSTANCE" in concept_a and "SUBSTANCE" in concept_b:
            comp_a = self._extract_components(concept_a["SUBSTANCE"])
            comp_b = self._extract_components(concept_b["SUBSTANCE"])
            shared_comp = set(comp_a) & set(comp_b)
            result["shared_components"] = list(shared_comp)
        
        # 3. Compare ARRANGEMENT (spatial structure)
        if "ARRANGEMENT" in concept_a and "ARRANGEMENT" in concept_b:
            parts_a = self._extract_parts(concept_a["ARRANGEMENT"])
            parts_b = self._extract_parts(concept_b["ARRANGEMENT"])
            
            # Find structural mappings based on relative position patterns
            mappings = self._map_parts(parts_a, parts_b)
            result["structural_mappings"] = mappings
        
        # 4. Compare CAUSATION
        if "CAUSATION" in concept_a and "CAUSATION" in concept_b:
            caus_a = concept_a["CAUSATION"]
            caus_b = concept_b["CAUSATION"]
            
            req_overlap = set(caus_a.get("requires", [])) & set(caus_b.get("requires", []))
            prod_overlap = set(caus_a.get("produces", [])) & set(caus_b.get("produces", []))
            
            result["relation_overlap"].extend([f"both require {r}" for r in req_overlap])
            result["relation_overlap"].extend([f"both produce {p}" for p in prod_overlap])
        
        # 5. Compare CLASSIFICATION
        if "CLASSIFICATION" in concept_a and "CLASSIFICATION" in concept_b:
            chain_a = concept_a["CLASSIFICATION"].get("categorical_chain", [])
            chain_b = concept_b["CLASSIFICATION"].get("categorical_chain", [])
            shared_chain = set(chain_a) & set(chain_b)
            if shared_chain:
                result["shared_categories"].extend(list(shared_chain))
        
        # 6. Find key differences
        only_a = cats_a - cats_b
        only_b = cats_b - cats_a
        if only_a:
            result["differences"].append(f"A has: {list(only_a)}")
        if only_b:
            result["differences"].append(f"B has: {list(only_b)}")
        
        # Calculate overlap score
        total_cats = len(cats_a | cats_b)
        if total_cats > 0:
            result["overlap_score"] = len(shared_cats) / total_cats
        
        return result
    
    def _extract_components(self, substance: Dict) -> List[str]:
        """Extract component names from SUBSTANCE."""
        components = []
        comp = substance.get("composition", {})
        
        for level in comp.get("levels", []):
            for c in level.get("components", []):
                if isinstance(c, dict):
                    components.append(c.get("name", "").lower())
                else:
                    components.append(str(c).lower())
        
        return components
    
    def _extract_parts(self, arrangement: Dict) -> List[Dict]:
        """Extract parts from ARRANGEMENT."""
        spatial = arrangement.get("structure_spatial", {})
        return spatial.get("parts", [])
    
    def _map_parts(self, parts_a: List[Dict], parts_b: List[Dict]) -> List[Dict]:
        """Find structural mappings between parts based on position patterns."""
        mappings = []
        
        for pa in parts_a:
            for pb in parts_b:
                similarity = self._part_similarity(pa, pb)
                if similarity > 0.5:
                    mappings.append({
                        "a_part": pa.get("name"),
                        "b_part": pb.get("name"),
                        "similarity": similarity,
                        "basis": self._explain_similarity(pa, pb)
                    })
        
        return mappings
    
    def _part_similarity(self, part_a: Dict, part_b: Dict) -> float:
        """Calculate similarity between two parts."""
        score = 0.0
        
        # Same relative_to pattern
        if part_a.get("relative_to") == part_b.get("relative_to"):
            score += 0.3
        
        # Similar position pattern
        pos_a = part_a.get("position", {})
        pos_b = part_b.get("position", {})
        
        # Check if same axis dominance
        if pos_a and pos_b:
            max_axis_a = max(pos_a.items(), key=lambda x: abs(x[1]) if isinstance(x[1], (int, float)) else 0)
            max_axis_b = max(pos_b.items(), key=lambda x: abs(x[1]) if isinstance(x[1], (int, float)) else 0)
            if max_axis_a[0] == max_axis_b[0]:
                score += 0.3
        
        # Name similarity (basic)
        name_a = part_a.get("name", "").lower()
        name_b = part_b.get("name", "").lower()
        if name_a == name_b:
            score += 0.4
        elif name_a in name_b or name_b in name_a:
            score += 0.2
        
        return min(score, 1.0)
    
    def _explain_similarity(self, part_a: Dict, part_b: Dict) -> str:
        """Generate explanation for why parts are similar."""
        reasons = []
        
        if part_a.get("relative_to") == part_b.get("relative_to"):
            reasons.append("same relative position")
        
        if part_a.get("name", "").lower() == part_b.get("name", "").lower():
            reasons.append("same name")
        
        return ", ".join(reasons) if reasons else "structural pattern"
    
    def find_analogues(self, concept_name: str, limit: int = 5) -> List[Dict]:
        """Find concepts most structurally similar to the given one."""
        concept = self.graph.get_concept(concept_name)
        if not concept:
            return []
        
        results = []
        
        for name, other in self.graph._concept_cache.items():
            if name == concept_name.lower():
                continue
            
            comparison = self.compare_structure(concept, other)
            if comparison["overlap_score"] > 0.3:
                results.append({
                    "name": name,
                    "score": comparison["overlap_score"],
                    "shared": comparison["shared_categories"][:3]
                })
        
        # Sort by score
        results.sort(key=lambda x: x["score"], reverse=True)
        return results[:limit]
    
    def explain_analogy(self, concept_a: str, concept_b: str) -> str:
        """Generate natural language explanation of analogy."""
        a_data = self.graph.get_concept(concept_a)
        b_data = self.graph.get_concept(concept_b)
        
        if not a_data or not b_data:
            return f"Cannot compare: concept not found"
        
        comparison = self.compare_structure(a_data, b_data)
        
        lines = [f"**{concept_a.title()} is like {concept_b.title()}** because:"]
        
        if comparison["shared_categories"]:
            lines.append(f"- Both have: {', '.join(comparison['shared_categories'][:5])}")
        
        if comparison.get("shared_components"):
            lines.append(f"- Both contain: {', '.join(comparison['shared_components'][:5])}")
        
        for mapping in comparison.get("structural_mappings", [])[:3]:
            lines.append(f"- {concept_a}'s {mapping['a_part']} ≈ {concept_b}'s {mapping['b_part']}")
        
        if comparison["relation_overlap"]:
            for rel in comparison["relation_overlap"][:3]:
                lines.append(f"- {rel}")
        
        if comparison["differences"]:
            lines.append(f"\n**Key differences:**")
            for diff in comparison["differences"][:3]:
                lines.append(f"- {diff}")
        
        lines.append(f"\n**Structural Overlap**: {comparison['overlap_score']*100:.0f}%")
        
        return "\n".join(lines)


# Singleton
_engine = None

def get_analogy_engine() -> AnalogyEngine:
    global _engine
    if _engine is None:
        _engine = AnalogyEngine()
    return _engine


if __name__ == "__main__":
    engine = AnalogyEngine()
    
    print("Testing Analogy Engine:")
    print(engine.explain_analogy("earth", "mars"))
