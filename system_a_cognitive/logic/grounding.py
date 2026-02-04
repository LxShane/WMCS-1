"""
Grounding Engine (v1.0)
Verifies the evidence chain for concepts. Checks confidence and grounding types.
"""
from typing import Dict, List, Optional

class GroundingEngine:
    def __init__(self):
        pass

    def get_grounding_score(self, grounding_data: Dict) -> float:
        """Returns the confidence score (0.0 - 1.0)."""
        return float(grounding_data.get("confidence", 0.0))

    def evaluate_grounding(self, grounding_data: Dict) -> Dict:
        """
        Evaluates the quality of grounding.
        Returns: { "status": str, "strength": str, "issues": List[str] }
        """
        score = self.get_grounding_score(grounding_data)
        chain = grounding_data.get("chain", [])
        base_types = grounding_data.get("base_types", [])
        
        issues = []
        if not chain: issues.append("No grounding chain")
        if not base_types: issues.append("No base evidence types")
        
        # Strength logic
        strength = "WEAK"
        if score > 0.9: strength = "ROCK_SOLID"
        elif score > 0.7: strength = "STRONG"
        elif score > 0.4: strength = "MEDIUM"
        
        # Base type check
        if "perceptual" in base_types or "measurement" in base_types:
            has_solid_base = True
        else:
            has_solid_base = False
            issues.append("Lacks perceptual/measurement grounding")

        status = "VERIFIED" if (score > 0.8 and has_solid_base) else "UNVERIFIED"
        
        return {
            "status": status,
            "strength": strength,
            "issues": issues,
            "depth": len(chain)
        }

# Test
if __name__ == "__main__":
    eng = GroundingEngine()
    mock_data = {
        "confidence": 0.95,
        "chain": ["cat", "animal", "organism"],
        "base_types": ["perceptual", "attestation"]
    }
    print(eng.evaluate_grounding(mock_data))
