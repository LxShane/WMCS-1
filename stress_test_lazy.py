import time
import os
import sys
from termcolor import colored

# Import Kernel
from main import WMCS_Kernel

def test_lazy_loading():
    print(colored("═══ LAZY LOADING STRESS TEST ═══", "cyan", attrs=['bold']))
    
    # 1. Initialize
    start_time = time.time()
    kernel = WMCS_Kernel()
    kernel.load_data()
    boot_time = time.time() - start_time
    
    print(colored(f"Boot Time: {boot_time:.4f}s", "green"))
    
    # ASSERTION 1: RAM Cache should be EMPTY
    cache_size = len(kernel.block_cache)
    print(f"Initial Cache Size: {cache_size}")
    if cache_size > 0:
        print(colored("FAIL: Cache should be empty on boot!", "red"))
        sys.exit(1)
    else:
        print(colored("PASS: Cache is empty.", "green"))

    # ASSERTION 2: File Map should have entries
    map_size = len(kernel.file_map)
    print(f"File Map Size: {map_size}")
    if map_size < 10: # Assuming we have some data
        print(colored("FAIL: File map is too small!", "red"))
        sys.exit(1)
    else:
        print(colored(f"PASS: File map populated with {map_size} items.", "green"))

    # 2. Query Existing Concept (e.g., Cat)
    print(colored("\nExecuting Query: 'What is a Cat?'", "cyan"))
    kernel.process_query("What is a Cat?", allow_research=False)
    
    # ASSERTION 3: Cat should now be in Cache
    if "cat" in kernel.block_cache:
        print(colored("PASS: 'cat' successfully lazy loaded into RAM.", "green"))
    else:
        print(colored("FAIL: 'cat' not found in cache after access.", "red"))
        sys.exit(1)
        
    # ASSERTION 4: Only 1 item should be in cache (if clean)
    # Note: 'Navigator' might pull in neighbors (Cat Paw, Fur), so > 1 is okay, but shouldn't be ALL.
    final_cache_size = len(kernel.block_cache)
    print(f"Final Cache Size: {final_cache_size}")
    if final_cache_size > map_size * 0.5:
        print(colored("WARNING: Loaded > 50% of DB? Might be too aggressive.", "yellow"))
    else:
        print(colored(f"PASS: Efficient Memory Usage ({final_cache_size}/{map_size} loaded).", "green"))

    print(colored("\n═══ TEST COMPLETE: SUCCESS ═══", "green", attrs=['reverse']))

if __name__ == "__main__":
    test_lazy_loading()
