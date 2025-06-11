from app.services.retriever import Retriever

retriever = Retriever(embedding_model="huggingface")

query = "¿Qué función tienen los centros de emergencias?"
resultados = retriever.retrieve(query)

print("\n Resultados de la búsqueda:")
for i, res in enumerate(resultados):
    print(f"\nChunk {i+1}:")
    print(res['text'][:300])  # Mostrar solo los primeros 300 caracteres
