import os
import json
from config import Config
from system_b_llm.interfaces.gemini_client import GeminiClient
from system_a_cognitive.meta.verifier import ExternalVerifier
from termcolor import colored

def audit_knowledge_base():
    # 1. Setup
    print(colored("Initializing Audit System...", "cyan"))
    client = GeminiClient(api_key=Config.LLM_API_KEY, model=Config.LLM_MODEL)
    verifier = ExternalVerifier(client)
    
    concept_dir = "data/concepts"
    report = []
    
    files = [f for f in os.listdir(concept_dir) if f.endswith(".json")]
    print(colored(f"Found {len(files)} concepts to audit.\n", "cyan"))

    # 2. Loop
    for i, filename in enumerate(files):
        filepath = os.path.join(concept_dir, filename)
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                data = json.load(f)
                
            name = data.get('name', 'Unknown')
            type_ = data.get('type', 'Unknown')
            facets = data.get('facets', [])
            
            # Construct a "System Representation" to test
            # We simulate the system answering "What is X?"
            fact_str = f"{name} is a {type_}. "
            for facet in facets:
                fact_str += f"{facet.get('value', '')}. "
            
            print(f"[{i+1}/{len(files)}] Auditing '{name}'...", end="", flush=True)
            
            # 3. Verify
            # We ask the Verifier: "Is this representation accurate?"
            result = verifier.verify(f"What is {name}?", fact_str)
            
            score = result.get('score', 0)
            status = result.get('status', 'UNKNOWN')
            
            print(f" Score: {score}/10 ({status})")
            
            report.append({
                "file": filename,
                "name": name,
                "score": score,
                "status": status,
                "critique": result.get('missing_context', ''),
                "correction": result.get('correction', '')
            })
            
        except Exception as e:
            print(colored(f" ERROR: {e}", "red"))

    # 4. Final Summary
    print(colored("\n════════════════════ AUDIT REPORT ════════════════════", "white", attrs=['bold']))
    avg_score = sum(r['score'] for r in report) / len(report) if report else 0
    print(colored(f"Global Knowledge Quality Score: {avg_score:.1f}/10", "yellow"))
    
    print("\nTop 3 Weakest Concepts (Need /trust updates):")
    weakest = sorted(report, key=lambda x: x['score'])[:3]
    for w in weakest:
        print(f"1. {w['name']} (Score: {w['score']})")
        print(f"   Critique: {w['critique'][:100]}...")

    print("\nTop 3 Strongest Concepts:")
    strongest = sorted(report, key=lambda x: x['score'], reverse=True)[:3]
    for s in strongest:
        print(f"1. {s['name']} (Score: {s['score']})")

if __name__ == "__main__":
    audit_knowledge_base()
