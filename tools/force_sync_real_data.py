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

def force_sync():
    print(colored("FORCE SYNC: Ingesting ALL real JSON files into Chroma...", "magenta"))
    kernel = WMCS_Kernel() # Connects to DB
    
    concepts_dir = "data/concepts"
    count = 0
    
    for root, dirs, files in os.walk(concepts_dir):
        for file in files:
            if file.endswith(".json"):
                path = os.path.join(root, file)
                try:
                    with open(path, 'r', encoding='utf-8') as f:
                        data = json.load(f)
                    
                    # Construct Text
                    name = data.get('name', 'Unknown')
                    # Basic claims text
                    claims_text = ""
                    for c in data.get('claims', []):
                        claims_text += f"{c.get('predicate', 'is')} {c.get('object', '')}. "
                    
                    full_text = f"Concept: {name}. Type: {data.get('type')}. {claims_text}"
                    
                    # ID
                    grp = data.get('id', {}).get('group', 99)
                    itm = data.get('id', {}).get('item', 0)
                    doc_id = f"{grp},{itm}"
                    
                    # Upsert
                    kernel.vector_store.add(
                        doc_id=doc_id,
                        text=full_text,
                        metadata={"name": name, "group": grp}
                    )
                    print(f"  Indexed: {name} ({doc_id})")
                    count += 1
                except Exception as e:
                    print(colored(f"  Error on {file}: {e}", "red"))

    print(colored(f"\n[SUCCESS] Force-synced {count} real files.", "green"))

if __name__ == "__main__":
    force_sync()
