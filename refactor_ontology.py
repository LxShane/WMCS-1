import os
import json
from termcolor import colored
from system_b_llm.interfaces.gemini_client import GeminiClient
from config import Config

def refactor_ontology():
    print(colored("SYSTEM: Initiating Ontology Migration...", "cyan"))
    
    concepts_dir = "data/concepts"
    files = [f for f in os.listdir(concepts_dir) if f.endswith(".json")]
    
    client = GeminiClient(Config.LLM_API_KEY, Config.LLM_MODEL)
    
    prompt_template = """
    Classify the following concept into one of these Universal Categories:
    1. LIVING_SYSTEM (Animals, Plants, Bacteria, People)
    2. INANIMATE_OBJECT (Rocks, Atoms, Particles, Artifacts)
    3. ABSTRACT_CONCEPT (Ideas, Mathematics, Laws, Theories)
    4. PROCESS_EVENT (Actions, History, Phenomena, Forces)
    5. QUANTITY_MEASURE (Units, Dimensions, Constants like speed/mass)
    6. LOCATION_SPACE (Places, Regions)

    Concept Name: "{name}"
    Current Definition: "{definition}"

    Return ONLY the category name.
    """

    updated_count = 0

    for filename in files:
        filepath = os.path.join(concepts_dir, filename)
        with open(filepath, 'r', encoding='utf-8') as f:
            data = json.load(f)
            
        name = data.get('name')
        definition = data.get('surface_layer', {}).get('definition', '')
        current_type = data.get('type')
        
        # Ask LLM to re-classify
        sys_prompt = "You are an Ontology Classifier. Return only the Category Name."
        prompt = prompt_template.format(name=name, definition=definition)
        new_type = client.completion(sys_prompt, prompt).strip().replace("'", "").replace('"', "")
        
        # Clean up response (sometimes LLMs add extra text)
        valid_types = ["LIVING_SYSTEM", "INANIMATE_OBJECT", "ABSTRACT_CONCEPT", 
                       "PROCESS_EVENT", "QUANTITY_MEASURE", "LOCATION_SPACE"]
        
        # Simple heuristic matching if LLM is chatty
        found_type = current_type
        for vt in valid_types:
            if vt in new_type:
                found_type = vt
                break
        
        if found_type != current_type:
            data['type'] = found_type
            
            with open(filepath, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2)
                
            print(f"  > Migrated '{name}': {current_type} -> {colored(found_type, 'green')}")
            updated_count += 1
        else:
            print(f"  . '{name}' remains {current_type}")

    print(colored(f"\nSYSTEM: Ontology Refactor Complete. Updated {updated_count} concepts.", "yellow"))

if __name__ == "__main__":
    refactor_ontology()
