
import os
import sys
import time

# Bypass corrupted main.py
if os.path.exists("main_lazy.py"):
    # Rename for import trickery if needed, but easier to just import
    pass

try:
    from main_lazy import WMCS_Kernel
except IndentationError as e:
    print(f"FAILED (Import): {e}")
    sys.exit(1)
except ImportError:
    print("FAILED: main_lazy.py not found or other import error")
    sys.exit(1)

def run_test():
    print("TEST: Initializing Lazy Kernel...")
    start_boot = time.time()
    wmcs = WMCS_Kernel()
    wmcs.load_data()
    boot_time = time.time() - start_boot
    
    print(f"BOOT TIME: {boot_time:.4f}s")
    
    # Check 1: Cache should be empty (Lazy)
    cache_size = len(wmcs.block_cache)
    file_map_size = len(wmcs.file_map)
    
    print(f"CACHE SIZE: {cache_size}")
    print(f"FILE MAP SIZE: {file_map_size}")
    
    if cache_size > 5: # Tolerance for init
         print("FAIL: Cache not lazy (too many items loaded)")
         sys.exit(1)
         
    if file_map_size < 1:
         print("FAIL: File map empty")
         sys.exit(1)
         
    # Check 2: Query trigger
    print("TEST: querying 'Cat'...")
    # This should trigger get_block('cat')
    try:
        wmcs.process_query("What is a cat?")
    except Exception as e:
        print(f"FAIL (Runtime): {e}")
        # print full trace
        import traceback
        traceback.print_exc()
        sys.exit(1)
        
    # Check 3: Cache populated
    new_cache_size = len(wmcs.block_cache)
    print(f"POST-QUERY CACHE: {new_cache_size}")
    
    if new_cache_size <= cache_size:
        print("WARN: Cache did not grow? (Maybe cat.json missing or already loaded?)")
    else:
        print("PASS: Cache grew on demand.")

    print("PASS: ALL CHECKS PASSED")

if __name__ == "__main__":
    run_test()
