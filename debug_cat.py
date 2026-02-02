import sys
import os
import json
from termcolor import colored

# Path Hack
sys.path.append(os.getcwd())
try:
    from main import WMCS_Kernel
except ImportError:
    sys.path.append(os.path.join(os.getcwd(), '..'))
    from main import WMCS_Kernel

def debug_cat():
    print(colored("DEBUGGING CONCEPT: CAT", "magenta"))
    
    # 1. Initialize Kernel
    wmcs = WMCS_Kernel()
    
    # 2. Check JSON
    json_path = "data/concepts/cat.json"
    if os.path.exists(json_path):
        print(colored(f"[OK] Found {json_path}", "green"))
    else:
        print(colored(f"[FAIL] Missing {json_path}", "red"))

    # 3. Check Chroma
    print(colored("Checking ChromaDB...", "cyan"))
    results = wmcs.vector_store.search("cat")
    found_in_chroma = False
    for res in results:
        print(f"  - Found: {res['name']} (Score: {res.get('score', 'N/A')})")
        if 'cat' in res['name'].lower():
            found_in_chroma = True
            
    if not found_in_chroma:
        print(colored("[FAIL] 'cat' not found in Chroma Index! (Stale Index)", "red"))
        
        # FIX IT: Force add
        if os.path.exists(json_path):
            print(colored("  > Force-indexing cat.json...", "yellow"))
            with open(json_path, 'r') as f:
                data = json.load(f)
            # Create a simple text repr
            text = f"Concept: {data['name']}. Type: {data.get('type','Object')}. Claims: "
            for c in data.get('claims', []):
                text += f"{c.get('predicate')} {c.get('object')}. "
            
            # Upsert
            wmcs.vector_store.add(
                doc_id=f"{data.get('id',{}).get('group',0)},{data.get('id',{}).get('item',0)}",
                text=text,
                metadata={"name": data['name'], "group": data.get('id',{}).get('group',0)}
            )
            print(colored("  > Indexed.", "green"))
    else:
        print(colored("[OK] 'cat' is in Chroma.", "green"))

    # 4. Run Query logic
    print(colored("\nRunning process_query('whats a cat')...", "cyan"))
    response = wmcs.process_query("whats a cat", allow_research=False)
    
    print(colored(f"Raw Response Type: {type(response)}", "yellow"))
    print(colored(f"Raw Response Value: {repr(response)}", "yellow"))

if __name__ == "__main__":
    debug_cat()
