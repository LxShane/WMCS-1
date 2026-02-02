import sys
import os
import json
from termcolor import colored

# Path Hack
sys.path.append(os.getcwd())
try:
    from main import WMCS_Kernel
except ImportError:
    sys.path.append(os.path.join(os.getcwd(), '..'))
    from main import WMCS_Kernel

def run_grand_test():
    print(colored("╔════════════════════════════════════════════════════╗", "magenta"))
    print(colored("║   GRAND UNIFIED SYSTEM TEST: 'Is a Virus Alive?'   ║", "magenta"))
    print(colored("╚════════════════════════════════════════════════════╝", "magenta"))
    
    wmcs = WMCS_Kernel()
    
    # 🌟 STEP 1: INGESTION (Conflicting & Structural Data) 🌟
    print(colored("\n[1] INGESTION: Planting the Seeds of Conflict...", "cyan"))
    
    # Fact A: Virology (Structural)
    wmcs.ingestor.ingest_text(
        "A Virus consists of genetic material (DNA or RNA) enclosed in a protein coat. It cannot reproduce on its own.", 
        source_name="Virology_Textbook_2023"
    )
    
    # Fact B: The "Alive" Argument
    wmcs.ingestor.ingest_text(
        "Some biologists argue that viruses are 'Alive' because they undergo evolution and natural selection.",
        source_name="Evolutionary_Biology_Paper_2019"
    )
    
    # Fact C: The "Dead" Argument
    wmcs.ingestor.ingest_text(
        "Most definitions of life require metabolism. Viruses lack metabolism, therefore they are 'Not Alive' (Inanimate Biological Entities).",
        source_name="Standard_Model_Biology"
    )
    
    # Force Sync to Chroma
    wmcs.load_data() 
    
    # 🌟 STEP 2: THE DEEP QUERY 🌟
    print(colored("\n[2] COGNITION: Executing Deep Query...", "cyan"))
    
    # We turn OFF 'allow_research' to force it to use ONLY what we taught it (Internal Validity Check)
    # OR we leave it ON to see if it fills gaps. Let's leave it ON.
    response = wmcs.process_query("Is a virus considered a living organism?", allow_research=True)
    
    print(colored("\n[3] FINAL OUTPUT:", "green"))
    print(colored(response, "white"))
    
    # 🌟 STEP 4: INTROSPECTION (What did the system actually 'think'?) 🌟
    # We can't easily print internal state here without hacking main.py logs, 
    # but the console output from main.py will show the TRACE.
    
if __name__ == "__main__":
    run_grand_test()
