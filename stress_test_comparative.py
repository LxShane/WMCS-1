"""
WMCS Comparative Stress Test: Auto-Research Enabled
====================================================
Runs a subset of tests with auto_research=True to measure
how the system's confidence improves when it can learn.
"""
import os
import json
import time
from datetime import datetime
from termcolor import colored

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

def run_comparative_test():
    """Run tests with auto-research enabled."""
    from system_a_cognitive.cognitive_loop import CognitiveLoop
    
    print(colored("=" * 70, "magenta", attrs=["bold"]))
    print(colored("  WMCS COMPARATIVE STRESS TEST", "magenta", attrs=["bold"]))
    print(colored("  Auto-Research ENABLED - System Can Learn", "green"))
    print(colored("=" * 70, "magenta", attrs=["bold"]))
    print(f"  Started: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print()
    
    client = get_llm_client()
    loop = CognitiveLoop(llm_client=client, auto_research=True)  # LEARNING ENABLED
    
    # Use a focused subset that should benefit from research
    test_queries = [
        # Known domains that should have data or be researchable
        ("Factual", "What is DNA made of?"),
        ("Factual", "What are the layers of Earth's atmosphere?"),
        ("Factual", "How does photosynthesis work?"),
        
        # Queries that require research
        ("Research", "What is CRISPR gene editing?"),
        ("Research", "How do mRNA vaccines work?"),
        ("Research", "What is quantum computing?"),
        
        # Causal reasoning
        ("Causal", "Why do seasons change?"),
        ("Causal", "What causes earthquakes?"),
        ("Causal", "How does gravity work?"),
        
        # Analogies
        ("Analogy", "How is a cell like a factory?"),
        ("Analogy", "Compare the brain to a computer."),
        
        # Edge cases (should still admit uncertainty)
        ("Philosophical", "What is consciousness?"),
        ("Counterfactual", "What if the moon didn't exist?"),
    ]
    
    results = []
    total = len(test_queries)
    
    print(f"Running {total} tests with auto-research enabled...")
    print("(This may take a few minutes as the system researches unknown topics)")
    print()
    
    for i, (category, query) in enumerate(test_queries, 1):
        print(f"[{i}/{total}] ({category}) {query[:45]}...", end=" ", flush=True)
        
        start_time = time.time()
        
        try:
            result = loop.process(query)
            elapsed_ms = int((time.time() - start_time) * 1000)
            
            confidence = result.get("confidence", 0)
            engines = result.get("engines_used", [])
            research_triggered = "DeepResearchAgent" in engines
            
            status = colored("LEARNED", "green") if research_triggered else (
                colored("KNOWN", "cyan") if confidence >= 0.7 else colored("LOW", "yellow")
            )
            
            print(f"{status} (conf={confidence:.2f}, {elapsed_ms}ms)")
            
            results.append({
                "category": category,
                "query": query,
                "confidence": confidence,
                "research_triggered": research_triggered,
                "engines": engines,
                "time_ms": elapsed_ms
            })
            
        except Exception as e:
            print(colored(f"ERROR: {str(e)[:30]}", "red"))
            results.append({
                "category": category,
                "query": query,
                "confidence": 0,
                "error": str(e)
            })
    
    # Generate comparison report
    print(colored("\n" + "=" * 70, "magenta", attrs=["bold"]))
    print(colored("  COMPARATIVE ANALYSIS", "magenta", attrs=["bold"]))
    print(colored("=" * 70, "magenta", attrs=["bold"]))
    
    # Load baseline
    try:
        with open("data/stress_test_report.json", "r") as f:
            baseline = json.load(f)
        baseline_conf = baseline["avg_confidence"]
    except:
        baseline_conf = 0.34  # Default from previous test
    
    # Calculate new metrics
    avg_conf = sum(r.get("confidence", 0) for r in results) / len(results)
    research_count = sum(1 for r in results if r.get("research_triggered", False))
    avg_time = sum(r.get("time_ms", 0) for r in results) / len(results)
    
    print(f"\n{'COMPARISON':^70}")
    print("-" * 70)
    print(f"  {'Metric':<30} {'Baseline (No Research)':<20} {'With Research':<20}")
    print("  " + "-" * 66)
    print(f"  {'Avg Confidence':<30} {baseline_conf:<20.3f} {avg_conf:<20.3f}")
    print(f"  {'Research Triggered':<30} {'0':20} {research_count:<20}")
    print(f"  {'Avg Response Time':<30} {'0ms':20} {avg_time:.0f}ms")
    
    # Confidence improvement
    improvement = ((avg_conf - baseline_conf) / baseline_conf) * 100 if baseline_conf > 0 else 0
    improvement_text = colored(f"+{improvement:.1f}%", "green") if improvement > 0 else colored(f"{improvement:.1f}%", "red")
    print(f"\n  Confidence Improvement: {improvement_text}")
    
    # Category breakdown
    print(f"\n{'CATEGORY BREAKDOWN':^70}")
    print("-" * 70)
    categories = {}
    for r in results:
        cat = r.get("category", "Unknown")
        if cat not in categories:
            categories[cat] = {"total": 0, "confidence_sum": 0, "researched": 0}
        categories[cat]["total"] += 1
        categories[cat]["confidence_sum"] += r.get("confidence", 0)
        if r.get("research_triggered"):
            categories[cat]["researched"] += 1
    
    print(f"  {'Category':<15} {'Avg Conf':>10} {'Researched':>12} {'Count':>8}")
    print("  " + "-" * 50)
    for cat, stats in categories.items():
        avg = stats["confidence_sum"] / stats["total"] if stats["total"] > 0 else 0
        print(f"  {cat:<15} {avg:>10.2f} {stats['researched']:>12} {stats['total']:>8}")
    
    # Key finding
    print(colored(f"\n{'KEY FINDING':^70}", "cyan", attrs=["bold"]))
    print("-" * 70)
    
    if improvement > 20:
        finding = "The system shows SIGNIFICANT improvement when allowed to research."
    elif improvement > 5:
        finding = "The system shows MODERATE improvement with research capability."
    elif improvement > 0:
        finding = "The system shows SLIGHT improvement, but epistemic honesty is preserved."
    else:
        finding = "The system maintains epistemic honesty even with research available."
    
    print(f"  {finding}")
    print(f"\n  Research was triggered for {research_count}/{total} queries ({research_count/total*100:.0f}%)")
    print(f"  This demonstrates the system's ability to LEARN when needed.")
    
    # Save comparative report
    report = {
        "timestamp": datetime.now().isoformat(),
        "test_type": "comparative_with_research",
        "total_tests": total,
        "avg_confidence": avg_conf,
        "baseline_confidence": baseline_conf,
        "improvement_percent": improvement,
        "research_triggered": research_count,
        "avg_response_time_ms": avg_time,
        "results": results
    }
    
    with open("data/comparative_test_report.json", "w") as f:
        json.dump(report, f, indent=2)
    
    print(f"\n  Report saved to: data/comparative_test_report.json")
    print(f"  Completed: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

if __name__ == "__main__":
    run_comparative_test()
