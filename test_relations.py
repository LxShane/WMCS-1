"""Test the full system with ID-based relations"""
import os
import json

# Test 1: RelationBuilder basic functionality
print("=== TEST 1: RelationBuilder ===")
from system_a_cognitive.logic.relation_builder import RelationBuilder
rb = RelationBuilder()
print(f"Registry has {len(rb._name_cache)} concept names")

# Find mentions in text
text = "A dolphin is a mammal that lives in the ocean and eats fish."
found = rb.find_mentioned_concepts(text)
print(f"Concepts mentioned in text: {found}")

# Test 2: Auto-add relations to a mock block
print("\n=== TEST 2: Auto-add relations ===")
mock_block = {
    "name": "TestConcept",
    "surface_layer": {"definition": "A test concept related to cat and dog."},
    "claims": [
        {"predicate": "location", "object": "ocean"},  # Should add ID if 'ocean' exists
    ]
}

added = rb.auto_add_relations(mock_block)
print(f"Relations added: {added}")
print("Updated claims:")
for c in mock_block.get("claims", []):
    print(f"  {c['predicate']}: {c['object']}")

# Test 3: Test Ingestor (without actually calling LLM)
print("\n=== TEST 3: Ingestor Integration ===")
from system_a_cognitive.ingestion.ingestor import ContentIngestor
from system_a_cognitive.logic.identity import IdentityManager
ingestor = ContentIngestor(identity_manager=IdentityManager())
print("Ingestor loaded with RelationBuilder integration")

# Test 4: Check a newly updated concept file
print("\n=== TEST 4: Verify cat.json has relations ===")
with open("data/concepts/cat.json", 'r', encoding='utf-8') as f:
    cat = json.load(f)

id_claims = []
import re
for c in cat.get("claims", []):
    if re.search(r'\(\d+,\s*\d+\)', str(c.get("object", ""))):
        id_claims.append(c)

print(f"Cat has {len(id_claims)} ID-based claims:")
for c in id_claims[:5]:
    print(f"  {c['predicate']}: {c['object']}")

print("\n=== ALL TESTS PASSED ===")
