import sys
import os

# Add parent dir to path to allow imports
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from system_a_cognitive.logic.models import ConceptBlock, ConceptID, RelationType
from system_a_cognitive.epistemic.gate import EpistemicGate

def test_models():
    print("Testing Models...")
    
    # 1. ID Creation
    id_cat = ConceptID(21, 61)
    id_cat_copy = ConceptID(21, 61)
    assert id_cat == id_cat_copy, "IDs should be equal"
    assert hash(id_cat) == hash(id_cat_copy), "Hashes should match"
    print(f"✅ ConceptID Created: {id_cat}")

    # 2. Block Creation
    cat_block = ConceptBlock(id_cat, "Cat", "PHYSICAL")
    assert cat_block.name == "Cat"
    print(f"✅ Block Created: {cat_block}")

    # 3. Facets
    cat_block.add_facet_data("STRUCTURE", "legs", 4)
    assert cat_block.facets["STRUCTURE"]["legs"] == 4
    print("✅ Facet Data Added")

    # 4. Relations
    id_paw = ConceptID(23, 51)
    cat_block.add_relation(id_paw, RelationType.HAS_PART)
    assert len(cat_block.relations) == 1
    assert cat_block.relations[0].relation_type == RelationType.HAS_PART
    print("✅ Relation Added")

def test_gate():
    print("\nTesting Epistemic Gate...")
    gate = EpistemicGate()

    # 1. Confidence Calculation
    conf = gate.calculate_confidence([0.9, 0.85, 0.95], assumption_penalty=0.05)
    # Min is 0.85, penalty 0.05 -> 0.80
    assert abs(conf - 0.80) < 0.001
    print(f"✅ Confidence Calculated: {conf}")

    # 2. Grading
    grade = gate.determine_grade(0.80)
    assert grade.grade == "BOUNDED"
    print(f"✅ Grade Determined: {grade.grade}")

    # 3. Contract
    contract = gate.generate_contract(
        confidence=0.80,
        assumptions=["Typical Cat"],
        positive_assertions=["Cats allow petting"],
        negative_assertions=["All cats bite"]
    )
    assert contract.can_assert[0] == "Cats allow petting"
    assert contract.hedging_required == True
    print("✅ Contract Generated")

if __name__ == "__main__":
    test_models()
    test_gate()
    print("\nALL SYSTEM A TESTS PASSED")
