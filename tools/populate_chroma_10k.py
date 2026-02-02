import sys
import os
import random
import time
from termcolor import colored

# Path hack
sys.path.append(os.getcwd())
from system_a_cognitive.memory.chroma_store import ChromaStore

def populate_10k():
    print(colored("Generating 10k Synthetic Chemical Concepts into ChromaDB...", "cyan"))
    store = ChromaStore()
    
    # 0. Clean slate?
    # store.reset() 
    
    start_time = time.time()
    
    batch_docs = []
    batch_metas = []
    batch_ids = []
    
    BATCH_SIZE = 500
    TOTAL = 10000
    
    properties = ["Radioactive", "Inert", "Metallic", "Liquid", "Gas", "Toxic", "Noble"]
    colors = ["Red", "Silver", "Colorless", "Blue", "Gold"]
    
    for i in range(TOTAL):
        # Create unique ID (Group 100, Item i)
        doc_id = f"100,{i}"
        name = f"Element-{i}"
        
        # Synthetic Content
        prop = random.choice(properties)
        col = random.choice(colors)
        atomic_mass = 10 + (i * 0.5)
        
        text_content = f"Concept: {name}. Claims: property: {prop}. color: {col}. atomic_mass: {atomic_mass}."
        
        batch_docs.append(text_content)
        batch_metas.append({"name": name, "group": 100, "item": i, "property": prop})
        batch_ids.append(doc_id)
        
        # Batch Upsert
        if len(batch_ids) >= BATCH_SIZE:
            store.collection.upsert(
                documents=batch_docs,
                metadatas=batch_metas,
                ids=batch_ids
            )
            print(f"  > Pushed batch {i+1}/{TOTAL}")
            batch_docs = []
            batch_metas = []
            batch_ids = []
            
    # Push remaining
    if batch_ids:
        store.collection.upsert(documents=batch_docs, metadatas=batch_metas, ids=batch_ids)

    duration = time.time() - start_time
    print(colored(f"\nSUCCESS: Ingested {TOTAL} items in {duration:.2f}s", "green"))
    print(f"Total Database Size: {store.count()} concepts")

if __name__ == "__main__":
    populate_10k()
