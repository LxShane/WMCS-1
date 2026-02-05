"""
Epistemic Gate (WMCS v1.0)
The critical component that prevents LLM hallucination.
Verifies all claims against System A before passing to output.
"""
import re
from typing import Dict, List, Optional, Set, Tuple
from system_a_cognitive.logic.graph_engine import get_graph_engine


class EpistemicGate:
    """
    The Epistemic Gate enforces the Two-Brain Architecture rule:
    "System B (LLM) is FORBIDDEN from guessing facts. Must use System A's data."
    
    It works by:
    1. Extracting factual claims from LLM output
    2. Verifying each claim against the concept store
    3. Flagging or removing unverified claims
    """
    
    def __init__(self, strict_mode: bool = False):
        """
        strict_mode: If True, remove unverified claims entirely.
                     If False, flag them with [UNVERIFIED].
        """
        self.graph = get_graph_engine()
        self.strict_mode = strict_mode
        
        # Known facts cache
        self._known_names = set(self.graph._concept_cache.keys())
        self._known_claims = self._build_claims_index()
    
    def _build_claims_index(self) -> Dict[str, Set[str]]:
        """
        Build index of known facts from concepts.
        Returns {concept_name: set of claim strings}
        """
        index = {}
        
        for name, concept in self.graph._concept_cache.items():
            claims = set()
            
            # Add definition
            defn = concept.get("CORE", {}).get("definition", "")
            if defn:
                claims.add(defn.lower())
            
            # Add type
            type_str = concept.get("CORE", {}).get("type", "")
            if type_str:
                claims.add(f"{name} is a {type_str}")
            
            # Add classification
            chain = concept.get("CLASSIFICATION", {}).get("categorical_chain", [])
            for cat in chain:
                claims.add(f"{name} is a {cat.lower()}")
            
            # Add causation facts
            caus = concept.get("CAUSATION", {})
            for req in caus.get("requires", []):
                claims.add(f"{name} requires {str(req).lower()}")
            for prod in caus.get("produces", []):
                claims.add(f"{name} produces {str(prod).lower()}")
            
            # Add connection facts
            conns = concept.get("CONNECTIONS", {})
            for rel in conns.get("relational", []):
                if isinstance(rel, dict):
                    rel_str = rel.get("relation", "")
                    target = rel.get("target", "")
                    if isinstance(target, str):
                        claims.add(f"{name} {rel_str} {target.lower()}")
                    elif isinstance(target, list):
                        for t in target:
                            if isinstance(t, str):
                                claims.add(f"{name} {rel_str} {t.lower()}")
            
            index[name] = claims
        
        return index
    
    def extract_claims(self, text: str) -> List[str]:
        """
        Extract factual claims from text.
        A claim is any statement that asserts a fact about the world.
        """
        claims = []
        
        # Split into sentences
        sentences = re.split(r'[.!?]', text)
        
        for sent in sentences:
            sent = sent.strip()
            if not sent:
                continue
            
            # Skip questions
            if '?' in sent:
                continue
            
            # Skip hedged statements (these are opinions, not claims)
            hedges = ['maybe', 'perhaps', 'might', 'could be', 'possibly', 'i think', 'i believe']
            if any(h in sent.lower() for h in hedges):
                continue
            
            # Skip meta-statements
            meta = ['let me', 'i will', 'i can', 'here is', 'based on']
            if any(m in sent.lower() for m in meta):
                continue
            
            # This looks like a factual claim
            claims.append(sent)
        
        return claims
    
    def verify_claim(self, claim: str) -> Dict:
        """
        Verify a single claim against System A.
        Returns {
            verified: bool,
            confidence: float,
            source: str or None,
            reason: str
        }
        """
        claim_lower = claim.lower()
        
        # 1. Check if claim mentions known concepts
        mentioned = []
        for name in self._known_names:
            if name in claim_lower:
                mentioned.append(name)
        
        if not mentioned:
            return {
                "verified": False,
                "confidence": 0.0,
                "source": None,
                "reason": "No recognized concepts mentioned"
            }
        
        # 2. Check if claim matches known facts
        for name in mentioned:
            known = self._known_claims.get(name, set())
            
            # Direct match
            for known_claim in known:
                if self._claims_match(claim_lower, known_claim):
                    return {
                        "verified": True,
                        "confidence": 0.9,
                        "source": name,
                        "reason": f"Matches known fact about {name}"
                    }
            
            # Partial match
            for known_claim in known:
                if self._claims_overlap(claim_lower, known_claim):
                    return {
                        "verified": True,
                        "confidence": 0.6,
                        "source": name,
                        "reason": f"Partially matches facts about {name}"
                    }
        
        # 3. Claim mentions concepts but doesn't match any known facts
        return {
            "verified": False,
            "confidence": 0.3,
            "source": mentioned[0] if mentioned else None,
            "reason": f"Mentions {mentioned} but claim not in knowledge base"
        }
    
    def _claims_match(self, claim1: str, claim2: str) -> bool:
        """Check if two claims are essentially the same."""
        # Simple word overlap heuristic
        words1 = set(claim1.split())
        words2 = set(claim2.split())
        
        overlap = len(words1 & words2)
        min_len = min(len(words1), len(words2))
        
        return overlap / max(min_len, 1) > 0.7
    
    def _claims_overlap(self, claim1: str, claim2: str) -> bool:
        """Check if claims have significant overlap."""
        words1 = set(claim1.split())
        words2 = set(claim2.split())
        
        overlap = len(words1 & words2)
        return overlap >= 3  # At least 3 words in common
    
    def filter_response(self, llm_output: str) -> Dict:
        """
        Filter LLM response to mark/remove unverified claims.
        Returns {
            filtered_text: str,
            verified_count: int,
            unverified_count: int,
            claims: [{claim, verified, confidence, source}]
        }
        """
        claims = self.extract_claims(llm_output)
        results = []
        filtered_text = llm_output
        verified_count = 0
        unverified_count = 0
        
        for claim in claims:
            verification = self.verify_claim(claim)
            results.append({
                "claim": claim[:100],  # Truncate for display
                **verification
            })
            
            if verification["verified"]:
                verified_count += 1
            else:
                unverified_count += 1
                
                if self.strict_mode:
                    # Remove unverified claim entirely
                    filtered_text = filtered_text.replace(claim, "[CLAIM REMOVED]")
                else:
                    # Flag unverified claim
                    flagged = f"[UNVERIFIED: {claim}]"
                    filtered_text = filtered_text.replace(claim, flagged)
        
        return {
            "filtered_text": filtered_text,
            "verified_count": verified_count,
            "unverified_count": unverified_count,
            "claims": results
        }
    
    def get_trust_score(self, llm_output: str) -> float:
        """
        Calculate overall trust score for LLM output.
        Returns 0.0 to 1.0.
        """
        result = self.filter_response(llm_output)
        total = result["verified_count"] + result["unverified_count"]
        
        if total == 0:
            return 1.0  # No claims = nothing to verify
        
        return result["verified_count"] / total
    
    def enforce(self, llm_output: str, min_trust: float = 0.5) -> Tuple[str, bool]:
        """
        Enforce epistemic standards on LLM output.
        Returns (filtered_output, passed_gate).
        """
        trust = self.get_trust_score(llm_output)
        filtered = self.filter_response(llm_output)
        
        if trust < min_trust:
            # Add warning
            warning = f"\n\n⚠️ EPISTEMIC WARNING: This response has low verification ({trust*100:.0f}%). {filtered['unverified_count']} claims could not be verified against the knowledge base.\n"
            return filtered["filtered_text"] + warning, False
        
        return filtered["filtered_text"], True


# Singleton
_gate = None

def get_epistemic_gate(strict_mode: bool = False) -> EpistemicGate:
    global _gate
    if _gate is None:
        _gate = EpistemicGate(strict_mode)
    return _gate


if __name__ == "__main__":
    gate = EpistemicGate()
    
    test_text = """
    Earth is the third planet from the Sun. It orbits the Sun once every 365 days.
    The Moon is made entirely of cheese. Earth has one moon.
    Cats can fly at speeds up to 100 mph.
    """
    
    print("Testing Epistemic Gate:")
    result = gate.filter_response(test_text)
    print(f"Verified: {result['verified_count']}")
    print(f"Unverified: {result['unverified_count']}")
    print(f"Trust Score: {gate.get_trust_score(test_text)*100:.0f}%")
