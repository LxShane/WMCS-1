"""
Test: System behavior with truly missing data
"""
from system_a_cognitive.cognitive_loop import CognitiveLoop

def test_truly_unknown():
    loop = CognitiveLoop()
    
    # Test with topic definitely NOT in our Solar System database
    unknown_queries = [
        "What is a quark?",
        "How does photosynthesis work?",
        "What is the Eiffel Tower made of?",
    ]
    
    print("=== TEST: Truly Unknown Topics ===")
    
    for query in unknown_queries:
        print(f"\nQuery: {query}")
        result = loop.process(query)
        concepts = result['concepts_used']
        confidence = result['confidence']
        
        if len(concepts) == 0:
            print(f"  Status: NO DATA FOUND")
            print(f"  Answer: {result['answer'][:100]}")
            print(f"  → System correctly admits lack of knowledge")
        else:
            print(f"  Status: Found {len(concepts)} related concepts")
            print(f"  Confidence: {confidence*100:.0f}%")
            print(f"  Concepts: {concepts[:3]}")

if __name__ == "__main__":
    test_truly_unknown()
