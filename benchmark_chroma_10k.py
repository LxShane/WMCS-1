import time
import sys
import os
from termcolor import colored

sys.path.append(os.getcwd())
from main import WMCS_Kernel

def benchmark_chroma():
    print(colored("BENCHMARK: CHROMA DB (10k REAL ITEMS)", "magenta", attrs=['bold']))
    
    # 1. Startup
    t0 = time.time()
    kernel = WMCS_Kernel()
    kernel.load_data()
    t_startup = time.time() - t0
    print(f"Startup Time: {t_startup:.2f}s")
    
    # 2. Check Count
    count = kernel.vector_store.count()
    print(colored(f"Database Size: {count} concepts", "white"))
    
    if count < 10000:
        print(colored("WARNING: Database not fully populated yet.", "yellow"))
    else:
        print(colored("PASS: 10k items present.", "green"))
        
    # 3. Query Latency
    queries = [
        "What is Element-5000?",
        "List radioactive elements",
        "red thing with high mass"
    ]
    
    latencies = []
    for q in queries:
        t_start = time.time()
        # Direct vector search for speed test (bypassing full reasoning for pure DB bench)
        results = kernel.vector_store.search(q, top_k=5)
        lat = time.time() - t_start
        latencies.append(lat)
        print(f"  Query: '{q}' -> Found {len(results)} results in {lat:.4f}s")
        for r in results:
             print(f"    - {r.get('name')}")
             
    avg = sum(latencies) / len(latencies)
    print(colored(f"\nAverage Vector Latency: {avg:.4f}s", "cyan", attrs=['bold']))
    
    if avg < 0.05: # Chroma HNSW should be < 50ms
        print(colored("RESULT: S-RECOVERY (Instant)", "green"))
    elif avg < 0.20:
        print(colored("RESULT: PRODUCTION ACCEPTABLE", "green"))
    else:
        print(colored("RESULT: SLOW (Check Optimization)", "red"))

if __name__ == "__main__":
    benchmark_chroma()
