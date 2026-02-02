import sys
import os

# Add parent dir to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from system_b_llm.parsers.query_parser import QueryParser
from system_b_llm.generators.response_generator import ResponseGenerator

# Mock objects to simulate System A inputs
class MockGrade:
    grade = "BOUNDED"
class MockContract:
    grade = MockGrade()
    confidence = 0.82
    can_assert = ["Dogs cannot climb trees due to blunt claws"]
    cannot_assert = []
    assumptions = ["Typical dog breed"]
    hedging_required = True

def test_system_b():
    print("Testing System B (LLM Layer)...")
    
    # 1. Parser
    parser = QueryParser()
    query = "Can a dog climb a tree?"
    parsed = parser.parse(query)
    
    assert parsed["action"] == "climb"
    assert "dog" in parsed["entities"]
    assert parsed["question_type"] == "CAUSAL"
    print(f"✅ Parser Output: {parsed}")
    
    # 2. Generator
    generator = ResponseGenerator()
    contract = MockContract()
    response = generator.generate(contract, parsed)
    
    print(f"✅ Generated Response:\n---\n{response}\n---")
    assert "Typically" in response
    assert "cannot climb" in response
    assert "Assumptions" in response

if __name__ == "__main__":
    test_system_b()
    print("\nALL SYSTEM B TESTS PASSED")
