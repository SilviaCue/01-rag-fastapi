from sentence_transformers import SentenceTransformer
# Proveedor para obtener embeddings usando Hugging Face

model = SentenceTransformer("sentence-transformers/all-MiniLM-L6-v2")
# Función para obtener embeddings usando Hugging Face
def get_embedding(text: str) -> list[float]:
    try:
        embedding = model.encode(text).tolist()
        return embedding
    except Exception as e:
        print(" Error en Hugging Face embedding:", e)
        return []
