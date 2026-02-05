"""
Synthesis Engine (v1.0)
Generates HYPOTHETICAL concepts by combining existing knowledge patterns.

CRITICAL: All outputs are marked as HYPOTHETICAL and require verification
before being promoted to actual knowledge in the graph.
"""
import json
import os
from typing import Dict, List, Optional
from datetime import datetime

class SynthesisEngine:
    """
    Engine for creative synthesis of hypothetical concepts.
    
    All generated concepts have:
    - status: "HYPOTHETICAL" (never "VERIFIED" until explicitly promoted)
    - confidence: 0.0 - 0.3 range (low confidence by design)
    - requires_verification: True
    - verification_methods: suggested ways to verify
    """
    
    def __init__(self, llm_client=None, graph_engine=None):
        self.llm_client = llm_client
        self.graph = graph_engine
        self.hypotheticals_dir = "data/hypotheticals"  # SEPARATE from concepts/
        os.makedirs(self.hypotheticals_dir, exist_ok=True)
        
    def synthesize(self, constraints: Dict) -> Dict:
        """
        Generate a hypothetical concept based on constraints.
        
        Args:
            constraints: Dict with keys like:
                - "has_property": ["flies", "self-replicating"]
                - "made_of": ["organic", "silicon"]
                - "inspired_by": ["bird", "drone"]
                - "purpose": "surveillance"
                - "environment": "underwater"
        
        Returns:
            A ConceptBlock with HYPOTHETICAL status
        """
        # Build synthesis prompt
        prompt = self._build_synthesis_prompt(constraints)
        
        if self.llm_client:
            response = self.llm_client.json_completion("SynthesisEngine", prompt)
        else:
            # Mock response for testing
            response = self._mock_synthesis(constraints)
        
        # CRITICAL: Force hypothetical markers
        return self._enforce_hypothetical_status(response, constraints)
    
    def synthesize_analogy(self, source_concept: str, target_domain: str) -> Dict:
        """
        Generate a hypothetical concept by transferring structure from
        source_concept to target_domain.
        
        Example: synthesize_analogy("solar_system", "economy")
        -> Hypothetical "Economic Solar System" where:
           - Central bank = Sun
           - Currencies = Planets
           - etc.
        """
        prompt = f"""
        You are a creative synthesis engine. 
        
        Take the STRUCTURE of '{source_concept}' and apply it to '{target_domain}'.
        Generate a HYPOTHETICAL concept that represents this mapping.
        
        CRITICAL: This is PURELY HYPOTHETICAL for creative exploration.
        It is NOT a factual claim.
        
        Output JSON:
        {{
            "name": "Hypothetical: [descriptive name]",
            "source_concept": "{source_concept}",
            "target_domain": "{target_domain}",
            "mapping": [
                {{"source_element": "...", "maps_to": "...", "rationale": "..."}}
            ],
            "novel_predictions": [
                "If this analogy holds, then..."
            ],
            "limitations": [
                "This analogy breaks down when..."
            ]
        }}
        """
        
        if self.llm_client:
            response = self.llm_client.json_completion("SynthesisEngine", prompt)
        else:
            response = {
                "name": f"Hypothetical: {target_domain} as {source_concept}",
                "source_concept": source_concept,
                "target_domain": target_domain,
                "mapping": [],
                "novel_predictions": [],
                "limitations": ["This is a mock response"]
            }
        
        return self._enforce_hypothetical_status(response, {
            "type": "analogy_transfer",
            "source": source_concept,
            "target": target_domain
        })
    
    def synthesize_counterfactual(self, base_concept: str, change: str) -> Dict:
        """
        Generate a hypothetical variant by changing one aspect.
        
        Example: synthesize_counterfactual("earth", "no_magnetic_field")
        -> Hypothetical "Earth without magnetosphere" with predicted effects
        """
        prompt = f"""
        You are a counterfactual reasoning engine.
        
        Take '{base_concept}' and imagine: What if '{change}'?
        
        Generate a HYPOTHETICAL concept representing this counterfactual.
        
        CRITICAL: This is PURELY HYPOTHETICAL thought experiment.
        It is NOT a factual claim about reality.
        
        Output JSON:
        {{
            "name": "Hypothetical: {base_concept} with {change}",
            "base_concept": "{base_concept}",
            "change_applied": "{change}",
            "predicted_effects": [
                {{"domain": "...", "effect": "...", "confidence": 0.1-0.3}}
            ],
            "cascading_consequences": [
                "This would lead to..."
            ],
            "assumptions_made": [
                "This assumes that..."
            ]
        }}
        """
        
        if self.llm_client:
            response = self.llm_client.json_completion("SynthesisEngine", prompt)
        else:
            response = {
                "name": f"Hypothetical: {base_concept} with {change}",
                "base_concept": base_concept,
                "change_applied": change,
                "predicted_effects": [],
                "cascading_consequences": [],
                "assumptions_made": ["This is a mock response"]
            }
        
        return self._enforce_hypothetical_status(response, {
            "type": "counterfactual",
            "base": base_concept,
            "change": change
        })
    
    def _build_synthesis_prompt(self, constraints: Dict) -> str:
        """Build prompt for constrained synthesis."""
        constraint_text = "\n".join([
            f"- {key}: {value}" for key, value in constraints.items()
        ])
        
        return f"""
        You are a creative synthesis engine for generating HYPOTHETICAL concepts.
        
        Given these constraints:
        {constraint_text}
        
        Generate a NOVEL concept that satisfies these constraints.
        This concept may not exist in reality - it is purely hypothetical.
        
        CRITICAL RULES:
        1. This is NOT a factual claim
        2. Mark all outputs as speculative
        3. Include ways to verify/falsify the concept
        4. Acknowledge limitations and assumptions
        
        Output JSON:
        {{
            "CORE": {{
                "name": "Hypothetical: [descriptive name]",
                "type": "hypothetical.[category]",
                "definition": "[speculative definition]"
            }},
            "SYNTHESIS_META": {{
                "constraints_used": {json.dumps(constraints)},
                "creative_leaps": ["list of non-obvious combinations made"],
                "assumptions": ["what we assumed to generate this"]
            }},
            "VERIFICATION": {{
                "testable_predictions": ["if this exists, then X should be true"],
                "falsification_criteria": ["this would be disproven if..."],
                "required_experiments": ["to verify, one would need to..."]
            }},
            "GROUNDING": {{
                "chain": ["speculation", "creative combination"],
                "confidence": 0.1,
                "evidence_summary": "HYPOTHETICAL - no empirical evidence"
            }}
        }}
        """
    
    def _mock_synthesis(self, constraints: Dict) -> Dict:
        """Generate mock response for testing."""
        return {
            "CORE": {
                "name": f"Hypothetical: {constraints.get('purpose', 'Unknown')} Entity",
                "type": "hypothetical.entity",
                "definition": f"A speculative concept combining: {constraints}"
            },
            "SYNTHESIS_META": {
                "constraints_used": constraints,
                "creative_leaps": ["Combined disparate domains"],
                "assumptions": ["Assumed physical compatibility"]
            },
            "VERIFICATION": {
                "testable_predictions": ["Would exhibit property X"],
                "falsification_criteria": ["Material incompatibility would disprove"],
                "required_experiments": ["Lab synthesis would be needed"]
            },
            "GROUNDING": {
                "chain": ["speculation", "creative combination"],
                "confidence": 0.1,
                "evidence_summary": "HYPOTHETICAL - no empirical evidence"
            }
        }
    
    def _enforce_hypothetical_status(self, concept: Dict, constraints: Dict) -> Dict:
        """
        CRITICAL: Force all outputs to be marked as hypothetical.
        This is a safety mechanism - synthesis NEVER produces facts.
        """
        # Add mandatory hypothetical markers
        concept["_STATUS"] = "HYPOTHETICAL"
        concept["_REQUIRES_VERIFICATION"] = True
        concept["_GENERATED_AT"] = datetime.now().isoformat()
        concept["_GENERATION_CONSTRAINTS"] = constraints
        concept["_WARNING"] = (
            "THIS IS A HYPOTHETICAL CONCEPT. "
            "It has NOT been verified and should NOT be treated as fact. "
            "Use VERIFICATION.required_experiments to validate before use."
        )
        
        # Ensure confidence is capped
        if "GROUNDING" in concept:
            concept["GROUNDING"]["confidence"] = min(
                concept["GROUNDING"].get("confidence", 0.1), 
                0.3  # MAX confidence for hypotheticals
            )
            concept["GROUNDING"]["status"] = "UNVERIFIED"
        
        return concept
    
    def save_hypothetical(self, concept: Dict) -> str:
        """
        Save a hypothetical concept to the HYPOTHETICALS directory.
        This is SEPARATE from the verified concepts directory.
        """
        name = concept.get("CORE", {}).get("name", "unnamed")
        safe_name = name.lower().replace(' ', '_').replace(':', '')
        for char in ['/', '\\', '*', '?', '"', '<', '>', '|']:
            safe_name = safe_name.replace(char, '-')
        
        filename = f"{safe_name}.json"
        path = os.path.join(self.hypotheticals_dir, filename)
        
        with open(path, 'w', encoding='utf-8') as f:
            json.dump(concept, f, indent=2)
        
        return path
    
    def verify_and_promote(self, hypothetical_path: str, evidence: Dict) -> bool:
        """
        Attempt to promote a hypothetical to verified status.
        
        This requires:
        1. Evidence that satisfies testable_predictions
        2. No falsification criteria being met
        3. Manual approval flag
        
        Returns True if promoted, False if still hypothetical.
        """
        with open(hypothetical_path, 'r') as f:
            concept = json.load(f)
        
        # Check if evidence satisfies verification requirements
        predictions = concept.get("VERIFICATION", {}).get("testable_predictions", [])
        satisfied = evidence.get("predictions_satisfied", [])
        
        if not predictions:
            return False  # Cannot verify without predictions
        
        satisfaction_rate = len(satisfied) / len(predictions)
        
        if satisfaction_rate >= 0.8 and evidence.get("manual_approval", False):
            # Promote to verified
            concept["_STATUS"] = "VERIFIED"
            concept["_REQUIRES_VERIFICATION"] = False
            concept["_VERIFIED_AT"] = datetime.now().isoformat()
            concept["_VERIFICATION_EVIDENCE"] = evidence
            concept["GROUNDING"]["confidence"] = min(0.7, satisfaction_rate)
            concept["GROUNDING"]["status"] = "VERIFIED"
            
            # Move to concepts directory
            name = concept["CORE"]["name"].replace("Hypothetical: ", "")
            concept["CORE"]["name"] = name
            
            safe_name = name.lower().replace(' ', '_')
            new_path = f"data/concepts/{safe_name}.json"
            
            with open(new_path, 'w') as f:
                json.dump(concept, f, indent=2)
            
            # Remove from hypotheticals
            os.remove(hypothetical_path)
            
            return True
        
        return False


# Factory function
_synthesis_engine = None

def get_synthesis_engine(llm_client=None, graph_engine=None):
    global _synthesis_engine
    if _synthesis_engine is None:
        _synthesis_engine = SynthesisEngine(llm_client, graph_engine)
    return _synthesis_engine
