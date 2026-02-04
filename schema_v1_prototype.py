"""
WMCS v1.0 Concept Schema Prototype
Implements the Universal Category System defined in the technical specification.
"""
from typing import List, Dict, Optional, Any, Union
from pydantic import BaseModel, Field

# --- Sub-Models for Complex Fields ---

class ID(BaseModel):
    group: int
    item: int
    subitem: Optional[int] = None
    
    def __str__(self):
        s = f"{self.group}.{self.item}"
        if self.subitem: s += f".{self.subitem}"
        return s

class GroundingStep(BaseModel):
    step: str
    type: str # perceptual, measurement, etc

class Grounding(BaseModel):
    chain: List[str] = Field(..., description="Steps to base reality")
    base_types: List[str] = Field(..., description="[perceptual, measurement, logical...]")
    evidence_summary: str
    confidence: float

class CompositionLevel(BaseModel):
    depth: int
    name: str # e.g. "Organs"
    components: List[Dict[str, Any]] # {name, ref, quantity}

class Composition(BaseModel):
    levels: List[CompositionLevel]
    base_layer: Dict[str, str] # {domain, concept, ref}
    assembly: str

class SpatialPart(BaseModel):
    name: str
    ref: Optional[str]
    relative_to: str # e.g. "body_core"
    position: Dict[str, Any] # {x, y, z, unit}
    rotation: Optional[Dict[str, Any]]
    shape: Optional[str]
    size: Optional[Dict[str, Any]]

class SpatialStructure(BaseModel):
    center: Dict[str, str] # {name, description}
    overall: Dict[str, Any] # {shape, size, volume}
    parts: List[SpatialPart]
    symmetry: Optional[Dict[str, Any]]

# --- The Main Concept Block ---

class ConceptBlockV1(BaseModel):
    # 1. CORE
    id: ID
    name: str
    aliases: List[str] = []
    type: str # e.g. "organism.animal.mammal"
    definition: str
    
    # 2. GROUNDING
    grounding: Grounding
    
    # 3. CLASSIFICATION
    classification: Dict[str, Any] = Field(default_factory=dict) # chain, siblings
    
    # 4. SUBSTANCE (Composition)
    composition: Optional[Composition] = None
    
    # 5. ARRANGEMENT (Structure)
    structure_spatial: Optional[SpatialStructure] = None
    structure_temporal: Optional[Dict[str, Any]] = None
    
    # 6. ATTRIBUTES
    properties: Dict[str, Any] = Field(default_factory=dict) # physical, intrinsic...
    
    # 7. DYNAMICS
    dynamics: Dict[str, Any] = Field(default_factory=dict) # behavior, function...
    
    # 8. CONNECTIONS
    connections: Dict[str, Any] = Field(default_factory=dict) # relational, parts...
    
    # 9. META
    meta: Dict[str, Any] = Field(default_factory=dict) # confidence, flags...

    class Config:
        extra = "allow" # Allow extra fields for flexibility during prototyping

# Example Usage / Test
if __name__ == "__main__":
    print("Schema v1.0 Prototype Loaded.")
