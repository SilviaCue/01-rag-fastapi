# app/providers/sentence_embedder.py
from sentence_transformers import SentenceTransformer

model = SentenceTransformer("all-MiniLM-L6-v2")  # Ligero y rápido

def get_embedding(text: str) -> list[float]:
    embedding = model.encode(text)
    return embedding.tolist()
