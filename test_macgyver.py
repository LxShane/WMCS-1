from main import WMCS_Kernel
from termcolor import colored
import json

def test_macgyver():
    print(colored("╔═══ TEST: MACGYVER LOGIC (FIRST PRINCIPLES) ═══╗", "magenta", attrs=['bold']))
    
    kernel = WMCS_Kernel()
    
    # 1. Inject Concepts (Hot Loading)
    # We define Pedal by its FUNCTION and MECHANISM
    pedal_data = {
        "name": "Bicycle Pedal",
        "type": "MECHANICAL_PART",
        "id": {"group": 20, "item": 8881},
        "structure": {
             "shape": "Flat platform with axis",
             "material": "Plastic or Metal"
        },
        "deep_layer": {
            "mechanism": "Transmits downward force from foot to crank arm via rotation.",
            "requirements": ["Flat surface for foot", "Rotatable axis", "Rigidity"]
        }
    }
    
    # We define Wood Block by its PROPERTIES
    wood_data = {
        "name": "Wood Block",
        "type": "OBJECT",
        "id": {"group": 20, "item": 8882},
        "structure": {
             "shape": "Cuboid, Flat surfaces",
             "material": "Wood (Solid)"
        },
        "facets": {
            "PROPERTIES": {
                "rigidity": "High",
                "flammability": "Medium"
            }
        }
    }
    
    print(colored("Step 1: Injecting Concepts...", "yellow"))
    kernel.block_cache['bicycle_pedal'] = pedal_data
    kernel.block_cache['wood_block'] = wood_data
    
    # 2. The MacGyver Query
    # Can it infer that Wood Block fits the "Requirements" of the Pedal?
    query = "My bicycle pedal broke. I have a solid wood block and tools. Can I use the wood block to fix it? Explain based on mechanics."
    
    print(colored(f"\nStep 2: Asking: '{query}'", "cyan"))
    response = kernel.process_query(query, allow_research=False)
    
    print(colored(f"\nResponse: {response['text'][:500]}...", "white"))
    
    text = response['text'].lower()
    if "yes" in text and ("flat" in text or "force" in text or "rigid" in text):
        print(colored("\n[PASS] System exhibited First Principles Reasoning.", "green"))
    else:
        print(colored("\n[FAIL] System missed the functional equivalence.", "red"))

if __name__ == "__main__":
    test_macgyver()
