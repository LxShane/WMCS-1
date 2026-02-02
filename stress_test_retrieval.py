import sys
import os
from termcolor import colored

# Fix path
sys.path.append(os.getcwd())

from config import Config
from system_b_llm.interfaces.gemini_client import GeminiClient
from system_a_cognitive.memory.vector_store import VectorStore

def run_retrieval_test():
    print(colored("### STRESS TEST: VECTOR RETRIEVAL ###", "magenta", attrs=['bold']))
    
    client = GeminiClient(Config.LLM_API_KEY, Config.LLM_MODEL)
    store = VectorStore(client)
    
    # 1. Add Data (Concept: Cat)
    print(colored("Step 1: Indexing 'Cat' concept...", "cyan"))
    store.add(
        doc_id="concept_cat", 
        text="A small carnivorous mammal with soft fur, claws, and whiskers. Often kept as a pet."
    )
    
    # 2. Search Failure (Keyword)
    query = "feline hunter"
    print(colored(f"\nQuery: '{query}'", "yellow"))
    
    if "cat" not in query.lower():
        print(colored("  > Keyword Search would FAIL (No 'cat' in query).", "red"))
        
    # 3. Search Success (Vector)
    print(colored("Step 2: Running Vector Search (Threshold 0.1)...", "cyan"))
    # Lower threshold to see what we get
    results = store.search(query, threshold=0.1) 
    
    print(f"Debug: Raw Results: {results}")

    if results:
        print(colored(f"  > SUCCESS! Found: {results[0]['id']} (Score: {results[0]['score']:.2f})", "green"))
    else:
        print(colored("  > FAIL. No results found.", "red"))

if __name__ == "__main__":
    run_retrieval_test()
