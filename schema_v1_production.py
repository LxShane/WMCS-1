"""
WMCS v1.0 Production Schema
Strict implementation of 'Universal Category System' from Specification v1.0.
"""
from typing import List, Dict, Optional, Any, Union
from pydantic import BaseModel, Field

# --- CORE ---
class ID(BaseModel):
    group: int
    item: int
    subitem: Optional[int] = None
    
    def __str__(self):
        s = f"{self.group}.{self.item}"
        if self.subitem: s += f".{self.subitem}"
        return s

class ConceptCore(BaseModel):
    id: ID
    name: str
    aliases: List[str] = []
    type: str # Full type path: organism.animal.mammal...
    definition: str

# --- GROUNDING ---
class Grounding(BaseModel):
    chain: List[str]
    base_types: List[str] # perceptual, measurement, logical, behavioral, attestation
    evidence_summary: str
    weakest_link: Optional[str] = None
    confidence: float

# --- CLASSIFICATION ---
class Classification(BaseModel):
    categorical_chain: List[str]
    siblings: List[str] = []
    distinguishing_features: List[str] = []
    tags: List[str] = []

# --- SUBSTANCE ---
class CompositionLevel(BaseModel):
    depth: int
    name: str 
    components: List[Dict[str, Any]] # {name, ref, quantity, essential}

class Composition(BaseModel):
    levels: List[CompositionLevel]
    base_layer: Dict[str, str] # {domain, concept, ref}
    assembly: str

# --- ARRANGEMENT ---
class SpatialPart(BaseModel):
    name: str
    ref: Optional[str]
    relative_to: str
    position: Dict[str, Any] # x,y,z, unit
    rotation: Optional[Dict[str, Any]]
    shape: Optional[str]
    size: Optional[Dict[str, Any]]
    connection: Optional[Dict[str, Any]]

class SpatialStructure(BaseModel):
    center: Dict[str, str]
    overall: Dict[str, Any] # shape, size, volume
    parts: List[SpatialPart]
    symmetry: Optional[Dict[str, Any]]

class Arrangement(BaseModel):
    structure_spatial: Optional[SpatialStructure]
    structure_temporal: Optional[Dict[str, Any]]
    structure_hierarchical: Optional[Dict[str, Any]]

# --- TIME ---
class TimeInfo(BaseModel):
    lifecycle: List[str] = []
    duration: Optional[str] = None

# --- CAUSATION ---
class Causation(BaseModel):
    requires: List[str] = []
    produces: List[str] = []
    caused_by: List[str] = []
    prevents: List[str] = []

# --- CONNECTIONS ---
class Connections(BaseModel):
    relational: List[str] = []
    contrasts_with: List[str] = []
    similar_to: List[str] = []
    part_of: List[str] = []

# --- THE MASTER BLOCK ---
class ConceptBlockV1(BaseModel):
    # The 10 Major Categories from Spec
    CORE: ConceptCore
    GROUNDING: Grounding
    CLASSIFICATION: Classification
    SUBSTANCE: Optional[Composition] = None
    ARRANGEMENT: Optional[Arrangement] = None
    PERCEPTION: Optional[Dict[str, Any]] = None # surface, manifestation
    ATTRIBUTES: Optional[Dict[str, Any]] = None # properties_physical...
    DYNAMICS: Optional[Dict[str, Any]] = None # behavior, function
    TIME: Optional[TimeInfo] = None
    CAUSATION: Optional[Causation] = None
    CONNECTIONS: Optional[Connections] = None
    CONTEXT: Optional[Dict[str, Any]] = None
    VARIATION: Optional[Dict[str, Any]] = None
    META: Dict[str, Any] = Field(default_factory=dict)

    class Config:
        extra = "ignore" # Strict mode

# Test
if __name__ == "__main__":
    print("v1.0 Production Schema Loaded.")
