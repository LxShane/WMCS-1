import numpy as np
from termcolor import colored
import json

class VectorStore:
    """
    A lightweight, in-memory Vector Database.
    Storage Format:
    [
        {'id': str, 'vector': np.array, 'text': str, 'metadata': dict}
    ]
    """
    def __init__(self, client):
        self.vectors = []
        self.client = client
        self.dim = 768 # Standard for text-embedding-004

    def add(self, doc_id: str, text: str, metadata: dict = None):
        """
        Converts text to vector and stores it.
        """
        vector = self.client.embed_content(text)
        if not vector:
            return False
            
        self.vectors.append({
            'id': doc_id,
            'vector': np.array(vector),
            'text': text,
            'metadata': metadata or {}
        })
        return True

    def search(self, query: str, top_k: int = 3, threshold: float = 0.5):
        """
        Semantic Search using Cosine Similarity.
        """
        if not self.vectors:
            return []

        # 1. Embed Query
        query_vec = self.client.embed_content(query)
        if not query_vec:
            return []
        
        q_v = np.array(query_vec)
        q_norm = np.linalg.norm(q_v)
        
        results = []
        
        # 2. Brute-Force Cosine Similarity (Fast enough for <10k items)
        for item in self.vectors:
            doc_v = item['vector']
            d_norm = np.linalg.norm(doc_v)
            
            if d_norm == 0 or q_norm == 0:
                score = 0
            else:
                score = np.dot(q_v, doc_v) / (q_norm * d_norm)
                
            if score >= threshold:
                results.append((score, item))
                
        # 3. Sort
        results.sort(key=lambda x: x[0], reverse=True)
        
        # 4. Format Output
        final_results = []
        for score, item in results[:top_k]:
            final_results.append({
                'score': float(score),
                'id': item['id'],
                'metadata': item['metadata'],
                'snippet': item['text'][:100]
            })
            
        return final_results

    def save_index(self, path="data/vector_index.json"):
        # We can't save numpy arrays directly to JSON without conversion
        serializable = []
        for item in self.vectors:
            serializable.append({
                'id': item['id'],
                'vector': item['vector'].tolist(),
                'text': item['text'],
                'metadata': item['metadata']
            })
        with open(path, "w", encoding="utf-8") as f:
            json.dump(serializable, f)

    def load_index(self, path="data/vector_index.json"):
        try:
            with open(path, "r", encoding="utf-8") as f:
                data = json.load(f)
                self.vectors = []
                for item in data:
                    item['vector'] = np.array(item['vector'])
                    self.vectors.append(item)
            print(colored(f"[Memory] Loaded {len(self.vectors)} vectors from disk.", "green"))
        except FileNotFoundError:
            print(colored("[Memory] No existing vector index found. Starting fresh.", "yellow"))
