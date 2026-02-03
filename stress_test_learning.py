
import sys
import os
import json
import time
from termcolor import colored
from main import WMCS_Kernel

# Topics designed to be diverse: History, Biology, Engineering
TOPICS = [
    "Explain the tactics used in the Great Emu War of 1932.",
    "How does ZAP-70 protein contribute to T-cell signaling?",
    "Describe the construction techniques of the Pantheon dome in Rome."
]

def analyze_result(topic, result, initial_file_count, final_file_count, visited):
    print(colored(f"\n--- ANALYSIS FOR: '{topic}' ---", "yellow"))
    
    # 1. Did we learn?
    new_files = final_file_count - initial_file_count
    if new_files > 0:
        print(colored(f"[PASS] Active Learning Triggered. Ingested {new_files} new Concept Blocks.", "green"))
    else:
        print(colored(f"[WARN] No new files created. System might be lazy or topic already known.", "red"))

    # 2. Did we use the knowledge?
    if len(visited) > 0:
        print(colored(f"[PASS] Logic Engine utilized {len(visited)} memory nodes.", "green"))
    else:
        print(colored(f"[FAIL] Logic Engine visited 0 nodes. Reasoning might be hallucinated.", "red"))

    # 3. Output Check
    response_len = len(result.get('text', ''))
    if response_len > 100:
        print(colored(f"[PASS] Detailed Response Generated ({response_len} chars).", "green"))
    else:
        print(colored(f"[WARN] Response suspiciously short: '{result.get('text','')}'", "yellow"))

def run_stress_test():
    print(colored("### STARTING MULTI-DOMAIN LEARNING STRESS TEST ###", "magenta", attrs=['bold']))
    
    kernel = WMCS_Kernel()
    kernel.load_data()
    
    initial_total_files = len(kernel.file_map)
    print(colored(f"Initial Knowledge Base Size: {initial_total_files} Concepts.", "cyan"))
    
    for i, topic in enumerate(TOPICS):
        print(colored(f"\n\n==================================================", "white"))
        print(colored(f"TEST CASE {i+1}: {topic}", "cyan", attrs=['bold']))
        print(colored(f"==================================================", "white"))
        
        # Snapshot before
        count_before = len(kernel.file_map)
        
        # EXECUTE
        # We assume main.py handles the reflex loop internally now
        start_time = time.time()
        result = kernel.process_query(topic, allow_research=True)
        duration = time.time() - start_time
        
        # Snapshot after (Refresh file map since Ingestor adds files to disk)
        # Note: kernel.file_map might be updated in memory, but let's verify disk for rigour
        # Actually kernel.file_map is updated by _trigger_reflex hot-loading
        count_after = len(kernel.file_map)
        
        print(colored(f"\nTime Taken: {duration:.2f}s", "blue"))
        
        # ANALYZE
        analyze_result(topic, result, count_before, count_after, result.get('visited_nodes', []))
        
        print("\nFinal Output Snapshot:")
        print(colored(result['text'][:300] + "...", "white"))

if __name__ == "__main__":
    run_stress_test()
