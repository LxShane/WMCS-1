import os
import json
import re
from termcolor import colored
from system_b_llm.interfaces.gemini_client import GeminiClient
from config import Config

def audit_relations():
    concepts_dir = "data/concepts"
    files = [f for f in os.listdir(concepts_dir) if f.endswith(".json")]
    
    print(colored("SYSTEM: Initiating Deep Relation Audit...", "cyan"))
    
    client = GeminiClient(Config.LLM_API_KEY, Config.LLM_MODEL)
    
    # 1. Gather all Relations
    all_facts = []
    rel_pattern = re.compile(r"(.+?)\s+([A-Z_]+(?:_[A-Z]+)*)\s+(.+)")
    
    for filename in files:
        with open(os.path.join(concepts_dir, filename), 'r', encoding='utf-8') as f:
            data = json.load(f)
            
        source_name = data.get('name', 'Unknown')
        facets = data.get("facets", [])
        
        # Normalize
        facet_list = []
        if isinstance(facets, list): facet_list = facets
        elif isinstance(facets, dict):
            for v in facets.values():
                if isinstance(v, list): facet_list.extend(v)
                
        for facet in facet_list:
            if not isinstance(facet, dict): continue
            val = facet.get('value', '')
            match = rel_pattern.match(val)
            if match:
                subj, rel, obj = match.groups()
                # We only audit facts where the Subject matches the File Concept
                # to avoid auditing the same fact twice (or facts not claimed by this block)
                if subj.lower() == source_name.lower():
                    all_facts.append((filename, val))
                    
    print(colored(f"Found {len(all_facts)} relations to verify.\n", "cyan"))

    # 2. Verify with LLM
    issues = []
    
    for i, (fname, fact) in enumerate(all_facts):
        # Batching could be faster, but per-fact is safer for accuracy
        print(f"[{i+1}/{len(all_facts)}] Verifying: {fact}...", end="", flush=True)
        
        sys_prompt = "You are a Logic Auditor. Verify if the statement is semantically TRUE or FALSE."
        user_prompt = f"""
        Statement: "{fact}"
        
        Rules:
        - "Breed IS_A Dog" is FALSE (Breed is a Category, Poodle is a Dog).
        - "Dog IS_A Mammal" is TRUE.
        - "Photon IS_A Wave" is TRUE (in some contexts).
        
        Output format: TRUE or FALSE | Reason
        """
        
        response = client.completion(sys_prompt, user_prompt).strip()
        
        is_valid = "TRUE" in response.upper().split("|")[0]
        
        if is_valid:
            print(colored(" OK", "green"))
        else:
            print(colored(f" FAIL -> {response}", "red"))
            issues.append({
                "file": fname,
                "fact": fact,
                "reason": response
            })
            
    # 3. Report
    print(colored("\n════════════ AUDIT REPORT ════════════", "white", attrs=['bold']))
    if not issues:
        print(colored("All relations passed verification.", "green"))
    else:
        print(colored(f"Found {len(issues)} logic errors:", "red"))
        for issue in issues:
            print(f"File: {issue['file']}")
            print(f"  Fact: {issue['fact']}")
            print(f"  Critique: {issue['reason']}")
            print("-" * 40)
            
if __name__ == "__main__":
    audit_relations()
