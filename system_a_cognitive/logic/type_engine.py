"""
Type Enforcement Engine (WMCS v1.0)
Validates concepts against the full type hierarchy from the specification.
Determines required categories based on type.
"""
from typing import Dict, List, Optional, Set, Tuple

# Full Type Tree from Specification Section 4.2
TYPE_TREE = {
    "PHYSICAL": {
        "organism": {
            "organism.plant": {},
            "organism.animal": {
                "organism.animal.mammal": {},
                "organism.animal.bird": {},
                "organism.animal.reptile": {},
                "organism.animal.fish": {},
                "organism.animal.invertebrate": {}
            },
            "organism.fungi": {},
            "organism.microorganism": {}
        },
        "natural_object": {
            "natural_object.geological": {},
            "natural_object.astronomical": {},
            "natural_object.atmospheric": {},
            "natural_object.water_body": {}
        },
        "artifact.physical": {
            "artifact.physical.tool": {},
            "artifact.physical.vehicle": {},
            "artifact.physical.building": {},
            "artifact.physical.furniture": {},
            "artifact.physical.clothing": {},
            "artifact.physical.container": {}
        },
        "artifact.temporal": {
            "artifact.temporal.music": {},
            "artifact.temporal.video": {},
            "artifact.temporal.performance": {},
            "artifact.temporal.broadcast": {}
        },
        "place": {
            "place.natural": {},
            "place.constructed": {},
            "place.conceptual": {}
        }
    },
    "EVENT_LIKE": {
        "event": {
            "event.moment": {},
            "event.period": {},
            "event.continuous": {}
        },
        "process": {
            "process.instructional": {},
            "process.natural": {},
            "process.social": {}
        },
        "phenomenon": {
            "phenomenon.physical": {},
            "phenomenon.weather": {},
            "phenomenon.optical": {},
            "phenomenon.social": {}
        }
    },
    "SYSTEM": {
        "system.governance": {
            "system.governance.political": {},
            "system.governance.legal": {},
            "system.governance.economic": {}
        },
        "system.interactive": {
            "system.interactive.game": {},
            "system.interactive.conversation": {},
            "system.interactive.negotiation": {},
            "system.interactive.ritual": {}
        },
        "system.language": {
            "system.language.natural": {},
            "system.language.formal": {},
            "system.language.programming": {}
        },
        "system.technical": {
            "system.technical.mechanical": {},
            "system.technical.electrical": {},
            "system.technical.software": {},
            "system.technical.network": {}
        }
    },
    "AGENT_ATTACHED": {
        "organization": {
            "organization.corporate": {},
            "organization.governmental": {},
            "organization.social": {},
            "organization.religious": {}
        },
        "pattern": {
            "pattern.habit": {},
            "pattern.tradition": {},
            "pattern.routine": {},
            "pattern.addiction": {}
        },
        "ability": {
            "ability.physical": {},
            "ability.cognitive": {},
            "ability.social": {},
            "ability.creative": {}
        },
        "state": {
            "state.physical": {},
            "state.emotional": {},
            "state.social": {},
            "state.phase": {}
        }
    },
    "EXPERIENCE": {
        "experience.emotion": {
            "experience.emotion.basic": {},
            "experience.emotion.complex": {},
            "experience.emotion.social": {}
        },
        "experience.sensation": {
            "experience.sensation.pain": {},
            "experience.sensation.pleasure": {},
            "experience.sensation.hunger": {},
            "experience.sensation.temperature": {},
            "experience.sensation.pressure": {}
        },
        "experience.cognitive": {
            "experience.cognitive.memory": {},
            "experience.cognitive.deja_vu": {},
            "experience.cognitive.insight": {},
            "experience.cognitive.confusion": {}
        }
    },
    "PROPERTY": {
        "property.sensory": {
            "property.sensory.color": {},
            "property.sensory.sound": {},
            "property.sensory.texture": {},
            "property.sensory.taste": {},
            "property.sensory.smell": {}
        },
        "property.relational": {
            "property.relational.price": {},
            "property.relational.distance": {},
            "property.relational.similarity": {},
            "property.relational.rank": {}
        },
        "property.intrinsic": {
            "property.intrinsic.mass": {},
            "property.intrinsic.age": {},
            "property.intrinsic.density": {},
            "property.intrinsic.temperature": {}
        }
    },
    "ABSTRACT": {
        "abstraction.formal": {
            "abstraction.formal.number": {},
            "abstraction.formal.shape": {},
            "abstraction.formal.set": {},
            "abstraction.formal.function": {},
            "abstraction.formal.logical_operator": {}
        },
        "abstraction.conceptual": {
            "abstraction.conceptual.philosophical": {},
            "abstraction.conceptual.social": {},
            "abstraction.conceptual.aesthetic": {}
        },
        "category": {
            "category.taxonomic": {},
            "category.genre": {},
            "category.classification": {}
        },
        "relation": {
            "relation.causal": {},
            "relation.compositional": {},
            "relation.hierarchical": {},
            "relation.associative": {}
        }
    },
    "META": {
        "reference": {
            "reference.temporal": {},
            "reference.spatial": {},
            "reference.possessive": {},
            "reference.demonstrative": {}
        },
        "potential": {
            "potential.possibility": {},
            "potential.risk": {},
            "potential.opportunity": {},
            "potential.plan": {}
        },
        "composite": {
            "composite.dream": {},
            "composite.story": {},
            "composite.scenario": {},
            "composite.plan": {}
        }
    },
    "STRUCTURAL": {
        "absence": {
            "absence.spatial": {},
            "absence.temporal": {},
            "absence.conceptual": {}
        },
        "boundary": {
            "boundary.physical": {},
            "boundary.conceptual": {},
            "boundary.social": {}
        },
        "law": {
            "law.physical": {},
            "law.biological": {},
            "law.economic": {},
            "law.social": {}
        }
    },
    "LINGUISTIC": {
        "linguistic.speech_act": {
            "linguistic.speech_act.assertive": {},
            "linguistic.speech_act.directive": {},
            "linguistic.speech_act.commissive": {},
            "linguistic.speech_act.expressive": {},
            "linguistic.speech_act.declarative": {}
        },
        "linguistic.unit": {
            "linguistic.unit.word": {},
            "linguistic.unit.phrase": {},
            "linguistic.unit.sentence": {},
            "linguistic.unit.text": {}
        }
    }
}

# Required categories by type root (from Spec Section 4.3)
REQUIRED_CATEGORIES = {
    "PHYSICAL": ["CORE", "GROUNDING", "CLASSIFICATION", "SUBSTANCE", "ARRANGEMENT"],
    "EVENT_LIKE": ["CORE", "GROUNDING", "CLASSIFICATION", "TIME", "CAUSATION"],
    "SYSTEM": ["CORE", "GROUNDING", "CLASSIFICATION", "DYNAMICS"],
    "AGENT_ATTACHED": ["CORE", "GROUNDING", "CLASSIFICATION", "DYNAMICS"],
    "EXPERIENCE": ["CORE", "GROUNDING", "CLASSIFICATION", "PERCEPTION"],
    "PROPERTY": ["CORE", "GROUNDING", "ATTRIBUTES"],
    "ABSTRACT": ["CORE", "GROUNDING", "CLASSIFICATION"],
    "META": ["CORE", "GROUNDING"],
    "STRUCTURAL": ["CORE", "GROUNDING", "CLASSIFICATION"],
    "LINGUISTIC": ["CORE", "GROUNDING", "CLASSIFICATION"]
}

# Structure type by concept type (from Spec Table 4.3)
STRUCTURE_TYPE = {
    "organism": "spatial",
    "artifact.physical": "spatial",
    "artifact.temporal": "temporal",
    "event": "temporal",
    "process": "sequential",
    "phenomenon": "causal",
    "system.governance": "hierarchical",
    "system.interactive": "state_based",
    "organization": "hierarchical",
    "experience.emotion": "manifestation",
    "experience.sensation": "body_located",
    "property": "definitional",
    "abstraction.formal": "axiomatic",
    "abstraction.conceptual": "definitional",
    "category": "membership",
    "relation": "directional",
    "reference": "contextual",
    "potential": "conditional",
    "composite": "nested",
    "absence": "boundary_defined",
    "boundary": "edge_defined",
    "law": "domain_defined",
    "linguistic": "functional"
}


class TypeEngine:
    def __init__(self):
        self._all_types = self._flatten_types(TYPE_TREE)
    
    def _flatten_types(self, tree: Dict, prefix: str = "") -> Set[str]:
        """Flatten nested type tree into set of all valid type strings."""
        result = set()
        for key, subtree in tree.items():
            full_key = f"{prefix}.{key}" if prefix else key
            result.add(key)
            result.add(full_key)
            if subtree:
                result.update(self._flatten_types(subtree, key))
        return result
    
    def validate_type(self, type_string: str) -> Tuple[bool, str]:
        """Check if type string is valid. Returns (is_valid, message)."""
        if not type_string:
            return False, "Type is empty"
        
        # Check exact match
        if type_string in self._all_types:
            return True, f"Valid type: {type_string}"
        
        # Check partial match (e.g., "planet.terrestrial" should match under natural_object.astronomical)
        parts = type_string.split(".")
        if parts[0] in self._all_types:
            return True, f"Valid type root: {parts[0]}"
        
        return False, f"Unknown type: {type_string}. Expected one of the spec types."
    
    def get_type_root(self, type_string: str) -> Optional[str]:
        """Get the root category (PHYSICAL, EVENT_LIKE, etc.) for a type."""
        if not type_string:
            return None
        
        first_part = type_string.split(".")[0]
        
        # Check which root contains this type
        for root, subtree in TYPE_TREE.items():
            if first_part in subtree or first_part == root:
                return root
            for subtype in subtree:
                if first_part == subtype or first_part.startswith(subtype):
                    return root
        
        # Fallback: check common mappings
        type_to_root = {
            "organism": "PHYSICAL", "natural_object": "PHYSICAL", "artifact": "PHYSICAL",
            "place": "PHYSICAL", "planet": "PHYSICAL", "star": "PHYSICAL",
            "event": "EVENT_LIKE", "process": "EVENT_LIKE", "phenomenon": "EVENT_LIKE",
            "system": "SYSTEM", "organization": "AGENT_ATTACHED", "pattern": "AGENT_ATTACHED",
            "ability": "AGENT_ATTACHED", "state": "AGENT_ATTACHED",
            "experience": "EXPERIENCE", "property": "PROPERTY",
            "abstraction": "ABSTRACT", "category": "ABSTRACT", "relation": "ABSTRACT",
            "reference": "META", "potential": "META", "composite": "META",
            "absence": "STRUCTURAL", "boundary": "STRUCTURAL", "law": "STRUCTURAL",
            "linguistic": "LINGUISTIC"
        }
        
        return type_to_root.get(first_part, "PHYSICAL")  # Default to PHYSICAL
    
    def get_required_categories(self, type_string: str) -> List[str]:
        """Get list of required categories for a given type."""
        root = self.get_type_root(type_string)
        if root and root in REQUIRED_CATEGORIES:
            return REQUIRED_CATEGORIES[root]
        return ["CORE", "GROUNDING"]  # Minimum required
    
    def get_structure_type(self, type_string: str) -> str:
        """Get the primary structure type (spatial, temporal, hierarchical, etc.)."""
        first_part = type_string.split(".")[0]
        return STRUCTURE_TYPE.get(first_part, "spatial")
    
    def validate_concept(self, concept: Dict) -> Dict:
        """
        Full validation of a concept against spec requirements.
        Returns {valid: bool, errors: [], warnings: [], suggestions: []}
        """
        result = {"valid": True, "errors": [], "warnings": [], "suggestions": []}
        
        # 1. Check CORE exists
        if "CORE" not in concept:
            result["valid"] = False
            result["errors"].append("Missing CORE category")
            return result
        
        core = concept["CORE"]
        
        # 2. Check type
        type_str = core.get("type", "")
        is_valid, msg = self.validate_type(type_str)
        if not is_valid:
            result["warnings"].append(msg)
        
        # 3. Check required categories
        required = self.get_required_categories(type_str)
        for cat in required:
            if cat not in concept:
                result["warnings"].append(f"Missing recommended category: {cat}")
        
        # 4. Check structure type alignment
        struct_type = self.get_structure_type(type_str)
        if struct_type == "spatial" and "ARRANGEMENT" in concept:
            arr = concept["ARRANGEMENT"]
            if "structure_spatial" not in arr:
                result["suggestions"].append("Type requires spatial structure, but ARRANGEMENT.structure_spatial is missing")
        elif struct_type == "temporal" and "ARRANGEMENT" in concept:
            arr = concept["ARRANGEMENT"]
            if "structure_temporal" not in arr:
                result["suggestions"].append("Type requires temporal structure, but ARRANGEMENT.structure_temporal is missing")
        
        return result
    
    def infer_type(self, concept: Dict) -> str:
        """Suggest a type based on concept content."""
        # Simple heuristics
        if "ARRANGEMENT" in concept:
            arr = concept["ARRANGEMENT"]
            if "structure_spatial" in arr:
                return "organism.animal" if "parts" in arr.get("structure_spatial", {}) else "natural_object"
            if "structure_temporal" in arr:
                return "artifact.temporal"
        
        if "CAUSATION" in concept:
            return "process.natural"
        
        return "abstraction.conceptual"


# Singleton access
_engine = None

def get_type_engine() -> TypeEngine:
    global _engine
    if _engine is None:
        _engine = TypeEngine()
    return _engine


if __name__ == "__main__":
    # Quick test
    engine = TypeEngine()
    print("Type Validation Tests:")
    print(engine.validate_type("organism.animal.mammal"))
    print(engine.validate_type("planet.terrestrial"))
    print(engine.validate_type("invalid_type"))
    print("\nRequired categories for 'organism.animal':")
    print(engine.get_required_categories("organism.animal"))
