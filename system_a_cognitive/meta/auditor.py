import os
import json
import re
from termcolor import colored
from system_b_llm.interfaces.gemini_client import GeminiClient
from config import Config

class RelationAuditor:
    """
    Audits the Semantic Validity of Knowledge Graph Relations using Web Search Grounding.
    """
    def __init__(self, concepts_dir="data/concepts"):
        self.concepts_dir = concepts_dir
        # Initialize standard client if not provided
        self.client = GeminiClient(Config.LLM_API_KEY, Config.LLM_MODEL)

    def audit(self, interactive=True):
        files = [f for f in os.listdir(self.concepts_dir) if f.endswith(".json")]
        
        if interactive:
            print(colored("SYSTEM: Initiating Deep Relation Audit (Web-Grounded)...", "cyan"))
        
        # 1. Gather all Relations AND Structure Specs
        all_facts = []
        structure_checks = []
        rel_pattern = re.compile(r"(.+?)\s+([A-Z_]+(?:_[A-Z]+)*)\s+(.+)")
        
        for filename in files:
            filepath = os.path.join(self.concepts_dir, filename)
            try:
                with open(filepath, 'r', encoding='utf-8') as f:
                    data = json.load(f)
            except Exception as e:
                print(f"Skipping corrupt file {filename}: {e}")
                continue
                
            source_name = data.get('name', 'Unknown')
            ctype = data.get('type', 'UNKNOWN')
            cid_group = data.get('id', {}).get('group', 0)
            
            # Structural Audit: Check ID vs Type
            expected_group_range = None
            if ctype in ["LIVING_SYSTEM", "INANIMATE_OBJECT", "PHYSICAL_OBJECT", "SUBSTANCE"]:
                expected_group_range = range(20, 60) # Physical
            elif ctype == "MATHEMATICAL_OBJECT":
                expected_group_range = range(40, 50)
            elif ctype == "ABSTRACT_CONCEPT":
                expected_group_range = range(50, 60)
            elif ctype == "SOCIAL_CONSTRUCT":
                expected_group_range = range(60, 70)
                
            if expected_group_range and cid_group not in expected_group_range:
                # Flag structural error
                 structure_checks.append({
                     "file": filename,
                     "name": source_name,
                     "current_type": ctype,
                     "current_group": cid_group
                 })

            facets = data.get("facets", [])
            
            # Normalize list/dict
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
                    if subj.lower() == source_name.lower():
                        all_facts.append((filename, val))
                        
        if interactive:
            print(colored(f"Found {len(all_facts)} relations and {len(structure_checks)} structural issues to verify.\n", "cyan"))

        issues = []
        
        # 1.5 Process Structural Issues First
        for issue in structure_checks:
            if interactive:
                print(colored(f"\n  [STRUCTURAL FAIL] {issue['name']} (Type: {issue['current_type']}, ID Group: {issue['current_group']})", "red"))
                print(colored(f"  > Suggestion: UPDATE_ID based on Type", "yellow"))
            issues.append({
                "file": issue['file'],
                "fact": "STRUCTURAL_MISMATCH",
                "action": "UPDATE_ID",
                "correction": str(issue['current_type']), # Pass type as param
                "reason": f"ID Group {issue['current_group']} does not match Type {issue['current_type']}"
            })

        # 2. Verify Relations with LLM (Search Enabled)
        for i, (fname, fact) in enumerate(all_facts):
            if interactive:
                print(f"\r[{i+1}/{len(all_facts)}] Verifying: {fact[:50]}...", end="", flush=True)
            
            sys_prompt = "You are a Logic Class Validator. Verify if the statement is Semantically Valid."
            user_prompt = f"""
            Fact: "{fact}"
            
            Determine if this fact is SEMANTICALLY VALID and FACTUALLY TRUE.
            
            Options:
            - VALID
            - INVALID | DELETE
            - INVALID | REPLACE | <New Fact>
            
            Examples:
            - "Breed IS_A Dog" -> INVALID | DELETE
            - "Dog IS_A Mammal" -> VALID
            - "Photon HAS_PART Rest Mass" -> INVALID | DELETE
            - "Fire CAUSES Heat" -> VALID
            - "Rain PREVENTS Fire" -> VALID
            
            Output format: Status | Action | Correction | Reason
            
            IMPORTANT: You MUST output all 4 parts separated by pipes '|'.
            If a field is not applicable, use "N/A".
            
            Examples of Valid Outputs:
            - VALID | N/A | N/A | Relation aligns with standard physics.
            - INVALID | DELETE | N/A | Photons are elementary particles, not composites.
            - INVALID | REPLACE | Dog IS_A Mammal | 'Animal' is too broad; 'Mammal' is more precise.
            """
            
            # Use WEB SEARCH for grounding
            response = self.client.completion_with_search(sys_prompt, user_prompt).strip()
            
            # Parsing response
            parts = [p.strip() for p in response.split('|')]
            # Ensure we have enough parts
            while len(parts) < 4: parts.append("N/A")
            
            status = parts[0].upper()
            action = parts[1]
            correction = parts[2]
            reason = parts[3]
            
            if "INVALID" in status:
                if interactive:
                    print(colored(f"\n  [FAIL] {fact}", "red"))
                    print(colored(f"  > Suggestion: {action} {correction if correction != 'N/A' else ''}", "yellow"))
                    print(colored(f"  > Reason: {reason}", "magenta"))
                
                issues.append({
                    "file": fname,
                    "fact": fact,
                    "action": action,
                    "correction": correction if correction != 'N/A' else "",
                    "reason": reason
                })
        
        if interactive:
            print("\n")
            # 3. Report & Fix
            print(colored("════════════ AUDIT REPORT ════════════", "white", attrs=['bold']))
            if not issues:
                print(colored("STATUS: GREEN (All relations valid)", "green"))
            else:
                print(colored(f"STATUS: RED ({len(issues)} logic errors found)", "red"))
                
                # Auto-Correction Logic
                confirm = input(colored(f"Apply {len(issues)} fixes? (y/n): ", "yellow")).lower()
                if confirm == 'y':
                    self.apply_fixes(issues)
        
        return issues

    def apply_fixes(self, issues):
        print(colored("Applying fixes...", "cyan"))
        for issue in issues:
            filepath = os.path.join(self.concepts_dir, issue['file'])
            fact_to_remove = issue['fact']
            action = issue['action']
            new_fact = issue['correction']
            
            try:
                with open(filepath, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                
                modified = False

                if action == "UPDATE_ID":
                    # Smart ID Re-assignment
                    ctype = new_fact # We passed type as 'correction'
                    import random
                    new_group = 99
                    if ctype == "ABSTRACT_CONCEPT": new_group = 50
                    elif ctype == "SOCIAL_CONSTRUCT": new_group = 60
                    elif ctype == "MATHEMATICAL_OBJECT": new_group = 40
                    elif ctype in ["LIVING_SYSTEM", "INANIMATE_OBJECT"]: new_group = 21
                    
                    if "id" not in data: data["id"] = {}
                    old_group = data["id"].get("group")
                    data["id"]["group"] = new_group
                    data["autocorrected"] = True
                    modified = True
                    print(f"  [STRUCTURE_FIX] {issue['file']}: Group {old_group} -> {new_group}")

                else:
                    # Relation Fixes
                    original_facets = data.get("facets", [])
                    
                    # Helper to process list
                    def clean_list(flist):
                        new_list = []
                        changed = False
                        for existing in flist:
                            # We match by value
                            if existing.get('value') == fact_to_remove:
                                changed = True
                                # If replace, append new
                                if action == "REPLACE" and new_fact:
                                    # Keep type, change value
                                    replacement = existing.copy()
                                    replacement['value'] = new_fact
                                    replacement['auto_generated'] = True
                                    new_list.append(replacement)
                            else:
                                new_list.append(existing)
                        return new_list, changed

                    if isinstance(original_facets, list):
                        new_facets, changed = clean_list(original_facets)
                        if changed:
                            data['facets'] = new_facets
                            modified = True
                    elif isinstance(original_facets, dict):
                        for lens, content in original_facets.items():
                            if isinstance(content, list):
                                new_list, changed = clean_list(content)
                                if changed:
                                    original_facets[lens] = new_list
                                    modified = True
                        data['facets'] = original_facets

                if modified:
                    with open(filepath, 'w', encoding='utf-8') as f:
                        json.dump(data, f, indent=2)
                    if action != "UPDATE_ID":
                        print(f"  [FIXED] {issue['file']} ({action})")
                else:
                    if action != "UPDATE_ID":
                         print(f"  [SKIPPED] Could not find exact match in {issue['file']}")
                    
            except Exception as e:
                print(f"  [ERROR] Failed to fix {issue['file']}: {e}")
                
        print(colored("System Logic Repaired.", "green"))

if __name__ == "__main__":
    auditor = RelationAuditor()
    auditor.audit(interactive=True)
