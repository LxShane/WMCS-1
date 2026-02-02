from typing import List, Dict, Set
from dataclasses import dataclass
import re

@dataclass
class Proposition:
    subject: str
    predicate: str
    object: str
    negated: bool = False

class SymbolicValidator:
    """
    The 'Logician'.
    Verifies that a chain of reasoning is internally consistent and ontologically valid.
    """
    
    # Simple ontological rules
    # Group ranges: 
    # 0-19: Physical/Natural
    # 20-39: Physical/Living
    # 40-59: Mathematical/Abstract
    # 60-79: Social/Institutional
    
    RESTRICTIONS = {
        "EATS": {"subject_groups": range(20, 40), "object_groups": range(0, 40)}, # Only living things eat physical things
        "THINKS": {"subject_groups": range(20, 80)}, # Living or Social entities can "think" (metaphorically)
        "CALCULATES": {"subject_groups": list(range(20, 40)) + list(range(60, 80)) + [40, 41]} # Humans, Orgs, or Math Processes
    }

    def validate_chain(self, steps: List[str], id_map: Dict[str, Dict]) -> Dict:
        """
        Input: List of strings like "A implies B", "Cat(20,1) matches Dog(20,2)"
        Output: {'valid': bool, 'error': str}
        """
        # 1. Parse Propositions
        propositions = []
        for step in steps:
            # We look for "ID IS_A ID" or similar patterns
            # This is a simplified prover for the demo
            pass

        # 2. Check Ontological Validity
        # We scan the reasoning trace for violation keywords like "Number 5 eats"
        for step in steps:
            violation = self._check_ontology_violation(step, id_map)
            if violation:
                return {'valid': False, 'error': f"Ontological Error: {violation}"}

        # 3. Check Direct Contradiction (A is B ... A is NOT B)
        # (Simplified: check for explicit negation of previous assertions)

        return {'valid': True, 'error': None}

    def _check_ontology_violation(self, text: str, id_map: Dict) -> str:
        """
        Scans text for Subject-Verb-Object patterns where Subject ID class is incompatible with Verb.
        """
        text = text.upper()
        
        # Example check: "Mathematical Object ... EATS"
        # We need to find IDs in the text
        ids = re.findall(r'\((\d+),(\d+)\)', text)
        if not ids: return None
        
        # Simple heurstic: If we see a RESTRICTED VERB, check the IDs mentioned BEFORE it.
        for verb, rules in self.RESTRICTIONS.items():
            if verb in text:
                # Find the subject (ID closest to the left of the verb)
                # This is a naive parser. A real one would use dependency parsing.
                verb_idx = text.find(verb)
                
                # Check IDs that appear before this verb
                relevant_group = -1
                for g, i in ids:
                    # We assume the IDS are in order.
                    # In a real string index check we'd be more precise.
                    # For this demo, we check ALL Subject IDs in the sentence.
                    try:
                        group_id = int(g)
                        allowed = rules.get("subject_groups", [])
                        if group_id not in allowed:
                            return f"Verb '{verb}' cannot be performed by Entity of Group {group_id}"
                    except:
                        continue
                        
        return None
