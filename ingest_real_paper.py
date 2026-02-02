import sys
import os
from termcolor import colored

# Ensure we can import system modules
sys.path.append(os.getcwd())
from main import WMCS_Kernel

# Text synthesized from 2023 Research Findings (Current Biology, etc.)
REAL_PAPER_TEXT = """
TITLE: Anatomical Mechanisms of Low-Frequency Phonation in Felis catus (The Purr)

ABSTRACT
The domestic cat (Felis catus) produces a low-frequency vocalization known as the purr (25-150 Hz). Recent investigations into the laryngology of felines have identified specific anatomical structures responsible for this phenomenon. Unlike the active muscular contraction hypothesis alone, new evidence suggests a key role for specialized connective tissue.

1. LARYNGEAL OSCILLATOR
The core mechanism is located in the larynx. A central pattern generator, specifically a "Neural Oscillator" in the cat's brain, sends rhythmic repetitive nerve impulses to the intrinsic laryngeal muscles. These signals occur at a frequency of 20 to 30 bursts per second. This causes the glottis to open and close rapidly, creating airflow interruptions that generate sound.

2. VOCAL FOLD PADS
A 2023 study identified distinct "Vocal Fold Pads" embedded within the vocal cords. These pads consist of collagen and elastin fibers (connective tissue). Their increased mass allows the vocal folds to vibrate slowly even without intense neural input, enabling the production of low frequencies (low pitch) that would otherwise be impossible for an animal of this size. This operates similarly to the "fry register" in human speech.

3. HYOID RESONANCE
The vibratory energy generated at the larynx is transmitted to the Hyoid Bone. In domestic cats, the hyoid is completely ossified (rigid), acting as a resonator that amplifies the low-frequency rumble throughout the body. This contrasts with the Panthera genus (lions), which possess a flexible cartilaginous hyoid suited for roaring but ill-suited for continuous purring.

4. RESPIRATORY PHASE
Uniquely, the purring mechanism operates continuously during both inhalation and exhalation. The diaphragm aids in maintaining necessary airflow pressure to sustain the vibration of the Vocal Fold Pads across the respiratory cycle.
"""

def run_real_ingestion():
    print(colored("### INGESTING REAL RESEARCH CONTENT ###", "magenta", attrs=['bold']))
    wmcs = WMCS_Kernel()
    wmcs.load_data()
    
    # We use the Ingestor directy
    from system_a_cognitive.ingestion.ingestor import ContentIngestor
    from system_a_cognitive.logic.identity import IdentityManager
    
    identity_manager = IdentityManager()
    ingestor = ContentIngestor(identity_manager=identity_manager)
    
    print(colored("\nFeeding Text...", "cyan"))
    new_concepts = ingestor.ingest_text(REAL_PAPER_TEXT, source_name="research_paper_2023")
    
    print(colored(f"\nCompleted. Generated {len(new_concepts)} blocks:", "green"))
    for c in new_concepts:
        print(f" - {c}")

if __name__ == "__main__":
    run_real_ingestion()
