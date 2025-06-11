from app.providers.hf_embedder import get_embedding

texto = "Esto es una prueba con Hugging Face (renombrado a hf_embedder)."

embedding = get_embedding(texto)

if embedding:
    print(" Embedding generado correctamente con Hugging Face.")
    print(" Dimensión:", len(embedding))
    print(" Primeros 10 valores:", embedding[:10])
else:
    print(" Error al generar embedding.")
