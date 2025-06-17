


RAG API - Sistema de Asistente Documental con FastAPI
Este proyecto implementa un sistema completo RAG (Retrieval Augmented Generation) para asistencia documental interna, pensado inicialmente para onboarding de personal RRHH y consultas sobre documentación interna.

La arquitectura permite cargar documentos, procesarlos con embeddings semánticos, almacenarlos en un índice vectorial (FAISS), y realizar consultas sobre el contenido de forma interactiva vía API.

Tecnologías usadas
FastAPI (backend principal)

FAISS (almacenamiento vectorial)

HuggingFace sentence-transformers (embeddings)

Gemini API (embeddings y generación de texto)

OpenAI API (generación de texto)

PyMuPDF (lectura de PDFs)

pytesseract (OCR integrado para PDFs escaneados)

Pillow (procesamiento de imágenes para OCR)

Estructura del proyecto


│idearium_rag_fastapi/
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
│   │   ├── openai_embedder.py (sin configurar)
│   │   └── openai_generator.py
│   ├── routers/
│   │   ├── chat.py
│   │   ├── download.py
│   │   └── upload.py
│   └── services/
│       ├── file_parser.py
│       ├── model_selector.py
│       ├── text_splitter.py
│       └── vector_store.py
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


Flujo de trabajo
Los documentos se colocan manualmente en storage/docs_raw/.

El endpoint /upload-all/ procesa todos los PDFs (incluyendo subcarpetas).

Si un PDF es escaneado, se activa automáticamente el OCR.

El texto extraído se convierte en embeddings.

Los embeddings se almacenan en FAISS junto con los metadatos.

Las consultas se realizan vía /chat/, con recuperación contextual sobre los documentos cargados.

Ejecución del proyecto
1. Instalar dependencias

pip install -r requirements.txt
2. Configurar las API Keys
Crear el archivo secret_keys.json con el siguiente formato:

json
Copiar
Editar
{
  "GEMINI_API_KEY": "tu_clave_gemini",
  "HUGGINGFACE_API_KEY": "tu_clave_huggingface",
  "OPENAI_API_KEY": "tu_clave_openai"
}
Nota: Corregir el pequeño typo de la clase SecretKeys si es necesario.

3. Arrancar FastAPI
Desde la raíz del proyecto:
uvicorn main:app --reload
La documentación Swagger UI estará disponible en:


http://127.0.0.1:8000/docs
Gestión del índice vectorial
Resetear FAISS antes de cada nueva carga (opcional durante pruebas)
Para limpiar el índice vectorial:

python -m app.admin.reset_vector_store
Esto deja el vector store vacío para cargar nuevos documentos desde cero.

Procesar documentos
Una vez colocados los PDFs en storage/docs_raw/:

Llamar al endpoint /upload-all/ desde Swagger UI o desde cualquier cliente API.

El sistema procesará todos los PDFs, incluyendo subcarpetas.

Consultar el RAG
El endpoint /chat/ permite realizar consultas sobre los documentos cargados.

Ejemplo de payload:


{
  "question": "Dame un resumen del protocolo de bienvenida"
}
Consideraciones actuales
Soporte actual de documentos: solo PDFs.

OCR automático activado para PDFs escaneados.

Embeddings configurables vía EmbeddingSelector (Gemini o HuggingFace).

Generación de respuestas configurable vía GenerationSelector (Gemini o OpenAI).

Selección de modelo vía variables de entorno o configuración.

Subida de documentos masiva gestionada por el endpoint /upload-all/.

Próximos pasos:
Implementación de frontend simple para permitir subida de documentos sin intervención directa.

Soporte para nuevos formatos: Word, Excel, TXT.

Gestión incremental del vector store (eliminar documentos individualmente).

Sistema de logs de auditoría y control de respuestas.

Requisitos previos para Windows
Instalar Tesseract OCR y asegurarse de tener cargado el fichero spa.traineddata en el directorio tessdata.

Ajustar en file_parser.py las rutas de:

python

pytesseract.pytesseract.tesseract_cmd = r"C:\Program Files\Tesseract-OCR\tesseract.exe"
os.environ["TESSDATA_PREFIX"] = r"C:\Program Files\Tesseract-OCR\tessdata"
