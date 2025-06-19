RAG API - Sistema de Asistente Documental con FastAPI

Este proyecto implementa un sistema completo RAG (Retrieval Augmented Generation) para asistencia documental interna. Está diseñado para permitir la carga, procesamiento, indexación y consulta de documentos mediante técnicas de búsqueda semántica y generación de texto con IA.

Tecnologías usadas:

FastAPI (backend principal)

FAISS (almacenamiento vectorial)

HuggingFace sentence-transformers (embeddings)

Gemini API (embeddings y generación de texto)

OpenAI API (generación de texto)

PyMuPDF (lectura de PDFs)

pytesseract (OCR integrado para PDFs escaneados)



Estructura del proyecto:

idearium_rag_fastapi/
│
├── app/
│   ├── admin/
│   │   └── reset_vector_store.py
│   ├── config/
│   │   ├── secret_keys.py
│   │   └── settings.py
│   ├── models/
│   ├── providers/
│   │   ├── gemini_embedder.py
│   │   ├── gemini_generator.py
│   │   ├── hf_embedder.py
│   │   ├── openai_embedder.py
│   │   └── openai_generator.py
│   ├── routers/
│   │   ├── chat.py
│   │   ├── download.py
│   │   ├── upload.py
│   │   ├── upload_one.py
│   │   └── upload_multiple.py
│   └── services/
│       ├── file_parser.py
│       ├── model_selector.py
│       ├── text_splitter.py
│       ├── vector_store.py
│       ├── vector_store_singleton.py
│       ├── generation_selector.py
│       └── embedding_selector.py
│
├── storage/
│   ├── docs_raw/
│   ├── docs_chunks/
│   └── vector_index/
│       ├── index.faiss
│       └── metadata.json
│
├── secret_keys.json
├── main.py
├── requirements.txt
└── README.md

Flujo de trabajo:

Los documentos se colocan en storage/docs_raw/

El endpoint /upload-all/ procesa todos los PDFs (soporta subcarpetas)

Si un PDF es escaneado, se activa el OCR automáticamente

El texto extraído se convierte en embeddings semánticos

Los embeddings se almacenan en FAISS junto con metadatos

Las consultas se realizan mediante el endpoint /chat/

Se recuperan los chunks más relevantes y se genera una respuesta contextualizada

Ejecución del proyecto:

1. Instalar dependencias:

pip install -r requirements.txt


2. Configurar las claves API:

Crear el archivo secret_keys.json con el siguiente formato:

{
  "GEMINI_API_KEY": "tu_clave_gemini",
  "HUGGINGFACE_API_KEY": "tu_clave_huggingface",
  "OPENAI_API_KEY": "tu_clave_openai"
}


3. Arrancar FastAPI:

Desde la raíz del proyecto:

uvicorn app.main:app --reload

La documentación interactiva Swagger UI estará disponible en:

http://127.0.0.1:8000/docs

Gestión del índice vectorial


Para limpiar el índice vectorial y cargar nuevos documentos desde cero:

python -m app.admin.reset_vector_store


Procesar documentos:

Colocar los archivos PDF en storage/docs_raw/

Llamar al endpoint /upload-all/ (vía Swagger UI o cliente API)

Consultar el RAG

El endpoint /chat/ permite realizar consultas semánticas:

{
  "question": "Dame un resumen del protocolo de bienvenida"
}


Consideraciones actuales:

Soporte actual: solo PDFs

OCR automático para PDFs escaneados

Embeddings configurables (Gemini o HuggingFace)

Generación de respuestas: Gemini o OpenAI

Selector de modelos: EmbeddingSelector y GenerationSelector

Subida masiva de documentos: /upload-all/

Requisitos para Windows:

Instalar Tesseract OCR.