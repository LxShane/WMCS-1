import sys
import os

# Ensure we can import system modules
sys.path.append(os.getcwd())

from system_a_cognitive.ingestion.ingestor import ContentIngestor
from system_a_cognitive.logic.identity import IdentityManager
import json

# 1. Simulate "Downloading" a Research Paper (Raw Text)
RESEARCH_PAPER_TEXT = """
TITLE: The Mechanics of Feline Claw Retraction and Protraction
ABSTRACT
The unique retractile claw mechanism of Felidae is a key adaptation for predation. Unlike Canidae, where claws remain exposed, the feline distal phalanx (P3) is capable of dorsal hyperextension, effectively sheathing the claw.

ANATOMICAL STRUCTURE
The mechanism relies on a specific arrangement of the distal phalanx (P3), the middle phalanx (P2), and the connecting ligaments. In the resting state, the Strong Dorsal Elastic Ligament (SDEL) exerts a passive tension that pulls the dorsal aspect of P3 proximally. This causes P3 to rotate upward and backward relative to P2, tucking the claw tip into a dermal sheath (the "hood").

MECHANISM OF ACTION
Protraction (extension) is an active muscular process. The Flexor Digitorum Profundus (FDP) muscle contracts, pulling on its tendon which inserts into the plantar tubercle of P3. This overcomes the passive tension of the Dorsal Elastic Ligament. Result: P3 rotates ventrally and forward, exposing the claw.
Retraction is passive. When the FDP relaxes, the stored potential energy in the Dorsal Elastic Ligament snaps P3 back into the hyperextended position.
"""

def run_test():
    print("Initializing Ingestion System...")
    
    # Initialize Identity Manager
    id_mgr = IdentityManager()
    ingestor = ContentIngestor(identity_manager=id_mgr)
    
    print("\n--- INGESTING RESEARCH PAPER ---")
    print(RESEARCH_PAPER_TEXT)
    print("--------------------------------\n")
    
    # Run Ingestion
    new_concepts = ingestor.ingest_text(RESEARCH_PAPER_TEXT, source_name="research_paper_001.pdf")
    
    print(f"\nCompleted! Generated {len(new_concepts)} blocks.")
    for concept in new_concepts:
        print(f" - {concept}")
        
    # Validation
    if "Distal Phalanx" in new_concepts or "distal_phalanx" in [c.lower().replace(" ", "_") for c in new_concepts]:
        print("\nSUCCESS: Anatomy extracted.")
    else:
        print("\nWARNING: Might have missed atomic parts.")

if __name__ == "__main__":
    run_test()
