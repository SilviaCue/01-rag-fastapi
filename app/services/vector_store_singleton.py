from app.services.vector_store import VectorStore

# Instancia única de vector store en todo el proyecto
vector_store_instance = VectorStore(embedding_model="huggingface")
# ===============================================================
# vector_store_instance: Instancia única del almacén de vectores
#
# ¿Qué es el índice?
# - El índice es el lugar donde se guardan todas las representaciones numéricas
#   (vectores) de los textos de los documentos.
# - Sirve para encontrar de forma rápida y “por significado” los fragmentos de texto
#   más parecidos a la pregunta del usuario, aunque no use las mismas palabras.
#
# ¿Para qué sirve esto?
# - En el sistema RAG, todos los fragmentos de texto de los documentos
#   se convierten en "vectores" y se guardan en un índice llamado FAISS.
# - Este objeto (vector_store_instance) es ese índice.
#
# ¿Por qué lo hacemos así?
# - Queremos que toda la aplicación (subida de documentos, chat, etc.)
#   use SIEMPRE el mismo índice, para que todas las búsquedas sean coherentes.
# - Si se crearan varias instancias, los datos estarían "separados"
#   y las búsquedas podrían fallar o no encontrar lo que buscamos.
#
# ¿Cómo se usa?
# - Cualquier parte del código que necesite buscar o guardar información
#   en el índice de vectores, debe importar y usar este objeto.
#
# Ejemplo de uso:
#   from app.services.vector_store_singleton import vector_store_instance as vector_store
#   vector_store.index_chunks(chunks, document_id=document_id)
# ===============================================================
