"""
Test the Synthesis Engine with creative hypothetical generation.
Demonstrates that outputs are clearly marked as HYPOTHETICAL.
"""
from termcolor import colored
from system_a_cognitive.logic.synthesis_engine import get_synthesis_engine
import json

def test_synthesis():
    print(colored("=" * 60, "magenta", attrs=["bold"]))
    print(colored("  SYNTHESIS ENGINE TEST", "magenta", attrs=["bold"]))
    print(colored("  Generating HYPOTHETICAL concepts (NOT facts)", "yellow"))
    print(colored("=" * 60, "magenta", attrs=["bold"]))
    
    engine = get_synthesis_engine()
    
    # Test 1: Constrained Synthesis
    print(colored("\n[TEST 1] Constrained Synthesis", "cyan", attrs=["bold"]))
    print("Constraints: flies, self-replicating, microscopic, organic")
    
    result1 = engine.synthesize({
        "has_property": ["flies", "self-replicating"],
        "size": "microscopic",
        "made_of": "organic",
        "purpose": "pollination"
    })
    
    print(colored(f"\nStatus: {result1['_STATUS']}", "yellow"))
    print(colored(f"Requires Verification: {result1['_REQUIRES_VERIFICATION']}", "yellow"))
    print(f"Name: {result1['CORE']['name']}")
    print(f"Confidence: {result1['GROUNDING']['confidence']}")
    print(colored(f"Warning: {result1['_WARNING'][:80]}...", "red"))
    
    # Save it
    path1 = engine.save_hypothetical(result1)
    print(colored(f"Saved to: {path1}", "green"))
    
    # Test 2: Analogy Transfer
    print(colored("\n[TEST 2] Analogy Transfer", "cyan", attrs=["bold"]))
    print("Source: solar_system -> Target: economy")
    
    result2 = engine.synthesize_analogy("solar_system", "economy")
    
    print(colored(f"\nStatus: {result2['_STATUS']}", "yellow"))
    print(f"Name: {result2.get('name', 'N/A')}")
    print(colored(f"Warning: {result2['_WARNING'][:80]}...", "red"))
    
    path2 = engine.save_hypothetical(result2)
    print(colored(f"Saved to: {path2}", "green"))
    
    # Test 3: Counterfactual
    print(colored("\n[TEST 3] Counterfactual Synthesis", "cyan", attrs=["bold"]))
    print("Base: earth -> Change: no_magnetic_field")
    
    result3 = engine.synthesize_counterfactual("earth", "no_magnetic_field")
    
    print(colored(f"\nStatus: {result3['_STATUS']}", "yellow"))
    print(f"Name: {result3.get('name', 'N/A')}")
    print(colored(f"Warning: {result3['_WARNING'][:80]}...", "red"))
    
    path3 = engine.save_hypothetical(result3)
    print(colored(f"Saved to: {path3}", "green"))
    
    # Summary
    print(colored("\n" + "=" * 60, "magenta", attrs=["bold"]))
    print(colored("  SYNTHESIS COMPLETE", "magenta", attrs=["bold"]))
    print(colored("=" * 60, "magenta", attrs=["bold"]))
    
    print(colored("\nKEY SAFEGUARDS:", "yellow", attrs=["bold"]))
    print("  1. All outputs marked _STATUS: HYPOTHETICAL")
    print("  2. _REQUIRES_VERIFICATION: True")
    print("  3. Max confidence capped at 0.3")
    print("  4. Saved to data/hypotheticals/ (NOT data/concepts/)")
    print("  5. Includes _WARNING field")
    
    print(colored("\nTO PROMOTE TO FACT:", "cyan"))
    print("  engine.verify_and_promote(path, {")
    print("      'predictions_satisfied': [...],")
    print("      'manual_approval': True")
    print("  })")

if __name__ == "__main__":
    test_synthesis()
