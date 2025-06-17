import os
import json
import numpy as np
import faiss
from app.services.embedding_selector import EmbeddingSelector

class VectorStore:

    def __init__(self, embedding_model: str = "huggingface"):
        self.embedding_model = embedding_model
        self.embedding_dimension = self._get_embedding_dimension()
        self.index_path = "storage/vector_index/index.faiss"
        self.metadata_path = "storage/vector_index/metadata.json"
        self._load_or_initialize()

    def _get_embedding_dimension(self):
        selector = EmbeddingSelector(self.embedding_model)
        dummy_embedding = selector.get_embedding("test")
        return len(dummy_embedding)

    def _load_or_initialize(self):
        os.makedirs("storage/vector_index", exist_ok=True)
        if os.path.exists(self.index_path) and os.path.exists(self.metadata_path):
            self.index = faiss.read_index(self.index_path)
            with open(self.metadata_path, "r", encoding="utf-8") as f:
                self.metadata = json.load(f)
            print("Vector store cargado desde disco.")
        else:
            self.index = faiss.IndexFlatL2(self.embedding_dimension)
            self.metadata = []
            self.save()
            print("Nuevo vector store inicializado.")

    def save(self):
        faiss.write_index(self.index, self.index_path)
        with open(self.metadata_path, "w", encoding="utf-8") as f:
            json.dump(self.metadata, f, ensure_ascii=False, indent=2)

    def reset(self):
        self.index = faiss.IndexFlatL2(self.embedding_dimension)
        self.metadata = []
        self.save()
        print("Vector store reseteado.")

    def index_chunks(self, chunks: list, document_id: str):
        selector = EmbeddingSelector(self.embedding_model)
        for i, chunk_text in enumerate(chunks):
            embedding = selector.get_embedding(chunk_text)
            vector = np.array(embedding, dtype=np.float32).reshape(1, -1)
            self.index.add(vector)
            self.metadata.append({
                "document_id": document_id,
                "chunk": i,
                "text": chunk_text
            })
        self.save()

    def search(self, query: str, top_k: int = 5):
        selector = EmbeddingSelector(self.embedding_model)
        query_embedding = selector.get_embedding(query)
        query_vector = np.array(query_embedding, dtype=np.float32).reshape(1, -1)
        distances, indices = self.index.search(query_vector, top_k)

        results = []
        for dist, idx in zip(distances[0], indices[0]):
            if idx < len(self.metadata):
                meta = self.metadata[idx]
                results.append({
                    "document_id": meta["document_id"],
                    "chunk": meta["chunk"],
                    "text": meta["text"],
                    "distance": float(dist)
                })
        return results
