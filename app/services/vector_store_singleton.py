from app.services.vector_store import VectorStore

# Instancia única de vector store en todo el proyecto
vector_store_instance = VectorStore(embedding_model="huggingface")
