"""
Test: How the system handles unknown/missing data
"""
from system_a_cognitive.cognitive_loop import CognitiveLoop

def test_unknown_topic():
    loop = CognitiveLoop()
    
    # Test with topic NOT in our Solar System database
    print("=== TEST: Unknown Topic ===")
    result = loop.process("What is a black hole?")
    print(f"Query: What is a black hole?")
    print(f"Concepts found: {len(result['concepts_used'])}")
    print(f"Confidence: {result['confidence']*100:.0f}%")
    print(f"Answer: {result['answer'][:200]}")
    
    print("\nTrace:")
    for step in result['trace'][:5]:
        print(f"  - {step['step']}: {step['detail'][:60]}")
    
    # Test with partial data
    print("\n=== TEST: Edge Case Query ===")
    result2 = loop.process("What is between Earth and Mars?")
    print(f"Query: What is between Earth and Mars?")
    print(f"Concepts found: {len(result2['concepts_used'])}")
    print(f"Answer: {result2['answer'][:200]}")

if __name__ == "__main__":
    test_unknown_topic()
