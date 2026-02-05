"""
Reflective Reasoner (v1.0)
A unified system that combines synthesis, verification, and meta-learning
with self-awareness about reasoning quality.

Core principle: Know when NOT to trust yourself.
"""
import json
import os
from typing import Dict, List, Optional, Tuple
from datetime import datetime
from enum import Enum

class UncertaintyType(Enum):
    """Why the system is uncertain."""
    DATA_MISSING = "data_missing"           # Data exists but not in graph
    NOVEL_QUESTION = "novel_question"       # Genuinely open question
    PATTERN_MISMATCH = "pattern_mismatch"   # Query doesn't fit known patterns
    CONTRADICTION = "contradiction"          # Conflicting evidence
    FUNDAMENTAL_LIMIT = "fundamental_limit" # Unanswerable by nature


class ReflectiveReasoner:
    """
    The meta-cognitive layer that:
    1. Detects WHY confidence is low
    2. Chooses appropriate response strategy
    3. Tracks outcomes for learning
    4. Knows its own limitations
    """
    
    def __init__(self, llm_client=None):
        self.llm_client = llm_client
        self.meta_state_path = "data/meta/reasoning_state.json"
        self.meta_state = self._load_meta_state()
        os.makedirs("data/meta", exist_ok=True)
        
    def _load_meta_state(self) -> Dict:
        """Load accumulated learning about reasoning patterns."""
        if os.path.exists(self.meta_state_path):
            try:
                with open(self.meta_state_path, 'r') as f:
                    return json.load(f)
            except:
                pass
        return {
            "total_queries": 0,
            "outcomes": {"success": 0, "partial": 0, "failure": 0, "admitted_unknown": 0},
            "uncertainty_patterns": {},
            "engine_performance": {},
            "learned_limitations": []
        }
    
    def _save_meta_state(self):
        """Persist learning state."""
        os.makedirs(os.path.dirname(self.meta_state_path), exist_ok=True)
        with open(self.meta_state_path, 'w') as f:
            json.dump(self.meta_state, f, indent=2)
    
    def analyze_uncertainty(self, query: str, context: Dict) -> Tuple[UncertaintyType, str]:
        """
        CRITICAL: Understand WHY we're uncertain, not just THAT we're uncertain.
        
        Returns:
            (uncertainty_type, explanation)
        """
        concepts_found = len(context.get("concepts", {}))
        gaps = context.get("gaps", [])
        confidence = context.get("confidence", 0.5)
        engines_used = context.get("engines_used", [])
        
        # Case 1: No data at all
        if concepts_found == 0:
            # Is this a data gap or a genuinely novel question?
            if self._is_known_domain(query):
                return (UncertaintyType.DATA_MISSING, 
                       "This topic exists but is not in my knowledge graph. Research needed.")
            else:
                return (UncertaintyType.NOVEL_QUESTION,
                       "This appears to be a genuinely open or speculative question.")
        
        # Case 2: Data exists but doesn't fit
        if concepts_found > 0 and confidence < 0.4:
            # Check for contradictions
            if self._has_contradictions(context):
                return (UncertaintyType.CONTRADICTION,
                       "I found conflicting evidence. Cannot determine truth.")
            else:
                return (UncertaintyType.PATTERN_MISMATCH,
                       "The query doesn't match patterns in my reasoning engines.")
        
        # Case 3: Fundamental limits
        fundamental_markers = ["meaning of life", "consciousness", "free will", 
                               "what happens after death", "purpose of existence"]
        if any(marker in query.lower() for marker in fundamental_markers):
            return (UncertaintyType.FUNDAMENTAL_LIMIT,
                   "This is a philosophical question without empirical answer.")
        
        # Default: data missing
        return (UncertaintyType.DATA_MISSING, "Insufficient data for confident answer.")
    
    def _is_known_domain(self, query: str) -> bool:
        """Check if query is about a domain that should have data."""
        known_domains = ["planet", "element", "animal", "country", "scientist",
                        "physics", "chemistry", "biology", "history", "geography"]
        return any(domain in query.lower() for domain in known_domains)
    
    def _has_contradictions(self, context: Dict) -> bool:
        """Check if context contains contradicting claims."""
        facts = context.get("derived_facts", [])
        # Simple check: look for negations of same subject
        subjects = {}
        for fact in facts:
            if isinstance(fact, dict):
                subj = fact.get("subject", "")
                pred = fact.get("predicate", "")
                key = f"{subj}_{pred}"
                if key in subjects:
                    return True  # Same subject+predicate seen twice
                subjects[key] = True
        return False
    
    def choose_strategy(self, uncertainty: UncertaintyType, query: str, context: Dict) -> Dict:
        """
        Based on uncertainty type, choose the right response strategy.
        
        Returns:
            {
                "strategy": str,
                "action": str,
                "should_synthesize": bool,
                "should_research": bool,
                "should_admit_limit": bool,
                "explanation": str
            }
        """
        strategies = {
            UncertaintyType.DATA_MISSING: {
                "strategy": "RESEARCH",
                "action": "Search for information and ingest into graph",
                "should_synthesize": False,
                "should_research": True,
                "should_admit_limit": False,
                "explanation": "I don't have this data, but I can find it."
            },
            UncertaintyType.NOVEL_QUESTION: {
                "strategy": "SYNTHESIZE",
                "action": "Generate hypothetical with clear uncertainty markers",
                "should_synthesize": True,
                "should_research": False,
                "should_admit_limit": False,
                "explanation": "This is speculative - I can propose a hypothesis."
            },
            UncertaintyType.PATTERN_MISMATCH: {
                "strategy": "DECOMPOSE",
                "action": "Break query into simpler sub-questions",
                "should_synthesize": False,
                "should_research": True,
                "should_admit_limit": False,
                "explanation": "Let me approach this differently."
            },
            UncertaintyType.CONTRADICTION: {
                "strategy": "PRESENT_ALTERNATIVES",
                "action": "Show conflicting views without claiming truth",
                "should_synthesize": False,
                "should_research": False,
                "should_admit_limit": True,
                "explanation": "There are conflicting perspectives on this."
            },
            UncertaintyType.FUNDAMENTAL_LIMIT: {
                "strategy": "ADMIT_LIMIT",
                "action": "Acknowledge this is beyond empirical knowledge",
                "should_synthesize": False,
                "should_research": False,
                "should_admit_limit": True,
                "explanation": "This is a philosophical question I cannot answer definitively."
            }
        }
        
        return strategies.get(uncertainty, strategies[UncertaintyType.DATA_MISSING])
    
    def reflect_on_answer(self, query: str, answer: Dict, 
                          uncertainty: UncertaintyType, strategy: Dict) -> Dict:
        """
        Add meta-cognitive reflection to the answer.
        
        This is the key insight: the system doesn't just answer,
        it explains WHY it's confident or not.
        """
        reflection = {
            "self_assessment": {
                "uncertainty_type": uncertainty.value,
                "strategy_used": strategy["strategy"],
                "confidence_explanation": strategy["explanation"]
            },
            "epistemic_status": self._classify_epistemic_status(answer, uncertainty),
            "what_would_increase_confidence": self._suggest_improvements(uncertainty),
            "known_limitations": self._get_relevant_limitations(query)
        }
        
        answer["_REFLECTION"] = reflection
        return answer
    
    def _classify_epistemic_status(self, answer: Dict, uncertainty: UncertaintyType) -> str:
        """Classify the epistemic status of the answer."""
        confidence = answer.get("confidence", 0.5)
        
        if confidence >= 0.9:
            return "VERIFIED_FACT"
        elif confidence >= 0.7:
            return "HIGH_CONFIDENCE"
        elif confidence >= 0.5:
            return "MODERATE_CONFIDENCE"
        elif uncertainty == UncertaintyType.NOVEL_QUESTION:
            return "HYPOTHETICAL"
        elif uncertainty == UncertaintyType.FUNDAMENTAL_LIMIT:
            return "PHILOSOPHICAL"
        else:
            return "LOW_CONFIDENCE"
    
    def _suggest_improvements(self, uncertainty: UncertaintyType) -> List[str]:
        """Suggest what would increase confidence."""
        suggestions = {
            UncertaintyType.DATA_MISSING: [
                "Add more data about this topic to the graph",
                "Research authoritative sources"
            ],
            UncertaintyType.NOVEL_QUESTION: [
                "This is inherently speculative",
                "Verification would require empirical testing"
            ],
            UncertaintyType.PATTERN_MISMATCH: [
                "Train on more examples of this query type",
                "Add new reasoning patterns"
            ],
            UncertaintyType.CONTRADICTION: [
                "Gather more evidence to resolve conflict",
                "Identify temporal context (claims may be from different eras)"
            ],
            UncertaintyType.FUNDAMENTAL_LIMIT: [
                "This may not have an objective answer",
                "Consider philosophical frameworks"
            ]
        }
        return suggestions.get(uncertainty, [])
    
    def _get_relevant_limitations(self, query: str) -> List[str]:
        """Return known limitations relevant to this query."""
        return self.meta_state.get("learned_limitations", [])[:3]
    
    def record_outcome(self, query: str, answer: Dict, 
                       actual_success: bool, feedback: Optional[str] = None):
        """
        Learn from outcomes to improve future reasoning.
        
        This is the meta-learning component.
        """
        self.meta_state["total_queries"] += 1
        
        # Record outcome
        if actual_success:
            self.meta_state["outcomes"]["success"] += 1
        elif answer.get("_REFLECTION", {}).get("epistemic_status") == "HYPOTHETICAL":
            self.meta_state["outcomes"]["admitted_unknown"] += 1
        else:
            self.meta_state["outcomes"]["failure"] += 1
        
        # Track uncertainty patterns
        uncertainty = answer.get("_REFLECTION", {}).get("self_assessment", {}).get("uncertainty_type", "unknown")
        if uncertainty not in self.meta_state["uncertainty_patterns"]:
            self.meta_state["uncertainty_patterns"][uncertainty] = {"count": 0, "success_rate": 0}
        
        pattern = self.meta_state["uncertainty_patterns"][uncertainty]
        pattern["count"] += 1
        if actual_success:
            pattern["success_rate"] = (
                (pattern["success_rate"] * (pattern["count"] - 1) + 1) / pattern["count"]
            )
        else:
            pattern["success_rate"] = (
                pattern["success_rate"] * (pattern["count"] - 1) / pattern["count"]
            )
        
        # Track engine performance
        engines = answer.get("engines_used", [])
        for engine in engines:
            if engine not in self.meta_state["engine_performance"]:
                self.meta_state["engine_performance"][engine] = {"uses": 0, "success_rate": 0.5}
            
            perf = self.meta_state["engine_performance"][engine]
            perf["uses"] += 1
            if actual_success:
                perf["success_rate"] = min(1.0, perf["success_rate"] + 0.05)
            else:
                perf["success_rate"] = max(0.0, perf["success_rate"] - 0.05)
        
        # Learn limitations from failures
        if not actual_success and feedback:
            limitation = f"Failed on: {query[:50]}... | Feedback: {feedback}"
            if limitation not in self.meta_state["learned_limitations"]:
                self.meta_state["learned_limitations"].append(limitation)
                # Keep only recent limitations
                self.meta_state["learned_limitations"] = self.meta_state["learned_limitations"][-20:]
        
        self._save_meta_state()
    
    def get_confidence_adjustment(self, query_type: str, engines: List[str]) -> float:
        """
        Based on historical performance, adjust confidence.
        
        This is the practical output of meta-learning.
        """
        base_adjustment = 1.0
        
        # Adjust based on engine performance
        for engine in engines:
            perf = self.meta_state["engine_performance"].get(engine, {})
            engine_rate = perf.get("success_rate", 0.5)
            base_adjustment *= (0.5 + engine_rate / 2)  # Scale from 0.5 to 1.0
        
        return min(1.5, max(0.5, base_adjustment))  # Clamp between 0.5 and 1.5


# Factory function
_reflective_reasoner = None

def get_reflective_reasoner(llm_client=None):
    global _reflective_reasoner
    if _reflective_reasoner is None:
        _reflective_reasoner = ReflectiveReasoner(llm_client)
    return _reflective_reasoner
