from typing import List, Dict, Any, Optional
from dataclasses import dataclass

@dataclass
class AnswerGrade:
    grade: str
    min_confidence: float
    hedging_required: bool
    description: str

@dataclass
class Contract:
    grade: AnswerGrade
    confidence: float
    can_assert: List[str]
    cannot_assert: List[str]
    assumptions: List[str]
    hedging_required: bool

class EpistemicGate:
    """
    The Guardian of Truth.
    Validates confidence, enforces hedging, and prevents hallucination.
    """
    
    SOURCE_TRUST_LEVELS = {
        "PEER_REVIEWED": 0.90,
        "TEXTBOOK": 0.85,
        "OFFICIAL_DOC": 0.80,
        "ENCYCLOPEDIA": 0.75,
        "NEWS_MAJOR": 0.50,
        "BLOG": 0.30,
        "SOCIAL_MEDIA": 0.10,
        "LLM_GENERATED": 0.00
    }

    GRADES = {
        "ANSWER": AnswerGrade("ANSWER", 0.90, False, "Definitive answer"),
        "BOUNDED": AnswerGrade("BOUNDED", 0.70, True, "Light hedging required"),
        "WITH_ASSUMPTIONS": AnswerGrade("WITH_ASSUMPTIONS", 0.50, True, "Must state assumptions"),
        "HYPOTHESIS": AnswerGrade("HYPOTHESIS", 0.30, True, "Possible but uncertain"),
        "CANNOT_CONCLUDE": AnswerGrade("CANNOT_CONCLUDE", 0.00, False, "I don't know")
    }

    def get_source_trust(self, source_type: str) -> float:
        return self.SOURCE_TRUST_LEVELS.get(source_type, 0.1)

    def calculate_confidence(self, source_confidences: List[float], assumption_penalty: float = 0.0) -> float:
        if not source_confidences:
            return 0.0
        
        # Conservative: take the minimum of the primary sources (weakest link)
        # Alternatively could be average, but 'weakest link' is safer for truth.
        base_confidence = min(source_confidences)
        
        final_confidence = base_confidence - assumption_penalty
        return max(0.0, min(1.0, final_confidence))

    def determine_grade(self, confidence: float) -> AnswerGrade:
        if confidence >= 0.90:
            return self.GRADES["ANSWER"]
        elif confidence >= 0.70:
            return self.GRADES["BOUNDED"]
        elif confidence >= 0.50:
            return self.GRADES["WITH_ASSUMPTIONS"]
        elif confidence >= 0.30:
            return self.GRADES["HYPOTHESIS"]
        else:
            return self.GRADES["CANNOT_CONCLUDE"]

    def generate_contract(self, 
                         confidence: float, 
                         assumptions: List[str], 
                         positive_assertions: List[str],
                         negative_assertions: List[str]) -> Contract:
        
        # 1. Run Symbolic Validation
        from system_a_cognitive.logic.prover import SymbolicValidator
        validator = SymbolicValidator()
        
        # We treat assertions and assumptions as the "Trace" to validate
        full_trace = assumptions + positive_assertions
        # We need an id_map (passed or mocked)
        # For this demo, we assume the Validator parses IDs from text directly
        result = validator.validate_chain(full_trace, {})
        
        if not result['valid']:
            print(f"  [GATE] LOGIC REJECTED: {result['error']}")
            confidence = 0.0 # Force rejection
            negative_assertions.append(f"Logic Violation: {result['error']}")
            positive_assertions = [] # Clear invalid claims

        grade = self.determine_grade(confidence)
        
        return Contract(
            grade=grade,
            confidence=confidence,
            can_assert=positive_assertions if grade.grade != "CANNOT_CONCLUDE" else [],
            cannot_assert=negative_assertions,
            assumptions=assumptions,
            hedging_required=grade.hedging_required
        )
