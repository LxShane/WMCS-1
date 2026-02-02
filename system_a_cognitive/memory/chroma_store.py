import chromadb
from chromadb.utils import embedding_functions
from termcolor import colored
import os

class ChromaStore:
    """
    Industrial-Grade Vector Memory using ChromaDB.
    Replaces the list-based VectorStore.
    """
    def __init__(self, persistence_path="data/chroma_db"):
        print(colored("Initializing ChromaDB (The Scale Engine)...", "magenta"))
        
        # 1. Setup Client
        self.client = chromadb.PersistentClient(path=persistence_path)
        
        # 2. Setup Embedding (Local, Free, High Performance)
        # using the default SentenceTransformer (all-MiniLM-L6-v2)
        try:
            self.ef = embedding_functions.DefaultEmbeddingFunction()
        except:
             # Fallback if libraries missing, but usually included in chromadb[full]
             print(colored("Warning: Default embedding function failed. Using dummy.", "red"))
             self.ef = None

        # 3. Get/Create Collection
        self.collection = self.client.get_or_create_collection(
            name="wmcs_concepts",
            embedding_function=self.ef,
            metadata={"hnsw:space": "cosine"} # Optimization
        )
        print(colored(f"  > Chroma Collection Ready. Items: {self.collection.count()}", "green"))

    def add(self, doc_id, text, metadata=None):
        """
        Add or Update a document.
        doc_id: Expected to be "group,item" string (e.g. "20,55")
        """
        if metadata is None: metadata = {}
        
        # Ensure metadata is flat (Chroma doesn't like nested dicts)
        clean_meta = {}
        for k,v in metadata.items():
            if isinstance(v, (str, int, float, bool)):
                clean_meta[k] = v
            else:
                clean_meta[k] = str(v) # Stringify complex objects

        self.collection.upsert(
            documents=[text],
            metadatas=[clean_meta],
            ids=[doc_id]
        )

    def search(self, query, top_k=3, threshold=0.0):
        """
        Semantic Search.
        Returns list of blocks (mocked as dicts with ID/Metadata) to match Kernel expectation.
        """
        results = self.collection.query(
            query_texts=[query],
            n_results=top_k
        )
        
        # Parse Chroma result format -> WMCS format
        # results['ids'] = [['id1', 'id2']]
        # results['metadatas'] = [[meta1, meta2]]
        # results['distances'] = [[0.1, 0.2]]
        
        parsed_results = []
        if results['ids']:
            ids = results['ids'][0]
            metas = results['metadatas'][0]
            if 'distances' in results and results['distances']:
                dists = results['distances'][0]
            else:
                dists = [0.0] * len(ids)

            for i, uid in enumerate(ids):
                # Filter by threshold (Cosine Distance: 0=Same, 1=Diff)
                # If threshold is similarity (0-1), we need to invert.
                # Assuming threshold=0.0 means "Accept all" for now.
                dist = dists[i]
                
                # Reconstruct a partial block from metadata
                # The Kernel expects 'id': {'group': X, 'item': Y} logic
                # We parse uid "20,55"
                try:
                    g, it = uid.split(',')
                    id_obj = {'group': int(g), 'item': int(it)}
                except:
                    id_obj = {'group': 0, 'item': 0, 'raw': uid}
                
                # Fetch Name
                name = metas[i].get('name', 'Unknown')
                
                # We return the format expected by Main.py
                # hit['metadata'].get('name') and hit['score']
                score = 1.0 - dist # Convert Distance to Similarity approximation
                
                res_obj = {
                    'id': id_obj,
                    'name': name, # Top level for convenience
                    'metadata': {'name': name}, # Nested for compatibility
                    'score': score
                }
                parsed_results.append(res_obj)
                
        return parsed_results
    
    def add_concept_block(self, block: dict):
        """
        Helper: Serializes a Concept Block and adds it to the DB.
        """
        text_rep = f"Concept: {block.get('name', 'Unknown')}. "
        for k, v in block.get('facets', {}).items():
            text_rep += f"{k}: {v}. "
        for c in block.get('claims', []):
                pred = c.get('predicate', '')
                obj = c.get('object', '')
                text_rep += f"{pred}: {obj}. "
        
        # ID Construction
        gid = block.get('id',{}).get('group', 0)
        iid = block.get('id',{}).get('item', 0)
        doc_id = f"{gid},{iid}"
        
        self.add(doc_id, text_rep, metadata={'name': block.get('name', 'Unknown'), 'group': gid})
    def load_index(self): pass
    def save_index(self): pass

    def count(self):
        return self.collection.count()

    def reset(self):
        """Wipes the database. Use with caution."""
        self.client.delete_collection("wmcs_concepts")
        self.collection = self.client.get_or_create_collection(
            name="wmcs_concepts", 
            embedding_function=self.ef
        )
