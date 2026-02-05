"""
Test the Reflective Reasoner integration with the Cognitive Loop.
Demonstrates self-awareness about uncertainty types and reasoning strategies.
"""
import json
import os
from termcolor import colored
from system_a_cognitive.cognitive_loop import CognitiveLoop

def get_llm_client():
    """Get LLM client with proper initialization."""
    try:
        from system_b_llm.interfaces.gemini_client import GeminiClient
        api_key = os.environ.get("GEMINI_API_KEY", "")
        if api_key:
            return GeminiClient(api_key=api_key, model="gemini-2.0-flash")
    except:
        pass
    return None

def test_reflective_reasoning():
    print(colored("=" * 60, "magenta", attrs=["bold"]))
    print(colored("  REFLECTIVE REASONER TEST", "magenta", attrs=["bold"]))
    print(colored("  Testing meta-cognitive self-awareness", "yellow"))
    print(colored("=" * 60, "magenta", attrs=["bold"]))
    
    client = get_llm_client()
    loop = CognitiveLoop(llm_client=client, auto_research=False)  # Disable research for quick test
    
    # Test queries to trigger different uncertainty types
    test_cases = [
        {
            "query": "What is the chemical composition of water?",
            "expected_type": "Should have data (DATA_MISSING or HIGH_CONFIDENCE)",
            "category": "Known Domain"
        },
        {
            "query": "What would happen if humans could photosynthesize?",
            "expected_type": "NOVEL_QUESTION - genuinely speculative",
            "category": "Counterfactual"
        },
        {
            "query": "What is the meaning of life?",
            "expected_type": "FUNDAMENTAL_LIMIT - philosophical",
            "category": "Philosophical"
        },
        {
            "query": "How does a quark taste?",
            "expected_type": "PATTERN_MISMATCH - category error",
            "category": "Nonsensical"
        }
    ]
    
    results = []
    
    for i, test in enumerate(test_cases, 1):
        print(colored(f"\n[TEST {i}] {test['category']}", "cyan", attrs=["bold"]))
        print(f"Query: {test['query']}")
        print(f"Expected: {test['expected_type']}")
        print("-" * 50)
        
        try:
            result = loop.process(test['query'])
            
            # Check for reflection
            reflection = result.get("_REFLECTION", {})
            
            print(f"Confidence: {result.get('confidence', 'N/A'):.2f}")
            print(f"Engines Used: {result.get('engines_used', [])}")
            
            if reflection:
                self_assess = reflection.get("self_assessment", {})
                print(colored(f"✓ Uncertainty Type: {self_assess.get('uncertainty_type', 'N/A')}", "green"))
                print(colored(f"✓ Strategy: {self_assess.get('strategy_used', 'N/A')}", "green"))
                print(f"  Epistemic Status: {reflection.get('epistemic_status', 'N/A')}")
                print(f"  Improvements: {reflection.get('what_would_increase_confidence', [])[:2]}")
            else:
                print(colored("  (High confidence - no reflection needed)", "yellow"))
            
            results.append({
                "query": test["query"],
                "category": test["category"],
                "confidence": result.get("confidence", 0),
                "has_reflection": bool(reflection),
                "uncertainty_type": reflection.get("self_assessment", {}).get("uncertainty_type", "N/A")
            })
            
        except Exception as e:
            print(colored(f"ERROR: {e}", "red"))
            results.append({"query": test["query"], "error": str(e)})
    
    # Summary
    print(colored("\n" + "=" * 60, "magenta", attrs=["bold"]))
    print(colored("  TEST SUMMARY", "magenta", attrs=["bold"]))
    print(colored("=" * 60, "magenta", attrs=["bold"]))
    
    reflected = sum(1 for r in results if r.get("has_reflection", False))
    
    print(f"\nTotal Tests: {len(results)}")
    print(f"Reflective Analysis Triggered: {reflected}/{len(results)}")
    
    print("\nUncertainty Types Detected:")
    for r in results:
        print(f"  - {r.get('category', 'Unknown')}: {r.get('uncertainty_type', 'N/A')}")
    
    # Check meta-learning state
    print(colored("\n[META-LEARNING STATE]", "cyan", attrs=["bold"]))
    try:
        with open("data/meta/reasoning_state.json", "r") as f:
            meta = json.load(f)
            print(f"  Total Queries Tracked: {meta.get('total_queries', 0)}")
            print(f"  Outcomes: {meta.get('outcomes', {})}")
            print(f"  Uncertainty Patterns: {list(meta.get('uncertainty_patterns', {}).keys())}")
    except FileNotFoundError:
        print("  (No meta-learning state yet - will accumulate over time)")

if __name__ == "__main__":
    test_reflective_reasoning()
