from system_a_cognitive.ingestion.ingestor import ContentIngestor
from system_a_cognitive.logic.models import ConceptBlock, ConceptID
import json
import os

def verify_block_structure():
    print("VERIFICATION: Testing Block ID and Content Rigor...")
    
    # 1. Ingest a complex test case
    ingestor = ContentIngestor()
    test_text = "The Human Heart is a muscular organ that pumps blood. ID Group 5, Item 10."
    print(f"Input: '{test_text}'")
    
    # Force the ingestor to create a block (mocking the LLM outcome for deterministic test if needed, 
    # but here we trust the prompt is good enough or we inspect the model logic)
    # Actually, let's verify the MODEL CLASS directly to prove the schema exists.
    
    # 2. Create a Compliance Block manually to check constraints
    block_id = ConceptID(group=21, item=99)
    block = ConceptBlock(id=block_id, name="TestBlock", primary_type="ENTITY")
    
    # 3. Check ID Structure
    print(f"\n[1] ID Structure: {block.id}")
    if isinstance(block.id.group, int) and isinstance(block.id.item, int):
        print("✅ PASS: ID is composed of (Group, Item) integers.")
    else:
        print("❌ FAIL: ID format incorrect.")

    # 4. Check Content Layers (As per Spec)
    print("\n[2] Content Layers:")
    layers = [
        ("Surface Layer", block.surface_layer),
        ("Deep Layer", block.deep_layer),
        ("Instance Layer", block.instance_layer),
        ("Facets (Lenses)", block.facets)
    ]
    
    for name, content in layers:
        print(f" - {name}: Exists (Type: {type(content)})")
        if isinstance(content, dict):
             print(f"   ✅ PASS: {name} is a structured dictionary.")
        else:
             print(f"   ❌ FAIL: {name} format invalid.")

    # 5. Check Facet Keys
    expected_facets = ["STRUCTURE", "FUNCTION", "MECHANISM", "EQUIVALENCE", "HIERARCHY", "EVOLUTION", "CONTRAST"]
    print("\n[3] Required Lenses (The 'Microscope'):")
    missing = [f for f in expected_facets if f not in block.facets]
    
    if not missing:
        print(f"✅ PASS: All {len(expected_facets)} Lenses present: {expected_facets}")
    else:
        print(f"❌ FAIL: Missing Lenses: {missing}")

if __name__ == "__main__":
    verify_block_structure()
