"""
Test: Auto-Research Flow
Demonstrates how the system automatically researches unknown topics.
"""
from system_a_cognitive.cognitive_loop import CognitiveLoop
from termcolor import colored

def test_auto_research():
    # Create loop with auto-research ENABLED
    loop = CognitiveLoop(auto_research=True)
    
    print(colored("=== AUTO-RESEARCH TEST ===", "magenta", attrs=["bold"]))
    print("Query: What is a quark?")
    print("(This topic is NOT in our Solar System database)")
    print()
    
    result = loop.process("What is a quark?")
    
    print(colored("Result:", "cyan"))
    print(f"  Confidence: {result['confidence']*100:.0f}%")
    print(f"  Engines Used: {result['engines_used']}")
    print(f"  Concepts Found: {len(result['concepts_used'])}")
    print(f"  Iterations: {result['iterations']}")
    
    print(colored("\nTrace:", "yellow"))
    for step in result['trace']:
        print(f"  - {step['step']}: {step['detail'][:50]}")
    
    # Check if research was triggered
    if "DeepResearchAgent" in result['engines_used']:
        print(colored("\n✓ AUTO-RESEARCH WAS TRIGGERED!", "green", attrs=["bold"]))
    else:
        print(colored("\n✗ Auto-research was not triggered", "red"))
    
    print(colored("\nAnswer:", "cyan"))
    print(result['answer'][:200])

if __name__ == "__main__":
    test_auto_research()
