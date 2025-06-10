# app/test/test_sentence_embedding.py
from app.providers.sentence_embedder import get_embedding

texto = "Esto es una prueba de embedding local con sentence-transformers."

embedding = get_embedding(texto)

print("✅ Embedding generado.")
print("🔢 Dimensión:", len(embedding))
print("📊 Primeros 10 valores:", embedding[:10])
