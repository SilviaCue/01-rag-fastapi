import os
import faiss
import numpy as np
import pickle
from app.services.embedding_selector import EmbeddingSelector

class VectorStore:

    def __init__(self, embedding_model: str, index_path: str = "storage/vector_index/faiss.index", metadata_path: str = "storage/vector_index/metadata.pkl"):
        self.embedding_selector = EmbeddingSelector(model_name=embedding_model)
        self.index_path = index_path
        self.metadata_path = metadata_path
        self.index = None
        self.metadata = []

        self._load_or_initialize()

    def _load_or_initialize(self):
        if os.path.exists(self.index_path) and os.path.exists(self.metadata_path):
            self.index = faiss.read_index(self.index_path)
            with open(self.metadata_path, "rb") as f:
                self.metadata = pickle.load(f)
            print(" Vector store cargado desde disco.")
        else:
            self.index = None
            self.metadata = []
            print(" Nuevo vector store inicializado.")

    def index_chunks(self, chunks: list, document_id: str):
        embeddings = [self.embedding_selector.get_embedding(chunk) for chunk in chunks]
        embeddings_np = np.array(embeddings).astype("float32")

        if self.index is None:
            dimension = embeddings_np.shape[1]
            self.index = faiss.IndexFlatL2(dimension)

        self.index.add(embeddings_np)

        # Guardamos info de cada chunk (puede ser el nombre de documento)
        self.metadata.extend([(document_id, i) for i in range(len(chunks))])

        self._save()

    def _save(self):
        os.makedirs(os.path.dirname(self.index_path), exist_ok=True)
        faiss.write_index(self.index, self.index_path)
        with open(self.metadata_path, "wb") as f:
            pickle.dump(self.metadata, f)

    def search(self, query: str, top_k: int = 5):
        query_embedding = np.array([self.embedding_selector.get_embedding(query)]).astype("float32")
        distances, indices = self.index.search(query_embedding, top_k)

        results = []
        for dist, idx in zip(distances[0], indices[0]):
            if idx < len(self.metadata):
                doc_id, chunk_num = self.metadata[idx]
                results.append({"document_id": doc_id, "chunk": chunk_num, "distance": dist})
        return results
