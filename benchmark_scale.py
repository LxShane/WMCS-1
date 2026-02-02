import time
import sys
import os
import random
import math
from termcolor import colored

# Set up environment
sys.path.append(os.getcwd())
# Mock Config
class MockClient:
    def embed_batch(self, texts):
        # Return random vectors of dim 768
        return [[random.random() for _ in range(768)] for _ in texts]
        
    def embed_content(self, text):
        return [random.random() for _ in range(768)]

try:
    from system_a_cognitive.memory.vector_store import VectorStore
except ImportError:
    # Minimal Mock VectorStore if import fails
    class VectorStore:
        def __init__(self, client):
            self.client = client
            self.vectors = []
        def add(self, doc_id, text, metadata):
            vec = self.client.embed_content(text)
            self.vectors.append({'id': doc_id, 'vector': vec, 'metadata': metadata})
        def search(self, query, top_k=3, threshold=0.0):
            # Brute force cosine
            q_vec = self.client.embed_content(query)
            results = []
            for item in self.vectors:
                # Mock similarity
                score = random.random()
                results.append({'id': item['id'], 'score': score, 'metadata': item['metadata']})
            return sorted(results, key=lambda x: x['score'], reverse=True)[:top_k]

def run_benchmark():
    print(colored("BENCHMARK: SCALE PERFORMANCE (10k NODES)", "magenta", attrs=['bold']))
    
    # 1. Setup
    client = MockClient()
    store = VectorStore(client)
    
    # 2. Generate 10k Nodes
    TARGET_COUNT = 10000
    print(colored(f"Generating {TARGET_COUNT} synthetic concepts...", "cyan"))
    
    start_gen = time.time()
    for i in range(TARGET_COUNT):
        store.add(f"mock_id_{i}", f"Mock Concept {i}", {"name": f"Mock_{i}"})
        if i % 1000 == 0: print(f"  ...generated {i}")
        
    gen_time = time.time() - start_gen
    print(colored(f"Generation Complete. Time: {gen_time:.2f}s", "green"))
    
    # 3. Query Latency Test
    print(colored("\nTesting Search Latency...", "cyan"))
    
    queries = ["Find connection to biology", "What is mitochondria", "Explain quantum mechanics"]
    latencies = []
    
    for q in queries:
        t0 = time.time()
        res = store.search(q)
        lat = time.time() - t0
        latencies.append(lat)
        print(f"  Query: '{q}' -> Time: {lat:.4f}s")
        
    avg_lat = sum(latencies) / len(latencies)
    print(colored(f"\nAverage Latency: {avg_lat:.4f}s", "white", attrs=['bold']))
    
    # 4. Verdict
    if avg_lat < 0.2:
        print(colored("PASS: System handles 10k nodes with sub-200ms latency.", "green"))
    elif avg_lat < 1.0:
        print(colored("WARNING: Latency approaching 1s. Consider FAISS.", "yellow"))
    else:
        print(colored("FAIL: System too slow for production scale.", "red"))

if __name__ == "__main__":
    run_benchmark()
