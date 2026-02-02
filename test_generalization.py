import sys
from config import Config
from system_a_cognitive.logic.identity import IdentityManager
from system_a_cognitive.ingestion.ingestor import ContentIngestor
from system_a_cognitive.logic.functional_search import FunctionalSearcher

print("--- GENERALIZATION TEST: Can it learn 'Shield' and 'Firewall' from scratch? ---")

# 1. Initialize
im = IdentityManager()
ingestor = ContentIngestor(identity_manager=im)
searcher = FunctionalSearcher()

# 2. Teach (Ingest) totally new concepts
text_shield = "A Medieval Shield is a piece of personal armor held in the hand. Its function is to intercept attacks and protect the user from harm."
text_firewall = "A Network Firewall is a security system that monitors and controls network traffic. Its function is to block unauthorized access and protect the network."

print(f"\n[Learning] {text_shield}...")
ingestor.ingest_text(text_shield, source_name="test_shield")

print(f"\n[Learning] {text_firewall}...")
ingestor.ingest_text(text_firewall, source_name="test_firewall")

# 3. Reload Searcher (to see new files)
searcher.autoload()

# 4. The "Magic Trick": Ask for the functional equivalent
print("\n[Reasoning] Searching for 'Shield' equivalents...")
results = searcher.find_equivalents("Medieval Shield")

print("\n--- RESULTS ---")
if results.get("equivalents"):
    for role, items in results["equivalents"].items():
        print(f"Role found: {role}")
        for item in items:
            print(f"  Found Equivalent: {item['name']} (ID: {item['id']})")
else:
    print("No connections found (Failed).")
