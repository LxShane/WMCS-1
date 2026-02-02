import os
import time
from system_a_cognitive.ingestion.ingestor import ContentIngestor

def main():
    print("Initializing Ingestion Engine...")
    ingestor = ContentIngestor()
    memory_dir = "memory"
    
    if not os.path.exists(memory_dir):
        print(f"Error: Directory '{memory_dir}' not found.")
        return

    files = [f for f in os.listdir(memory_dir) if os.path.isfile(os.path.join(memory_dir, f))]
    print(f"Found {len(files)} documents in memory/: {files}")
    
    total_concepts = 0
    
    for filename in files:
        filepath = os.path.join(memory_dir, filename)
        print(f"\n--- Ingesting {filename} ---")
        try:
            concepts = ingestor.ingest_file(filepath)
            count = len(concepts)
            total_concepts += count
            if count == 0:
                print("  (No concepts extracted. Check if file content matches prompt expectations.)")
        except Exception as e:
            print(f"  FAILED to ingest {filename}: {e}")
        
        # Rate limit safety
        time.sleep(2)

    print(f"\nINGESTION COMPLETE. Total new concepts: {total_concepts}")

if __name__ == "__main__":
    main()
