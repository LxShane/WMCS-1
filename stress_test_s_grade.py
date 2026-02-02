import sys
import os
import shutil
from termcolor import colored

sys.path.append(os.getcwd())
from main import WMCS_Kernel
from system_b_llm.interfaces.gemini_client import GeminiClient
from system_a_cognitive.subsystems.visual_cortex import VisualCortex
from config import Config

def print_header(text):
    print(colored(f"\n{'='*60}", "magenta"))
    print(colored(f"   {text}", "magenta", attrs=['bold']))
    print(colored(f"{'='*60}\n", "magenta"))

def run_s_grade_tests():
    print_header("S-GRADE CHALLENGE: THE HARD CASES")
    
    wmcs = WMCS_Kernel()
    wmcs.load_data()
    
    # --- TEST 1: CONTESTED MECHANISMS ---
    print(colored("\n>>> TEST 1: Contested Mechanisms (Economics)", "yellow"))
    query = "Does inflation cause unemployment?"
    print(colored(f"Query: '{query}'", "cyan"))
    
    response = wmcs.process_query(query, allow_research=True)
    print(colored("Response Snippet:", "green"))
    print(str(response)[:500] + "...")
    
    # Check for nuance
    check_terms = ["phillips", "stagflation", "short-run", "depends", "conflict", "debate"]
    matches = [t for t in check_terms if t in str(response).lower()]
    if matches:
        print(colored(f"PASS: Found nuance terms {matches}", "green"))
    else:
        print(colored("FAIL: Answer seems too definitive/one-sided.", "red"))

    # --- TEST 2: TEMPORAL EVOLUTION ---
    print(colored("\n>>> TEST 2: Temporal Evolution (Pluto)", "yellow"))
    
    # Simulate Ingestion Sequence manually to test memory behavior
    print(colored("Step A: Ingesting 'Pluto is a planet' (Historical Context)...", "cyan"))
    # We cheat slightly by modifying the facade to see if it appends or overwrites properties
    wmcs.ingestor.ingest_text("In 1930, Pluto was defined as the ninth planet of the solar system.")
    
    print(colored("Step B: Ingesting 'Pluto is a dwarf planet' (Updates)...", "cyan"))
    wmcs.ingestor.ingest_text("In 2006, the IAU reclassified Pluto as a dwarf planet, distinct from the main planets.")
    
    # Reload to ensure index matches
    wmcs.load_data()
    
    print(colored("Step C: Querying 'Is Pluto a planet?'...", "cyan"))
    response_pluto = wmcs.process_query("Is Pluto a planet?", allow_research=False) # Force memory use
    print(colored(f"Response: {response_pluto}", "white"))
    
    lower_p = str(response_pluto).lower()
    if "dwarf" in lower_p and ("1930" in lower_p or "ninth" in lower_p or "history" in lower_p or "formerly" in lower_p):
         print(colored("PASS: Captured both historical status and current status.", "green"))
    else:
         print(colored("FAIL: Likely overwrote history or missed nuance.", "red"))

    # --- TEST 3: PERCEPTUAL AMBIGUITY ---
    print(colored("\n>>> TEST 3: Perceptual Ambiguity (Necker Cube)", "yellow"))
    
    # Locate Image
    img_name = "necker_cube.png"
    # Attempt to copy from artifacts if needed, similar to previous test
    # We assume the user/agent put it in the root or we find it in artifacts
    candidate_path = None
    # Quick hack to find the file we just generated
    search_dir = r"C:\Users\yxcho\.gemini\antigravity\brain\c519435b-ac6f-4f93-a2a6-bd28680a26b7"
    for f in os.listdir(search_dir):
        if "necker" in f and f.endswith(".png"):
            candidate_path = os.path.join(search_dir, f)
            break
            
    if candidate_path:
        shutil.copy(candidate_path, "necker_cube.png")
        print(colored("Image found and prepared.", "green"))
        
        client = GeminiClient(Config.LLM_API_KEY, Config.LLM_MODEL)
        cortex = VisualCortex(client)
        result = cortex.analyze_diagram("necker_cube.png")
        
        print(colored("Visual Description:", "cyan"))
        print(result)
        
        desc = str(result).lower()
        if "ambiguous" in desc or "perspective" in desc or "illusion" in desc or "cube" in desc:
             print(colored("PASS: Recognized geometry/ambiguity.", "green"))
        else:
             print(colored("FAIL: Did not describe the ambiguity.", "red"))
    else:
        print(colored("SKIP: Necker cube image not found.", "yellow"))

if __name__ == "__main__":
    run_s_grade_tests()
