"""
WMCS v1.0 Stress Test
Tests all cognitive engines with diverse queries.
"""
from system_a_cognitive.cognitive_loop import CognitiveLoop
from termcolor import colored

def stress_test():
    loop = CognitiveLoop()
    
    tests = [
        ("Spatial", "Can the Moon fit inside Earth?"),
        ("Composition", "What is Jupiter made of?"),
        ("Analogy", "How is Saturn like Jupiter?"),
        ("Counterfactual", "What would happen if Mars disappeared?"),
        ("Causal", "Why does Earth have an atmosphere?"),
        ("Graph", "What is related to the Sun?"),
        ("General", "Tell me about Venus"),
        ("Spatial 2", "How big is the Sun compared to Earth?"),
        ("Composition 2", "What are the layers of the Sun?"),
        ("Graph 2", "What orbits Jupiter?"),
    ]
    
    print(colored("=== WMCS v1.0 STRESS TEST ===", "magenta", attrs=["bold"]))
    
    passed = 0
    failed = 0
    
    for category, query in tests:
        print(colored(f"\n[{category}] {query}", "cyan"))
        try:
            result = loop.process(query)
            engines = result["engines_used"]
            confidence = result["confidence"] * 100
            concepts = len(result["concepts_used"])
            answer = result["answer"][:120].replace("\n", " ")
            
            print(f"  Engines: {engines}")
            print(f"  Confidence: {confidence:.0f}%")
            print(f"  Concepts Used: {concepts}")
            print(f"  Answer: {answer}...")
            
            if concepts > 0:
                print(colored("  ✓ PASS", "green"))
                passed += 1
            else:
                print(colored("  ✗ FAIL (no concepts)", "red"))
                failed += 1
                
        except Exception as e:
            print(colored(f"  ✗ ERROR: {e}", "red"))
            failed += 1
    
    print(colored("\n=== STRESS TEST COMPLETE ===", "magenta", attrs=["bold"]))
    print(f"Passed: {passed}/{len(tests)}")
    print(f"Failed: {failed}/{len(tests)}")
    
    return passed, failed

if __name__ == "__main__":
    stress_test()
