import sys
import os
import json
from termcolor import colored

sys.path.append(os.getcwd())
try:
    from main import WMCS_Kernel
except ImportError:
    sys.path.append(os.path.join(os.getcwd(), '..'))
    from main import WMCS_Kernel

def deep_check():
    print(colored("=== DEEP SYSTEM DIAGNOSTIC ===", "cyan"))
    
    # 1. Inspect File System
    print(colored("\n[1] Checking File System...", "yellow"))
    if os.path.exists("data/concepts/cat.json"):
        print(colored("  > cat.json FOUND.", "green"))
    else:
        print(colored("  > cat.json MISSING!", "red"))

    # 2. Inspect Vector DB
    print(colored("\n[2] Checking Vector Database (Chroma)...", "yellow"))
    kern = WMCS_Kernel()
    res = kern.vector_store.search("cat")
    if res and len(res) > 0:
        print(colored(f"  > Found {len(res)} matches.", "green"))
        print(f"  > Top Match: {res[0]['name']} (Score: {res[0]['score']})")
        if "cat" not in res[0]['name'].lower():
             print(colored("  > WARNING: Top match is not 'Cat'!", "magenta"))
    else:
        print(colored("  > NO MATCHES FOUND IN DB!", "red"))

    # 3. Simulate Logic Flow
    print(colored("\n[3] Simulating 'process_query('whats a cat')'...", "yellow"))
    
    # Manually step through to see where it breaks
    query = "whats a cat"
    
    # Step A: Retrieval
    print("  > Retrieving context (Manually via vector_store)...")
    hits = kern.vector_store.search(query, top_k=3, threshold=0.45)
    context = []
    
    for hit in hits:
        name = hit['metadata'].get('name', '').lower()
        if name in kern.blocks:
            block = kern.blocks[name]
            print(colored(f"    - Found Entry: {block['name']} (Score: {hit['score']:.2f})", "green"))
            
            # Format like main.py
            content_dump = {
                "claims": block.get("claims", []),
                "facets": block.get("facets", {})
            }
            context_str = f"Concept: {block['name']} (ID: {block.get('id')}). Content: {json.dumps(content_dump, default=str)}"
            context.append(context_str)
            
    print(f"  > Context Size: {len(context)}")
    if len(context) == 0:
        print(colored("  > FATAL: Context is empty!", "red"))
    
    # Step B: Logic
    print("  > Reasoning (Simulating LLM Logic Synthesis)...")
    # Simulate the logic synthesis step from main.py
    found_info = context # Rename for clarity
    
    # We skip the specific Logic Synthesis LLM call for the diagnostic to save time/tokens, 
    # and just assume a basic synthesis or pass the facts directly.
    # In main.py: combinad_context = found_info + [f"Logic Synthesis: ..."]
    
    combined_context = found_info + ["Logic Synthesis: Validated by Deep Check."]
    
    print("  > Generating Contract (Epistemic Gate)...")
    contract = kern.gate.generate_contract(
        confidence=0.8 if found_info else 0.1, 
        assumptions=combined_context,
        positive_assertions=["Use the internal knowledge."], 
        negative_assertions=[]
    )
    print(f"  > Contract MUST SAY: {contract.can_assert}")
    
    if not contract.can_assert:
        print(colored("  > WARNING: Contract is empty. LLM will likely say nothing.", "magenta"))

    # Step C: Generation
    print("  > Generating Response (LLM)...")
    # We call the generator directly to check the prompt
    from system_b_llm.generators.response_generator import ResponseGenerator
    gen = ResponseGenerator(kern.llm_client)
    
    # Using the exact code from main.py logic
    # intent must be an object or dict as per main.py
    intent = {'raw_query': query}
    response = gen.generate(contract, intent)
    
    print(colored("\n[4] FINAL RAW RESPONSE:", "cyan"))
    print(response)
    print(colored(f"Type: {type(response)}", "cyan"))
    
    if response == "[]" or response == []:
        print(colored("\nFAILED: Response is empty list!", "red"))
    else:
        print(colored("\nPASSED: Response is a string.", "green"))

if __name__ == "__main__":
    deep_check()
