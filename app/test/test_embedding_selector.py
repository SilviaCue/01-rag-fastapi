from app.services.embedding_selector import EmbeddingSelector

texto = "Probando selector de embeddings."

# Primero prueba Gemini
selector_gemini = EmbeddingSelector(model_name="gemini")
embedding_gemini = selector_gemini.get_embedding(texto)

if embedding_gemini:
    print(" Gemini: Embedding generado correctamente.")
    print(" Dimensión:", len(embedding_gemini))
    print(" Primeros 5 valores:", embedding_gemini[:5])
else:
    print(" Error al generar embedding con Gemini.")

# Ahora prueba Hugging Face
selector_hf = EmbeddingSelector(model_name="huggingface")
embedding_hf = selector_hf.get_embedding(texto)

if embedding_hf:
    print(" Hugging Face: Embedding generado correctamente.")
    print(" Dimensión:", len(embedding_hf))
    print(" Primeros 5 valores:", embedding_hf[:5])
else:
    print(" Error al generar embedding con Hugging Face.")
