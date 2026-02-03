import time
from system_a_cognitive.memory.chroma_store import ChromaStore
from termcolor import colored

def benchmark():
    print(colored("Starting Speed Benchmark...", "cyan"))
    
    # 1. Measure Init Time
    t0 = time.time()
    store = ChromaStore()
    t1 = time.time()
    print(f"Initialization Time: {(t1-t0)*1000:.2f} ms")
    
    queries = [
        "What is a biological cell?",
        "Photosynthesis mechanism",
        "Printing press history",
        "Atomic structure of gold",
        "Spatial location of the heart"
    ]
    
    # 2. Warmup
    store.search("warmup")
    
    # 3. Measure Search Speed
    total_time = 0
    print("\n--- Search Latency ---")
    for q in queries:
        start = time.time()
        results = store.search(q, top_k=5)
        end = time.time()
        dur = (end - start) * 1000
        total_time += dur
        print(f"Query: '{q}' -> {len(results)} hits in {dur:.2f} ms")
        
    avg = total_time / len(queries)
    print(colored(f"\nAverage Search Time: {avg:.2f} ms", "green", attrs=['bold']))
    print(colored(f"Items in Index: {store.count()}", "yellow"))

if __name__ == "__main__":
    benchmark()
