import sys
from config import Config
from system_a_cognitive.logic.identity import IdentityManager
from system_a_cognitive.ingestion.ingestor import ContentIngestor

print("Initializing...")
im = IdentityManager()
ingestor = ContentIngestor(identity_manager=im)

text = "The Golden Eagle is a large bird of prey that belongs to the family Accipitridae."
print(f"Ingesting: {text}")

concepts = ingestor.ingest_text(text, source_name="direct_test")
print(f"Result: {concepts}")
