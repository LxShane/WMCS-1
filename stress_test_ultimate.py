from main import WMCS_Kernel
from termcolor import colored
import time

def stress_test_ultimate():
    print(colored("\n╔═══ ULTIMATE STRESS TEST: SPATIAL REASONING ═══╗", "magenta", attrs=['bold']))
    
    kernel = WMCS_Kernel()
    kernel.load_data()
    
    # 1. Ensure Data Exists
    target = "Secondary_Immune_Response"
    if not kernel.block_exists(target):
         # Try loading forcefully if not found
         kernel.load_data(force=True)
         
    # 2. Complex Spatial Query
    query = "Describe the spatial location and connections of the Secondary Immune Response."
    
    print(colored(f"\nQuery: {query}", "cyan"))
    print(colored("Running Cognitive Loop...", "yellow"))
    
    start = time.time()
    response = kernel.process_query(query)
    end = time.time()
    
    print(colored(f"\nTime: {end-start:.2f}s", "green"))
    print(colored(f"Response:\n{response}", "white", attrs=['bold']))
    
    # 3. Validation Logic
    # Handle Response Object potential structure
    if isinstance(response, dict):
        # Taking a guess at the key based on main.py usually returning Contract or Dict
        # If it returns a Contract object, it might have .content or similar?
        # Actually process_query returns 'response' which is from generator.generate().
        # generator.generate returns STR.
        # Wait, why did it say 'dict has no attribute lower'?
        # Maybe response IS a dict? Let's print type.
        response_text = str(response)
    else:
        response_text = response
        
    score = 0
    response_lower = response_text.lower()
    if "spleen" in response_lower: score += 1
    if "lymph" in response_lower: score += 1
    if "systemic" in response_lower or "body" in response_lower: score += 1
    
    print(colored("\n--- Grading ---", "cyan"))
    if score >= 3:
        print(colored("[PASS] System harnessed full spatial potential.", "green"))
    elif score > 0:
        print(colored(f"[PARTIAL] System mentioned some details ({score}/3).", "yellow"))
    else:
        print(colored("[FAIL] System gave a generic/lazy answer.", "red"))

if __name__ == "__main__":
    stress_test_ultimate()
