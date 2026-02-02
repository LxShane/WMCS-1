import sys
import os

# Set root
sys.path.append(os.getcwd())

from system_a_cognitive.meta.deep_researcher import DeepResearchAgent

def test_research():
    print("Initializing DeepResearchAgent...")
    try:
        agent = DeepResearchAgent()
        
        topic = "mechanism of a computer"
        print(f"Testing Research on: '{topic}'")
        
        concepts = agent.conduct_deep_research(topic, max_depth=1)
        
        print("\n--- RESULTS ---")
        print(f"Concepts Created: {concepts}")
        
        if not concepts:
            print("FAILURE: No concepts returned.")
        else:
            print("SUCCESS: Concepts returned.")
            
    except Exception as e:
        print(f"CRASH: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_research()
