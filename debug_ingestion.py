import os
import sys

try:
    print("1. Loading Config...")
    from config import Config
    print(f"   API Key Present: {bool(Config.LLM_API_KEY)}")

    print("2. Importing IdentityManager...")
    from system_a_cognitive.logic.identity import IdentityManager
    im = IdentityManager()
    print(f"   IdentityManager initialized. Registry size: {len(im.registry)}")
    
    print("\n3. Testing Minting...")
    # Mint a test ID
    new_id = im.mint_id("Test_Eagle_Debug", 21)
    print(f"   Minted ID: {new_id}")
    
    print("\n4. Importing ContentIngestor...")
    from system_a_cognitive.ingestion.ingestor import ContentIngestor
    ingestor = ContentIngestor(identity_manager=im)
    print("   ContentIngestor initialized.")
    
    print("\n5. DONE.")
    
except Exception as e:
    print(f"\nCRASH: {e}")
    import traceback
    traceback.print_exc()
