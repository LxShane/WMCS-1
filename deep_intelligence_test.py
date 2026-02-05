"""
WMCS v1.0 Deep Intelligence Test
Tests the full system with unexpected topics across multiple domains.
Evaluates: auto-research, reasoning engines, epistemic honesty, output quality.
"""
import time
from termcolor import colored
from system_a_cognitive.cognitive_loop import CognitiveLoop

def deep_test():
    """Run deep intelligence tests across unexpected domains."""
    
    print(colored("=" * 70, "magenta", attrs=["bold"]))
    print(colored("  WMCS v1.0 DEEP INTELLIGENCE TEST", "magenta", attrs=["bold"]))
    print(colored("  Testing with Unexpected Topics Outside Solar System Domain", "yellow"))
    print(colored("=" * 70, "magenta", attrs=["bold"]))
    
    # Create loop with auto-research ENABLED
    loop = CognitiveLoop(auto_research=True, max_iterations=3)
    
    # Test categories: Biology, Chemistry, History, Philosophy, Technology, Medicine
    tests = [
        # BIOLOGY - Should trigger research
        {
            "domain": "Biology",
            "query": "How does DNA replicate?",
            "type": "causal",
            "expects_research": True
        },
        {
            "domain": "Biology", 
            "query": "How is a neuron like a computer chip?",
            "type": "analogy",
            "expects_research": True
        },
        
        # CHEMISTRY - Should trigger research
        {
            "domain": "Chemistry",
            "query": "What is water made of?",
            "type": "composition",
            "expects_research": True
        },
        
        # HISTORY - Should trigger research
        {
            "domain": "History",
            "query": "What would have happened if Rome never fell?",
            "type": "counterfactual",
            "expects_research": True
        },
        
        # PHILOSOPHY - Abstract reasoning
        {
            "domain": "Philosophy",
            "query": "What is consciousness?",
            "type": "abstract",
            "expects_research": True
        },
        
        # CROSS-DOMAIN - Can it connect existing Solar System knowledge?
        {
            "domain": "Cross-Domain",
            "query": "How is the structure of an atom like the Solar System?",
            "type": "analogy",
            "expects_research": False  # Solar System is known
        },
        
        # TECHNOLOGY - Should trigger research
        {
            "domain": "Technology",
            "query": "How does a transistor work?",
            "type": "mechanism",
            "expects_research": True
        },
        
        # MEDICINE - Should trigger research
        {
            "domain": "Medicine",
            "query": "Why do viruses mutate?",
            "type": "causal",
            "expects_research": True
        },
        
        # MATHEMATICS - Abstract
        {
            "domain": "Mathematics",
            "query": "What is a fractal?",
            "type": "definition",
            "expects_research": True
        },
        
        # ECOLOGY - Complex systems
        {
            "domain": "Ecology",
            "query": "What would happen if all bees disappeared?",
            "type": "counterfactual",
            "expects_research": True
        },
    ]
    
    results = []
    
    for i, test in enumerate(tests, 1):
        print(colored(f"\n{'=' * 70}", "cyan"))
        print(colored(f"TEST {i}/{len(tests)}: [{test['domain']}] {test['type'].upper()}", "cyan", attrs=["bold"]))
        print(colored(f"Query: {test['query']}", "yellow"))
        print(colored(f"{'=' * 70}", "cyan"))
        
        start_time = time.time()
        
        try:
            result = loop.process(test['query'])
            elapsed = time.time() - start_time
            
            # Analyze result
            concepts_found = len(result['concepts_used'])
            engines_used = result['engines_used']
            confidence = result['confidence'] * 100
            iterations = result['iterations']
            trust = result.get('trust_score', 0) * 100
            research_triggered = 'DeepResearchAgent' in engines_used
            
            print(colored(f"\nMETRICS:", "green", attrs=["bold"]))
            print(f"  Time: {elapsed:.1f}s")
            print(f"  Concepts Found: {concepts_found}")
            print(f"  Engines Used: {engines_used}")
            print(f"  Confidence: {confidence:.0f}%")
            print(f"  Trust Score: {trust:.0f}%")
            print(f"  Iterations: {iterations}")
            print(f"  Research Triggered: {'YES' if research_triggered else 'NO'}")
            
            # Show trace
            print(colored(f"\nREASONING TRACE:", "yellow"))
            for step in result['trace'][:6]:
                detail = step['detail'][:50] if len(step['detail']) > 50 else step['detail']
                print(f"  -> {step['step']}: {detail}")
            
            # Show answer
            print(colored(f"\nANSWER:", "magenta", attrs=["bold"]))
            answer = result['answer']
            lines = answer.split('\n')[:8]
            for line in lines:
                if len(line) > 80:
                    print(f"  {line[:80]}...")
                else:
                    print(f"  {line}")
            if len(answer.split('\n')) > 8:
                print(f"  ... ({len(answer)} chars total)")
            
            # Evaluate
            if concepts_found > 0 and confidence > 50:
                status = "PASS"
            elif research_triggered:
                status = "LEARNING"
            else:
                status = "LOW_CONF"
            
            print(colored(f"\nSTATUS: {status}", "green" if status == "PASS" else "yellow"))
            
            results.append({
                "domain": test['domain'],
                "query": test['query'][:25],
                "status": status,
                "concepts": concepts_found,
                "confidence": confidence,
                "research": research_triggered,
                "time": elapsed
            })
            
        except Exception as e:
            print(colored(f"\nERROR: {e}", "red", attrs=["bold"]))
            results.append({
                "domain": test['domain'],
                "query": test['query'][:25],
                "status": "ERROR",
                "error": str(e)
            })
        
        # Small delay between tests
        time.sleep(1)
    
    # Summary
    print(colored(f"\n{'=' * 70}", "magenta", attrs=["bold"]))
    print(colored("  DEEP TEST SUMMARY", "magenta", attrs=["bold"]))
    print(colored(f"{'=' * 70}", "magenta", attrs=["bold"]))
    
    passed = sum(1 for r in results if r.get('status') == 'PASS')
    learning = sum(1 for r in results if r.get('status') == 'LEARNING')
    low_conf = sum(1 for r in results if r.get('status') == 'LOW_CONF')
    errors = sum(1 for r in results if r.get('status') == 'ERROR')
    
    print(f"\n  Domain          | Query                   | Status")
    print(f"  " + "-" * 55)
    for r in results:
        domain = r['domain'][:14]
        query = r['query'][:23]
        status = r['status']
        print(f"  {domain:<14} | {query:<23} | {status}")
    
    print(colored(f"\n  PASS: {passed}  |  LEARNING: {learning}  |  LOW: {low_conf}  |  ERROR: {errors}", "cyan"))
    
    # Intelligence assessment
    score = (passed * 10 + learning * 7) / len(results)
    print(colored(f"\n  INTELLIGENCE SCORE: {score:.1f}/10", "magenta", attrs=["bold"]))
    
    if score >= 8:
        print(colored("  EXCELLENT: System demonstrates strong reasoning capabilities", "green"))
    elif score >= 6:
        print(colored("  GOOD: System shows solid reasoning with room for growth", "yellow"))
    elif score >= 4:
        print(colored("  DEVELOPING: System needs more training data", "yellow"))
    else:
        print(colored("  NEEDS WORK: System requires significant improvements", "red"))

if __name__ == "__main__":
    deep_test()
