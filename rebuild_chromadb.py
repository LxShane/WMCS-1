"""
Rebuild ChromaDB v2 - Uses filename as unique ID to avoid duplicates
"""
import json
import os
import chromadb
from chromadb.utils import embedding_functions
from termcolor import colored

print(colored("=== CHROMADB REBUILD v2 ===", "magenta", attrs=['bold']))

# 1. Create fresh ChromaDB
print("\n1. Creating fresh ChromaDB...")
client = chromadb.PersistentClient(path="data/chroma_db")

try:
    client.delete_collection("wmcs_concepts")
    print("   Deleted old collection")
except:
    pass

try:
    ef = embedding_functions.DefaultEmbeddingFunction()
    print("   Using SentenceTransformer embeddings")
except Exception as e:
    print(f"   Warning: {e}")
    ef = None

collection = client.get_or_create_collection(
    name="wmcs_concepts",
    embedding_function=ef,
    metadata={"hnsw:space": "cosine"}
)

# 2. Batch process all files
print("\n2. Processing concepts...")
concept_dir = "data/concepts"
files = sorted([f for f in os.listdir(concept_dir) if f.endswith('.json')])
print(f"   Found {len(files)} files")

batch_size = 100  # Smaller batches for stability
documents = []
metadatas = []
ids = []
processed = 0
errors = 0

for i, fname in enumerate(files):
    try:
        with open(os.path.join(concept_dir, fname), 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        name = data.get('name', fname.replace('.json', ''))
        definition = data.get('surface_layer', {}).get('definition', '')
        text = f"Concept: {name}. {definition}"
        
        for c in data.get('claims', [])[:3]:
            text += f" {c.get('predicate', '')}: {c.get('object', '')}."
        
        # Use FILENAME as unique ID (guaranteed unique)
        doc_id = fname.replace('.json', '')
        
        documents.append(text)
        metadatas.append({
            'name': name,
            'group': data.get('id', {}).get('group', 0),
            'item': data.get('id', {}).get('item', 0),
            'type': data.get('type', 'UNKNOWN')
        })
        ids.append(doc_id)
        
        if len(documents) >= batch_size:
            collection.upsert(documents=documents, metadatas=metadatas, ids=ids)
            processed += len(documents)
            print(f"   Progress: {processed}/{len(files)} ({100*processed//len(files)}%)")
            documents, metadatas, ids = [], [], []
            
    except Exception as e:
        errors += 1
        if errors <= 5:
            print(f"   Error in {fname}: {str(e)[:50]}")

# Final batch
if documents:
    collection.upsert(documents=documents, metadatas=metadatas, ids=ids)
    processed += len(documents)

print(f"\n3. Complete!")
print(f"   Processed: {processed}")
print(f"   Errors: {errors}")
print(f"   Collection count: {collection.count()}")

# 4. Test
print("\n4. Testing search...")
results = collection.query(query_texts=["cat"], n_results=5)
print(f"   'cat' query returned {len(results['ids'][0])} results:")
for i, uid in enumerate(results['ids'][0][:5]):
    print(f"     - {uid}")

print(colored("\n=== DONE ===", "green", attrs=['bold']))
