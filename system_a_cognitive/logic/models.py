from dataclasses import dataclass, field
from typing import List, Dict, Optional, Any, Set
from enum import Enum

@dataclass(frozen=True)
class ConceptID:
    """
    Immutable unique identifier for a Concept Block.
    Format: (Group, Item)
    Example: (21, 61) for CAT
    """
    group: int
    item: int

    def __str__(self):
        return f"({self.group}, {self.item})"

    def __repr__(self):
        return self.__str__()

class RelationType(Enum):
    # Hierarchical
    IS_A = "IS_A"
    INSTANCE_OF = "INSTANCE_OF"
    HAS_TYPE = "HAS_TYPE"
    # Compositional
    HAS_PART = "HAS_PART"
    PART_OF = "PART_OF"
    # Functional
    FILLS_ROLE = "FILLS_ROLE"
    PRODUCES = "PRODUCES"
    ENABLES = "ENABLES"
    # Causal
    CAUSES = "CAUSES"
    CAUSED_BY = "CAUSED_BY"
    # Equivalence
    EQUIVALENT_TO = "EQUIVALENT_TO"
    NOT_EQUIVALENT_FOR = "NOT_EQUIVALENT_FOR"

@dataclass(frozen=True)
class Relation:
    source: ConceptID
    target: ConceptID
    relation_type: RelationType
    metadata: Optional[Dict[str, Any]] = None

@dataclass
class Grounding:
    type: str  # e.g., "PHYSICAL", "MATHEMATICAL"
    method: str
    confidence: float

@dataclass
class Source:
    doc_id: str
    trust_score: float
    original_text: str

class ConceptBlock:
    """
    The atomic unit of knowledge in WMCS.
    """
    def __init__(self, id: ConceptID, name: str, primary_type: str):
        self.id = id
        self.name = name
        self.primary_type = primary_type
        self.status = "PROVISIONAL"
        
        # Facets - Flexible dictionaries for multi-lens views
        self.facets: Dict[str, Dict[str, Any]] = {
            "STRUCTURE": {},
            "FUNCTION": {},
            "MECHANISM": {},
            "EQUIVALENCE": {},
            "HIERARCHY": {},
            "EVOLUTION": {},
            "CONTRAST": {},
        }
        
        # Layers
        self.surface_layer: Dict[str, Any] = {}
        self.deep_layer: Dict[str, Any] = {}
        self.instance_layer: Dict[str, Any] = {}

        # Knowledge Graph Connections
        self.relations: List[Relation] = []

        # Epistemic Metadata
        self.sources: List[Source] = []
        self.grounding_stack: List[Grounding] = []
        self._confidence: float = 0.0

    def add_facet_data(self, lens: str, key: str, value: Any):
        if lens not in self.facets:
            raise ValueError(f"Unknown lens: {lens}")
        self.facets[lens][key] = value

    def add_relation(self, target: ConceptID, type: RelationType, meta: Dict = None):
        rel = Relation(self.id, target, type, meta)
        self.relations.append(rel)

    @property
    def confidence(self) -> float:
        return self._confidence

    @confidence.setter
    def confidence(self, value: float):
        if not (0.0 <= value <= 1.0):
            raise ValueError("Confidence must be between 0.0 and 1.0")
        self._confidence = value

    def __str__(self):
        return f"Block[{self.id}] {self.name} ({self.status})"

# ═══════════════════════════════════════════════════════════════
# REFLECTION & META-REASONING MODELS (Phase 7)
# ═══════════════════════════════════════════════════════════════

class Outcome(Enum):
    SUCCESS = "SUCCESS"
    FAILURE = "FAILURE"
    PARTIAL = "PARTIAL"

@dataclass
class ReasoningTrace:
    """
    Logs the cognitive steps taken to answer a query.
    Used for reflection.
    """
    query: str
    steps: List[str] = field(default_factory=list)
    blocks_used: List[str] = field(default_factory=list)
    outcome: Outcome = Outcome.SUCCESS
    timestamp: float = 0.0

@dataclass
class MetaLesson:
    """
    A learned strategy or rule about reasoning itself.
    "Knowing HOW to think".
    """
    id: str
    lesson_type: str # STRATEGY, CAUTION, DEPTH
    content: str     # The text of the lesson
    trigger: str     # When to apply this (e.g., "physics questions")
    confidence: float = 0.5
    created_at: str = ""

    def to_dict(self):
        return {
            "id": self.id,
            "type": self.lesson_type,
            "content": self.content,
            "trigger": self.trigger,
            "confidence": self.confidence,
            "created_at": self.created_at
        }
    
    @staticmethod
    def from_dict(data):
        return MetaLesson(
            id=data["id"],
            lesson_type=data["type"],
            content=data["content"],
            trigger=data["trigger"],
            confidence=data["confidence"],
            created_at=data["created_at"]
        )
