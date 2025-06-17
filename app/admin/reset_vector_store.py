from app.services.vector_store import VectorStore

def reset_vector_store():
    vs = VectorStore(embedding_model="huggingface")
    vs.reset()
    print("Vector store reseteado correctamente.")

if __name__ == "__main__":
    reset_vector_store()

# python -m app.admin.reset_vector_store unicamente para resetear FAISS

