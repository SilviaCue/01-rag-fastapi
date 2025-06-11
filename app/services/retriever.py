from app.services.vector_store import VectorStore
from app.services.text_splitter import TextSplitter

class Retriever:

    def __init__(self, embedding_model: str = "huggingface"):
        self.vector_store = VectorStore(embedding_model=embedding_model)

    def retrieve(self, query: str, top_k: int = 5):
        results = self.vector_store.search(query, top_k=top_k)
        return results
