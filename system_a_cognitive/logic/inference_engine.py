"""
Inference Engine (WMCS v1.0)
Forward/backward chaining, causal inference, counterfactual reasoning.
"""
import json
from typing import Dict, List, Optional, Set, Tuple
from system_a_cognitive.logic.graph_engine import get_graph_engine


class InferenceEngine:
    def __init__(self):
        self.graph = get_graph_engine()
        self._rules = []  # List of (condition, conclusion) tuples
        self._build_rules()
    
    def _build_rules(self):
        """Build inference rules from concept causation data."""
        for name, concept in self.graph._concept_cache.items():
            if "CAUSATION" not in concept:
                continue
            
            caus = concept["CAUSATION"]
            
            # "X requires Y" → IF Y is false, X cannot be true
            for req in caus.get("requires", []):
                self._rules.append({
                    "type": "requires",
                    "subject": name,
                    "condition": req.lower() if isinstance(req, str) else str(req).lower(),
                    "conclusion": f"{name} cannot exist without {req}"
                })
            
            # "X produces Y" → IF X is true, Y becomes true
            for prod in caus.get("produces", []):
                self._rules.append({
                    "type": "produces",
                    "subject": name,
                    "condition": name,
                    "conclusion": prod.lower() if isinstance(prod, str) else str(prod).lower()
                })
            
            # "X caused by Y" → IF Y happened, X can happen
            for cause in caus.get("caused_by", []):
                self._rules.append({
                    "type": "caused_by",
                    "subject": name,
                    "condition": cause.lower() if isinstance(cause, str) else str(cause).lower(),
                    "conclusion": f"{name} can occur"
                })
    
    def forward_chain(self, facts: List[str], max_iterations: int = 10) -> List[str]:
        """
        Given a set of true facts, derive all possible conclusions.
        Returns list of derived facts.
        """
        facts_set = set(f.lower() for f in facts)
        derived = set()
        
        for _ in range(max_iterations):
            new_derived = set()
            
            for rule in self._rules:
                condition = rule["condition"]
                conclusion = rule["conclusion"]
                
                if rule["type"] == "produces":
                    # If the subject is in facts, add what it produces
                    if condition in facts_set and conclusion not in facts_set:
                        new_derived.add(conclusion)
                
                elif rule["type"] == "caused_by":
                    # If the cause is in facts, the effect can occur
                    if condition in facts_set:
                        effect = rule["subject"]
                        if effect not in facts_set:
                            new_derived.add(effect)
            
            if not new_derived:
                break
            
            derived.update(new_derived)
            facts_set.update(new_derived)
        
        return list(derived)
    
    def backward_chain(self, goal: str, known_facts: List[str] = None) -> Dict:
        """
        What would need to be true for goal to be achievable?
        Returns {achievable: bool, required: [], missing: [], chain: []}
        """
        goal_lower = goal.lower()
        known = set(f.lower() for f in (known_facts or []))
        
        result = {
            "goal": goal,
            "achievable": False,
            "required": [],
            "missing": [],
            "chain": []
        }
        
        # Find what the goal requires
        concept = self.graph.get_concept(goal)
        if not concept:
            result["chain"].append(f"Cannot find concept: {goal}")
            return result
        
        requirements = concept.get("CAUSATION", {}).get("requires", [])
        
        for req in requirements:
            req_lower = req.lower() if isinstance(req, str) else str(req).lower()
            result["required"].append(req_lower)
            
            if req_lower in known:
                result["chain"].append(f"✓ {req_lower} (known)")
            else:
                result["missing"].append(req_lower)
                result["chain"].append(f"✗ {req_lower} (missing)")
        
        result["achievable"] = len(result["missing"]) == 0
        
        return result
    
    def counterfactual(self, subject: str, hypothesis: str) -> Dict:
        """
        "What if X were true?" or "What if X didn't exist?"
        Inject hypothetical, trace causal effects.
        Returns {hypothesis, effects: [], conflicts: []}
        """
        result = {
            "hypothesis": hypothesis,
            "subject": subject,
            "effects": [],
            "conflicts": [],
            "chain": []
        }
        
        # Parse hypothesis
        is_removal = "not" in hypothesis.lower() or "without" in hypothesis.lower() or "disappeared" in hypothesis.lower()
        
        subject_lower = subject.lower()
        concept = self.graph.get_concept(subject)
        
        if not concept:
            result["chain"].append(f"Cannot find concept: {subject}")
            return result
        
        if is_removal:
            # What would happen if subject didn't exist?
            result["chain"].append(f"Simulating removal of: {subject}")
            
            # Find what produces the subject
            produced_by = concept.get("CAUSATION", {}).get("produced_by", [])
            
            # Find what depends on the subject
            for name, other in self.graph._concept_cache.items():
                if name == subject_lower:
                    continue
                
                other_caus = other.get("CAUSATION", {})
                
                # Does other require subject?
                for req in other_caus.get("requires", []):
                    req_str = req.lower() if isinstance(req, str) else str(req).lower()
                    if req_str == subject_lower or subject_lower in req_str:
                        result["effects"].append(f"{name} would lose requirement: {subject}")
                        result["conflicts"].append(f"{name} cannot exist without {subject}")
                
                # Does other get caused by subject?
                for cause in other_caus.get("caused_by", []):
                    cause_str = cause.lower() if isinstance(cause, str) else str(cause).lower()
                    if cause_str == subject_lower or subject_lower in cause_str:
                        result["effects"].append(f"{name} would lose its cause")
        
        else:
            # What happens if subject exists/is enhanced?
            result["chain"].append(f"Simulating presence/enhancement of: {subject}")
            
            # What does subject produce?
            produces = concept.get("CAUSATION", {}).get("produces", [])
            for prod in produces:
                prod_str = prod.lower() if isinstance(prod, str) else str(prod).lower()
                result["effects"].append(f"Would produce: {prod_str}")
            
            # Forward chain from subject
            derived = self.forward_chain([subject])
            for d in derived[:10]:
                result["effects"].append(f"Chain effect: {d}")
        
        return result
    
    def explain_causation(self, from_concept: str, to_concept: str) -> str:
        """Find and explain the causal chain between two concepts."""
        path = self.graph.find_path(from_concept, to_concept)
        
        if not path:
            return f"No causal chain found between {from_concept} and {to_concept}"
        
        lines = [f"**Causal Chain: {from_concept} → {to_concept}**"]
        
        for i, step in enumerate(path):
            if i == 0:
                lines.append(f"1. Start: {step['name']}")
            else:
                lines.append(f"{i+1}. --({step['relation']})--> {step['name']}")
        
        return "\n".join(lines)


# Singleton
_engine = None

def get_inference_engine() -> InferenceEngine:
    global _engine
    if _engine is None:
        _engine = InferenceEngine()
    return _engine


if __name__ == "__main__":
    engine = InferenceEngine()
    
    print("Forward Chain from 'sun':")
    results = engine.forward_chain(["sun"])
    for r in results[:5]:
        print(f"  → {r}")
    
    print("\nCounterfactual: 'What if the sun disappeared?'")
    cf = engine.counterfactual("sun", "what if sun disappeared")
    for effect in cf["effects"][:5]:
        print(f"  {effect}")
