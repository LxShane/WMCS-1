"""
Data Filling System (WMCS v1.0)
Auto-detects missing required fields and fills them using LLM inference.
Integrates with TypeEngine to determine what's missing.
"""
import json
import os
from typing import Dict, List, Optional, Tuple
from termcolor import colored

from system_a_cognitive.logic.type_engine import get_type_engine


class DataFiller:
    def __init__(self, llm_client=None):
        self.type_engine = get_type_engine()
        self.llm_client = llm_client
    
    def get_missing_fields(self, concept: Dict) -> Dict:
        """
        Analyze concept and return missing required fields.
        Returns {category: [field1, field2, ...], ...}
        """
        missing = {}
        
        # Get required categories from type
        type_str = concept.get("CORE", {}).get("type", "")
        required_cats = self.type_engine.get_required_categories(type_str)
        
        for cat in required_cats:
            if cat not in concept:
                missing[cat] = ["entire_category"]
            else:
                # Check specific fields within category
                cat_missing = self._check_category_fields(cat, concept[cat])
                if cat_missing:
                    missing[cat] = cat_missing
        
        return missing
    
    def _check_category_fields(self, category: str, data: Dict) -> List[str]:
        """Check for missing fields within a specific category."""
        missing = []
        
        # Required fields by category
        required = {
            "CORE": ["id", "name", "type", "definition"],
            "GROUNDING": ["chain", "base_types", "confidence"],
            "CLASSIFICATION": ["categorical_chain"],
            "SUBSTANCE": ["composition"],
            "ARRANGEMENT": [],  # Depends on structure type
            "PERCEPTION": ["surface"],
            "ATTRIBUTES": [],
            "DYNAMICS": ["behavior"],
            "TIME": ["lifecycle"],
            "CAUSATION": ["requires", "produces"],
            "CONNECTIONS": ["relational"],
            "CONTEXT": [],
            "VARIATION": [],
            "META": []
        }
        
        for field in required.get(category, []):
            if field not in data or data[field] is None:
                missing.append(field)
        
        return missing
    
    def get_fill_priority(self, missing: Dict) -> List[Tuple[str, str]]:
        """
        Prioritize which fields to fill first.
        Returns list of (category, field) tuples in priority order.
        """
        priority_order = [
            "CORE", "GROUNDING", "CLASSIFICATION", 
            "SUBSTANCE", "ARRANGEMENT", "CAUSATION",
            "DYNAMICS", "TIME", "CONNECTIONS"
        ]
        
        result = []
        for cat in priority_order:
            if cat in missing:
                for field in missing[cat]:
                    result.append((cat, field))
        
        return result
    
    def fill_missing(self, concept: Dict, dry_run: bool = False) -> Dict:
        """
        Fill missing fields using LLM inference.
        Returns updated concept with filled fields marked as inferred.
        """
        missing = self.get_missing_fields(concept)
        if not missing:
            return concept
        
        if dry_run:
            print(colored(f"Would fill: {missing}", "yellow"))
            return concept
        
        if not self.llm_client:
            print(colored("No LLM client configured for filling", "red"))
            return concept
        
        # Build fill prompt
        name = concept.get("CORE", {}).get("name", "Unknown")
        type_str = concept.get("CORE", {}).get("type", "Unknown")
        
        prompt = f"""
        You are the WMCS Data Filler.
        Fill in the missing fields for concept: '{name}' (type: {type_str})
        
        Current data:
        {json.dumps(concept, indent=2)}
        
        Missing fields: {missing}
        
        INSTRUCTIONS:
        - Infer realistic values based on scientific/common knowledge
        - For ARRANGEMENT.structure_spatial, estimate 3D coordinates in cm
        - For SUBSTANCE.composition, provide recursive breakdown
        - For GROUNDING, provide evidence chain
        - Mark all inferred data with "source": "inferred"
        
        Return ONLY the missing categories/fields as JSON.
        """
        
        try:
            result = self.llm_client.json_completion("DataFiller", prompt)
            
            # Merge filled data
            for cat, data in result.items():
                if cat not in concept:
                    concept[cat] = data
                elif isinstance(data, dict):
                    concept[cat].update(data)
            
            # Mark as auto-filled
            if "META" not in concept:
                concept["META"] = {}
            concept["META"]["auto_filled"] = True
            concept["META"]["filled_fields"] = list(missing.keys())
            
            print(colored(f"  Filled {len(missing)} categories for '{name}'", "green"))
            
        except Exception as e:
            print(colored(f"  Fill error: {e}", "red"))
        
        return concept
    
    def audit_concept(self, concept: Dict) -> Dict:
        """
        Full audit of concept against spec requirements.
        Returns detailed report.
        """
        report = {
            "name": concept.get("CORE", {}).get("name", "Unknown"),
            "type": concept.get("CORE", {}).get("type", "Unknown"),
            "type_validation": self.type_engine.validate_type(
                concept.get("CORE", {}).get("type", "")
            ),
            "concept_validation": self.type_engine.validate_concept(concept),
            "missing_fields": self.get_missing_fields(concept),
            "completeness": 0.0
        }
        
        # Calculate completeness score
        missing = report["missing_fields"]
        type_str = report["type"]
        required = self.type_engine.get_required_categories(type_str)
        
        if required:
            present = len([c for c in required if c in concept and c not in missing])
            report["completeness"] = present / len(required)
        
        return report
    
    def batch_audit(self, directory: str) -> List[Dict]:
        """Audit all concepts in a directory."""
        reports = []
        
        for fname in os.listdir(directory):
            if fname.endswith(".json"):
                path = os.path.join(directory, fname)
                try:
                    with open(path, 'r', encoding='utf-8') as f:
                        concept = json.load(f)
                    reports.append(self.audit_concept(concept))
                except Exception as e:
                    reports.append({"name": fname, "error": str(e)})
        
        return reports


# Singleton
_filler = None

def get_data_filler(llm_client=None) -> DataFiller:
    global _filler
    if _filler is None:
        _filler = DataFiller(llm_client)
    return _filler


if __name__ == "__main__":
    # Quick test
    filler = DataFiller()
    
    test_concept = {
        "CORE": {
            "name": "Test",
            "type": "organism.animal.mammal"
        }
    }
    
    print("Missing fields:")
    print(filler.get_missing_fields(test_concept))
    
    print("\nFull audit:")
    print(json.dumps(filler.audit_concept(test_concept), indent=2))
