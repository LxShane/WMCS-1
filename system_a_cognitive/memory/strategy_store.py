import chromadb
from chromadb.utils import embedding_functions
from termcolor import colored
from ..logic.models import MetaLesson

class StrategyStore:
    """
    Long-Term Memory for 'How to Think' (Meta-Learning).
    Stores 'MetaLesson' objects wrapped in vectors.
    """
    def __init__(self, persistence_path="data/chroma_db"):
        print(colored("Initializing Strategy Store (Wisdom Engine)...", "magenta"))
        self.client = chromadb.PersistentClient(path=persistence_path)
        
        try:
            self.ef = embedding_functions.DefaultEmbeddingFunction()
        except:
            self.ef = None

        self.collection = self.client.get_or_create_collection(
            name="wmcs_strategies",
            embedding_function=self.ef,
            metadata={"hnsw:space": "cosine"}
        )

    def add_lesson(self, lesson: MetaLesson):
        """
        Stores a generalized lesson.
        The 'Embedding' is based on the TRIGGER and CONTENT.
        """
        # We embed the "Trigger" primarily, so we find this lesson when the trigger context appears again.
        embed_text = f"{lesson.trigger}. {lesson.content}"
        
        meta = {
            "type": lesson.lesson_type,
            "trigger": lesson.trigger,
            "content": lesson.content,
            "confidence": lesson.confidence,
            "created_at": lesson.created_at
        }
        
        self.collection.upsert(
            documents=[embed_text],
            metadatas=[meta],
            ids=[lesson.id]
        )
        print(colored(f"  [Memory] Stored Strategy: '{lesson.content}'", "cyan"))

    def recall_strategies(self, context_query: str, top_k=3):
        """
        Retrieves relevant strategies for the current context.
        """
        results = self.collection.query(
            query_texts=[context_query],
            n_results=top_k
        )
        
        strategies = []
        if results['ids'] and results['ids'][0]:
            metas = results['metadatas'][0]
            dists = results['distances'][0] if 'distances' in results else [0]*len(metas)
            
            for i, m in enumerate(metas):
                # Filter weak matches if needed (dist > 0.5)
                # For now, we take top_k
                strategies.append(f"[{m['type']}] {m['content']} (Trigger: {m['trigger']})")
                
        return strategies
