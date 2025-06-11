import os
from app.services.text_splitter import TextSplitter
from app.services.vector_store import VectorStore

# Creamos ejemplo con texto simulado
texto_largo = (
    "Los centros de llamadas de emergencias reciben muchas llamadas diarias. "
    "Cada operador gestiona las emergencias y coordina los recursos disponibles. "
    "La correcta atención a las llamadas es clave en situaciones críticas. "
) * 10

# Simula trocear el texto
splitter = TextSplitter(chunk_size=100, overlap=20)
chunks = splitter.split_text(texto_largo)

# Inicializa el vector store
vector_store = VectorStore(embedding_model="huggingface")

# Indexa los chunks
vector_store.index_chunks(chunks, document_id="Emergencias112")

# Simula búsqueda
query = "gestión de llamadas de emergencias"
resultados = vector_store.search(query)

print(" Resultados de la búsqueda:")
for r in resultados:
    print(r)
