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
# ===============================================================
# Clase VectorStore: almacén de vectores para el sistema RAG
#
# ¿Qué es esto?
# - Es la clase que gestiona el "índice" donde se guardan los fragmentos de texto
#   de los documentos, convertidos en vectores (embeddings), para hacer búsquedas semánticas.
#
# ¿Cómo funciona?
# - Cuando se crea la clase, intenta cargar el índice y la información asociada (metadata)
#   desde disco (storage/vector_index). Así mantiene todo lo que ya estaba indexado.
# - Si no existen esos archivos (es la primera vez o los borraste), crea un índice nuevo y vacío.
# - Solo se borra y vuelve a empezar de cero si se llama explícitamente al método reset().
#
# ¿Por qué es útil?
# - Permite añadir nuevos fragmentos de texto al índice sin perder lo anterior.
# - Permite buscar de forma eficiente los fragmentos más parecidos a una pregunta del usuario.
#
# ¿Cuándo se reinicia (borra todo)?
# - Solo si llamas a .reset() manualmente, nunca por defecto.
#
# Ejemplo de uso normal:
#   vs = VectorStore(embedding_model="huggingface")
#   vs.index_chunks(chunks, document_id="documento.pdf")
#   resultados = vs.search("¿Qué es el vector store?")
# ===============================================================
