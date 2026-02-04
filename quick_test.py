"""
WMCS Quick Test - Bypass slow sync using existing vector DB
"""
import json
import os
from config import Config
from system_b_llm.interfaces.gemini_client import GeminiClient
from system_a_cognitive.memory.chroma_store import ChromaStore
from system_a_cognitive.epistemic.gate import EpistemicGate
from system_b_llm.generators.response_generator import ResponseGenerator
from system_b_llm.parsers.query_parser import QueryParser

print("=== WMCS QUICK TEST (No Sync) ===\n")

# 1. Init components directly (skip slow ingest_all)
print("1. Initializing components...")
llm = GeminiClient(api_key=Config.LLM_API_KEY, model=Config.LLM_MODEL)
vector_store = ChromaStore()
parser = QueryParser(llm)
gate = EpistemicGate()
generator = ResponseGenerator(llm)

print(f"   Vector DB has {vector_store.count()} concepts")

# 2. File map (fast - just filenames)
file_map = {}
for fn in os.listdir('data/concepts'):
    if fn.endswith('.json'):
        file_map[fn.replace('.json', '')] = os.path.join('data/concepts', fn)
print(f"   Mapped {len(file_map)} concept files")

# 3. Simple query
query = "What is a cat?"
print(f"\n2. Testing query: '{query}'")

# Vector search
hits = vector_store.search(query, top_k=3)
print(f"   Found {len(hits)} semantic matches:")
for h in hits:
    print(f"     - {h['name']} (score: {h['score']:.3f})")

# Load actual blocks from disk
blocks = []
for h in hits:
    name = h['name'].lower().replace(' ', '_')
    if name in file_map:
        with open(file_map[name], 'r', encoding='utf-8') as f:
            blocks.append(json.load(f))
            
print(f"   Loaded {len(blocks)} blocks from disk")

# 4. LLM Reasoning
if blocks:
    context = []
    for b in blocks:
        context.append(f"Concept: {b.get('name')} - {b.get('surface_layer', {}).get('definition', 'N/A')}")
    
    prompt = f"""Based on these concepts:
{json.dumps(context, indent=2)}

Answer: {query}"""
    
    print(f"\n3. Asking LLM...")
    answer = llm.completion("You answer based only on provided facts.", prompt)
    
    print(f"\n=== RESPONSE ===\n{answer}")
else:
    print("   No blocks found, cannot generate response")
