"""
Fix ChromaDB - diagnose and rebuild if needed
"""
import traceback
import os
import shutil
import json

print("=== CHROMADB DIAGNOSTIC ===")

# Phase 1: Test direct chromadb access
print("\n1. Testing direct chromadb import...")
try:
    import chromadb
    print(f"   ChromaDB version: {chromadb.__version__}")
except Exception as e:
    print(f"   FAILED: {e}")
    traceback.print_exc()
    exit(1)

# Phase 2: Test PersistentClient
print("\n2. Testing PersistentClient...")
try:
    client = chromadb.PersistentClient(path="data/chroma_db")
    print("   Client created OK")
except Exception as e:
    print(f"   FAILED: {e}")
    traceback.print_exc()
    print("\n   Recommendation: Delete data/chroma_db and rebuild")
    exit(1)

# Phase 3: Test collection access
print("\n3. Testing collection access...")
try:
    collection = client.get_or_create_collection("wmcs_concepts")
    count = collection.count()
    print(f"   Collection 'wmcs_concepts' has {count} items")
except Exception as e:
    print(f"   FAILED: {e}")
    traceback.print_exc()
    exit(1)

# Phase 4: Test search
print("\n4. Testing vector search...")
try:
    results = collection.query(query_texts=["cat"], n_results=3)
    print(f"   Search returned {len(results['ids'][0])} results")
    for i, id in enumerate(results['ids'][0]):
        print(f"      - {results['metadatas'][0][i].get('name', 'Unknown')}")
except Exception as e:
    print(f"   FAILED: {e}")
    traceback.print_exc()

print("\n=== DIAGNOSTIC COMPLETE ===")
