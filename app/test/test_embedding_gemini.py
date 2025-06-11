
from app.providers.gemini_embedder import get_embedding

texto = "Esto es una prueba para obtener el embedding con Gemini."

embedding = get_embedding(texto)

if embedding:
    print(" Embedding generado correctamente con Gemini.")
    print(" Dimensión:", len(embedding))
    print(" Primeros 10 valores:", embedding[:10])
else:
    print(" Error al generar embedding.")
