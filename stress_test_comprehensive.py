"""
WMCS Comprehensive Stress Test Suite
=====================================
A rigorous, researcher-grade evaluation of the complete system.

Tests:
1. Engine Coverage - Each of the 9+ engines
2. Query Types - Factual, causal, spatial, analogical, counterfactual
3. Edge Cases - Ambiguity, contradiction, nonsense, philosophical
4. Stress Conditions - No data, conflicting data, novel domains
5. Meta-Cognitive - Reflective reasoning, uncertainty handling
6. Integration - Full cognitive loop end-to-end
"""
import os
import json
import time
from datetime import datetime
from typing import Dict, List, Tuple
from termcolor import colored
from dataclasses import dataclass, field

@dataclass
class TestResult:
    query: str
    category: str
    subcategory: str
    passed: bool
    confidence: float
    engines_used: List[str]
    has_reflection: bool
    uncertainty_type: str
    response_time_ms: int
    notes: str = ""
    error: str = ""

@dataclass
class StressTestReport:
    total_tests: int = 0
    passed: int = 0
    failed: int = 0
    errors: int = 0
    avg_confidence: float = 0.0
    avg_response_time_ms: float = 0.0
    engine_usage: Dict[str, int] = field(default_factory=dict)
    category_results: Dict[str, Dict] = field(default_factory=dict)
    results: List[TestResult] = field(default_factory=list)

def get_llm_client():
    """Get LLM client if available."""
    try:
        from system_b_llm.interfaces.gemini_client import GeminiClient
        api_key = os.environ.get("GEMINI_API_KEY", "")
        if api_key:
            return GeminiClient(api_key=api_key, model="gemini-2.0-flash")
    except:
        pass
    return None

def run_stress_test():
    """Run the comprehensive stress test."""
    from system_a_cognitive.cognitive_loop import CognitiveLoop
    
    print(colored("=" * 70, "magenta", attrs=["bold"]))
    print(colored("  WMCS COMPREHENSIVE STRESS TEST", "magenta", attrs=["bold"]))
    print(colored("  Researcher-Grade System Evaluation", "yellow"))
    print(colored("=" * 70, "magenta", attrs=["bold"]))
    print(f"  Started: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print()
    
    client = get_llm_client()
    loop = CognitiveLoop(llm_client=client, auto_research=False)  # Fast mode
    
    report = StressTestReport()
    
    # =========================================================================
    # TEST CATEGORIES
    # =========================================================================
    
    test_suite = [
        # Category 1: ENGINE COVERAGE
        ("Engine Coverage", "Graph Navigation", [
            "What are the parts of a cell?",
            "What is connected to the heart?",
            "List all organs in the digestive system."
        ]),
        ("Engine Coverage", "Type Validation", [
            "Is water a liquid?",
            "What type of entity is DNA?",
            "Classify a neuron."
        ]),
        ("Engine Coverage", "Analogy Engine", [
            "How is an atom like a solar system?",
            "What is the relationship between DNA and a blueprint?",
            "Compare a cell to a factory."
        ]),
        ("Engine Coverage", "Inference Engine", [
            "If water contains oxygen, and oxygen supports combustion, can water burn?",
            "All mammals have hearts. Is a whale a mammal?",
            "If A causes B and B causes C, does A cause C?"
        ]),
        ("Engine Coverage", "Spatial Engine", [
            "Where is the nucleus located in a cell?",
            "What surrounds the Earth's core?",
            "Describe the spatial relationship between the lungs and the heart."
        ]),
        ("Engine Coverage", "Temporal Engine", [
            "What happens during cell division over time?",
            "Describe the sequence of digestion.",
            "What is the lifecycle of a star?"
        ]),
        ("Engine Coverage", "Causal Engine", [
            "What causes rain?",
            "Why do leaves change color in autumn?",
            "What mechanism makes muscles contract?"
        ]),
        ("Engine Coverage", "Composition Engine", [
            "What is water made of?",
            "What are the components of DNA?",
            "List the elements in air."
        ]),
        
        # Category 2: QUERY TYPES
        ("Query Types", "Factual", [
            "What is the boiling point of water?",
            "How many chromosomes do humans have?",
            "What is the speed of light?"
        ]),
        ("Query Types", "Definitional", [
            "What is photosynthesis?",
            "Define entropy.",
            "What is a quasar?"
        ]),
        ("Query Types", "Procedural", [
            "How does the heart pump blood?",
            "Explain how DNA replication works.",
            "Describe the process of fermentation."
        ]),
        ("Query Types", "Comparative", [
            "What is the difference between mitosis and meiosis?",
            "Compare DNA and RNA.",
            "How do prokaryotes differ from eukaryotes?"
        ]),
        
        # Category 3: EDGE CASES
        ("Edge Cases", "Ambiguous Queries", [
            "What is a bank?",
            "Explain the nature of light.",
            "What is Mercury?"
        ]),
        ("Edge Cases", "Nonsensical Queries", [
            "What color is the number 7?",
            "How much does sadness weigh?",
            "What is the smell of time?"
        ]),
        ("Edge Cases", "Philosophical", [
            "What is the meaning of life?",
            "Does free will exist?",
            "What is consciousness?"
        ]),
        ("Edge Cases", "Unanswerable", [
            "What will happen in 1000 years?",
            "What exists outside the universe?",
            "Why does anything exist at all?"
        ]),
        
        # Category 4: STRESS CONDITIONS
        ("Stress Conditions", "Novel Domains", [
            "Explain quantum entanglement in cooking terms.",
            "What would a civilization on a neutron star look like?",
            "How would biology work in 2D?"
        ]),
        ("Stress Conditions", "Counterfactuals", [
            "What if the Earth had no moon?",
            "What if humans had photosynthesis?",
            "What if gravity were twice as strong?"
        ]),
        ("Stress Conditions", "Multi-Hop Reasoning", [
            "If plants need CO2 and animals exhale CO2, how does this create a cycle?",
            "How does sunlight become food energy in animals?",
            "Trace the journey of a water molecule from ocean to cloud to river."
        ]),
        
        # Category 5: META-COGNITIVE
        ("Meta-Cognitive", "Uncertainty Handling", [
            "What do we not know about dark matter?",
            "How confident should we be about climate predictions?",
            "What are the limits of current AI understanding?"
        ]),
        ("Meta-Cognitive", "Self-Reference", [
            "How reliable is this answer?",
            "What would increase your confidence?",
            "What are you uncertain about?"
        ])
    ]
    
    # =========================================================================
    # RUN TESTS
    # =========================================================================
    
    total_queries = sum(len(queries) for _, _, queries in test_suite)
    print(f"Total Test Cases: {total_queries}")
    print(f"Categories: {len(set(cat for cat, _, _ in test_suite))}")
    print()
    
    test_num = 0
    for category, subcategory, queries in test_suite:
        print(colored(f"\n[{category}] {subcategory}", "cyan", attrs=["bold"]))
        print("-" * 50)
        
        if category not in report.category_results:
            report.category_results[category] = {"passed": 0, "failed": 0, "total": 0}
        
        for query in queries:
            test_num += 1
            print(f"  [{test_num}/{total_queries}] {query[:50]}...", end=" ", flush=True)
            
            start_time = time.time()
            
            try:
                result = loop.process(query)
                elapsed_ms = int((time.time() - start_time) * 1000)
                
                confidence = result.get("confidence", 0)
                engines = result.get("engines_used", [])
                reflection = result.get("_REFLECTION", {})
                uncertainty = reflection.get("self_assessment", {}).get("uncertainty_type", "none")
                
                # Determine pass/fail based on:
                # - Got an answer
                # - Used appropriate engines
                # - Reasonable confidence OR acknowledged uncertainty
                passed = (
                    result.get("answer") is not None and
                    len(engines) > 0 and
                    (confidence >= 0.3 or uncertainty != "none")
                )
                
                test_result = TestResult(
                    query=query,
                    category=category,
                    subcategory=subcategory,
                    passed=passed,
                    confidence=confidence,
                    engines_used=engines,
                    has_reflection=bool(reflection),
                    uncertainty_type=uncertainty,
                    response_time_ms=elapsed_ms
                )
                
                # Track engine usage
                for engine in engines:
                    report.engine_usage[engine] = report.engine_usage.get(engine, 0) + 1
                
                if passed:
                    print(colored(f"PASS", "green"), end="")
                    report.passed += 1
                    report.category_results[category]["passed"] += 1
                else:
                    print(colored(f"FAIL", "red"), end="")
                    report.failed += 1
                    report.category_results[category]["failed"] += 1
                
                print(f" (conf={confidence:.2f}, {elapsed_ms}ms)")
                
            except Exception as e:
                elapsed_ms = int((time.time() - start_time) * 1000)
                test_result = TestResult(
                    query=query,
                    category=category,
                    subcategory=subcategory,
                    passed=False,
                    confidence=0,
                    engines_used=[],
                    has_reflection=False,
                    uncertainty_type="error",
                    response_time_ms=elapsed_ms,
                    error=str(e)
                )
                print(colored(f"ERROR: {str(e)[:30]}", "red"))
                report.errors += 1
            
            report.results.append(test_result)
            report.category_results[category]["total"] += 1
            report.total_tests += 1
    
    # =========================================================================
    # GENERATE REPORT
    # =========================================================================
    
    print(colored("\n" + "=" * 70, "magenta", attrs=["bold"]))
    print(colored("  STRESS TEST REPORT", "magenta", attrs=["bold"]))
    print(colored("=" * 70, "magenta", attrs=["bold"]))
    
    # Overall Stats
    pass_rate = (report.passed / report.total_tests * 100) if report.total_tests > 0 else 0
    avg_conf = sum(r.confidence for r in report.results) / len(report.results) if report.results else 0
    avg_time = sum(r.response_time_ms for r in report.results) / len(report.results) if report.results else 0
    
    print(f"\n{'OVERALL RESULTS':^70}")
    print("-" * 70)
    print(f"  Total Tests: {report.total_tests}")
    print(f"  Passed: {report.passed} ({pass_rate:.1f}%)")
    print(f"  Failed: {report.failed}")
    print(f"  Errors: {report.errors}")
    print(f"  Avg Confidence: {avg_conf:.3f}")
    print(f"  Avg Response Time: {avg_time:.0f}ms")
    
    # Category Breakdown
    print(f"\n{'CATEGORY BREAKDOWN':^70}")
    print("-" * 70)
    print(f"  {'Category':<25} {'Passed':>8} {'Failed':>8} {'Rate':>10}")
    print("  " + "-" * 55)
    for cat, stats in report.category_results.items():
        rate = (stats['passed'] / stats['total'] * 100) if stats['total'] > 0 else 0
        status = colored(f"{rate:.0f}%", "green" if rate >= 70 else "yellow" if rate >= 50 else "red")
        print(f"  {cat:<25} {stats['passed']:>8} {stats['failed']:>8} {status:>10}")
    
    # Engine Usage
    print(f"\n{'ENGINE USAGE':^70}")
    print("-" * 70)
    sorted_engines = sorted(report.engine_usage.items(), key=lambda x: x[1], reverse=True)
    for engine, count in sorted_engines:
        bar = "█" * min(count, 30)
        print(f"  {engine:<25} {bar} ({count})")
    
    # Reflection Stats
    reflections = sum(1 for r in report.results if r.has_reflection)
    print(f"\n{'META-COGNITIVE STATS':^70}")
    print("-" * 70)
    print(f"  Reflective Analyses: {reflections}/{report.total_tests}")
    
    uncertainty_types = {}
    for r in report.results:
        if r.uncertainty_type and r.uncertainty_type != "none":
            uncertainty_types[r.uncertainty_type] = uncertainty_types.get(r.uncertainty_type, 0) + 1
    
    print(f"  Uncertainty Types Detected:")
    for ut, count in uncertainty_types.items():
        print(f"    - {ut}: {count}")
    
    # Final Score
    print(colored(f"\n{'FINAL SCORE':^70}", "magenta", attrs=["bold"]))
    print("-" * 70)
    
    # Calculate composite score
    score = (
        pass_rate * 0.4 +  # 40% weight on pass rate
        (avg_conf * 100) * 0.3 +  # 30% weight on confidence
        min(100, (reflections / max(1, report.total_tests)) * 200) * 0.2 +  # 20% on self-awareness
        min(100, len(report.engine_usage) * 10) * 0.1  # 10% on engine diversity
    )
    
    grade = "A+" if score >= 90 else "A" if score >= 85 else "B+" if score >= 80 else \
            "B" if score >= 75 else "C+" if score >= 70 else "C" if score >= 65 else \
            "D" if score >= 60 else "F"
    
    print(f"  Composite Score: {score:.1f}/100")
    print(f"  Grade: {colored(grade, 'green' if grade.startswith('A') or grade.startswith('B') else 'yellow')}")
    
    # Save report
    report_path = "data/stress_test_report.json"
    os.makedirs("data", exist_ok=True)
    
    report_data = {
        "timestamp": datetime.now().isoformat(),
        "total_tests": report.total_tests,
        "passed": report.passed,
        "failed": report.failed,
        "errors": report.errors,
        "pass_rate": pass_rate,
        "avg_confidence": avg_conf,
        "avg_response_time_ms": avg_time,
        "composite_score": score,
        "grade": grade,
        "engine_usage": report.engine_usage,
        "category_results": report.category_results,
        "uncertainty_types": uncertainty_types
    }
    
    with open(report_path, 'w') as f:
        json.dump(report_data, f, indent=2)
    
    print(f"\n  Report saved to: {report_path}")
    print(f"  Completed: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    return report

if __name__ == "__main__":
    run_stress_test()
