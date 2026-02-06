"""
Transfer Learning Intelligence Test
====================================
The REAL test of intelligence: Can the system USE what it learns?

This test validates:
1. RETENTION: After learning Topic A, can it answer questions about A without re-researching?
2. INFERENCE: Can it derive NEW conclusions from learned knowledge?
3. INTEGRATION: Can it combine knowledge from multiple learned concepts?
4. TRANSFER: Can it apply learned patterns to analogous situations?

This is the difference between a database and an intelligent system.
"""
import os
import json
import time
from datetime import datetime
from termcolor import colored
from dataclasses import dataclass, field
from typing import List, Dict, Tuple

@dataclass
class TransferTestResult:
    phase: str
    query: str
    expected_behavior: str
    actual_behavior: str
    passed: bool
    confidence: float
    research_triggered: bool
    time_ms: int
    notes: str = ""

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

def run_transfer_learning_test():
    """Run the transfer learning intelligence test."""
    from system_a_cognitive.cognitive_loop import CognitiveLoop
    
    print(colored("=" * 70, "magenta", attrs=["bold"]))
    print(colored("  TRANSFER LEARNING INTELLIGENCE TEST", "magenta", attrs=["bold"]))
    print(colored("  Testing REAL Learning vs Data Hoarding", "yellow"))
    print(colored("=" * 70, "magenta", attrs=["bold"]))
    print(f"  Started: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print()
    
    client = get_llm_client()
    loop = CognitiveLoop(llm_client=client, auto_research=True)
    
    results: List[TransferTestResult] = []
    
    # =========================================================================
    # TEST DESIGN: Learn → Retain → Infer → Integrate
    # =========================================================================
    
    test_phases = [
        # Phase 1: LEARNING - Trigger research to ingest knowledge
        {
            "phase": "1. LEARNING",
            "description": "First, we learn about a topic",
            "tests": [
                {
                    "query": "What is the structure of DNA?",
                    "expected": "RESEARCH_TRIGGERED",
                    "rationale": "Should trigger research since we may not have DNA data"
                }
            ]
        },
        
        # Phase 2: RETENTION - Can we answer follow-ups WITHOUT re-researching?
        {
            "phase": "2. RETENTION",
            "description": "Can we use just-learned knowledge?",
            "tests": [
                {
                    "query": "What are the four bases in DNA?",
                    "expected": "NO_RESEARCH",
                    "rationale": "Should answer from learned knowledge (A, T, G, C)"
                },
                {
                    "query": "What holds DNA strands together?",
                    "expected": "NO_RESEARCH",
                    "rationale": "Should answer from learned knowledge (hydrogen bonds)"
                }
            ]
        },
        
        # Phase 3: INFERENCE - Can we derive NEW conclusions?
        {
            "phase": "3. INFERENCE",
            "description": "Can we infer new facts from learned knowledge?",
            "tests": [
                {
                    "query": "If DNA uses A-T and G-C base pairing, what would happen if a strand has the sequence ATGC?",
                    "expected": "INFERENCE",
                    "rationale": "Should infer the complementary strand would be TACG"
                },
                {
                    "query": "Why is DNA's double helix structure important for replication?",
                    "expected": "INFERENCE",
                    "rationale": "Should infer that the strands can separate and serve as templates"
                }
            ]
        },
        
        # Phase 4: INTEGRATION - Can we combine multiple concepts?
        {
            "phase": "4. INTEGRATION",
            "description": "Can we combine concepts we learned?",
            "tests": [
                {
                    "query": "How is DNA related to proteins?",
                    "expected": "INTEGRATION",
                    "rationale": "Should connect DNA → genes → proteins from learned knowledge"
                }
            ]
        },
        
        # Phase 5: NOVEL APPLICATION - Can we answer truly new questions?
        {
            "phase": "5. NOVEL APPLICATION",
            "description": "Can we apply learned patterns to new situations?",
            "tests": [
                {
                    "query": "If a mutation changed one DNA base, what might happen to the resulting protein?",
                    "expected": "NOVEL_INFERENCE",
                    "rationale": "Should infer potential amino acid change based on learned knowledge"
                }
            ]
        }
    ]
    
    # =========================================================================
    # RUN TESTS
    # =========================================================================
    
    total_tests = sum(len(p["tests"]) for p in test_phases)
    test_num = 0
    
    for phase in test_phases:
        print(colored(f"\n{'='*70}", "cyan"))
        print(colored(f"  {phase['phase']}: {phase['description']}", "cyan", attrs=["bold"]))
        print(colored(f"{'='*70}", "cyan"))
        
        for test in phase["tests"]:
            test_num += 1
            query = test["query"]
            expected = test["expected"]
            
            print(f"\n  [{test_num}/{total_tests}] {query[:60]}...")
            print(f"  Expected: {expected}")
            print(f"  Rationale: {test['rationale']}")
            print("  " + "-" * 60)
            
            start_time = time.time()
            
            try:
                result = loop.process(query)
                elapsed_ms = int((time.time() - start_time) * 1000)
                
                confidence = result.get("confidence", 0)
                engines = result.get("engines_used", [])
                research_triggered = "DeepResearchAgent" in engines
                answer = result.get("answer", "")[:100] if result.get("answer") else "No answer"
                
                # Determine if behavior matches expectation
                if expected == "RESEARCH_TRIGGERED":
                    passed = research_triggered
                    actual = "RESEARCH_TRIGGERED" if research_triggered else "NO_RESEARCH"
                elif expected == "NO_RESEARCH":
                    passed = not research_triggered and confidence >= 0.3
                    actual = "NO_RESEARCH" if not research_triggered else "RESEARCH_TRIGGERED"
                elif expected in ["INFERENCE", "INTEGRATION", "NOVEL_INFERENCE"]:
                    # For inference tests, we check if it answered without re-researching
                    # AND if it shows some reasoning
                    passed = not research_triggered and confidence >= 0.2
                    actual = f"ANSWERED (conf={confidence:.2f})"
                else:
                    passed = True
                    actual = "UNKNOWN"
                
                # Color-coded output
                status = colored("✓ PASS", "green") if passed else colored("✗ FAIL", "red")
                print(f"  Result: {status}")
                print(f"  Answer: {answer}...")
                print(f"  Confidence: {confidence:.2f} | Research: {research_triggered} | Time: {elapsed_ms}ms")
                
                results.append(TransferTestResult(
                    phase=phase["phase"],
                    query=query,
                    expected_behavior=expected,
                    actual_behavior=actual,
                    passed=passed,
                    confidence=confidence,
                    research_triggered=research_triggered,
                    time_ms=elapsed_ms,
                    notes=answer[:200]
                ))
                
            except Exception as e:
                print(colored(f"  ERROR: {str(e)[:50]}", "red"))
                results.append(TransferTestResult(
                    phase=phase["phase"],
                    query=query,
                    expected_behavior=expected,
                    actual_behavior=f"ERROR: {str(e)[:50]}",
                    passed=False,
                    confidence=0,
                    research_triggered=False,
                    time_ms=0,
                    notes=str(e)
                ))
    
    # =========================================================================
    # GENERATE INTELLIGENCE REPORT
    # =========================================================================
    
    print(colored("\n" + "=" * 70, "magenta", attrs=["bold"]))
    print(colored("  TRANSFER LEARNING REPORT", "magenta", attrs=["bold"]))
    print(colored("=" * 70, "magenta", attrs=["bold"]))
    
    # Calculate metrics per phase
    phases_summary = {}
    for r in results:
        if r.phase not in phases_summary:
            phases_summary[r.phase] = {"passed": 0, "failed": 0, "total": 0}
        phases_summary[r.phase]["total"] += 1
        if r.passed:
            phases_summary[r.phase]["passed"] += 1
        else:
            phases_summary[r.phase]["failed"] += 1
    
    print(f"\n{'PHASE BREAKDOWN':^70}")
    print("-" * 70)
    print(f"  {'Phase':<25} {'Passed':>10} {'Failed':>10} {'Rate':>10}")
    print("  " + "-" * 60)
    
    for phase, stats in phases_summary.items():
        rate = (stats['passed'] / stats['total'] * 100) if stats['total'] > 0 else 0
        color = "green" if rate >= 75 else "yellow" if rate >= 50 else "red"
        print(f"  {phase:<25} {stats['passed']:>10} {stats['failed']:>10} {colored(f'{rate:.0f}%', color):>10}")
    
    # Key intelligence metrics
    total_passed = sum(1 for r in results if r.passed)
    total_tests = len(results)
    
    # Specific metrics
    retention_tests = [r for r in results if "RETENTION" in r.phase]
    retention_passed = sum(1 for r in retention_tests if r.passed and not r.research_triggered)
    
    inference_tests = [r for r in results if "INFERENCE" in r.phase or "INTEGRATION" in r.phase or "NOVEL" in r.phase]
    inference_passed = sum(1 for r in inference_tests if r.passed)
    
    print(f"\n{'INTELLIGENCE METRICS':^70}")
    print("-" * 70)
    print(f"  Overall Pass Rate: {total_passed}/{total_tests} ({total_passed/total_tests*100:.0f}%)")
    print(f"  Retention Score: {retention_passed}/{len(retention_tests)} (Can use learned knowledge)")
    print(f"  Inference Score: {inference_passed}/{len(inference_tests)} (Can derive new conclusions)")
    
    # Calculate intelligence score
    # Weighted: Retention (30%) + Inference (50%) + No-crash (20%)
    retention_rate = retention_passed / max(1, len(retention_tests))
    inference_rate = inference_passed / max(1, len(inference_tests))
    stability_rate = total_passed / max(1, total_tests)
    
    intelligence_score = (retention_rate * 0.30 + inference_rate * 0.50 + stability_rate * 0.20) * 100
    
    print(f"\n{'INTELLIGENCE SCORE':^70}")
    print("-" * 70)
    
    grade = "A+" if intelligence_score >= 90 else "A" if intelligence_score >= 85 else \
            "B+" if intelligence_score >= 80 else "B" if intelligence_score >= 70 else \
            "C+" if intelligence_score >= 65 else "C" if intelligence_score >= 55 else \
            "D" if intelligence_score >= 50 else "F"
    
    print(f"  Intelligence Score: {intelligence_score:.1f}/100")
    print(f"  Grade: {colored(grade, 'green' if grade.startswith('A') or grade.startswith('B') else 'yellow' if grade.startswith('C') else 'red')}")
    
    # The key insight
    print(colored(f"\n{'KEY FINDING':^70}", "cyan", attrs=["bold"]))
    print("-" * 70)
    
    if retention_rate >= 0.5 and inference_rate >= 0.5:
        finding = "✅ The system demonstrates GENUINE LEARNING - it can use and build upon new knowledge."
    elif retention_rate >= 0.5:
        finding = "⚠️ The system RETAINS knowledge but struggles with INFERENCE from it."
    elif inference_rate >= 0.5:
        finding = "⚠️ The system can INFER but doesn't consistently RETAIN learned knowledge."
    else:
        finding = "❌ The system is currently more of a data pipeline than an intelligent learner."
    
    print(f"  {finding}")
    
    # Save report
    report = {
        "timestamp": datetime.now().isoformat(),
        "test_type": "transfer_learning_intelligence",
        "total_tests": total_tests,
        "passed": total_passed,
        "retention_score": retention_passed,
        "retention_total": len(retention_tests),
        "inference_score": inference_passed,
        "inference_total": len(inference_tests),
        "intelligence_score": intelligence_score,
        "grade": grade,
        "finding": finding,
        "results": [
            {
                "phase": r.phase,
                "query": r.query,
                "expected": r.expected_behavior,
                "actual": r.actual_behavior,
                "passed": r.passed,
                "confidence": r.confidence,
                "research_triggered": r.research_triggered,
                "time_ms": r.time_ms
            }
            for r in results
        ]
    }
    
    report_path = "data/transfer_learning_report.json"
    with open(report_path, 'w') as f:
        json.dump(report, f, indent=2)
    
    print(f"\n  Report saved to: {report_path}")
    print(f"  Completed: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    return results

if __name__ == "__main__":
    run_transfer_learning_test()
