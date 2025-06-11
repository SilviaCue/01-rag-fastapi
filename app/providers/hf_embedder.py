from sentence_transformers import SentenceTransformer

# Cargamos el modelo una sola vez (eficiencia)
model = SentenceTransformer("sentence-transformers/all-MiniLM-L6-v2")

def get_embedding(text: str) -> list[float]:
    try:
        embedding = model.encode(text).tolist()
        return embedding
    except Exception as e:
        print(" Error en Hugging Face embedding:", e)
        return []
