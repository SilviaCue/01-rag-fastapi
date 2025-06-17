from app.services.vector_store_singleton import vector_store_instance
from app.services.text_splitter import TextSplitter

class Retriever:

    def __init__(self):
        self.vector_store = vector_store_instance

    def retrieve(self, query: str, top_k: int = 5):
        results = self.vector_store.search(query, top_k=top_k)
        return results
