Proyecto RAG FastAPI

Descripción
Sistema funcional de Retrieval-Augmented Generation (RAG) en local basado en FastAPI, con generación de respuestas sobre documentos cargados por el usuario.

Pipeline completo funcionando:

Upload de documentos vía API.
Extracción automática de texto.
División en chunks.
Indexado en FAISS local.
Recuperación de contexto usando embeddings.
Generación de respuesta vía Gemini 1.5 Pro.

Tecnologías principales:

FastAPI
FAISS
Google Gemini 1.5 Pro (Generación)
Hugging Face (Embeddings)
Python 3.11
Uvicorn

Estructura de carpetas:

app/
  config/
    secret_keys.py
    settings.py
  providers/
    gemini_generator.py
    openai_generator.py (preparado)
    gemini_embedder.py
    hf_embedder.py
  services/
    chat.py
    retriever.py
    vector_store.py
    embedding_selector.py
    generation_selector.py
  routers/
    upload.py
    chat.py
storage/
  docs_raw/
  docs_chunks/
  vector_store/
secret_keys.json

Configuración
Las API Keys se almacenan de forma centralizada en el archivo secret_keys.json:

json

{
  "GEMINI_API_KEY": "tu_clave_gemini",
  "HUGGINGFACE_API_KEY": "tu_clave_huggingface",
  "OPENAI_API_KEY": "tu_clave_openai"
}
El sistema carga automáticamente estos valores al iniciar FastAPI.

Ejecución
Dentro del entorno virtual:

uvicorn app.main:app --reload

Endpoints:

POST /upload/ -> Cargar documentos
POST /chat/ -> Realizar preguntas al sistema