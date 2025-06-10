from app.providers.gemini_embedder import get_embedding

texto = "Esto es una prueba para obtener el embedding con Gemini."

try:
    embedding = get_embedding(texto)
    print("✅ Embedding generado correctamente.")
    print("🔢 Dimensión:", len(embedding))
    print("📊 Primeros 10 valores:", embedding[:10])
except Exception as e:
    print("❌ Error al generar embedding:", str(e))
