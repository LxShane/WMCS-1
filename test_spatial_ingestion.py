from system_a_cognitive.ingestion.ingestor import ContentIngestor
import time
import json
import os

def test_spatial_ingestion():
    print("### TEST: Spatial Semantics Ingestion ###")
    ingestor = ContentIngestor()
    
    # Proposition with explicit connectivity and location
    text = "The Frobnosticator is a small bone located at the distal end of the arm. It is connected to the Wrist and the Elbow."
    
    print(f"Input: '{text}'")
    
    # Ingest
    # We use ingest_proposition which uses a simplified prompt, wait, 
    # ingest_proposition uses its OWN prompt defined inside the method?
    # Let me check ingestor.py... YES.
    # Wait, 'ingest_proposition' in ingestor.py (Line 40) HAS HARDCODED PROMPT.
    # It does NOT use INGESTION_SYSTEM_PROMPT from prompts.py.
    # CHECK: ingest_text (Line 70) DOES use INGESTION_SYSTEM_PROMPT.
    # So I must use ingest_text to test the changes I made to prompts.py.
    
    saved_files = ingestor.ingest_text(text, source_name="test_spatial")
    
    print(f"Saved Files: {saved_files}")
    
    for filename in saved_files:
        path = os.path.join("data", "concepts", f"{filename}.json")
        with open(path, 'r') as f:
            data = json.load(f)
            print(f"\n--- Checking {filename} ---")
            
            # Check for Facets
            facets = data.get("facets", {})
            spatial = facets.get("SPATIAL", {})
            
            print(f"SPATIAL DATA FOUND: {json.dumps(spatial, indent=2)}")
            
            if "Wrist" in str(spatial) or "Elbow" in str(spatial):
                print("PASS: Connectivity found.")
            else:
                print("FAIL: 'Connected to' data missing.")
                
            if "distal end" in str(spatial) or "arm" in str(spatial):
                 print("PASS: Location found.")
            else:
                 print("FAIL: Location data missing.")

if __name__ == "__main__":
    test_spatial_ingestion()
